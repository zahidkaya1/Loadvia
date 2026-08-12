from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QDialog

from src.models import MediaItem, MediaMetadata, MediaType


def test_main_window_carousel_selector_rejected_stops_download(main_window, monkeypatch):
    """If MediaSelectorDialog is rejected, download should not start."""
    # Setup a metadata that triggers carousel
    meta = MediaMetadata(
        webpage_url="https://www.instagram.com/p/12345678901",
        title="Carousel",
        media_items=[
            MediaItem(media_type=MediaType.IMAGE, index=0, url="http://img1"),
            MediaItem(media_type=MediaType.IMAGE, index=1, url="http://img2")
        ]
    )
    main_window.url_input.setText("https://www.instagram.com/p/12345678901")
    main_window._current_metadata = meta
    
    with patch("src.media_selector_dialog.MediaSelectorDialog") as MockDialog:
        mock_instance = MockDialog.return_value
        mock_instance.exec.return_value = QDialog.DialogCode.Rejected
        
        with patch.object(main_window, "_set_ui_downloading") as mock_set_ui:
            main_window.start_download()
            
            assert mock_instance.exec.call_count == 1
            # Download should not proceed, meaning UI state is not updated to downloading
            assert mock_set_ui.call_count == 0


@pytest.mark.parametrize("media_items", [
    [], # Empty fallback
    [MediaItem(media_type=MediaType.IMAGE, index=0, url="http://img1")], # Single IMAGE
    [MediaItem(media_type=MediaType.VIDEO, index=0, url="http://vid1")]  # Single VIDEO
])
def test_main_window_carousel_selector_single_media_regression(main_window, monkeypatch, media_items):
    """MediaSelectorDialog should not open for single media items or empty items."""
    meta = MediaMetadata(
        webpage_url="https://www.instagram.com/p/12345678901",
        title="Post",
        media_items=media_items
    )
    main_window.url_input.setText("https://www.instagram.com/p/12345678901")
    main_window._current_metadata = meta
    
    with (
        patch("src.media_selector_dialog.MediaSelectorDialog") as MockDialog,
        patch.object(main_window, "_set_ui_downloading") as mock_set_ui,
        patch("src.download_worker.DownloadWorker.run")
    ):
        main_window.start_download()

        # Dialog should NOT be instantiated or called
        assert MockDialog.call_count == 0
        # Download should proceed normally
        assert mock_set_ui.call_count == 1
