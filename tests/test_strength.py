import unittest

from passguard.strength import analyze, charset_size, format_duration, has_keyboard_pattern, is_common


class TestStrength(unittest.TestCase):
    def test_charset_size(self):
        self.assertEqual(charset_size("abc"), 26)
        self.assertEqual(charset_size("aB"), 52)
        self.assertEqual(charset_size("aB3"), 62)
        self.assertEqual(charset_size("aB3!"), 95)
        self.assertEqual(charset_size(""), 0)

    def test_common_passwords_detected(self):
        self.assertTrue(is_common("password"))
        self.assertTrue(is_common("PASSWORD"))
        self.assertTrue(is_common("p@ssw0rd"))  # leetspeak
        self.assertTrue(is_common("dragon123!"))  # common word + suffix
        self.assertFalse(is_common("violet-tractor-lamp"))

    def test_keyboard_patterns(self):
        self.assertTrue(has_keyboard_pattern("myqwertypass"))
        self.assertTrue(has_keyboard_pattern("x9876x"))  # reversed digits row
        self.assertFalse(has_keyboard_pattern("Tr0ub4dor"))

    def test_weak_password_scores_low(self):
        result = analyze("password")
        self.assertEqual(result.score, 0)
        self.assertEqual(result.crack_time, "instantly")
        self.assertTrue(result.warnings)

    def test_repeated_chars_penalized(self):
        self.assertLess(analyze("aaaaaaaaaaaa").entropy_bits, analyze("hqzmxkbwtrpd").entropy_bits)

    def test_strong_password_scores_high(self):
        result = analyze("violet-Tractor-lamp-river-92")
        self.assertEqual(result.score, 4)
        self.assertFalse(result.warnings)

    def test_format_duration(self):
        self.assertEqual(format_duration(0.5), "instantly")
        self.assertEqual(format_duration(1), "1 second")
        self.assertEqual(format_duration(7200), "2 hours")
        self.assertEqual(format_duration(1e30), "millions of centuries")


if __name__ == "__main__":
    unittest.main()
