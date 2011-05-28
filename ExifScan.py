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
    ROOT = argv[1]

    print 'Scanning ' + ROOT 
    DATA = scan_exif_data( ROOT )

    EXTS = set([ r['ext'] for r in DATA ])
    for ext in EXTS:
        has_data = []
        no_data = []
        for f in [ f for f in DATA if f['ext'] == ext ]:
            if len( f['exif'] ) > 0:
                has_data.append( f ) 
            else:
                no_data.append( f )
        print '%s - %d with EXIF, %d without EXIF:' % (ext, len(has_data), len(no_data))
        for f in no_data:
            print '\t' + joinpath( f['path'], f['name'] + f['ext'] )

