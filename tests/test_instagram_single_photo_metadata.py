from unittest.mock import MagicMock, patch

from src.metadata_worker import MetadataWorker
from src.models import MediaType


def test_instagram_single_photo_metadata_success():
    """
    Instagram tek fotoğraf yt-dlp metadata testi.
    - no formats
    - thumbnail mevcut
    - exception yok, failed signal yok
    - media_items içinde 1 adet IMAGE olmalı.
    """
    worker = MetadataWorker("https://www.instagram.com/p/pic123", session_method="none")

    # yt-dlp.YoutubeDL.extract_info mock
    mock_info = {
        "extractor": "instagram",
        "id": "pic123",
        "title": "A single photo",
        "thumbnail": "https://example.com/thumb.jpg",
        "ext": "jpg",
        # formats yok!
    }

    metadata = None
    failed_msg = None

    def on_metadata(meta):
        nonlocal metadata
        metadata = meta

    def on_failed(msg):
        nonlocal failed_msg
        failed_msg = msg

    worker.metadata_ready.connect(on_metadata)
    worker.failed.connect(on_failed)

    with patch("src.metadata_worker.create_ytdl") as mock_create_ytdl:
        mock_ytdl = MagicMock()
        mock_ytdl.extract_info.return_value = mock_info
        mock_create_ytdl.return_value.__enter__.return_value = mock_ytdl

        worker.run()

    # yt-dlp create opts should have ignore_no_formats_error
    call_args = mock_create_ytdl.call_args[0][0]
    assert call_args.get("ignore_no_formats_error") is True, "ignore_no_formats_error True olmali"

    assert failed_msg is None, f"Failed signal tetiklenmemeli, gelen: {failed_msg}"
    assert metadata is not None, "Metadata uretilmeli"
    assert len(metadata.media_items) == 1, "1 adet medya öğesi olmalı"

    item = metadata.media_items[0]
    assert item.media_type == MediaType.IMAGE, "Medya tipi IMAGE olmalı"
    assert item.index == 0, "Index 0 olmalı"

def test_legacy_error_not_used():
    from src.models import translate_social_error

    msg = translate_social_error("There is no video in this post", "https://instagram.com/p/pic123")
    assert "Fotoğraf indirme desteği henüz eklenmedi" not in msg
    assert "indirilebilir medya bulunamadı" in msg.lower()

def test_instagram_image_only_carousel():
    from src.models import MediaType, extract_media_items
    mock_info = {
        "extractor": "instagram",
        "_type": "playlist",
        "entries": [
            {
                "id": "pic1",
                "extractor": "instagram",
                "thumbnails": [{"url": "http://img1.jpg", "width": 100}],
            },
            {
                "id": "pic2",
                "extractor": "instagram",
                "thumbnails": [{"url": "http://img2.jpg", "width": 100}],
            },
            {
                "id": "pic3",
                "extractor": "instagram",
                "thumbnails": [{"url": "http://img3.jpg", "width": 100}],
            }
        ]
    }
    items = extract_media_items(mock_info)
    assert len(items) == 3
    for i in range(3):
        assert items[i].media_type == MediaType.IMAGE
        assert items[i].index == i
        assert items[i].url == f"http://img{i+1}.jpg"

def test_instagram_mixed_carousel():
    from src.models import MediaType, extract_media_items
    mock_info = {
        "extractor": "instagram",
        "_type": "playlist",
        "entries": [
            {
                "id": "img1",
                "extractor": "instagram",
                "thumbnails": [{"url": "http://img1.jpg", "width": 100}],
            },
            {
                "id": "vid1",
                "extractor": "instagram",
                "ext": "mp4",
                "vcodec": "h264",
                "url": "http://vid1.mp4",
            },
            {
                "id": "img2",
                "extractor": "instagram",
                "thumbnails": [{"url": "http://img2.jpg", "width": 100}],
            }
        ]
    }
    items = extract_media_items(mock_info)
    assert len(items) == 3
    assert items[0].media_type == MediaType.IMAGE
    assert items[0].url == "http://img1.jpg"
    assert items[1].media_type == MediaType.VIDEO
    assert items[1].url == "http://vid1.mp4"
    assert items[2].media_type == MediaType.IMAGE
    assert items[2].url == "http://img2.jpg"

def test_instagram_single_photo_thumbnail_fallback():
    from src.models import MediaType, extract_media_items
    mock_info = {
        "extractor": "instagram",
        "id": "single1",
        "thumbnails": [
            {"url": "http://thumb-low.jpg", "width": 100},
            {"url": "http://thumb-high.jpg", "width": 1000},
        ],
    }
    items = extract_media_items(mock_info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.IMAGE
    assert items[0].url == "http://thumb-high.jpg"
