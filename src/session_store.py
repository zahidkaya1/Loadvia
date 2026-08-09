"""Windows DPAPI kullanarak güvenli veri şifreleme ve depolama modülü."""

import ctypes
import os
from ctypes import wintypes
from pathlib import Path

# DPAPI Constants
CRYPTPROTECT_UI_FORBIDDEN = 0x01


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _encrypt_data(data: bytes) -> bytes:
    """Veriyi Windows DPAPI kullanarak kullanici hesabina bagli sifreler."""
    if os.name != "nt":
        raise NotImplementedError("DPAPI sadece Windows uzerinde desteklenir.")

    crypt32 = ctypes.windll.crypt32

    in_blob = DATA_BLOB()
    in_blob.cbData = len(data)
    in_blob.pbData = ctypes.cast(ctypes.c_char_p(data), ctypes.POINTER(ctypes.c_byte))

    out_blob = DATA_BLOB()

    # crypt32.CryptProtectData arguments:
    # pDataIn, szDataDescr, pOptionalEntropy, pvReserved, pPromptStruct, dwFlags, pDataOut
    success = crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )

    if not success:
        raise OSError(
            f"DPAPI sifreleme basarisiz oldu. Hata kodu: {ctypes.GetLastError()}"
        )

    result = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return result


def _decrypt_data(data: bytes) -> bytes:
    """Windows DPAPI ile sifrelenmis veriyi cozer."""
    if os.name != "nt":
        raise NotImplementedError("DPAPI sadece Windows uzerinde desteklenir.")

    crypt32 = ctypes.windll.crypt32

    in_blob = DATA_BLOB()
    in_blob.cbData = len(data)
    in_blob.pbData = ctypes.cast(ctypes.c_char_p(data), ctypes.POINTER(ctypes.c_byte))

    out_blob = DATA_BLOB()

    # crypt32.CryptUnprotectData arguments:
    # pDataIn, ppszDataDescr, pOptionalEntropy, pvReserved, pPromptStruct, dwFlags, pDataOut
    success = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )

    if not success:
        raise OSError(f"DPAPI cozme basarisiz oldu. Hata kodu: {ctypes.GetLastError()}")

    result = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return result


class SessionStore:
    """Oturum verilerini %LOCALAPPDATA% altinda sifreli olarak saklar."""

    def __init__(self) -> None:
        local_appdata = os.environ.get("LOCALAPPDATA")
        if not local_appdata:
            local_appdata = str(Path.home() / "AppData" / "Local")

        self.store_dir = Path(local_appdata) / "Loadvia" / "sessions"
        self.store_file = self.store_dir / "session.dat"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, cookie_data: str, metadata: dict | None = None) -> None:
        """Netscape cookie metnini (ve varsa metadata'yı) sifreleyip kaydeder."""
        if not cookie_data:
            return

        import json

        if metadata:
            payload = {"schema_version": 2, **metadata, "cookie_data": cookie_data}
            data_to_encrypt = json.dumps(payload).encode("utf-8")
        else:
            data_to_encrypt = cookie_data.encode("utf-8")

        encrypted = _encrypt_data(data_to_encrypt)

        with open(self.store_file, "wb") as f:
            f.write(encrypted)

    def load_session(self) -> str | None:
        """Sifreli cookie verisini okur ve cozer."""
        payload = self.load_session_payload()
        if not payload:
            return None
        if isinstance(payload, dict):
            return payload.get("cookie_data")
        return payload

    def load_session_payload(self) -> dict | str | None:
        """Sifreli veriyi okur ve cozer. V2 semasi ise dict, V1 ise string doner."""
        if not self.store_file.exists():
            return None

        try:
            with open(self.store_file, "rb") as f:
                encrypted_data = f.read()

            if not encrypted_data:
                return None

            decrypted = _decrypt_data(encrypted_data)
            decrypted_str = decrypted.decode("utf-8")

            import json

            try:
                payload = json.loads(decrypted_str)
                if isinstance(payload, dict) and payload.get("schema_version") == 2:
                    return payload
            except json.JSONDecodeError:
                pass

            return decrypted_str
        except Exception:  # noqa: BLE001
            # Bozuk veri veya cozulemeyen veri durumunda none don
            return None

    def delete_session(self) -> None:
        """Kayitli oturumu siler."""
        if self.store_file.exists():
            try:
                self.store_file.unlink()
            except OSError:
                pass
