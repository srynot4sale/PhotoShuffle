"""Scans a folder and builds a sorted structure based on image creation time."""

from os import walk, name as osname, makedirs
from os.path import splitext, getctime, join as joinpath, exists  
from sys import argv
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from subprocess import Popen, PIPE
from csv import DictWriter
from shutil import copyfile

def get_creation_time(fname):
    """Get the creation time of a file, uses stat on unix."""
    timestamp = 0
    if osname != 'posix':
        timestamp = getctime( fname )
    else:
        process = Popen(['stat', '-f%B', fname],
            stdout=PIPE, stderr=PIPE)
        if process.wait():
            raise OSError(process.stderr.read().rstrip())
        else:
            timestamp = int(process.stdout.read())
    return datetime.fromtimestamp( timestamp ) 

def get_exif(fname):
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
    return ret

if __name__ == '__main__':
    OLD = argv[1]
    NEW = argv[2]

    # Gather data about folder structure and file creation date.
    print 'Scanning ' + OLD 
    DATA = []
    for path, dirs, files in walk( OLD ):
        for name in files:
            row = {}
            row['path'] = path
            row['name'] = splitext( name )[0]
            row['ext'] = splitext( name )[1].lower()    
            filename = joinpath(path, name)
            info = get_exif( filename )
            # Get creation time from EXIF data or from OS.
            # datetime precidence is DateTimeOriginal > DateTime > ctime.
            if 'DateTimeOriginal' in info.keys():
                row['datetime'] = info['DateTimeOriginal']
            if 'DateTime' in info.keys() and 'datetime' not in row.keys():
                row['datetime'] = info['DateTime']
            if 'datetime' not in row.keys():
                ctime = get_creation_time( filename )
                row['datetime'] = ctime.strftime('%Y:%m:%d %H:%M:%S')
            # Generate new path using date.
            filetime = datetime.strptime(row['datetime'],'%Y:%m:%d %H:%M:%S')
            row['newpath'] = joinpath( NEW, filetime.strftime('%Y/%b/%d') )
            DATA.append( row )

    # Generate filenames: 1 to n+1 (zero padded).
    print 'Generating filenames.'
    for newdir in set( [ i['newpath'] for i in DATA ] ):
        files = [ row for row in DATA if row['newpath'] == newdir ]
        for i in range(len(files)):
            files[i]['newname'] = '%0*d' % (len(str(len(files))), i+1)

    # Write out report.
    print 'Writing report.csv'
    HEADERS = [ 'path', 'name', 'ext', 'datetime', 'newpath','newname' ]
    WRITER = DictWriter( open('report.csv', 'wb'), HEADERS )
    WRITER.writeheader()
    for row in DATA:
        WRITER.writerow( row )

    # Copy the files to new locations.
    print 'Copying files.'
    for row in DATA:
        oldfile = joinpath( row['path'], row['name'] + row['ext'] )
        newfile = joinpath( row['newpath'], row['newname'] + row['ext'] )
        print newfile
        if not exists( row['newpath'] ):
            makedirs( row['newpath'] )
        copyfile( oldfile, newfile )
