"""Oturum verilerinin yonetimi (Firefox/Cookie File import, test, temp file)."""

import contextlib
import datetime
import os
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yt_dlp.cookies

from src.session_store import SessionStore

ALLOWED_DOMAINS = {
    "threads.com",
    ".threads.com",
    "threads.net",
    ".threads.net",
    "instagram.com",
    ".instagram.com",
}


def _is_domain_allowed(domain: str) -> bool:
    d = domain.lower()
    return d in ALLOWED_DOMAINS or any(
        d.endswith("." + allowed) for allowed in ALLOWED_DOMAINS
    )


class ConnectionState(Enum):
    AVAILABLE_NO_SESSION = "Oturum gerekmiyor"
    CONNECTED = "Bağlı"
    SESSION_REQUIRED = "Oturum gerekli"
    SESSION_EXPIRED = "Oturum yenilenmeli"
    UNSUPPORTED = "Desteklenmiyor"
    CHECKING = "Kontrol ediliyor"
    ERROR = "Kontrol edilemedi"


@dataclass
class PlatformSessionStatus:
    platform: str
    display_name: str
    supported: bool
    downloadable: bool
    session_required: bool
    session_available: bool
    session_valid: bool
    session_source: str
    cookie_count: int
    state: ConnectionState


PLATFORM_MATRIX = {
    "youtube": {
        "display_name": "YouTube",
        "supported": True,
        "downloadable": True,
        "session_required": False,
    },
    "facebook": {
        "display_name": "Facebook",
        "supported": True,
        "downloadable": True,
        "session_required": False,
    },
    "tiktok": {
        "display_name": "TikTok",
        "supported": True,
        "downloadable": True,
        "session_required": False,
    },
    "x_twitter": {
        "display_name": "X / Twitter",
        "supported": True,
        "downloadable": True,
        "session_required": False,
    },
    "instagram": {
        "display_name": "Instagram",
        "supported": True,
        "downloadable": True,
        "session_required": True,
    },
    "threads": {
        "display_name": "Threads",
        "supported": True,
        "downloadable": True,
        "session_required": True,
    },
    "kick": {
        "display_name": "Kick",
        "supported": False,
        "downloadable": False,
        "session_required": False,
    },
}


class SessionManager:
    def __init__(self) -> None:
        self.store = SessionStore()

        local_appdata = os.environ.get("LOCALAPPDATA")
        if not local_appdata:
            local_appdata = str(Path.home() / "AppData" / "Local")

        self.temp_dir = Path(local_appdata) / "Loadvia" / "Temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_stale_temp_files(self) -> None:
        """Kapanistan kalmis olabilecek eski session-*.txt dosyalarini temizler."""
        if not self.temp_dir.exists():
            return
        for child in self.temp_dir.iterdir():
            if (
                child.is_file()
                and child.name.startswith("session-")
                and child.name.endswith(".txt")
            ):
                try:
                    child.unlink()
                except OSError:
                    pass

    def get_session_status(self) -> str:
        """'Yok', 'Bagli', 'Yenilenmeli' gibi temel durum dondurur."""
        data = self.store.load_session()
        if not data:
            return "Oturum yok"
        return "Bağlı"

    def get_platform_statuses(self) -> list[PlatformSessionStatus]:
        """Tüm platformların mevcut cookie durumlarına göre statülerini hesaplar."""
        payload = self.store.load_session_payload()

        cookie_data = payload.get("cookie_data", "") if payload else ""
        source_type = payload.get("source_type", "Bilinmiyor") if payload else ""
        if source_type == "firefox":
            source_type = "Firefox"
        elif source_type == "browser":
            btype = payload.get("browser_type", "")
            disp = {
                "chrome": "Google Chrome",
                "edge": "Microsoft Edge",
                "brave": "Brave",
                "opera": "Opera",
                "vivaldi": "Vivaldi",
                "firefox": "Firefox",
                "opera_gx": "Opera GX",
            }.get(btype, btype.title())
            source_type = disp
        elif source_type == "cookie_file":
            source_type = "Çerez Dosyası"

        lines = cookie_data.strip().split("\n")

        threads_count = 0
        instagram_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                host = parts[0].lower()
                if "threads" in host:
                    threads_count += 1
                elif "instagram" in host:
                    instagram_count += 1

        threads_connected = threads_count > 0 or instagram_count > 0
        instagram_connected = instagram_count > 0

        # Orijinal listedeki sirayi korumak adina (Threads basta vs) listeyi kendi siralayalim.
        # Amac: "Threads", "Instagram", "YouTube", "Facebook", "TikTok", "X / Twitter", "Kick" sirasi
        order = [
            "threads",
            "instagram",
            "youtube",
            "facebook",
            "tiktok",
            "x_twitter",
            "kick",
        ]

        statuses = []
        for key in order:
            config = PLATFORM_MATRIX[key]
            st = PlatformSessionStatus(
                platform=key,
                display_name=config["display_name"],
                supported=config["supported"],
                downloadable=config["downloadable"],
                session_required=config["session_required"],
                session_available=False,
                session_valid=False,
                session_source=source_type if payload else "",
                cookie_count=0,
                state=ConnectionState.AVAILABLE_NO_SESSION,
            )

            if not st.supported:
                st.state = ConnectionState.UNSUPPORTED
                st.downloadable = False
                statuses.append(st)
                continue

            if key == "threads":
                st.session_available = threads_connected
                st.session_valid = threads_connected
                st.cookie_count = threads_count + (
                    instagram_count if threads_count == 0 else 0
                )
                st.state = (
                    ConnectionState.CONNECTED
                    if threads_connected
                    else ConnectionState.SESSION_REQUIRED
                )

            elif key == "instagram":
                st.session_available = instagram_connected
                st.session_valid = instagram_connected
                st.cookie_count = instagram_count
                st.state = (
                    ConnectionState.CONNECTED
                    if instagram_connected
                    else ConnectionState.SESSION_REQUIRED
                )

            else:
                st.state = ConnectionState.AVAILABLE_NO_SESSION

            statuses.append(st)

        return statuses

    def import_from_browser(
        self, browser_type: str, profile_name: str
    ) -> tuple[bool, str]:
        """yt-dlp yardımıyla seçilen tarayıcı ve profilden instagram/threads çerezlerini alır."""
        yt_browser_type = browser_type
        yt_profile = profile_name

        if browser_type == "opera_gx":
            yt_browser_type = "opera"
            from src.browser_sessions import detect_available_browser_profiles

            for p in detect_available_browser_profiles():
                if p.browser == "opera_gx" and p.profile_name == profile_name and p.profile_path:
                    yt_profile = str(p.profile_path)
                    break

        try:
            jar = yt_dlp.cookies.extract_cookies_from_browser(
                yt_browser_type, yt_profile
            )
        except Exception:  # noqa: BLE001
            disp = {
                "chrome": "Google Chrome",
                "edge": "Microsoft Edge",
                "brave": "Brave",
                "opera": "Opera",
                "vivaldi": "Vivaldi",
                "firefox": "Firefox",
            }.get(browser_type, browser_type.title())
            return (
                False,
                f"{disp} oturum verileri okunamadı.\n\nTarayıcıyı tamamen kapatıp tekrar deneyebilir veya\nÇerez Dosyası Seç yöntemini kullanabilirsiniz.",
            )

        cookies_found = []
        for cookie in jar:
            if _is_domain_allowed(cookie.domain):
                cookies_found.append(cookie)

        if not cookies_found:
            return False, "Tarayıcıda uygun Threads veya Instagram oturumu bulunamadı."

        # Netscape formatina cevir
        netscape_lines = ["# Netscape HTTP Cookie File", "# Generated by Loadvia", ""]
        for cookie in cookies_found:
            host = cookie.domain
            path = cookie.path or "/"
            is_secure = "TRUE" if cookie.secure else "FALSE"
            expiry = str(cookie.expires or 0)
            name = cookie.name
            value = cookie.value

            # domain_flag: TRUE if domain starts with dot, FALSE otherwise
            domain_flag = "TRUE" if host.startswith(".") else "FALSE"

            line = (
                f"{host}\t{domain_flag}\t{path}\t{is_secure}\t{expiry}\t{name}\t{value}"
            )
            netscape_lines.append(line)

        metadata = {
            "source_type": "browser",
            "browser_type": browser_type,
            "browser_profile": profile_name,
            "imported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "allowed_domains": list(ALLOWED_DOMAINS),
        }
        self.store.save_session("\n".join(netscape_lines) + "\n", metadata)

        disp = {
            "chrome": "Google Chrome",
            "edge": "Microsoft Edge",
            "brave": "Brave",
            "opera": "Opera",
            "vivaldi": "Vivaldi",
            "firefox": "Firefox",
        }.get(browser_type, browser_type.title())
        return True, f"{disp} oturumu başarıyla içe aktarıldı."

    def import_from_firefox(self, profile_name: str | None = None) -> tuple[bool, str]:
        """Geriye dönük uyumluluk wrapper'ı"""
        if not profile_name:
            profile_name = "default-release"
        return self.import_from_browser("firefox", profile_name)

    def import_from_cookie_file(self, file_path: str | Path) -> tuple[bool, str]:
        """Netscape dosyasindan sadece izin verilen alan adlarini alip kaydeder."""
        path = Path(file_path)
        if not path.exists():
            return False, "Dosya bulunamadı."

        netscape_lines = ["# Netscape HTTP Cookie File", "# Imported by Loadvia", ""]
        valid_cookie_count = 0

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue

                    parts = stripped.split("\t")
                    if len(parts) >= 7:
                        host = parts[0]
                        if _is_domain_allowed(host):
                            netscape_lines.append(stripped)
                            valid_cookie_count += 1

            if valid_cookie_count == 0:
                return False, "Dosyada uygun Threads veya Instagram oturumu bulunamadı."

            metadata = {
                "source_type": "cookie_file",
                "imported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "allowed_domains": list(ALLOWED_DOMAINS),
            }
            self.store.save_session("\n".join(netscape_lines) + "\n", metadata)
            return True, "Çerez dosyası başarıyla içe aktarıldı."
        except Exception as exc:  # noqa: BLE001
            return False, f"Dosya okunamadı: {exc}"

    def remove_session(self) -> None:
        self.store.delete_session()

    def test_session(self) -> str:
        """
        Oturumun gecerliligini test eder.
        Dondurecegi degerler: 'Gecerli', 'Gecersiz', 'Oturum Yok', 'Ag Hatasi'
        Bu test icin aslinda kucuk bir request (urllib ile instagram anasayfasina veya threads'e) yapilabilir.
        Ancak basitce cookie iceriginde ds_user_id veya sessionid var mi diye de bakilabilir.
        Simdilik 'sessionid' cookie'si var mi diye icerigine bakalim. (Ag testi karmasikligi engellemek icin)
        """
        data = self.store.load_session()
        if not data:
            return "Oturum Yok"

        if "sessionid" in data:
            return "Geçerli"
        else:
            return "Geçersiz"

    @contextlib.contextmanager
    def create_temp_cookiefile(self):
        """
        yt-dlp icin gecici cookiefile olusturur ve yields eder.
        Kullanim:
        with session_mgr.create_temp_cookiefile() as cookie_path:
            if cookie_path:
                ydl_opts['cookiefile'] = cookie_path
        """
        data = self.store.load_session()
        if not data:
            yield None
            return

        temp_file = self.temp_dir / f"session-{uuid.uuid4().hex}.txt"

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(data)

            yield str(temp_file)
        finally:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
