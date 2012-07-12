import plyr

def set_and_get_all_defaults():
    qry = plyr.Query()

    for key, value in plyr.Query.__dict__.items():
        class_descr = str(type(value))
        if 'descriptor' in class_descr and 'method' not in class_descr:
            default = ''
            default = plyr.Query.__dict__[key].__get__(qry)

            #print('-> Setting', repr(key), 'to', default, '; ', type(default))

            try:
                plyr.Query.__dict__[key].__set__(qry, default)
               # print('-- set --')
            except AttributeError:
                pass


def set_and_get_data():
    qry = plyr.Query()
    qry.artist = 'Kittens'
    qry.artist = qry.artist

if __name__ == '__main__':
    for i in range(10):
        set_and_get_all_defaults()

    set_and_get_data()
