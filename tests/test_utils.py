import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.utils import format_iso_to_local, probe_media_codecs


class TestUtils(unittest.TestCase):
    def test_format_iso_to_local_valid(self):
        # Create a specific UTC time
        utc_dt = datetime(2026, 8, 9, 8, 6, 56, 629641, tzinfo=timezone.utc)
        iso_str = utc_dt.isoformat()

        # Format it
        result = format_iso_to_local(iso_str)

        # Calculate expected local time string
        expected = utc_dt.astimezone().strftime("%d.%m.%Y %H:%M")

        self.assertEqual(result, expected)
        self.assertNotIn("T", result)
        self.assertNotIn("+", result)
        self.assertNotIn(".", result.split(" ")[1])  # No microseconds in time part

    def test_format_iso_to_local_invalid_string(self):
        # Should return the original string safely
        self.assertEqual(format_iso_to_local("invalid_timestamp_123"), "invalid_timestamp_123")
        self.assertEqual(format_iso_to_local("Just some string"), "Just some string")

    def test_format_iso_to_local_empty_or_unknown(self):
        # Should return "Bilinmiyor"
        self.assertEqual(format_iso_to_local(""), "Bilinmiyor")
        self.assertEqual(format_iso_to_local(None), "Bilinmiyor")
        self.assertEqual(format_iso_to_local("Bilinmiyor"), "Bilinmiyor")

    @patch("subprocess.run")
    def test_probe_media_codecs_success(self, mock_run):
        # Mock successful ffprobe output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
        {
            "streams": [
                {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080, "pix_fmt": "yuv420p"},
                {"codec_type": "audio", "codec_name": "aac", "channels": 2, "sample_rate": "48000"}
            ],
            "format": {
                "duration": "120.5"
            }
        }
        """
        mock_run.return_value = mock_result

        with patch("pathlib.Path.exists", return_value=True):
            result = probe_media_codecs("dummy.mp4")

        # Verify subprocess.run was called correctly without duplicate kwargs
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        self.assertIn("check", kwargs)
        self.assertFalse(kwargs["check"])

        # Verify parsed results
        self.assertEqual(result["video_codec"], "h264")
        self.assertEqual(result["audio_codec"], "aac")
        self.assertEqual(result["width"], 1920)
        self.assertEqual(result["height"], 1080)
        self.assertEqual(result["pix_fmt"], "yuv420p")
        self.assertEqual(result["channels"], 2)
        self.assertEqual(result["sample_rate"], 48000)
        self.assertAlmostEqual(result["duration"], 120.5)

    @patch("subprocess.run")
    def test_probe_media_codecs_error(self, mock_run):
        # Mock failed ffprobe run (e.g. invalid file)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        with patch("pathlib.Path.exists", return_value=True):
            result = probe_media_codecs("dummy.mp4")

        self.assertEqual(result["video_codec"], "unknown")
        self.assertEqual(result["audio_codec"], "unknown")
        self.assertEqual(result["width"], 0)

if __name__ == "__main__":
    unittest.main()
