#################################################################
# This file is part of plyr
# + a commnandline tool and library to download various sort of musicrelated metadata.
# + Copyright (C) [2011-2012]  [Christopher Pahl]
# + Hosted at: https://github.com/sahib/python-glyr
#
# plyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# plyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with plyr. If not, see <http://www.gnu.org/licenses/>.
#################################################################
###########################################################################
#                    Common Utils on the Wrapper Side                     #
###########################################################################

# I refuse to write UTF-8 all the time
cdef _stringify(char * bytestring):
    'Convert bytes to str, using utf-8'
    if bytestring is NULL:
        return ''
    else:
        return bytestring.decode('UTF-8')



# We use UTF-8 anyways everywhere
cdef _bytify(string):
    'Convert str to bytes, using utf-8'
    return string.encode('UTF-8')
