import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea

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
    assert dialog.subtitle.text() == "3 medya • 3 seçili"
    assert dialog.btn_download.text() == "Seçilenleri İndir (3)"


def test_media_selector_dialog_clear_selection(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog._clear_selection()

    for w in dialog.item_widgets:
        assert w.is_selected() is False

    assert dialog.btn_download.isEnabled() is False
    assert dialog.subtitle.text() == "3 medya • 0 seçili"
    assert dialog.btn_download.text() == "Seçilenleri İndir"


def test_media_selector_dialog_select_all(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog._clear_selection()
    assert dialog.btn_download.isEnabled() is False

    dialog._select_all()
    for w in dialog.item_widgets:
        assert w.is_selected() is True

    assert dialog.btn_download.isEnabled() is True
    assert dialog.subtitle.text() == "3 medya • 3 seçili"


def test_media_selector_dialog_individual_selection(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog.item_widgets[1].set_selected(False)

    assert dialog.item_widgets[0].is_selected() is True
    assert dialog.item_widgets[1].is_selected() is False
    assert dialog.item_widgets[2].is_selected() is True

    selected_items = dialog.get_selected_items()
    assert len(selected_items) == 2
    assert selected_items[0].index == 0
    assert selected_items[1].index == 2
    assert dialog.btn_download.isEnabled() is True
    assert dialog.btn_download.text() == "Seçilenleri İndir (2)"


def test_media_selector_dialog_accept(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    dialog.item_widgets[0].set_selected(False)

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


def test_media_selector_dialog_card_click_toggles_checkbox(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)
    widget = dialog.item_widgets[0]

    assert widget.is_selected() is True

    from PySide6.QtCore import QPoint
    from PySide6.QtTest import QTest

    QTest.mouseClick(widget, Qt.MouseButton.LeftButton, pos=QPoint(50, 50))

    assert widget.is_selected() is False
    assert "3 medya • 2 seçili" in dialog.subtitle.text()


def test_media_selector_dialog_badges(qapp, sample_media_items):
    dialog = MediaSelectorDialog(sample_media_items)

    image_widget = dialog.item_widgets[0]
    assert image_widget.type_badge.text() == "FOTOĞRAF"

    video_widget = dialog.item_widgets[1]
    assert video_widget.type_badge.text() == "VİDEO"


def test_media_selector_dialog_original_index_preservation(qapp):
    items = [
        MediaItem(media_type=MediaType.IMAGE, index=1, url="http://example.com/1.jpg"),
        MediaItem(media_type=MediaType.VIDEO, index=4, url="http://example.com/4.mp4"),
    ]
    dialog = MediaSelectorDialog(items)
    selected_items = dialog.get_selected_items()

    assert len(selected_items) == 2
    assert selected_items[0].index == 1
    assert selected_items[1].index == 4

def test_media_selector_dialog_scroll_geometry(qapp):
    items_2 = [MediaItem(media_type=MediaType.IMAGE, index=i, url="url") for i in range(2)]
    dialog_2 = MediaSelectorDialog(items_2)

    items_5 = [MediaItem(media_type=MediaType.IMAGE, index=i, url="url") for i in range(5)]
    dialog_5 = MediaSelectorDialog(items_5)

    items_20 = [MediaItem(media_type=MediaType.IMAGE, index=i, url="url") for i in range(20)]
    dialog_20 = MediaSelectorDialog(items_20)

    # Verify dynamic height
    assert dialog_2.height() < dialog_5.height()
    assert dialog_20.height() <= 720

    # Verify scroll area properties
    scroll_area = dialog_20.findChild(QScrollArea)
    assert scroll_area is not None
    assert scroll_area.widgetResizable() is True

    # Verify geometry constraints
    assert dialog_20.minimumSize().width() <= 1366
    assert dialog_20.maximumSize().width() <= 1366
    assert dialog_20.maximumSize().height() <= 768

def test_media_selector_dialog_checkbox_real_click(qapp):
    items = [
        MediaItem(media_type=MediaType.IMAGE, index=1, url="http://example.com/1.jpg"),
    ]
    dialog = MediaSelectorDialog(items)
    widget = dialog.item_widgets[0]

    assert widget.is_selected() is True

    from PySide6.QtTest import QTest

    QTest.mouseClick(widget.checkbox, Qt.MouseButton.LeftButton)

    assert widget.is_selected() is False
