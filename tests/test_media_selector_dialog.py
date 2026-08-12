import pytest

from src.media_selector_dialog import MediaSelectorDialog
from src.models import MediaItem, MediaType


@pytest.fixture
def sample_media_items():
    return [
        MediaItem(media_type=MediaType.IMAGE, index=0, url="http://example.com/1.jpg"),
        MediaItem(media_type=MediaType.VIDEO, index=1, url="http://example.com/2.mp4"),
        MediaItem(media_type=MediaType.IMAGE, index=2, url="http://example.com/3.jpg"),
    ]


def test_media_selector_dialog_initial_state(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)

    assert len(dialog.item_widgets) == 3
    # Varsayılan olarak tümü seçili
    for w in dialog.item_widgets:
        assert w.is_selected() is True

    assert dialog.btn_download.isEnabled() is True
    assert "3 medyadan 3'i seçildi" in dialog.status_label.text()


def test_media_selector_dialog_clear_selection(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)

    dialog._clear_selection()

    for w in dialog.item_widgets:
        assert w.is_selected() is False

    assert dialog.btn_download.isEnabled() is False
    assert "3 medyadan 0'i seçildi" in dialog.status_label.text()


def test_media_selector_dialog_select_all(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)

    # Önce temizle
    dialog._clear_selection()
    assert dialog.btn_download.isEnabled() is False

    # Sonra tümünü seç
    dialog._select_all()
    for w in dialog.item_widgets:
        assert w.is_selected() is True

    assert dialog.btn_download.isEnabled() is True


def test_media_selector_dialog_individual_selection(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)

    # Ortadaki öğenin seçimini kaldır
    dialog.item_widgets[1].set_selected(False)

    assert dialog.item_widgets[0].is_selected() is True
    assert dialog.item_widgets[1].is_selected() is False
    assert dialog.item_widgets[2].is_selected() is True

    selected_items = dialog.get_selected_items()
    assert len(selected_items) == 2
    assert selected_items[0].index == 0
    assert selected_items[1].index == 2
    assert dialog.btn_download.isEnabled() is True


def test_media_selector_dialog_accept(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog.item_widgets[0].set_selected(False)
    
    # Just call accept manually instead of simulating click and wait Signal for simplicity
    dialog.accept()
        
    selected_items = dialog.get_selected_items()
    assert len(selected_items) == 2
    assert selected_items[0].index == 1
    assert selected_items[1].index == 2


def test_media_selector_dialog_reject_on_cancel(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog.reject()
    assert dialog.result() == MediaSelectorDialog.DialogCode.Rejected


def test_media_selector_dialog_reject_on_close(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog.close()
    assert dialog.result() == MediaSelectorDialog.DialogCode.Rejected

