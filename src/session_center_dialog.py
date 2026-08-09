"""Oturum Merkezi kullanici arayuzu dialogu."""

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.dialogs import AppMessageDialog
from src.session_manager import ConnectionState, SessionManager


class PlatformCard(QWidget):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Sadece border ekleyip arkaplani temaya birakiyoruz.
        self.setObjectName("PlatformCard")
        self.setStyleSheet(
            "#PlatformCard { border: 1px solid #64748b; border-radius: 6px; }"
        )

        # Header
        name_label = QLabel(f"<b>{status.display_name}</b>")
        layout.addWidget(name_label)

        # State
        state_label = QLabel(f"● {status.state.value}")
        if status.state == ConnectionState.CONNECTED:
            state_label.setStyleSheet("color: #16a34a; font-weight: bold;")
        elif status.state == ConnectionState.AVAILABLE_NO_SESSION:
            state_label.setStyleSheet("color: #3b82f6; font-weight: bold;")
        elif status.state in (
            ConnectionState.SESSION_REQUIRED,
            ConnectionState.SESSION_EXPIRED,
        ):
            state_label.setStyleSheet("color: #eab308; font-weight: bold;")
        elif status.state == ConnectionState.UNSUPPORTED:
            state_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        else:
            state_label.setStyleSheet("font-weight: bold;")

        layout.addWidget(state_label)

        # Downloadable
        if status.downloadable:
            dl_label = QLabel("İndirilebilir")
            dl_label.setStyleSheet("color: #16a34a;")
        else:
            dl_label = QLabel("İndirilemez")
            dl_label.setStyleSheet("color: #ef4444;")

        layout.addWidget(dl_label)


import time

from PySide6.QtWidgets import QApplication

from src.browser_sessions import (
    close_browser_gracefully,
    detect_available_browser_profiles,
    force_kill_browser,
    is_browser_running,
)


class CookieHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Çerez Dosyası Nasıl Hazırlanır?")
        self.setMinimumWidth(450)
        self.action_taken = "back"

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(
            "cookies.txt, tarayıcınızdaki oturum bilgilerini içeren bir dosyadır.\n"
            "Loadvia bu dosyadan yalnız Threads ve Instagram için gerekli oturum\n"
            "bilgilerini alır."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        steps = QLabel(
            "<b>Adımlar:</b>\n\n"
            "1. Tarayıcınızda Threads veya Instagram hesabınıza giriş yapın.\n\n"
            "2. Tarayıcınızdan cookies.txt biçiminde bir çerez dosyası dışa aktarın.\n\n"
            "3. Tarayıcınızda bu özellik yerleşik olarak bulunmuyorsa güvenilir bir\n"
            "   cookies.txt dışa aktarma aracı veya tarayıcı eklentisi kullanmanız\n"
            "   gerekebilir.\n\n"
            "4. Oluşturulan .txt dosyasını bilgisayarınızda güvenli bir yerde saklayın.\n\n"
            "5. Loadvia'ya dönerek:\n"
            "   Çerez Dosyasıyla Al → Dosya Seç\n"
            "   yolunu kullanın."
        )
        steps.setWordWrap(True)
        layout.addWidget(steps)

        sec = QLabel(
            "<b>Güvenlik</b>\n\n"
            "Çerez dosyanız hesabınıza erişim sağlayabilecek hassas oturum\n"
            "bilgileri içerebilir.\n\n"
            "• Dosyayı başkalarıyla paylaşmayın.\n"
            "• İnternet sitelerine yüklemeyin.\n"
            "• İşiniz bittikten sonra güvenli şekilde saklayın veya silin.\n\n"
            "Loadvia kalıcı olarak yalnız Threads ve Instagram için gerekli\n"
            "oturum bilgilerini saklar."
        )
        sec.setObjectName("warningText")
        sec.setWordWrap(True)
        layout.addWidget(sec)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Geri")
        self.btn_cancel.setObjectName("dialogSecondaryButton")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ready = QPushButton("Dosyam Hazır - Dosya Seç")
        self.btn_ready.setObjectName("dialogPrimaryButton")
        self.btn_ready.clicked.connect(self._on_ready)

        btn_layout.addWidget(self.btn_ready)
        btn_layout.addWidget(self.btn_cancel)

        layout.addSpacing(8)
        layout.addLayout(btn_layout)

    def _on_ready(self):
        self.action_taken = "file"
        self.accept()


class CookieFileImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Çerez Dosyasıyla Oturum Alma")
        self.setMinimumWidth(380)
        self.action_taken = "cancel"

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel(
            "Tarayıcıdan otomatik oturum alma çalışmadığında cookies.txt\n"
            "dosyası kullanarak Threads ve Instagram oturumunuzu Loadvia'ya\n"
            "aktarabilirsiniz.\n\n"
            "Henüz bir çerez dosyanız yoksa nasıl hazırlanacağını adım adım\n"
            "görebilirsiniz."
        )
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_help = QPushButton("Nasıl Hazırlanır?")
        self.btn_help.clicked.connect(self._on_help)

        self.btn_ready = QPushButton("Dosya Seç")
        self.btn_ready.setObjectName("dialogPrimaryButton")
        self.btn_ready.clicked.connect(self._on_ready)

        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setObjectName("dialogSecondaryButton")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_help)
        btn_layout.addWidget(self.btn_ready)
        btn_layout.addWidget(self.btn_cancel)

        layout.addSpacing(8)
        layout.addLayout(btn_layout)

    def _on_help(self):
        self.action_taken = "help"
        self.accept()

    def _on_ready(self):
        self.action_taken = "file"
        self.accept()


class BrowserErrorDialog(QDialog):
    def __init__(
        self, browser_type: str, browser_name: str, error_msg: str, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(f"{browser_name} oturum verileri okunamadı")
        self.setMinimumWidth(400)
        self.browser_type = browser_type
        self.browser_name = browser_name
        self.action_taken = "cancel"

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel(
            f"{browser_name} arka planda çalışıyor olabilir.\nOturum verilerini okuyabilmek için tarayıcının tamamen kapatılması gerekebilir."
        )
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_retry = QPushButton(f"{browser_name}'u Kapat ve Tekrar Dene")
        self.btn_retry.setObjectName("dialogPrimaryButton")
        self.btn_retry.clicked.connect(self._on_retry)

        self.btn_file = QPushButton("Çerez Dosyasından Al")
        self.btn_file.clicked.connect(self._on_file)

        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setObjectName("dialogSecondaryButton")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_retry)
        btn_layout.addWidget(self.btn_file)
        btn_layout.addWidget(self.btn_cancel)

        layout.addSpacing(8)
        layout.addLayout(btn_layout)

    def _on_file(self):
        self.action_taken = "file"
        self.accept()

    def _wait_and_process_events(self, ms: int):
        end = time.time() + (ms / 1000.0)
        while time.time() < end:
            QApplication.processEvents()
            time.sleep(0.05)

    def _on_retry(self):
        if not is_browser_running(self.browser_type):
            self.action_taken = "retry"
            self.accept()
            return

        self.btn_retry.setText("Kapatılıyor, lütfen bekleyin...")
        self.btn_retry.setEnabled(False)
        self.btn_file.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        QApplication.processEvents()

        close_browser_gracefully(self.browser_type)
        self._wait_and_process_events(2000)

        if is_browser_running(self.browser_type):
            reply = QMessageBox.question(
                self,
                "Tamamen Kapatılsın mı?",
                f"{self.browser_name} hâlâ arka planda çalışıyor.\n\nTamamen kapatılması açık sekmelerdeki kaydedilmemiş bilgilerin kaybolmasına neden olabilir.\n\n{self.browser_name} tamamen kapatılsın mı?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.btn_retry.setText("Zorla kapatılıyor...")
                QApplication.processEvents()
                force_kill_browser(self.browser_type)
                self._wait_and_process_events(2000)
            else:
                self.btn_retry.setText(f"{self.browser_name}'u Kapat ve Tekrar Dene")
                self.btn_retry.setEnabled(True)
                self.btn_file.setEnabled(True)
                self.btn_cancel.setEnabled(True)
                return

        self.action_taken = "retry"
        self.accept()


class BrowserSelectionDialog(QDialog):
    def __init__(self, browsers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tarayıcı ve Profil Seçimi")
        self.setMinimumWidth(360)
        self.browsers = browsers

        self.selected_browser_type = None
        self.selected_profile_id = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl_desc = QLabel(
            "Lütfen oturum verilerinin alınacağı tarayıcıyı ve profili seçin:"
        )
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        from PySide6.QtWidgets import QComboBox

        from src.utils import configure_combo_box

        self.browser_combo = QComboBox()
        configure_combo_box(self.browser_combo)

        layout.addWidget(QLabel("Tarayıcı:"))
        layout.addWidget(self.browser_combo)

        self.profile_combo = QComboBox()
        configure_combo_box(self.profile_combo)
        layout.addWidget(QLabel("Profil:"))
        layout.addWidget(self.profile_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.setObjectName("dialogSecondaryButton")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Seç")
        self.btn_ok.setObjectName("dialogPrimaryButton")
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)

        layout.addSpacing(8)
        layout.addLayout(btn_layout)

        # Group profiles by browser
        self.browser_map = {}
        for p in self.browsers:
            if p.browser not in self.browser_map:
                self.browser_map[p.browser] = []
            self.browser_map[p.browser].append(p)

        self.browser_combo.blockSignals(True)
        from src.browser_sessions import BROWSER_DEFINITIONS, is_browser_running

        for b_str in self.browser_map.keys():
            defn = BROWSER_DEFINITIONS.get(b_str)
            disp = defn["display_name"] if defn else b_str.title()

            if is_browser_running(b_str):
                self.browser_combo.addItem(f"{disp} (Bulundu — Açık)", b_str)
            else:
                self.browser_combo.addItem(f"{disp} (Bulundu)", b_str)

        self.browser_combo.blockSignals(False)

        self.browser_combo.currentIndexChanged.connect(self._on_browser_changed)
        if self.browser_map:
            self._on_browser_changed(0)

    def _on_browser_changed(self, idx):
        self.profile_combo.clear()
        self.selected_profile_id = None
        self.btn_ok.setEnabled(False)

        b_str = self.browser_combo.itemData(idx)
        if not b_str:
            return

        b_profs = self.browser_map.get(b_str, [])
        for p in b_profs:
            self.profile_combo.addItem(p.display_name, p.profile_name)

        if self.profile_combo.count() > 0:
            self.profile_combo.setCurrentIndex(0)
            self.btn_ok.setEnabled(True)

    def accept(self):
        b_str = self.browser_combo.itemData(self.browser_combo.currentIndex())
        if b_str:
            self.selected_browser_type = b_str
            self.selected_profile_id = self.profile_combo.currentData()
            super().accept()
        else:
            self.reject()


class SessionCenterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oturum Merkezi")
        self.setMinimumSize(400, 600)

        self.manager = SessionManager()

        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Loadvia Oturum Merkezi")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        desc = QLabel(
            "Platformların anlık bağlantı ve indirme destek durumlarını "
            "aşağıdaki listeden takip edebilirsiniz."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(desc)

        # Active Session Panel
        self.active_session_widget = QWidget()
        self.active_session_widget.setStyleSheet(
            "background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px;"
        )
        as_layout = QVBoxLayout(self.active_session_widget)
        as_layout.setContentsMargins(10, 10, 10, 10)
        self.lbl_active_session_title = QLabel("<b>Aktif Oturum</b>")
        self.lbl_active_session = QLabel("Kaydedilmiş oturum yok")
        self.lbl_active_session.setStyleSheet("color: #475569; font-size: 12px;")
        as_layout.addWidget(self.lbl_active_session_title)
        as_layout.addWidget(self.lbl_active_session)
        layout.addWidget(self.active_session_widget)

        # Scroll Area for platform cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")
        self.scroll_area.viewport().setStyleSheet("background-color: transparent;")

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_widget)
        layout.addWidget(self.scroll_area)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_browser = QPushButton("Tarayıcıdan Al")
        self.btn_browser.clicked.connect(self._import_browser)

        self.btn_file = QPushButton("Çerez Dosyasıyla Al")
        self.btn_file.clicked.connect(self._import_file)

        row1 = QHBoxLayout()
        row1.addWidget(self.btn_browser)
        row1.addWidget(self.btn_file)
        btn_layout.addLayout(row1)

        self.btn_refresh = QPushButton("Oturumları Yenile")
        self.btn_refresh.clicked.connect(self._refresh_sessions_action)

        self.btn_test = QPushButton("Oturumu Test Et")
        self.btn_test.clicked.connect(self._test_session)

        row2 = QHBoxLayout()
        row2.addWidget(self.btn_refresh)
        row2.addWidget(self.btn_test)
        btn_layout.addLayout(row2)

        self.btn_remove = QPushButton("Oturum Verilerini Kaldır")
        self.btn_remove.setStyleSheet("color: #ef4444;")
        self.btn_remove.clicked.connect(self._remove_session)
        btn_layout.addWidget(self.btn_remove)

        layout.addLayout(btn_layout)

    def _clear_cards(self):
        # Remove all widgets except the stretch at the end
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _refresh_status(self):
        self._clear_cards()
        statuses = self.manager.get_platform_statuses()

        for st in statuses:
            card = PlatformCard(st)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        has_session = any(st.session_available for st in statuses)

        if has_session:
            payload = self.manager.store.load_session_payload()
            if payload and isinstance(payload, dict):
                from src.utils import format_iso_to_local

                src = payload.get("source_type", "")
                raw_imported_at = payload.get("imported_at", "Bilinmiyor")
                imported_at = format_iso_to_local(raw_imported_at)

                if src == "browser":
                    btype = payload.get("browser_type", "")
                    bprof = payload.get("browser_profile", "")
                    from src.browser_sessions import BROWSER_DEFINITIONS

                    defn = BROWSER_DEFINITIONS.get(btype)
                    disp = defn["display_name"] if defn else btype.title()
                    text = (
                        f"Kaynak: {disp}\nProfil: {bprof}\nİçe aktarma: {imported_at}"
                    )
                elif src == "cookie_file":
                    text = f"Kaynak: Çerez Dosyası\nİçe aktarma: {imported_at}"
                else:
                    text = "Kaynak bilgisi mevcut değil"
                self.lbl_active_session.setText(text)
            else:
                self.lbl_active_session.setText("Kaynak bilgisi mevcut değil")
        else:
            self.lbl_active_session.setText("Kaydedilmiş oturum yok")

        # Enable/Disable buttons based on session presence
        self.btn_refresh.setEnabled(has_session)
        self.btn_test.setEnabled(has_session)
        self.btn_remove.setEnabled(has_session)

    def _import_browser(self):
        profiles = detect_available_browser_profiles()

        if not profiles:
            AppMessageDialog(
                "Hata", "Sistemde desteklenen bir tarayıcı bulunamadı.", "error", self
            ).exec()
            return

        dialog = BrowserSelectionDialog(profiles, self)
        if dialog.exec():
            b_type = dialog.selected_browser_type
            b_prof = dialog.selected_profile_id

            # Initial import
            success, msg = self.manager.import_from_browser(b_type, b_prof)
            if success:
                AppMessageDialog("Başarılı", msg, "success", self).exec()
                self._refresh_status()
                return

            # Error Flow
            disp = {
                "chrome": "Google Chrome",
                "edge": "Microsoft Edge",
                "brave": "Brave",
                "opera": "Opera",
                "vivaldi": "Vivaldi",
                "firefox": "Firefox",
            }.get(b_type, b_type.title())

            err_dialog = BrowserErrorDialog(b_type, disp, msg, self)
            err_dialog.exec()

            if err_dialog.action_taken == "file":
                self._import_file()
            elif err_dialog.action_taken == "retry":
                # Retry exact same import
                success, msg = self.manager.import_from_browser(b_type, b_prof)
                if success:
                    AppMessageDialog(
                        "Başarılı", "Oturum başarıyla alındı.", "success", self
                    ).exec()
                    self._refresh_status()
                else:
                    AppMessageDialog(
                        "Hata", f"{disp} oturum verileri yine okunamadı.", "error", self
                    ).exec()

    def _import_file(self):
        dialog = CookieFileImportDialog(self)
        if not dialog.exec():
            return

        action = dialog.action_taken
        if action == "help":
            self._show_cookie_help()
        elif action == "file":
            self._open_cookie_file_picker()

    def _show_cookie_help(self):
        help_dialog = CookieHelpDialog(self)
        if help_dialog.exec():
            if help_dialog.action_taken == "file":
                self._open_cookie_file_picker()

    def _open_cookie_file_picker(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Çerez Dosyası Seç", "", "Çerez Dosyaları (*.txt);;Tüm Dosyalar (*.*)"
        )
        if not file_path:
            return

        success, msg = self.manager.import_from_cookie_file(file_path)
        if success:
            self._refresh_status()
        else:
            self._show_cookie_error()

    def _show_cookie_error(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Çerez Dosyası Okunamadı")
        msg_box.setText("Seçilen dosya geçerli bir çerez dosyası olarak okunamadı.")
        msg_box.setIcon(QMessageBox.Critical)

        btn_help = msg_box.addButton("Nasıl Hazırlanır?", QMessageBox.ActionRole)
        btn_retry = msg_box.addButton("Başka Dosya Seç", QMessageBox.ActionRole)
        btn_cancel = msg_box.addButton("İptal", QMessageBox.RejectRole)

        msg_box.exec()

        clicked_btn = msg_box.clickedButton()
        if clicked_btn == btn_help:
            self._show_cookie_help()
        elif clicked_btn == btn_retry:
            self._open_cookie_file_picker()

    def _refresh_sessions_action(self):
        payload = self.manager.store.load_session_payload()
        if not payload:
            return

        source = payload.get("source_type", "")
        if source == "browser":
            btype = payload.get("browser_type", "")
            bprof = payload.get("browser_profile", "")
            success, _ = self.manager.import_from_browser(btype, bprof)
            if success:
                AppMessageDialog(
                    "Başarılı", "Oturum başarıyla yenilendi.", "success", self
                ).exec()
            else:
                AppMessageDialog(
                    "Uyarı",
                    "Oturum yenilenemedi. Mevcut kayıt korunuyor.",
                    "error",
                    self,
                ).exec()
            self._refresh_status()
        elif source == "firefox":
            # Geriye dönük uyumluluk
            success, _ = self.manager.import_from_browser("firefox", "default-release")
            if success:
                AppMessageDialog(
                    "Başarılı", "Oturum başarıyla yenilendi.", "success", self
                ).exec()
            else:
                AppMessageDialog(
                    "Uyarı",
                    "Oturum yenilenemedi. Mevcut kayıt korunuyor.",
                    "error",
                    self,
                ).exec()
            self._refresh_status()
        else:
            self._import_file()

    def _test_session(self):
        status = self.manager.test_session()

        payload = self.manager.store.load_session_payload()
        source_info = ""
        if payload:
            from src.utils import format_iso_to_local

            source = payload.get("source_type", "")
            raw_imported_at = payload.get("imported_at", "Bilinmiyor")
            imported_at = format_iso_to_local(raw_imported_at)

            if source == "browser":
                btype = payload.get("browser_type", "")
                disp = {
                    "chrome": "Google Chrome",
                    "edge": "Microsoft Edge",
                    "brave": "Brave",
                    "opera": "Opera",
                    "opera_gx": "Opera GX",
                    "vivaldi": "Vivaldi",
                    "firefox": "Firefox",
                }.get(btype, btype.title())
                bprof = payload.get("browser_profile", "")
                source_info = f"\n\nKaynak: {disp}\nProfil: {bprof}\nİçe aktarma: {imported_at}"
            elif source == "firefox":
                source_info = f"\n\nKaynak: Firefox\nİçe aktarma: {imported_at}"
            else:
                source_info = f"\n\nKaynak: Çerez Dosyası\nİçe aktarma: {imported_at}"

        if status == "Geçerli":
            AppMessageDialog(
                "Test Sonucu", f"Oturum geçerli.{source_info}", "success", self
            ).exec()
        elif status == "Geçersiz":
            AppMessageDialog(
                "Test Sonucu", "Oturum geçersiz. Yenilenmesi gerekiyor.", "error", self
            ).exec()
        else:
            AppMessageDialog("Test Sonucu", f"Durum: {status}", "info", self).exec()

        self._refresh_status()

    def _remove_session(self):
        reply = QMessageBox.question(
            self,
            "Onay",
            "Kaydedilmiş Threads ve Instagram oturum verileri kaldırılacak.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.manager.remove_session()
            AppMessageDialog(
                "Başarılı", "Oturum verileri kaldırıldı.", "success", self
            ).exec()
            self._refresh_status()
