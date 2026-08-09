"""Smoke tests for application imports to prevent startup regressions."""


def test_session_manager_public_import():
    from src.session_manager import SessionManager

    assert SessionManager is not None


def test_metadata_worker_import():
    from src.metadata_worker import MetadataWorker

    assert MetadataWorker is not None


def test_download_worker_import():
    from src.download_worker import DownloadWorker

    assert DownloadWorker is not None


def test_main_window_import():
    from src.main_window import MainWindow

    assert MainWindow is not None
