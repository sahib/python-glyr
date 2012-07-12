import plyr


def get_and_set_data():
    c = plyr.Cache()
    print(c.data)
    c.data = c.data
    print(c.data)
    c.data = b'Kittens'
    print(c.data)
    c.data = b'Kittens'
    print(c.data)
    c.data = c.data
    print(c.data)


if __name__ == '__main__':
    get_and_set_data()
