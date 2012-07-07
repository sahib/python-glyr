#include "query.pyx"
#include "cache.pyx"

def callback_test(c, q):
    return 0

q = Query()
q.verbosity = 3
q.artist = 'Akrea'
print(q.providers)
q.album = 'Lebenslinie'
q.title = 'Ein Leben lang'

#q.get_type = 2
q.get_type = 'lyrics'
q.callback = callback_test
print(q.commit())
print(q.error)


c = Cache()
