from __future__ import print_function
import plyr
import unittest


if __name__ == '__main__':
    class TestQuery(unittest.TestCase):
        def test_properties(self):
            qry = plyr.Query()
            for i in range(10):
                for key, value in plyr.Query.__dict__.items():
                    class_descr = str(type(value))
                    if 'descriptor' in class_descr and 'method' not in class_descr:
                        default = ''
                        default = plyr.Query.__dict__[key].__get__(qry)

                        print('-> Setting', repr(key), 'to', default, '; ', type(default))

                        try:
                            plyr.Query.__dict__[key].__set__(qry, default)
                            print('-- set --')
                        except AttributeError:
                            pass

        def test_setget_data(self):
            qry = plyr.Query()
            qry.artist = 'Kittens'
            qry.artist = qry.artist

    unittest.main()
