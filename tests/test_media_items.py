from src.models import MediaItem, MediaMetadata, MediaType, extract_media_items


def test_media_item_video_creation():
    item = MediaItem(media_type=MediaType.VIDEO, id="vid1", url="http://vid1")
    assert item.media_type == MediaType.VIDEO
    assert item.id == "vid1"
    assert item.url == "http://vid1"

def test_media_item_image_creation():
    item = MediaItem(media_type=MediaType.IMAGE, id="img1", width=1920, height=1080)
    assert item.media_type == MediaType.IMAGE
    assert item.id == "img1"
    assert item.width == 1920

def test_media_type_enum():
    assert MediaType.VIDEO.value == "video"
    assert MediaType.IMAGE.value == "image"
    assert MediaType.AUDIO.value == "audio"

def test_media_metadata_default_items():
    meta1 = MediaMetadata(title="Meta 1")
    assert meta1.media_items == []

def test_media_metadata_list_isolation():
    meta1 = MediaMetadata(title="Meta 1")
    meta2 = MediaMetadata(title="Meta 2")
    
    meta1.media_items.append(MediaItem(media_type=MediaType.VIDEO))
    assert len(meta1.media_items) == 1
    assert len(meta2.media_items) == 0  # Should not share the same list

def test_media_metadata_backward_compatibility():
    # Mevcut kwargs ile oluşturma
    meta = MediaMetadata(title="Video Title", duration_seconds=120)
    assert meta.title == "Video Title"
    assert meta.duration_seconds == 120
    assert meta.media_items == []

def test_extract_media_items_video():
    info = {
        "id": "123",
        "url": "http://video.mp4",
        "vcodec": "h264",
        "title": "A Video"
    }
    items = extract_media_items(info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.VIDEO
    assert items[0].id == "123"
    assert items[0].title == "A Video"

def test_extract_media_items_image():
    info = {
        "id": "pic1",
        "url": "http://image.jpg",
        "ext": "jpg",
        "vcodec": "none",
    }
    items = extract_media_items(info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.IMAGE
    assert items[0].id == "pic1"

def test_extract_media_items_missing_fields():
    info = {}
    items = extract_media_items(info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.UNKNOWN
    assert items[0].id is None

def test_extract_media_items_audio():
    info = {
        "id": "aud1",
        "vcodec": "none",
        "acodec": "mp4a",
    }
    items = extract_media_items(info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.AUDIO
    assert items[0].id == "aud1"

def test_extract_media_items_gif():
    info = {
        "id": "gif1",
        "ext": "gif",
    }
    items = extract_media_items(info)
    assert len(items) == 1
    assert items[0].media_type == MediaType.GIF
    assert items[0].id == "gif1"

def test_extract_media_items_carousel():
    info = {
        "entries": [
            {"id": "c1", "ext": "jpg"},
            {"id": "c2", "vcodec": "h264"}
        ]
    }
    items = extract_media_items(info)
    assert len(items) == 2
    assert items[0].media_type == MediaType.IMAGE
    assert items[0].id == "c1"
    assert items[1].media_type == MediaType.VIDEO
    assert items[1].id == "c2"
