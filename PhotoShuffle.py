"""Scans a folder and builds a sorted structure based on image creation time."""

from os import walk, name as osname
from os.path import splitext, getctime, join, isfile
from sys import argv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from subprocess import Popen, PIPE
from csv import DictWriter

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

    # Gather data about folder structure and file creation times.
    DATA = []
    for root, dirs, files in walk( OLD ):
        for name in files:
            row = {}
            row['path'] = root
            row['name'] = name
            filename = join(root, name)
            ext = splitext( name )[1].lower()    
            row['ext'] = ext
            info = get_exif( filename )
            # Get creation time from EXIF data or from OS.
            if 'DateTimeOriginal' in info.keys():
                row['DateTimeOriginal'] = info['DateTimeOriginal']
            if 'DateTime' in info.keys():
                row['DateTime'] = info['DateTime']
            row['ctime'] = get_creation_time( filename ).strftime('%Y:%m:%d %H:%M:%S')
            DATA.append( row )

    # Write out report.
    HEADERS = [ 'path', 'name', 'ext', 'DateTimeOriginal', 'DateTime', 'ctime' ]
    writer = DictWriter( open('report.csv', 'wb'), HEADERS )
    writer.writeheader()
    for row in DATA:
        writer.writerow( row )
