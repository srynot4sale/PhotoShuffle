"""Scans a given folder and its children and builds a sorted fodler structure based on meta data in images."""

from os import walk,name as osname
from os.path import splitext,getctime,join,isfile
from sys import argv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from subprocess import Popen,PIPE

def get_creation_time(path):
    """Get the creation time of a file, uses stat on unix."""
    timestamp = 0
    if osname != 'posix':
        timestamp = getctime( filename )
    else:
        p = Popen(['stat', '-f%B', path],
            stdout=PIPE, stderr=PIPE)
        if p.wait():
            raise OSError(p.stderr.read().rstrip())
        else:
            timestamp = int(p.stdout.read())
    return datetime.fromtimestamp( timestamp ) 

def get_exif(fn):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        i = Image.open(fn)
        if hasattr( i, '_getexif' ):
            info = i._getexif()
            if info != None:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
        else:
            print 'NO EXIF ' + fn
    except IOError:
        print 'IOERROR ' + fn
    return ret

if __name__ == '__main__':
    OLD = argv[1]

    print 'Scanning ' + OLD 
    exts = {}
    noinfo = 0
    withinfo = 0
    for root, dirs, files in walk( OLD ):
        if 'iPhoto Library' not in root:
            for name in files:
                filename = join(root,name)
                if isfile( filename ):
                    # record number of different file types (by extension).
                    ext = splitext( name )[1].lower()    
                    exts[ext] = exts.get( ext, 0 ) + 1 
                    if ext in ['.jpg','.jpeg','.png','.tiff']:
                        info = get_exif( filename )
                        if ('DateTime' in info.keys()) or ('DateTimeOriginal' in info.keys()):
                            #print filename
                            #print info['DateTime']
                            withinfo += 1
                        else:
                            print filename
                            print get_creation_time( filename )
                            noinfo += 1
    print exts 
    print withinfo
    print noinfo

