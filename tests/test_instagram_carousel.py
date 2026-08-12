import pytest

from src.metadata_worker import MetadataWorker
from src.models import MediaType


def test_instagram_single_video():
    worker = MetadataWorker("https://instagram.com/p/vid123", "")
    info = {
        "extractor": "instagram",
        "webpage_url": "https://instagram.com/p/vid123",
        "id": "vid1",
        "ext": "mp4",
        "vcodec": "h264",
        "title": "A Video"
    }
    meta = worker._build_metadata(info)
    assert not meta.is_playlist
    assert len(meta.media_items) == 1
    assert meta.media_items[0].media_type == MediaType.VIDEO

def test_instagram_single_photo():
    worker = MetadataWorker("https://instagram.com/p/pic123", "")
    info = {
        "extractor": "instagram",
        "webpage_url": "https://instagram.com/p/pic123",
        "id": "pic1",
        "ext": "jpg",
        "vcodec": "none",
        "title": "A Photo"
    }
    meta = worker._build_metadata(info)
    assert not meta.is_playlist
    assert len(meta.media_items) == 1
    assert meta.media_items[0].media_type == MediaType.IMAGE

def test_instagram_carousel():
    worker = MetadataWorker("https://instagram.com/p/carousel123", "")
    info = {
        "extractor": "instagram",
        "webpage_url": "https://instagram.com/p/carousel123",
        "id": "car1",
        "title": "A Carousel",
        "_type": "playlist",
        "entries": [
            {"id": "c1", "ext": "jpg"},
            {"id": "c2", "ext": "mp4"},
            {"id": "c3", "ext": "jpg"}
        ]
    }
    meta = worker._build_metadata(info)
    assert not meta.is_playlist
    assert len(meta.media_items) == 3
    assert meta.media_items[0].media_type == MediaType.IMAGE
    assert meta.media_items[0].index == 0
    assert meta.media_items[1].media_type == MediaType.VIDEO
    assert meta.media_items[1].index == 1
    assert meta.media_items[2].media_type == MediaType.IMAGE
    assert meta.media_items[2].index == 2

def test_youtube_playlist_preservation():
    worker = MetadataWorker("https://youtube.com/playlist?list=PL123", "")
    info = {
        "extractor": "youtube",
        "webpage_url": "https://youtube.com/playlist?list=PL123",
        "id": "PL123",
        "_type": "playlist",
        "entries": [
            {"id": "v1", "ext": "mp4"},
            {"id": "v2", "ext": "mp4"}
        ]
    }
    meta = worker._build_metadata(info)
    assert meta.is_playlist
    assert len(meta.media_items) == 2

def test_instagram_corrupt_metadata():
    worker = MetadataWorker("https://instagram.com/p/corrupt123", "")
    info = {
        "extractor": "instagram",
        "webpage_url": "https://instagram.com/p/corrupt123",
        "entries": [{"broken": "data"}]
    }
    with pytest.raises(ValueError, match="indirilebilir"):
        worker._build_metadata(info)
