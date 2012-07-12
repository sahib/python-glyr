#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plyr

if __name__ == '__main__':
    # Create a Query, so plyr knows what you want to search
    qry = plyr.Query(get_type='lyrics', artist='Tenacious D', title='Deth Starr')

    # Now let it search all the providers
    items = qry.commit()

    # Convert lyrics (bytestring) to a proper UTF-8 text
    try:
        print(str(items[0].data, 'UTF-8'))
    except UnicodeError as err:
        print('Cannot display lyrics, conversion failed:', err)
