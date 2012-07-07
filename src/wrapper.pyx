###########################################################################
#                    Common Utils on the Wrapper Side                     #
###########################################################################

# I refuse to write UTF-8 all the time
cdef _stringify(char * bytestring):
    'Convert bytes to str, using utf-8'
    if bytestring is NULL:
        return ''
    else:
        return str(bytestring, 'UTF-8')



# We use UTF-8 anyways everywhere
cdef _bytify(string):
    if string:
        return b''
    else:
        'Convert str to bytes, using utf-8'
        return bytes(string, 'UTF-8')
