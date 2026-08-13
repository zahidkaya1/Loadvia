from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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

def test_download_worker_image_progress_details_emits_ints(mock_ytdl):
    with patch("curl_cffi.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Length": "1024", "Content-Type": "image/jpeg"}
        mock_response.iter_content.return_value = [b"A" * 512, b"B" * 512]
        mock_get.return_value = mock_response
        
        request = DownloadRequest(
            url="https://www.instagram.com/p/single_photo/",
            output_dir=Path("C:/test/out"),
            media_type="Foto\u011fraf (JPG)",
            quality="En Iyi",
            playlist=False,
            media_items=[
                MediaItem(index=0, media_type=MediaType.IMAGE, url="http://img1.jpg", thumbnail="http://thumb1.jpg", title="Video by testuser"),
            ]
        )
        worker = DownloadWorker(request)
        worker._platform = PlatformType.INSTAGRAM_POST
        worker.progress_details = MagicMock()
        worker.run()
        
        # The second time progress_details is called (after first chunk)
        assert worker.progress_details.emit.call_count >= 1
        call_args = worker.progress_details.emit.call_args[0][0]
        assert isinstance(call_args["downloaded_bytes"], int)
        assert isinstance(call_args["total_bytes"], int)

def test_download_worker_removes_video_by_prefix_for_images(mock_execute_image_download, mock_ytdl):
    request = DownloadRequest(
        url="https://www.instagram.com/p/image_only_carousel/",
        output_dir=Path("C:/test/out"),
        media_type="T\u00fcm Medyalar",
        quality="En Iyi",
        playlist=True,
        media_items=[
            MediaItem(index=0, media_type=MediaType.IMAGE, url="http://img1.jpg", thumbnail="http://thumb1.jpg", title="Video by bpthaber"),
            MediaItem(index=1, media_type=MediaType.IMAGE, url="http://img2.jpg", thumbnail="http://thumb2.jpg", title="Video by bpthaber"),
        ]
    )
    worker = DownloadWorker(request)
    worker._platform = PlatformType.INSTAGRAM_POST
    # We inject fake info with "Video by bpthaber"
    mock_ytdl.extract_info.return_value = {"title": "Video by bpthaber", "id": "123"}
    
    with patch("src.history.reserve_unique_media_path") as mock_reserve:
        mock_reserve.return_value = Path("C:/test/out/fake.jpg")
        worker.run()
        
        # Check that base_name doesn't have "Video by "
        call_args1 = mock_reserve.call_args_list[0]
        assert "bpthaber_01" in call_args1[0][1]
        assert "Video_by" not in call_args1[0][1]

        call_args2 = mock_reserve.call_args_list[1]
        assert "bpthaber_02" in call_args2[0][1]
        assert "Video_by" not in call_args2[0][1]
