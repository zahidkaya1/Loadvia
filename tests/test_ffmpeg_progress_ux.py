from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.download_worker import DownloadWorker
from src.main_window import MainWindow
from src.models import DownloadRequest


@pytest.fixture
def mock_request(tmp_path):
    return DownloadRequest(
        url="https://youtube.com/watch?v=123",
        output_dir=tmp_path,
        media_type="Video (MP4)",
        quality="1080p",
        playlist=False,
    )

@patch("src.download_worker.probe_media_codecs")
@patch("subprocess.Popen")
def test_download_worker_emits_progress_mode(mock_popen, mock_probe, mock_request):
    mock_probe.return_value = {
        "video_codec": "vp9",
        "audio_codec": "opus",
        "pix_fmt": "yuv420p",
        "width": 1920,
        "height": 1080,
        "channels": 2,
    }

    process_mock = MagicMock()
    process_mock.poll.return_value = 0
    process_mock.returncode = 0
    process_mock.stderr.readline.return_value = ""
    mock_popen.return_value = process_mock

    worker = DownloadWorker(mock_request)
    mock_mode = MagicMock()
    worker.progress_mode_changed.connect(mock_mode)

    target = mock_request.output_dir / "test_ux.mp4"
    target.touch()
    worker._last_filename = str(target)

    with patch.object(Path, "rename"):
        temp_file = target.with_name(target.stem + ".wa_temp.mp4")
        temp_file.touch()
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 100
            worker._handle_post_download_transcode({"_filename": str(target)})

        # B) compatibility conversion başlayınca True (busy)
        # C) tamamlanınca False (normal)
        assert mock_mode.call_count == 2
        mock_mode.assert_any_call(True)
        mock_mode.assert_any_call(False)

@patch("src.download_worker.probe_media_codecs")
@patch("subprocess.Popen")
def test_download_worker_emits_progress_mode_on_cancel(mock_popen, mock_probe, mock_request):
    mock_probe.return_value = {
        "video_codec": "vp9",
        "audio_codec": "opus",
    }
    
    process_mock = MagicMock()
    process_mock.poll.return_value = None  # Running
    
    mock_popen.return_value = process_mock

    worker = DownloadWorker(mock_request)
    mock_mode = MagicMock()
    worker.progress_mode_changed.connect(mock_mode)
    
    target = mock_request.output_dir / "test_cancel.mp4"
    target.touch()
    worker._last_filename = str(target)
    
    # Set cancel flag during the loop
    def cancel_side_effect():
        worker._cancel_requested = True
        return ""
    
    process_mock.stderr.readline.side_effect = cancel_side_effect

    with patch.object(Path, "rename"):
        temp_file = target.with_name(target.stem + ".wa_temp.mp4")
        temp_file.touch()
        worker._handle_post_download_transcode({"_filename": str(target)})

        # D) conversion iptalde/hata durumunda bar normal moda resetleniyor (False)
        assert mock_mode.call_count == 2
        mock_mode.assert_any_call(True)
        mock_mode.assert_any_call(False)

def test_main_window_progress_ux(qapp):
    main_window = MainWindow()
    
    # A) normal download: progress 0-100
    main_window.progress_bar.setRange(0, 100)
    assert main_window.progress_bar.maximum() == 100
    
    # B) conversion starts: busy mode
    main_window._on_download_progress_mode_changed(True)
    assert main_window.progress_bar.minimum() == 0
    assert main_window.progress_bar.maximum() == 0
    
    # C) conversion finished: normal mode
    main_window._on_download_progress_mode_changed(False)
    assert main_window.progress_bar.minimum() == 0
    assert main_window.progress_bar.maximum() == 100
    
    # E) sonraki download: reset to 0-100 on start
    main_window.progress_bar.setRange(0, 0)
    main_window._set_ui_downloading(False)
    assert main_window.progress_bar.maximum() == 100
