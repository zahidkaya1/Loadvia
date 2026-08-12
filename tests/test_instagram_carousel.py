from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.download_worker import DownloadWorker
from src.models import DownloadRequest


@pytest.fixture
def temp_output_dir(tmp_path: Path):
    return tmp_path


@pytest.fixture
def mock_downloader():
    with patch("src.download_worker.create_ytdl") as mock_ytdl:
        downloader_instance = MagicMock()
        # when we do `with create_ytdl() as downloader:`
        mock_ytdl.return_value.__enter__.return_value = downloader_instance
        yield downloader_instance


@pytest.fixture
def mock_cffi_requests():
    with patch("curl_cffi.requests.get") as mock_get:
        yield mock_get


def _create_mock_carousel_info(items: list[dict], title="Test Carousel"):
    entries = []
    for i, item in enumerate(items, start=1):
        is_video = item.get("type") == "video"
        entry = {
            "id": f"item{i}",
            "title": item.get("title") or title,
            "url": f"https://example.com/media{i}.{'mp4' if is_video else 'jpg'}",
            "ext": "mp4" if is_video else "jpg",
            "vcodec": "h264" if is_video else "none",
            "acodec": "aac" if is_video else "none",
        }
        entries.append(entry)

    return {
        "_type": "playlist",
        "extractor": "instagram",
        "id": "carousel1",
        "title": title,
        "entries": entries,
    }


def test_download_carousel_all_images(
    temp_output_dir, mock_downloader, mock_cffi_requests
):
    info = _create_mock_carousel_info(
        [{"type": "image"}, {"type": "image"}, {"type": "image"}], "MyPost"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "image/jpeg", "Content-Length": "10"}
    mock_resp.iter_content.return_value = [b"data"]
    mock_cffi_requests.return_value = mock_resp

    mock_downloader.extract_info.return_value = info

    logs = []
    worker.log.connect(logs.append)
    worker.run()
    print("\n".join(logs))

    files = list(temp_output_dir.glob("*.jpg"))
    assert len(files) == 3
    names = [f.name for f in files]
    assert "MyPost_01.jpg" in names
    assert "MyPost_02.jpg" in names
    assert "MyPost_03.jpg" in names
    assert not list(temp_output_dir.glob("*.temp"))

    assert mock_cffi_requests.call_count == 3
    assert mock_downloader.process_ie_result.call_count == 0


def test_download_carousel_mixed(temp_output_dir, mock_downloader, mock_cffi_requests):
    info = _create_mock_carousel_info(
        [{"type": "image"}, {"type": "video"}, {"type": "image"}], "MixedPost"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    # image response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "image/jpeg", "Content-Length": "10"}
    mock_resp.iter_content.return_value = [b"data"]
    mock_cffi_requests.return_value = mock_resp

    mock_downloader.extract_info.return_value = info

    # Mock video process_ie_result to create the file so logic succeeds without error
    def side_effect_process(entry, download):
        # determine which file should be created based on mock outtmpl if provided, or fallback
        # Wait, the worker creates file based on entry_options["outtmpl"]
        pass

    mock_downloader.process_ie_result.side_effect = side_effect_process

    logs = []
    worker.log.connect(logs.append)
    worker.run()
    print("\n".join(logs))

    image_files = list(temp_output_dir.glob("*.jpg"))
    assert len(image_files) == 2
    names = [f.name for f in image_files]
    assert "MixedPost_01.jpg" in names
    assert "MixedPost_03.jpg" in names

    assert mock_cffi_requests.call_count == 2
    assert mock_downloader.process_ie_result.call_count == 1


def test_download_carousel_all_videos(
    temp_output_dir, mock_downloader, mock_cffi_requests
):
    info = _create_mock_carousel_info(
        [{"type": "video"}, {"type": "video"}], "VideoPost"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    mock_downloader.extract_info.return_value = info

    worker.run()

    assert mock_cffi_requests.call_count == 0
    assert mock_downloader.process_ie_result.call_count == 2


def test_download_carousel_one_image_error(
    temp_output_dir, mock_downloader, mock_cffi_requests
):
    info = _create_mock_carousel_info(
        [{"type": "image"}, {"type": "image"}], "ErrorPost"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    # fail on the first image, succeed on the second
    mock_resp_fail = MagicMock()
    mock_resp_fail.status_code = 403

    mock_resp_ok = MagicMock()
    mock_resp_ok.status_code = 200
    mock_resp_ok.headers = {"Content-Type": "image/jpeg", "Content-Length": "10"}
    mock_resp_ok.iter_content.return_value = [b"data"]

    mock_cffi_requests.side_effect = [mock_resp_fail, mock_resp_ok]

    mock_downloader.extract_info.return_value = info

    succeeded_msgs = []
    worker.succeeded.connect(succeeded_msgs.append)
    failed_msgs = []
    worker.failed.connect(failed_msgs.append)

    worker.run()

    assert mock_cffi_requests.call_count == 2
    files = list(temp_output_dir.glob("*.jpg"))
    assert len(files) == 1
    assert files[0].name == "ErrorPost_02.jpg"
    assert not list(temp_output_dir.glob("*.temp"))

    assert "Carousel indirildi. (2 medyadan 1 ba" in succeeded_msgs[0]


def test_download_carousel_video_error(
    temp_output_dir, mock_downloader, mock_cffi_requests
):
    info = _create_mock_carousel_info(
        [{"type": "video"}, {"type": "image"}], "VideoErrorPost"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    mock_downloader.extract_info.return_value = info

    # Video fail
    mock_downloader.process_ie_result.side_effect = Exception("Video download error")

    # Image ok
    mock_resp_ok = MagicMock()
    mock_resp_ok.status_code = 200
    mock_resp_ok.headers = {"Content-Type": "image/jpeg"}
    mock_resp_ok.iter_content.return_value = [b"data"]
    mock_cffi_requests.return_value = mock_resp_ok

    worker.run()

    assert mock_downloader.process_ie_result.call_count == 1
    assert mock_cffi_requests.call_count == 1
    files = list(temp_output_dir.glob("*.jpg"))
    assert len(files) == 1
    assert files[0].name == "VideoErrorPost_02.jpg"


def test_download_carousel_empty_items(temp_output_dir, mock_downloader):
    info = {}

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)
    mock_downloader.extract_info.return_value = info

    failed_msgs = []
    worker.failed.connect(failed_msgs.append)

    with patch("src.download_worker.extract_media_items", return_value=[]):
        worker.run()

    assert "Carousel gönderisinde indirilebilir medya bulunamadı." in failed_msgs[0]


def test_download_carousel_same_title_items(
    temp_output_dir, mock_downloader, mock_cffi_requests
):
    # Same title logic is already handled by zero-padding (_01, _02)
    # The framework will name them padded anyway. We just ensure no crash.
    info = _create_mock_carousel_info(
        [{"type": "image", "title": "Same"}, {"type": "image", "title": "Same"}], "Post"
    )

    req = DownloadRequest(
        url="https://instagram.com/p/carousel123",
        output_dir=temp_output_dir,
        media_type="Tüm Medyalar",
        quality="Orijinal",
        playlist=False,
    )
    worker = DownloadWorker(req)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "image/jpeg"}
    mock_resp.iter_content.return_value = [b"data"]
    mock_cffi_requests.return_value = mock_resp

    mock_downloader.extract_info.return_value = info

    worker.run()

    files = list(temp_output_dir.glob("*.jpg"))
    assert len(files) == 2
    names = [f.name for f in files]
    assert "Post_01.jpg" in names
    assert "Post_02.jpg" in names
