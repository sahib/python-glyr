import plyr
import unittest

"""
Very cheap tests.

There more for testing if the actual function passthrough works.
"""

class TestMisc(unittest.TestCase):
    def test_download(self):
        google_com = plyr.download('www.google.de')
        self.assertTrue(len(google_com.data) > 0)
        self.assertEqual(len(google_com.data), google_com.size)

    def test_VERSION(self):
        self.assertTrue(len(plyr.VERSION) == 3)

        def test_levenshtein_cmp(self):
            self.assertEqual(plyr.levenshtein_cmp('abc', 'zaab'), 3)

    def test_levenshtein_normcmp(self):
        self.assertEqual(plyr.levenshtein_normcmp('Akrea(CD 01)', '</a> akrea </a>'), 0)

    def test_type_is_image(self):
        self.assertTrue(plyr.type_is_image('cover'))
        self.assertTrue(plyr.type_is_image('backdrops'))
        self.assertFalse(plyr.type_is_image(''))
        self.assertFalse(plyr.type_is_image('blarghherhetr'))
        self.assertFalse(plyr.type_is_image('lyrics'))

if __name__ == '__main__':
    print(plyr.version())
    unittest.main()
