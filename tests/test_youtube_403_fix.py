from pathlib import Path
from unittest.mock import MagicMock, patch

from src.download_worker import DownloadWorker
from src.models import DownloadRequest


@patch("src.download_worker.reserve_unique_media_path")
@patch("src.download_worker.create_ytdl")
def test_youtube_video_direct_download(mock_create_ytdl, mock_reserve):
    """
    YouTube video indirmelerinde info extraction (download=False) ardindan
    process_ie_result(download=True) ÇAĞRILMAMALI, doğrudan fresh bir
    downloader ile extract_info(url, download=True) ÇAĞRILMALIDIR (403 fix).
    """
    mock_reserve.return_value = Path("test_out/test.mp4")
    
    req = DownloadRequest(
        url="https://youtube.com/watch?v=DX7HyN7oJjE",
        media_type="Video (MP4)",
        quality="1080p",
        output_dir=Path("test_out"),
        playlist=False
    )
    
    worker = DownloadWorker(req)
    worker._save_completed_record = MagicMock(return_value="test_out/test.mp4")
    worker.succeeded = MagicMock()
    worker.failed = MagicMock()
    worker.cancelled = MagicMock()
    
    mock_downloader_instance1 = MagicMock()
    mock_downloader_instance1.params = {"outtmpl": "test1.mp4"}
    mock_downloader_instance1.extract_info.return_value = {"_type": "video", "title": "test", "id": "123"}
    mock_downloader_instance1.prepare_filename.return_value = "test_out/test.mp4"
    
    mock_downloader_instance2 = MagicMock()
    mock_downloader_instance2.params = {"outtmpl": "test2.mp4"}
    mock_downloader_instance2.extract_info.return_value = {"title": "test_download", "id": "123"}
    
    # create_ytdl ile dönen downloader'lar sırasıyla
    mock_create_ytdl.side_effect = [
        MagicMock(__enter__=MagicMock(return_value=mock_downloader_instance1), __exit__=MagicMock(return_value=False)),
        MagicMock(__enter__=MagicMock(return_value=mock_downloader_instance2), __exit__=MagicMock(return_value=False))
    ]
    
    with patch("src.download_worker.patch_subprocess_for_hidden_console"):
        worker.run()
    
    # 1. downloader metadata extraction yapmis olabilir (download=False)
    mock_downloader_instance1.extract_info.assert_called_once_with(req.url, download=False)
    
    # 2. downloader (fresh) doğrudan indirme yapmış olmalı (download=True)
    mock_downloader_instance2.extract_info.assert_called_once_with(req.url, download=True)
    
    # HİÇBİR downloader'da process_ie_result ÇAĞRILMAMALI!
    mock_downloader_instance1.process_ie_result.assert_not_called()
    mock_downloader_instance2.process_ie_result.assert_not_called()

@patch("src.download_worker.reserve_unique_media_path")
@patch("src.session_manager.SessionManager")
@patch("src.download_worker.create_ytdl")
def test_youtube_video_retry_flow(mock_create_ytdl, mock_session_manager, mock_reserve):
    """
    İlk deneme başarısız olursa, retry mekanizması (örneğin session_center)
    devreye girdiğinde yine taze bir extract_info(download=True) çağrılmalıdır.
    """
    mock_reserve.return_value = Path("test_out/test.mp4")
    
    req = DownloadRequest(
        url="https://youtube.com/watch?v=DX7HyN7oJjE",
        media_type="Video (MP4)",
        quality="1080p",
        output_dir=Path("test_out"),
        playlist=False,
        session_method="auto"
    )
    
    worker = DownloadWorker(req)
    worker._save_completed_record = MagicMock(return_value="test_out/test.mp4")
    worker.succeeded = MagicMock()
    worker.failed = MagicMock()
    worker.cancelled = MagicMock()
    
    mock_temp_ctx = MagicMock()
    mock_temp_ctx.__enter__.return_value = "dummy_cookie.txt"
    mock_session_mgr_inst = MagicMock()
    mock_session_mgr_inst.create_temp_cookiefile.return_value = mock_temp_ctx
    mock_session_manager.return_value = mock_session_mgr_inst
    
    # 1. Attempt (No session) - FAILS on final download
    mock_dl_meta1 = MagicMock()
    mock_dl_meta1.params = {"outtmpl": "test1.mp4"}
    mock_dl_meta1.extract_info.return_value = {"_type": "video", "title": "test", "id": "123"}
    mock_dl_meta1.prepare_filename.return_value = "test_out/test.mp4"
    
    mock_dl_down1 = MagicMock()
    mock_dl_down1.params = {"outtmpl": "test2.mp4"}
    mock_dl_down1.extract_info.side_effect = Exception("Sign in to confirm you're not a bot (login required)")
    
    # 2. Attempt (session_center) - SUCCEEDS
    mock_dl_meta2 = MagicMock()
    mock_dl_meta2.params = {"outtmpl": "test3.mp4"}
    mock_dl_meta2.extract_info.return_value = {"_type": "video", "title": "test", "id": "123"}
    mock_dl_meta2.prepare_filename.return_value = "test_out/test.mp4"
    
    mock_dl_down2 = MagicMock()
    mock_dl_down2.params = {"outtmpl": "test4.mp4"}
    
    def trace_meta1(*a, **kw): return {"_type": "video", "title": "test", "id": "123"}
    def trace_down1(*a, **kw): raise Exception("Sign in to confirm you're not a bot (login required)")  # noqa: TRY002
    def trace_meta2(*a, **kw): return {"_type": "video", "title": "test", "id": "123"}
    def trace_down2(*a, **kw): return {"title": "test_download", "id": "123"}

    mock_dl_meta1.extract_info.side_effect = trace_meta1
    mock_dl_down1.extract_info.side_effect = trace_down1
    mock_dl_meta2.extract_info.side_effect = trace_meta2
    mock_dl_down2.extract_info.side_effect = trace_down2

    mock_create_ytdl.side_effect = [
        MagicMock(__enter__=MagicMock(return_value=mock_dl_meta1), __exit__=MagicMock(return_value=False)),
        MagicMock(__enter__=MagicMock(return_value=mock_dl_down1), __exit__=MagicMock(return_value=False)),
        MagicMock(__enter__=MagicMock(return_value=mock_dl_meta2), __exit__=MagicMock(return_value=False)),
        MagicMock(__enter__=MagicMock(return_value=mock_dl_down2), __exit__=MagicMock(return_value=False)),
    ]
    
    with patch("src.download_worker.patch_subprocess_for_hidden_console"):
        worker.run()
    
    # Her iki iterasyonda da process_ie_result kullanılmamalı
    mock_dl_meta1.process_ie_result.assert_not_called()
    mock_dl_down1.process_ie_result.assert_not_called()
    mock_dl_meta2.process_ie_result.assert_not_called()
    mock_dl_down2.process_ie_result.assert_not_called()
    
    # Her iki iterasyonda da extract_info(download=True) kullanılmış olmalı
    mock_dl_down1.extract_info.assert_called_once_with(req.url, download=True)
    mock_dl_down2.extract_info.assert_called_once_with(req.url, download=True)


@patch("src.download_worker.reserve_unique_media_path")
@patch("src.download_worker.create_ytdl")
def test_youtube_video_strict_quality_failure_no_unbounded_retry(mock_create_ytdl, mock_reserve):
    """
    YouTube VIDEO formatında kalite sınırlıysa ('Requested format is not available'),
    sınırsız (bv*+ba/b) bir fallback yapılmamalıdır. Exception yutulmamalı veya hata vermelidir.
    """
    mock_reserve.return_value = Path("test_out/test.mp4")

    req = DownloadRequest(
        url="https://youtube.com/watch?v=DX7HyN7oJjE",
        media_type="Video (MP4)",
        quality="1080p",
        output_dir=Path("test_out"),
        playlist=False,
        session_method="none"
    )

    worker = DownloadWorker(req)
    worker.failed = MagicMock()

    mock_dl_meta1 = MagicMock()
    mock_dl_meta1.params = {"outtmpl": "test1.mp4"}
    mock_dl_meta1.extract_info.return_value = {"_type": "video", "title": "test", "id": "123"}
    mock_dl_meta1.prepare_filename.return_value = "test_out/test.mp4"

    mock_dl_down1 = MagicMock()
    mock_dl_down1.params = {"outtmpl": "test2.mp4"}
    
    def trace_down1(*a, **kw): raise Exception("Requested format is not available")  # noqa: TRY002
    mock_dl_down1.extract_info.side_effect = trace_down1

    mock_create_ytdl.side_effect = [
        MagicMock(__enter__=MagicMock(return_value=mock_dl_meta1), __exit__=MagicMock(return_value=False)),
        MagicMock(__enter__=MagicMock(return_value=mock_dl_down1), __exit__=MagicMock(return_value=False)),
    ]

    with patch("src.download_worker.patch_subprocess_for_hidden_console"):
        worker.run()

    # Sadece metadata ve failing indirme çağrılmalı, 3. bir unbound fallback çağrısı olmamalı
    assert mock_create_ytdl.call_count == 2
    
    # Check that failed was called with a reason indicating the error
    worker.failed.emit.assert_called()
    
    # Bütün create_ytdl çağrılarındaki options dict'leri kontrol et
    for call in mock_create_ytdl.call_args_list:
        options = call.args[0]
        assert options.get("format") != "bv*+ba/b", "Sınırsız format fallback'i kullanılmamalı!"
