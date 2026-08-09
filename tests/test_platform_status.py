"""Tests for the new PlatformSessionStatus and ConnectionState logic."""

from src.session_manager import PLATFORM_MATRIX, ConnectionState, SessionManager


def test_platform_capabilities():
    # Matrix varligi ve dogruluk
    assert PLATFORM_MATRIX["youtube"]["supported"] is True
    assert PLATFORM_MATRIX["youtube"]["session_required"] is False
    assert PLATFORM_MATRIX["kick"]["supported"] is False


def test_get_platform_statuses_no_session(monkeypatch):
    mgr = SessionManager()
    monkeypatch.setattr(mgr.store, "load_session_payload", lambda: None)

    statuses = mgr.get_platform_statuses()

    # 7 platform dönmeli
    assert len(statuses) == 7

    # Kick desteklenmiyor olmali
    kick = next(s for s in statuses if s.platform == "kick")
    assert kick.state == ConnectionState.UNSUPPORTED
    assert kick.downloadable is False

    # Youtube oturum gerektirmemeli
    yt = next(s for s in statuses if s.platform == "youtube")
    assert yt.state == ConnectionState.AVAILABLE_NO_SESSION
    assert yt.downloadable is True

    # Threads oturum gerektiriyor, bagli degil
    th = next(s for s in statuses if s.platform == "threads")
    assert th.state == ConnectionState.SESSION_REQUIRED
    assert th.session_available is False


def test_get_platform_statuses_with_threads_cookie(monkeypatch):
    mgr = SessionManager()
    payload = {
        "cookie_data": "threads.com\tTRUE\t/\tTRUE\t1234\tsessionid\tabcd",
        "source_type": "firefox",
    }
    monkeypatch.setattr(mgr.store, "load_session_payload", lambda: payload)

    statuses = mgr.get_platform_statuses()
    th = next(s for s in statuses if s.platform == "threads")

    assert th.state == ConnectionState.CONNECTED
    assert th.session_available is True
    assert th.session_source == "Firefox"
    assert th.cookie_count == 1

    # Instagram'i sadece threads cookie'si ile baglamiyoruz
    ig = next(s for s in statuses if s.platform == "instagram")
    assert ig.state == ConnectionState.SESSION_REQUIRED
