"""Scans a folder for files with EXIF data."""

from os import walk 
from os.path import splitext, join as joinpath 
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_data(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        # An filetype not supported by PIL.
        ret = None
    return ret

def scan_exif_data( root ):
    """Scan a folder tree for exif data."""
    data = []
    for path, dirs, files in walk( root ):
        for name in files:
            row = {}
            row['path'] = path
            row['name'] = splitext( name )[0].lower()    
            row['ext'] = splitext( name )[1].lower()    
            exif = get_exif_data( joinpath(path, name) )
            if exif != None:
                row['exif'] = exif
                data.append( row )
    return data 

if __name__ == '__main__':
    from argparse import ArgumentParser
    from csv import DictWriter

    PARSER = ArgumentParser(description='Scan folder for files with EXIF data.')
    PARSER.add_argument( 'root', metavar='R', help='Dir to scan.')
    PARSER.add_argument( 'tags', metavar='T', nargs='+', help='EXIF tags.' )
    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument( '-hasdata', action='store_true', help='Has EXIF tags.' )
    GROUP.add_argument( '-nodata', action='store_true', help='No EXIF tags.' )
    ARGS = PARSER.parse_args()

    print 'Scanning ' + ARGS.root 
    FILES = scan_exif_data( ARGS.root )

    has_data = []
    no_data = []
    for f in FILES:
        for tag in ARGS.tags:
            if len( f['exif'] ) == 0:
                no_data.append( f ) 
            elif tag in f['exif'].keys():
                has_data.append( f )
            else:
                no_data.append( f ) 

    print '%d files with specified tags, %d files without.' % (len(has_data),len(no_data))

    if ARGS.hasdata == True:
        FILES = has_data
    elif ARGS.nodata == True:
        FILES = no_data

    print 'Creating CSV report.'
    # Extract keys out of sub-dictionary.
    for f in FILES:
        for k in f['exif'].keys():
            f[k] = f['exif'][k]
        del f['exif']

    HEADERS = ['path', 'name', 'ext' ]
    HEADERS = HEADERS + ARGS.tags 
    FILE = open('report.csv', 'wb')
    WRITER = DictWriter( FILE, HEADERS, extrasaction='ignore' )
    WRITER.writeheader()
    for f in FILES:
        WRITER.writerow( f )

