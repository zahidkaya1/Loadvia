
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.download_worker import DownloadWorker
from src.models import DownloadRequest


@pytest.fixture

def temp_output_dir():

    d = tempfile.mkdtemp()

    yield Path(d)

    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture

def mock_downloader():

    with patch("src.download_worker.create_ytdl") as mock_ytdl:

        instance = MagicMock()

        mock_ytdl.return_value.__enter__.return_value = instance

        yield instance

@pytest.fixture

def mock_cffi_requests():

    with patch("curl_cffi.requests.get") as mock_req:

        yield mock_req

def test_download_image_directly_success(temp_output_dir, mock_downloader, mock_cffi_requests):

    mock_downloader.extract_info.return_value = {

        "extractor": "instagram",

        

        "id": "pic1",

        "url": "https://scontent.cdninstagram.com/v/t51.2885-15/e35/12345.jpg",

        "ext": "jpg",

        "vcodec": "none",

        "title": "A Photo"

    }

    req = DownloadRequest(

        url="https://instagram.com/p/pic123",

        output_dir=temp_output_dir,

        media_type="Foto\u011fraf (JPG/PNG)",

        quality="Orijinal",

        playlist=False

    )

    worker = DownloadWorker(req)

    # Mock response

    mock_resp = MagicMock()

    mock_resp.status_code = 200

    mock_resp.headers = {"Content-Type": "image/jpeg", "Content-Length": "1000"}

    mock_resp.iter_content.return_value = [b"chunk1", b"chunk2"]

    mock_cffi_requests.return_value = mock_resp
    worker.run()

    # Check if a .jpg file was created

    files = list(temp_output_dir.glob("*.jpg"))
    assert len(files) == 1

    assert "A Photo" in files[0].name

    assert files[0].stat().st_size == 12  # len(b"chunk1" + b"chunk2")

def test_download_image_directly_no_url(temp_output_dir, mock_downloader):

    mock_downloader.extract_info.return_value = {

        "extractor": "instagram",

        

        "id": "pic1",

        "ext": "jpg",

        "vcodec": "none",

        "title": "A Photo"

        # No 'url' field

    }

    req = DownloadRequest(

        url="https://instagram.com/p/pic123",

        output_dir=temp_output_dir,

        media_type="Foto\u011fraf (JPG/PNG)",

        quality="Orijinal",

        playlist=False

    )

    worker = DownloadWorker(req)

    

    error_raised = False

    error_msg = ""

    def on_error(msg):

        nonlocal error_raised, error_msg

        error_raised = True

        error_msg = msg

    worker.failed.connect(on_error)

    worker.run()

    assert error_raised

    assert "geçerli bir medya bağlantısı bulunamadı" in error_msg.lower() or "fotoğraf bulunamadı" in error_msg.lower()

def test_download_image_directly_403_error(temp_output_dir, mock_downloader, mock_cffi_requests):

    mock_downloader.extract_info.return_value = {

        "extractor": "instagram",

        

        "id": "pic1",

        "url": "https://scontent.cdninstagram.com/v/t51.2885-15/e35/12345.jpg",

        "ext": "jpg",

        "vcodec": "none",

        "title": "A Photo"

    }

    req = DownloadRequest(

        url="https://instagram.com/p/pic123",

        output_dir=temp_output_dir,

        media_type="Foto\u011fraf (JPG/PNG)",

        quality="Orijinal",

        playlist=False

    )

    worker = DownloadWorker(req)

    # Mock response 403

    mock_resp = MagicMock()

    mock_resp.status_code = 403

    mock_resp.iter_content.return_value = []

    mock_cffi_requests.return_value = mock_resp

    error_raised = False

    error_msg = ""

    def on_error(msg):

        nonlocal error_raised, error_msg

        error_raised = True

        error_msg = msg

    worker.failed.connect(on_error)

    worker.run()

    assert error_raised

    assert "403" in error_msg

    # Ensure no temp or final file is left

    assert len(list(temp_output_dir.glob("*"))) == 0

def test_download_image_directly_404_error(temp_output_dir, mock_downloader, mock_cffi_requests):

    mock_downloader.extract_info.return_value = {

        "extractor": "instagram",

        

        "id": "pic1",

        "url": "https://scontent.cdninstagram.com/v/t51.2885-15/e35/12345.jpg",

        "ext": "jpg",

        "vcodec": "none",

        "title": "A Photo"

    }

    req = DownloadRequest(

        url="https://instagram.com/p/pic123",

        output_dir=temp_output_dir,

        media_type="Foto\u011fraf (JPG/PNG)",

        quality="Orijinal",

        playlist=False

    )

    worker = DownloadWorker(req)

    # Mock response 404

    mock_resp = MagicMock()

    mock_resp.status_code = 404

    mock_resp.iter_content.return_value = []

    mock_cffi_requests.return_value = mock_resp

    error_raised = False

    error_msg = ""

    def on_error(msg):

        nonlocal error_raised, error_msg

        error_raised = True

        error_msg = msg

    worker.failed.connect(on_error)

    worker.run()

    assert error_raised

    assert "404" in error_msg

    assert len(list(temp_output_dir.glob("*"))) == 0

def test_download_image_directly_connection_error(temp_output_dir, mock_downloader, mock_cffi_requests):

    mock_downloader.extract_info.return_value = {

        "extractor": "instagram",

        

        "id": "pic1",

        "url": "https://scontent.cdninstagram.com/v/t51.2885-15/e35/12345.jpg",

        "ext": "jpg",

        "vcodec": "none",

        "title": "A Photo"

    }

    req = DownloadRequest(

        url="https://instagram.com/p/pic123",

        output_dir=temp_output_dir,

        media_type="Foto\u011fraf (JPG/PNG)",

        quality="Orijinal",

        playlist=False

    )

    worker = DownloadWorker(req)

    # Mock connection error

    mock_cffi_requests.side_effect = Exception("Connection Timeout")

    error_raised = False

    error_msg = ""

    def on_error(msg):

        nonlocal error_raised, error_msg

        error_raised = True

        error_msg = msg

    worker.failed.connect(on_error)

    worker.run()

    assert error_raised

    assert "hata" in error_msg.lower() or "timeout" in error_msg.lower()

    assert len(list(temp_output_dir.glob("*"))) == 0


def test_video_does_not_use_image_path(temp_output_dir, mock_downloader, mock_cffi_requests):
    mock_downloader.extract_info.return_value = {
        "extractor": "instagram",
        "id": "vid1",
        "url": "https://scontent.cdninstagram.com/v/t51.2885-15/e35/12345.mp4",
        "ext": "mp4",
        "vcodec": "h264",
        "title": "A Video"
    }
    req = DownloadRequest(
        url="https://instagram.com/p/vid123",
        output_dir=temp_output_dir,
        media_type="Video (MP4)",
        quality="Orijinal",
        playlist=False
    )
    worker = DownloadWorker(req)
    
    try:
        worker.run()
    except Exception:  # noqa: BLE001, S110
        pass
        
    mock_cffi_requests.assert_not_called()

@pytest.mark.parametrize("content_type, url, expected_ext", [
    ("image/jpeg", "https://example.com/file", ".jpg"),
    ("image/png", "https://example.com/file", ".png"),
    ("image/webp", "https://example.com/file", ".webp"),
    ("application/octet-stream", "https://example.com/file.jpg", ".jpg"),
    ("application/octet-stream", "https://example.com/file.png", ".png"),
    ("application/octet-stream", "https://example.com/file.webp", ".webp"),
    ("application/octet-stream", "https://example.com/file", ".jpg"),
])
def test_image_extension_resolution(temp_output_dir, mock_downloader, mock_cffi_requests, content_type, url, expected_ext):
    mock_downloader.extract_info.return_value = {
        "extractor": "instagram",
        "id": "pic1",
        "url": url,
        "ext": "jpg",
        "vcodec": "none",
        "title": "Ext Test"
    }
    req = DownloadRequest(
        url="https://instagram.com/p/pic123",
        output_dir=temp_output_dir,
        media_type="Fotoğraf (JPG/PNG)",
        quality="Orijinal",
        playlist=False
    )
    worker = DownloadWorker(req)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": content_type, "Content-Length": "10"}
    mock_resp.iter_content.return_value = [b"data"]
    mock_cffi_requests.return_value = mock_resp

    worker.run()
    
    files = list(temp_output_dir.glob("*"))
    assert len(files) == 1
    assert files[0].suffix == expected_ext
