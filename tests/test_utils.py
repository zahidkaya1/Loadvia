import unittest
from datetime import datetime, timezone

from src.utils import format_iso_to_local


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

if __name__ == "__main__":
    unittest.main()
