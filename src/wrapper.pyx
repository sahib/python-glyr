###########################################################################
#                    Common Utils on the Wrapper Side                     #
###########################################################################

# I refuse to write UTF-8 all the time
cdef _stringify(bytestring):
    'Convert bytes to str, using utf-8'
    return str(bytestring, 'UTF-8')


# We use UTF-8 anyways everywhere
cdef _bytify(string):
    'Convert str to bytes, using utf-8'
    return bytes(string, 'UTF-8')
