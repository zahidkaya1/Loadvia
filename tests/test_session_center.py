import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QMessageBox

from src.session_center_dialog import SessionCenterDialog

app = QApplication.instance() or QApplication([])


class TestSessionCenterDialog(unittest.TestCase):
    @patch("src.session_center_dialog.SessionManager")
    def test_dialog_init(self, mock_sm_class):
        mock_sm = mock_sm_class.return_value
        mock_sm.get_platform_statuses.return_value = []

        dialog = SessionCenterDialog()
        # Ensure scroll area layout has one stretch
        self.assertEqual(dialog.cards_layout.count(), 1)

    @patch("src.session_center_dialog.SessionManager")
    @patch("src.session_center_dialog.AppMessageDialog")
    @patch("src.session_center_dialog.QMessageBox.question")
    def test_remove_session(self, mock_qmsgbox, mock_msg_dlg, mock_sm_class):
        mock_sm = mock_sm_class.return_value
        mock_sm.get_platform_statuses.return_value = []
        mock_qmsgbox.return_value = QMessageBox.Yes

        dialog = SessionCenterDialog()
        dialog._remove_session()

        mock_sm.remove_session.assert_called_once()
        mock_msg_dlg.return_value.exec.assert_called_once()

    def test_browser_selection_dialog_constructs_without_attribute_error(self):
        from pathlib import Path

        from src.browser_sessions import BrowserProfileCandidate
        from src.session_center_dialog import BrowserSelectionDialog

        # Test case 1: Empty browsers
        try:
            dialog1 = BrowserSelectionDialog([])
            self.assertFalse(dialog1.btn_ok.isEnabled())
        except AttributeError as e:
            self.fail(
                f"BrowserSelectionDialog raised AttributeError on empty browsers: {e}"
            )

        # Test case 2: Browser with profiles
        prof = BrowserProfileCandidate(
            browser="chrome",
            profile_name="Default",
            profile_path=Path("/fake/path"),
            display_name="Default",
            priority=1,
        )
        dialog3 = BrowserSelectionDialog([prof])
        self.assertTrue(dialog3.btn_ok.isEnabled())
        self.assertEqual(dialog3.browser_combo.count(), 1)
        self.assertEqual(dialog3.profile_combo.count(), 1)

    @patch("src.session_center_dialog.is_browser_running")
    @patch("src.session_center_dialog.close_browser_gracefully")
    @patch("src.session_center_dialog.force_kill_browser")
    @patch("src.session_center_dialog.SessionManager")
    def test_browser_error_dialog_graceful_close(
        self, mock_sm_class, mock_force, mock_close, mock_is_running
    ):
        from src.session_center_dialog import BrowserErrorDialog

        # Setup mocks
        # _on_retry will check is_browser_running:
        # 1st call: True (so it tries to close)
        # 2nd call: False (so it succeeds without force kill)
        mock_is_running.side_effect = [True, False]

        dialog = BrowserErrorDialog("chrome", "Google Chrome", "Error message")
        dialog._wait_and_process_events = lambda x: None  # mock wait
        dialog._on_retry()

        mock_close.assert_called_once_with("chrome")
        mock_force.assert_not_called()
        self.assertEqual(dialog.action_taken, "retry")

    @patch("src.session_center_dialog.QMessageBox.question")
    @patch("src.session_center_dialog.is_browser_running")
    @patch("src.session_center_dialog.close_browser_gracefully")
    @patch("src.session_center_dialog.force_kill_browser")
    @patch("src.session_center_dialog.SessionManager")
    def test_browser_error_dialog_force_kill(
        self, mock_sm_class, mock_force, mock_close, mock_is_running, mock_question
    ):
        from PySide6.QtWidgets import QMessageBox

        from src.session_center_dialog import BrowserErrorDialog

        # Setup mocks
        # 1st call: True (needs close)
        # 2nd call: True (close failed, needs force)
        mock_is_running.side_effect = [True, True]
        mock_question.return_value = QMessageBox.Yes

        dialog = BrowserErrorDialog("chrome", "Google Chrome", "Error message")
        dialog._wait_and_process_events = lambda x: None  # mock wait
        dialog._on_retry()

        mock_close.assert_called_once_with("chrome")
        mock_force.assert_called_once_with("chrome")
        self.assertEqual(dialog.action_taken, "retry")

    @patch("src.session_center_dialog.QMessageBox.question")
    @patch("src.session_center_dialog.is_browser_running")
    @patch("src.session_center_dialog.close_browser_gracefully")
    @patch("src.session_center_dialog.force_kill_browser")
    @patch("src.session_center_dialog.SessionManager")
    def test_browser_error_dialog_force_kill_rejected(
        self, mock_sm_class, mock_force, mock_close, mock_is_running, mock_question
    ):
        from PySide6.QtWidgets import QMessageBox

        from src.session_center_dialog import BrowserErrorDialog

        # Setup mocks
        # 1st call: True (needs close)
        # 2nd call: True (close failed, needs force)
        mock_is_running.side_effect = [True, True]
        mock_question.return_value = QMessageBox.No

        dialog = BrowserErrorDialog("chrome", "Google Chrome", "Error message")
        dialog._wait_and_process_events = lambda x: None  # mock wait
        dialog._on_retry()

        mock_close.assert_called_once_with("chrome")
        mock_force.assert_not_called()
        self.assertNotEqual(dialog.action_taken, "retry")

    @patch("src.session_center_dialog.CookieFileImportDialog")
    @patch("src.session_center_dialog.CookieHelpDialog")
    @patch("src.session_center_dialog.QFileDialog.getOpenFileName")
    @patch("src.session_center_dialog.QMessageBox")
    def test_cookie_import_flow(
        self,
        mock_msg_class,
        mock_get_file,
        mock_help_class,
        mock_import_class,
    ):
        mock_import_inst = mock_import_class.return_value
        mock_help_inst = mock_help_class.return_value
        mock_msg_inst = mock_msg_class.return_value

        # Setup QMessageBox buttons
        btn_help = "help_btn"
        btn_retry = "retry_btn"
        btn_cancel = "cancel_btn"
        mock_msg_inst.addButton.side_effect = [btn_help, btn_retry, btn_cancel]

        dialog = SessionCenterDialog()

        # Test 1: Button text
        self.assertEqual(dialog.btn_file.text(), "Çerez Dosyasıyla Al")

        # Test 2: Cancel from CookieFileImportDialog
        mock_import_inst.exec.return_value = 0  # Reject
        dialog._import_file()
        mock_get_file.assert_not_called()

        # Test 3: "Nasıl Hazırlanır?" -> "Geri" (Cancel from Help)
        mock_import_inst.exec.return_value = 1
        mock_import_inst.action_taken = "help"

        mock_help_inst.exec.return_value = 0
        mock_help_inst.action_taken = "back"

        dialog._import_file()
        mock_get_file.assert_not_called()

        # Test 4: "Nasıl Hazırlanır?" -> "Dosyam Hazır - Dosya Seç" -> File Picker Cancel
        mock_import_inst.exec.return_value = 1
        mock_import_inst.action_taken = "help"

        mock_help_inst.exec.return_value = 1
        mock_help_inst.action_taken = "file"

        mock_get_file.return_value = ("", "")  # Cancelled
        dialog._import_file()
        mock_get_file.assert_called_once()
        mock_get_file.reset_mock()

        # Test 5: "Dosya Seç" -> File Picker Success -> Invalid File
        mock_import_inst.exec.return_value = 1
        mock_import_inst.action_taken = "file"

        mock_get_file.return_value = ("fake_invalid.txt", "")

        # Setup invalid import
        dialog.manager.import_from_cookie_file = lambda p: (False, "Invalid format")

        # Simulate "İptal" on Error Dialog
        mock_msg_inst.clickedButton.return_value = btn_cancel

        dialog._import_file()
        mock_get_file.assert_called_once()
        mock_msg_inst.exec.assert_called_once()

        mock_get_file.reset_mock()
        mock_msg_inst.exec.reset_mock()

        # Test 6: "Dosya Seç" -> File Picker Success -> Valid File
        mock_import_inst.exec.return_value = 1
        mock_import_inst.action_taken = "file"

        mock_get_file.return_value = ("fake_valid.txt", "")

        # Setup valid import
        dialog.manager.import_from_cookie_file = lambda p: (True, "Success")
        dialog.manager.store.load_session_payload = lambda: {
            "source_type": "cookie_file",
            "imported_at": "Şimdi",
        }

        class DummyStatus:
            session_available = True
            display_name = "Threads"
            downloadable = True

            class State:
                value = "Bağlı"

            state = State()

        dialog.manager.get_platform_statuses = lambda: [DummyStatus()]  # dummy

        dialog._import_file()
        mock_get_file.assert_called_once()

        # Ensure UI updated properly
        self.assertIn("Kaynak: Çerez Dosyası", dialog.lbl_active_session.text())

    def test_cookie_help_dialog_content(self):
        from PySide6.QtWidgets import QLabel

        from src.session_center_dialog import CookieHelpDialog

        dialog = CookieHelpDialog()

        # Test steps
        steps_text = dialog.findChildren(QLabel)[1].text()
        self.assertIn("Adımlar:", steps_text)
        self.assertIn("1. Tarayıcınızda", steps_text)
        self.assertIn("2. Tarayıcınızdan cookies.txt", steps_text)

        # Test security text and styling
        sec_label = dialog.findChildren(QLabel)[2]
        sec_text = sec_label.text()
        self.assertIn("Güvenlik", sec_text)
        self.assertIn("hassas oturum", sec_text)
        self.assertIn("paylaşmayın", sec_text)
        self.assertNotIn("Cookie Hijacking", sec_text)
        self.assertNotIn("DPAPI", sec_text)

        # Verify hardcoded HEX is removed and theme objectName is used
        self.assertNotIn("#ef4444", sec_label.styleSheet())
        self.assertEqual(sec_label.objectName(), "warningText")
