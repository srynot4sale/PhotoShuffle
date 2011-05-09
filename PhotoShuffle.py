"""Scans a folder and builds a sorted structure based on image creation time."""

from os import walk, name as osname
from os.path import splitext, getctime, join, isfile
from sys import argv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from subprocess import Popen, PIPE

def get_creation_time(path):
    """Get the creation time of a file, uses stat on unix."""
    timestamp = 0
    if osname != 'posix':
        timestamp = getctime( path )
    else:
        process = Popen(['stat', '-f%B', path],
            stdout=PIPE, stderr=PIPE)
        if process.wait():
            raise OSError(process.stderr.read().rstrip())
        else:
            timestamp = int(process.stdout.read())
    return datetime.fromtimestamp( timestamp ) 

def get_exif(path):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(path)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
        else:
            print 'NO EXIF ' + path
    except IOError:
        print 'IOERROR ' + path
    return ret

if __name__ == '__main__':
    OLD = argv[1]

    print 'Scanning ' + OLD 
    NOINFO = 0
    WITHINFO = 0
    for root, dirs, files in walk( OLD ):
        if 'iPhoto Library' not in root:
            for name in files:
                filename = join(root, name)
                if isfile( filename ):
                    ext = splitext( name )[1].lower()    
                    if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
                        info = get_exif( filename )
                        # Get creation time from EXIF data or from OS.
                        if 'DateTimeOrginal' in info.keys():
                            WITHINFO += 1
                        elif 'DateTime' in info.keys():
                            #print filename
                            #print info['DateTime']
                            WITHINFO += 1
                        else:
                            print filename
                            print get_creation_time( filename )
                            NOINFO += 1
    print WITHINFO
    print NOINFO

