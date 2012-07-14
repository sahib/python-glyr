import plyr


def foreach_callback(query, cache):
    print(query)
    cache.print_cache()


if __name__ == '__main__':
    db = plyr.Database('/tmp')
    dummy = db.make_dummy()

    db.insert(plyr.Query(artist='Derp', album='Derpson', get_type='cover'), dummy)
    db.foreach(foreach_callback)
