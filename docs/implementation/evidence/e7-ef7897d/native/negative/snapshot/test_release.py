import unittest

from release import normalize_release


class NormalizeReleaseTests(unittest.TestCase):
    def test_accepts_bare_and_prefixed_versions(self):
        for value in ("1.2.3", "v1.2.3"):
            with self.subTest(value=value):
                self.assertEqual(normalize_release(value), "v1.2.3")

    def test_accepts_zero_and_large_components(self):
        for value, expected in (
            ("0.0.0", "v0.0.0"),
            ("v0.10.200", "v0.10.200"),
            ("12345678901234567890.98765432109876543210.0",
             "v12345678901234567890.98765432109876543210.0"),
        ):
            with self.subTest(value=value):
                self.assertEqual(normalize_release(value), expected)

    def test_rejects_malformed_strings(self):
        values = (
            "", "1", "1.2", "1.2.3.4", "1..3", ".1.2.3", "1.2.3.",
            "one.2.3", "v", "vv1.2.3", "V1.2.3", "1.2.-3", "-1.2.3",
            "+1.2.3", "1.2.+3", "1.2.3-rc1", "1.2.3+build",
            " 1.2.3", "1.2.3 ", "1.2.3\n", "v 1.2.3",
            "01.2.3", "1.02.3", "1.2.003", "v00.0.0", "1.2.٣",
        )
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_release(value)

    def test_rejects_nonstrings(self):
        for value in (None, 123, 1.2, b"1.2.3", [1, 2, 3], True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    normalize_release(value)


if __name__ == "__main__":
    unittest.main()
