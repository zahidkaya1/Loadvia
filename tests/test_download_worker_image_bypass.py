from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from src.download_worker import DownloadWorker
from src.models import DownloadRequest, MediaItem, MediaType, PlatformType


@pytest.fixture
def mock_execute_image_download():
    with patch("src.download_worker.DownloadWorker._execute_image_download") as mock:
        mock.return_value = Path("C:/fake/path.jpg")
        yield mock


@pytest.fixture
def mock_ytdl():
    with patch("src.download_worker.create_ytdl") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value.__enter__.return_value = mock_instance
        yield mock_instance


def test_download_worker_bypasses_extraction_for_image_only_selection(
    mock_execute_image_download, mock_ytdl
):
    request = DownloadRequest(
        url="https://www.instagram.com/p/image_only_carousel/",
        output_dir=Path("C:/test/out"),
        media_type="T\u00fcm Medyalar",
        quality="En Iyi",
        playlist=True,
        media_items=[
            MediaItem(
                index=0,
                media_type=MediaType.IMAGE,
                url="http://img1.jpg",
                thumbnail="http://thumb1.jpg",
            ),
            MediaItem(
                index=1,
                media_type=MediaType.IMAGE,
                url="http://img2.jpg",
                thumbnail="http://thumb2.jpg",
            ),
        ],
    )
    worker = DownloadWorker(request)
    worker.run()
    mock_ytdl.extract_info.assert_not_called()
    assert mock_execute_image_download.call_count == 2
    call_args1 = mock_execute_image_download.call_args_list[0][0]
    call_args2 = mock_execute_image_download.call_args_list[1][0]
    assert call_args1[0].index == 0
    assert call_args2[0].index == 1


def test_download_worker_bypasses_extraction_for_single_image_selection(
    mock_execute_image_download, mock_ytdl
):
    request = DownloadRequest(
        url="https://www.instagram.com/p/image_only_carousel/",
        output_dir=Path("C:/test/out"),
        media_type="Video (MP4)",  # Simulate user selecting image but media_type was not updated
        quality="En Iyi",
        playlist=False,
        media_items=[
            MediaItem(
                index=1,
                media_type=MediaType.IMAGE,
                url="http://img2.jpg",
                thumbnail="http://thumb2.jpg",
            ),
        ],
    )
    worker = DownloadWorker(request)
    worker.run()

    mock_ytdl.extract_info.assert_not_called()
    mock_ytdl.process_ie_result.assert_not_called()

    assert mock_execute_image_download.call_count == 1
    assert mock_execute_image_download.call_args[0][0].index == 1


def test_download_worker_bypasses_extraction_for_image_only_selection_with_incorrect_media_type(
    mock_execute_image_download, mock_ytdl
):
    # This specifically targets the fix: 2 IMAGE MediaItem with DownloadWorker
    request = DownloadRequest(
        url="https://www.instagram.com/p/image_only_carousel/",
        output_dir=Path("C:/test/out"),
        media_type="Video (MP4)",
        quality="En Iyi",
        playlist=True,
        media_items=[
            MediaItem(
                index=0,
                media_type=MediaType.IMAGE,
                url="http://img1.jpg",
                thumbnail="http://thumb1.jpg",
            ),
            MediaItem(
                index=1,
                media_type=MediaType.IMAGE,
                url="http://img2.jpg",
                thumbnail="http://thumb2.jpg",
            ),
        ],
    )
    # The user asked for create_ytdl patch side_effect=AssertionError
    mock_ytdl.extract_info.side_effect = AssertionError(
        "IMAGE download sırasında yt-dlp çağrılmamalı"
    )
    mock_ytdl.process_ie_result.side_effect = AssertionError(
        "IMAGE download sırasında yt-dlp çağrılmamalı"
    )

    worker = DownloadWorker(request)
    worker.run()

    mock_ytdl.extract_info.assert_not_called()
    mock_ytdl.process_ie_result.assert_not_called()
    assert mock_execute_image_download.call_count == 2


def test_download_worker_does_not_bypass_for_mixed_selection(
    mock_execute_image_download, mock_ytdl
):
    request = DownloadRequest(
        url="https://www.instagram.com/p/mixed_carousel/",
        output_dir=Path("C:/test/out"),
        media_type="T\u00fcm Medyalar",
        quality="En Iyi",
        playlist=True,
        media_items=[
            MediaItem(
                index=0,
                media_type=MediaType.IMAGE,
                url="http://img1.jpg",
                thumbnail="http://thumb1.jpg",
            ),
            MediaItem(
                index=1,
                media_type=MediaType.VIDEO,
                url="http://vid1.mp4",
                thumbnail="http://thumb2.jpg",
            ),
        ],
    )
    mock_ytdl.extract_info.return_value = {
        "title": "Mixed",
        "_type": "playlist",
        "entries": [{"id": "img1"}, {"id": "vid1", "ext": "mp4"}],
    }
    worker = DownloadWorker(request)
    worker._platform = PlatformType.INSTAGRAM_POST
    worker.run()
    assert mock_ytdl.extract_info.call_count == 1
    assert mock_execute_image_download.call_count == 1
    assert mock_ytdl.process_ie_result.call_count == 1


def test_download_worker_no_items_uses_fallback(mock_ytdl):
    request = DownloadRequest(
        url="https://www.instagram.com/p/no_items/",
        output_dir=Path("C:/test/out"),
        media_type="T\u00fcm Medyalar",
        quality="En Iyi",
        playlist=True,
        media_items=[],
    )
    mock_ytdl.extract_info.side_effect = yt_dlp.utils.DownloadError(
        "There is no video in this post"
    )
    worker = DownloadWorker(request)
    worker.run()
    assert mock_ytdl.extract_info.call_count > 0
