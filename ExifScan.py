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
    from sys import argv
    from csv import DictWriter
    # First arg is the root of directory tree.
    ROOT = argv[1]
    # Second arg is single EXIF column to include in CSV.
    DATA = argv[2]

    print 'Scanning ' + ROOT 
    FILES = scan_exif_data( ROOT )

    print 'Calculating stats.'
    EXTS = set([ r['ext'] for r in FILES ])
    print 'File\tData\tNoData'
    for ext in EXTS:
        has_data = 0
        no_data = 0
        for f in [ f for f in FILES if f['ext'] == ext ]:
            if len( f['exif'] ) > 0:
                has_data += 1
            else:
                no_data += 1
        print '%s\t%d\t%d' % (ext, has_data, no_data)

    print 'Creating CSV report.'

    # Extract keys out of sub-dictionary.
    for f in FILES:
        for k in f['exif'].keys():
            f[k] = f['exif'][k]
        del f['exif']

    HEADERS = ['path', 'name', 'ext' ]
    HEADERS.append( DATA )
    FILE = open('report.csv', 'wb')
    WRITER = DictWriter( FILE, HEADERS, extrasaction='ignore' )
    WRITER.writeheader()
    for f in FILES:
        WRITER.writerow( f )

