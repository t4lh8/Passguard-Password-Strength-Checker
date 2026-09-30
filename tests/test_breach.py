import unittest
from unittest.mock import MagicMock, patch

from passguard.breach import parse_range_response, pwned_count, sha1_hex, split_hash

# SHA-1("password") = 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
PASSWORD_SUFFIX = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"


class TestBreach(unittest.TestCase):
    def test_sha1_and_split(self):
        full = sha1_hex("password")
        self.assertEqual(full, "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8")
        self.assertEqual(split_hash(full), ("5BAA6", PASSWORD_SUFFIX))

    def test_parse_range_response(self):
        body = f"0018A45C4D1DEF81644B54AB7F969B88D65:1\r\n{PASSWORD_SUFFIX}:9545824\r\n"
        self.assertEqual(parse_range_response(body, PASSWORD_SUFFIX), 9545824)
        self.assertEqual(parse_range_response(body, "NOTINLIST"), 0)

    @patch("passguard.breach.urllib.request.urlopen")
    def test_only_prefix_is_sent(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = f"{PASSWORD_SUFFIX}:42".encode()
        mock_urlopen.return_value.__enter__.return_value = response

        self.assertEqual(pwned_count("password"), 42)
        sent_url = mock_urlopen.call_args[0][0].full_url
        self.assertTrue(sent_url.endswith("/range/5BAA6"))
        self.assertNotIn(PASSWORD_SUFFIX, sent_url)


if __name__ == "__main__":
    unittest.main()
