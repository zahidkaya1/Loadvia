from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.models import MediaItem, MediaType


class MediaItemWidget(QFrame):
    selection_changed = Signal(bool)

    def __init__(self, item: MediaItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.item = item
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Darker background for hover effect readiness, border radius
        self.setStyleSheet("""
            MediaItemWidget {
                background-color: transparent;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
            }
            MediaItemWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid #5a5a5a;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self.selection_changed.emit)
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        layout.addWidget(self.checkbox)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 80)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: #2c2c2c; border-radius: 4px;")
        
        # Fallback empty QPixmap with a text or color
        default_pixmap = QPixmap(32, 32)
        default_pixmap.fill(Qt.GlobalColor.transparent)
        self.thumbnail_label.setPixmap(default_pixmap)
        self.thumbnail_label.setText("V" if self.item.media_type == MediaType.VIDEO else "F")
        layout.addWidget(self.thumbnail_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        idx_label = QLabel(f"Sıra: {self.item.index + 1}")
        idx_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(idx_label)

        type_text = "Video (MP4)" if self.item.media_type == MediaType.VIDEO else "Fotoğraf (JPG)"
        type_label = QLabel(f"Tür: {type_text}")
        type_label.setStyleSheet("color: #a0a0a0;")
        info_layout.addWidget(type_label)
        
        if self.item.width and self.item.height:
            res_label = QLabel(f"Çözünürlük: {self.item.width}x{self.item.height}")
            res_label.setStyleSheet("color: #808080; font-size: 11px;")
            info_layout.addWidget(res_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)
        layout.addStretch()

    def set_thumbnail(self, pixmap: QPixmap) -> None:
        scaled_pixmap = pixmap.scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.thumbnail_label.setText("")
        self.thumbnail_label.setPixmap(scaled_pixmap)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()
        
    def set_selected(self, selected: bool) -> None:
        self.checkbox.setChecked(selected)


class MediaSelectorDialog(QDialog):
    def __init__(self, media_items: list[MediaItem], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.media_items = media_items
        self.item_widgets: list[MediaItemWidget] = []
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_thumbnail_downloaded)
        self.reply_to_widget: dict[QNetworkReply, MediaItemWidget] = {}
        
        self.setWindowTitle("Carousel Medyalarını Seç")
        self.setMinimumSize(450, 500)
        self.resize(500, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        self._load_thumbnails()
        self._update_status()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel(f"Bu gönderide {len(self.media_items)} medya bulundu.")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        for item in self.media_items:
            widget = MediaItemWidget(item)
            widget.selection_changed.connect(self._update_status)
            self.scroll_layout.addWidget(widget)
            self.item_widgets.append(widget)

        self.scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Status and Actions
        bottom_layout = QHBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #a0a0a0; font-weight: bold;")
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()

        btn_select_all = QPushButton("Tümünü Seç")
        btn_select_all.clicked.connect(self._select_all)
        bottom_layout.addWidget(btn_select_all)

        btn_clear = QPushButton("Seçimi Temizle")
        btn_clear.clicked.connect(self._clear_selection)
        bottom_layout.addWidget(btn_clear)

        layout.addLayout(bottom_layout)

        # Dialog Buttons
        button_box = QHBoxLayout()
        button_box.addStretch()
        
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        button_box.addWidget(btn_cancel)

        self.btn_download = QPushButton("Seçilenleri İndir")
        self.btn_download.setObjectName("primaryButton")
        self.btn_download.clicked.connect(self.accept)
        button_box.addWidget(self.btn_download)

        layout.addLayout(button_box)

    def _update_status(self) -> None:
        selected_count = sum(1 for w in self.item_widgets if w.is_selected())
        total_count = len(self.media_items)
        self.status_label.setText(f"{total_count} medyadan {selected_count}'i seçildi")
        self.btn_download.setEnabled(selected_count > 0)

    def _select_all(self) -> None:
        for w in self.item_widgets:
            w.set_selected(True)
        self._update_status()

    def _clear_selection(self) -> None:
        for w in self.item_widgets:
            w.set_selected(False)
        self._update_status()

    def _load_thumbnails(self) -> None:
        for widget in self.item_widgets:
            if widget.item.thumbnail:
                url = QUrl(widget.item.thumbnail)
                if url.isValid():
                    request = QNetworkRequest(url)
                    # Add standard User-Agent to avoid 403
                    request.setRawHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Loadvia")
                    reply = self.network_manager.get(request)
                    self.reply_to_widget[reply] = widget

    def _on_thumbnail_downloaded(self, reply: QNetworkReply) -> None:
        widget = self.reply_to_widget.get(reply)
        if widget and reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                widget.set_thumbnail(pixmap)
        
        if reply in self.reply_to_widget:
            del self.reply_to_widget[reply]
        reply.deleteLater()

    def get_selected_items(self) -> list[MediaItem]:
        return [w.item for w in self.item_widgets if w.is_selected()]
