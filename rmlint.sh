#!/bin/sh
#This file was autowritten by 'rmlint'
#rmlint was executed from: /home/chris/dev/python-glyr/docs/build/html

ask() {
cat << EOF
This script will delete certain files rmlint found.
It is highly advisable to view the script (or log) first!

Execute this script with -d to disable this message
Hit enter to continue; CTRL-C to abort immediately
EOF
read
}

usage()
{
cat << EOF
usage: $0 options

This script run the test1 or test2 over a machine.

OPTIONS:
-h      Show this message
-d      Do not ask before running
-x      Keep rmlint.sh and rmlint.log
EOF
}

DO_REMOVE=
DO_ASK=

while getopts “dhx” OPTION
do
  case $OPTION in
     h)
       usage
       exit 1
       ;;
     d)
       DO_ASK=false
       ;;
     x)
       DO_REMOVE=false
       ;;
  esac
done

if [[ -z $DO_ASK ]]
then
  usage
  ask 
fi
echo  '/tmp/archive/url.txt' # original
rm -f '/tmp/archive/archive/url.txt' # duplicate
echo  '/tmp/archive/xml/file.xsd' # original
rm -f '/tmp/archive/archive/xml/file.xsd' # duplicate
echo  '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=group&g=2799&sid=a995838be5756a09b3af19fbe0db2223/data' # original
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=group&g=2800&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=group&g=9&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
echo  '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=1438&sid=a995838be5756a09b3af19fbe0db2223/data' # original
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=2021&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=4107&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=4549&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=5139&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=5783&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6043&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6448&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6576&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6833&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6842&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=6927&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=7664&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=7704&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=7909&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8099&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8290&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8621&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8954&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8962&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
rm -f '/tmp/archive/content/www.blendpolis.de/memberlist.php?mode=viewprofile&u=8982&sid=a995838be5756a09b3af19fbe0db2223/data' # duplicate
                      
if [[ -z $DO_REMOVE ]]
then                  
  rm -f rmlint.log    
  rm -f rmlint.sh     
fi                    
