#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plyr
from time import sleep
from threading import Thread


def foo():
    i = 0
    while True:
        print(i)
        i += 1
        sleep(0.1)

worker = Thread(target=foo)
worker.start()

sleep(3)

while True:
    qry = plyr.Query(artist='Аркона', title='Гой Роде Гой!', get_type='lyrics')
    print('commit() started')
    qry.commit()
    print('commit() finished')
    sleep(3)
