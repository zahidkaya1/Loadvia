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

    def __init__(self, item: MediaItem, total_items: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.item = item
        self.total_items = total_items
        self._setup_ui()
        self.update_visual_state()

    def _setup_ui(self) -> None:
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        # Enable cursor for clickable indication
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        # Ensure checkbox does not steal the cursor if it has one
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.toggled.connect(self._on_checkbox_toggled)

        layout.addWidget(self.checkbox)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 80)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: #e2e8f0; border-radius: 4px; color: #64748b; font-size: 11px;")

        default_pixmap = QPixmap(32, 32)
        default_pixmap.fill(Qt.GlobalColor.transparent)
        self.thumbnail_label.setPixmap(default_pixmap)
        self.thumbnail_label.setText("Video" if self.item.media_type == MediaType.VIDEO else "Fotoğraf")
        layout.addWidget(self.thumbnail_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        top_info_layout = QHBoxLayout()
        idx_label = QLabel(f"{self.item.index + 1} / {self.total_items}")
        idx_label.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px;")
        top_info_layout.addWidget(idx_label)
        top_info_layout.addStretch()
        info_layout.addLayout(top_info_layout)

        self.type_badge = QLabel()
        if self.item.media_type == MediaType.VIDEO:
            self.type_badge.setText("VİDEO")
            self.type_badge.setStyleSheet("background-color: #ef4444; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 10px;")
        else:
            self.type_badge.setText("FOTOĞRAF")
            self.type_badge.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 10px;")

        badge_layout = QHBoxLayout()
        badge_layout.addWidget(self.type_badge)
        badge_layout.addStretch()
        info_layout.addLayout(badge_layout)

        if self.item.width and self.item.height:
            res_label = QLabel(f"Çözünürlük: {self.item.width}x{self.item.height}")
            res_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
            info_layout.addWidget(res_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)
        layout.addStretch()

    def _on_checkbox_toggled(self, checked: bool) -> None:
        self.update_visual_state()
        self.selection_changed.emit(checked)

    def update_visual_state(self) -> None:
        if self.checkbox.isChecked():
            self.setStyleSheet("""
                MediaItemWidget {
                    background-color: #eff6ff;
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                }
                MediaItemWidget:hover {
                    background-color: #dbeafe;
                    border: 1px solid #3b82f6;
                }
            """)
        else:
            self.setStyleSheet("""
                MediaItemWidget {
                    background-color: transparent;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                }
                MediaItemWidget:hover {
                    background-color: #f8fafc;
                    border: 1px solid #94a3b8;
                }
            """)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle checkbox if the user clicked the widget (but not the checkbox itself)
            # The checkbox consumes its own events, so this is only triggered when clicking outside it.
            self.checkbox.toggle()
        super().mousePressEvent(event)

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

        self.setWindowTitle("Gönderi Medyalarını Seç")
        # Set max dimension constraints to prevent it from growing out of bounds on 1366x768 screens
        self.setMinimumSize(450, 250)
        self.setMaximumSize(800, 720)

        base_height = 140
        card_height = 100
        target_height = base_height + (len(self.media_items) * card_height)
        self.resize(500, min(720, target_height))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        self._load_thumbnails()
        self._update_status()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        main_title = QLabel("Gönderi Medyaları")
        main_title.setStyleSheet("color: #1e293b; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(main_title)

        self.subtitle = QLabel()
        self.subtitle.setStyleSheet("color: #64748b; font-size: 13px;")
        title_layout.addWidget(self.subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        btn_select_all = QPushButton("Tümünü Seç")
        btn_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select_all.clicked.connect(self._select_all)
        header_layout.addWidget(btn_select_all)

        btn_clear = QPushButton("Seçimi Temizle")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_selection)
        header_layout.addWidget(btn_clear)

        layout.addLayout(header_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        total_items = len(self.media_items)
        for item in self.media_items:
            widget = MediaItemWidget(item, total_items)
            widget.selection_changed.connect(self._update_status)
            self.scroll_layout.addWidget(widget)
            self.item_widgets.append(widget)

        self.scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Dialog Buttons
        button_box = QHBoxLayout()
        button_box.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        button_box.addWidget(btn_cancel)

        self.btn_download = QPushButton("Seçilenleri İndir")
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setObjectName("primaryButton")
        self.btn_download.clicked.connect(self.accept)
        button_box.addWidget(self.btn_download)

        layout.addLayout(button_box)

    def _update_status(self) -> None:
        selected_count = sum(1 for w in self.item_widgets if w.is_selected())
        total_count = len(self.media_items)
        self.subtitle.setText(f"{total_count} medya • {selected_count} seçili")

        self.btn_download.setEnabled(selected_count > 0)
        if selected_count > 0:
            self.btn_download.setText(f"Seçilenleri İndir ({selected_count})")
        else:
            self.btn_download.setText("Seçilenleri İndir")

    def _select_all(self) -> None:
        for w in self.item_widgets:
            w.set_selected(True)
        # Calling _update_status is redundant if signals are emitted, but it is safe.
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
