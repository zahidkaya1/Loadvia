"""Tests for the new multi-browser import capabilities using yt-dlp."""

from unittest.mock import MagicMock, patch

from src.browser_sessions import detect_available_browser_profiles
from src.session_manager import SessionManager


@patch("src.browser_sessions.Path.exists")
@patch("src.browser_sessions.os.environ.get")
@patch("src.browser_sessions.configparser.ConfigParser.read")
def test_detect_browsers(mock_read, mock_env, mock_exists):
    mock_env.return_value = "C:\\MockAppData"

    def side_effect():
        # MagicMock.__bool__ can't be set by side_effect for Path object easily,
        # so we patch path exists directly.
        pass

    # Simple mock that makes all paths appear to exist
    mock_exists.return_value = True

    browsers = detect_available_browser_profiles()
    assert len(browsers) > 0

    chrome_profiles = [b for b in browsers if b.browser == "chrome"]
    assert len(chrome_profiles) > 0


@patch("yt_dlp.cookies.extract_cookies_from_browser")
def test_import_from_browser_success(mock_extract):
    mock_jar = MagicMock()
    mock_cookie = MagicMock()
    mock_cookie.domain = "instagram.com"
    mock_cookie.path = "/"
    mock_cookie.secure = True
    mock_cookie.expires = 0
    mock_cookie.name = "sessionid"
    mock_cookie.value = "test_value"

    mock_jar.__iter__.return_value = [mock_cookie]
    mock_extract.return_value = mock_jar

    manager = SessionManager()
    manager.store = MagicMock()

    success, msg = manager.import_from_browser("chrome", "Default")
    assert success is True
    assert "Chrome" in msg
    manager.store.save_session.assert_called_once()


@patch("yt_dlp.cookies.extract_cookies_from_browser")
def test_import_from_browser_fail_preserves_session(mock_extract):
    import yt_dlp.cookies

    mock_extract.side_effect = yt_dlp.cookies.CookieLoadError("locked")

    manager = SessionManager()
    manager.store = MagicMock()

    success, msg = manager.import_from_browser("chrome", "Default")
    assert success is False
    assert "okunamadı" in msg
    # Should not call save if it fails, thus preserving existing session
    manager.store.save_session.assert_not_called()


@patch("yt_dlp.cookies.extract_cookies_from_browser")
def test_import_from_browser_domain_filtering(mock_extract):
    mock_jar = MagicMock()
    mock_cookie1 = MagicMock()
    mock_cookie1.domain = "google.com"

    mock_cookie2 = MagicMock()
    mock_cookie2.domain = "instagram.com"

    mock_jar.__iter__.return_value = [mock_cookie1, mock_cookie2]
    mock_extract.return_value = mock_jar

    manager = SessionManager()
    manager.store = MagicMock()

    success, _ = manager.import_from_browser("chrome", "Default")
    assert success is True

    # Check that save_session was called, and google.com is NOT in the saved data
    args, _ = manager.store.save_session.call_args
    saved_data = args[0]
    assert "instagram.com" in saved_data
    assert "google.com" not in saved_data
