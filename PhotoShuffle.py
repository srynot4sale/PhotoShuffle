"""Scans a folder and builds a date sorted tree based on image creation time."""

from os import walk, makedirs
from os.path import splitext, join as joinpath, exists  
from sys import argv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from csv import DictWriter
from shutil import copyfile

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
        print 'IOERROR ' + fname
        ret = None
    return ret

if __name__ == '__main__':
    ORIG_PATH = argv[1]
    NEW_PATH = argv[2]

    # Get creation time from EXIF data.
    print 'Scanning ' + ORIG_PATH 
    DATA = []
    for path, dirs, files in walk( ORIG_PATH ):
        for name in files:
            r = {}
            r['path'] = path
            r['name'] = splitext( name )[0].lower()    
            r['ext'] = splitext( name )[1].lower()    
            info = get_exif_data( joinpath(path, name) )
            if info != None:
                # precidence is DateTimeOriginal > DateTime.
                if 'DateTimeOriginal' in info.keys():
                    r['ftime'] = info['DateTimeOriginal']
                elif 'DateTime' in info.keys():
                    r['ftime'] = info['DateTime']
            if 'ftime' in r.keys():
                r['ftime'] = datetime.strptime(r['ftime'],'%Y:%m:%d %H:%M:%S')
                DATA.append( r )

    # Generate new path YYYY/MM/DD/ using EXIF date.
    for r in DATA:
        r['newpath'] = joinpath( NEW_PATH, r['ftime'].strftime('%Y/%m/%d') )

    # Generate filenames per directory: 1 to n+1 (zero padded) with DDMMMYY.
    print 'Generating filenames.'
    for newdir in set( [ i['newpath'] for i in DATA ] ):
        files = [ r for r in DATA if r['newpath'] == newdir ]
        for i in range( len(files) ):
            datestr = files[i]['ftime'].strftime('%d%b%Y')
            pad = len( str( len(files) ) )
            files[i]['newname'] = '%0*d_%s' % (pad, i+1, datestr)

    # Write out CSV format report for debugging.
    print 'Writing report.csv'
    HEADERS = [ 'path', 'name', 'ext', 'ftime', 'newpath','newname' ]
    WRITER = DictWriter( open('report.csv', 'wb'), HEADERS )
    WRITER.writeheader()
    for r in DATA:
        WRITER.writerow( r )

    # Copy the files to their new locations, creating directories as requried.
    print 'Copying files.'
    for r in DATA:
        origfile = joinpath( r['path'], r['name'] + r['ext'] )
        newfile = joinpath( r['newpath'], r['newname'] + r['ext'] )
        if not exists( r['newpath'] ):
            makedirs( r['newpath'] )
        print origfile +' to '+ newfile
        copyfile( origfile, newfile )

