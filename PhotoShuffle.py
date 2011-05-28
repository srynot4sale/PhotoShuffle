"""Scans a folder and builds a date sorted tree based on image creation time."""

from os import makedirs, listdir, rmdir
from os.path import join as joinpath, exists  
from sys import argv
from datetime import datetime
from shutil import move
from ExifScan import scan_exif_data

if __name__ == '__main__':
    ORIG_PATH = argv[1]
    NEW_PATH = argv[2]

    print 'Gathering & processing EXIF data.'

    # Get creation time from EXIF data.
    DATA = scan_exif_data( ORIG_PATH )

    # Remove any files without EXIF data from list.
    DATA = [ f for f in DATA if len(f['exif']) > 0 ]

    # Process EXIF data.
    for r in DATA:
        info = r['exif']
        # precidence is DateTimeOriginal > DateTime.
        if 'DateTimeOriginal' in info.keys():
            r['ftime'] = info['DateTimeOriginal']
        elif 'DateTime' in info.keys():
            r['ftime'] = info['DateTime']
        if 'ftime' in r.keys():
            r['ftime'] = datetime.strptime(r['ftime'],'%Y:%m:%d %H:%M:%S')

    # Remove any files without datetime info.
    DATA = [ f for f in DATA if 'ftime' in f.keys() ]

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

    # Copy the files to their new locations, creating directories as requried.
    print 'Copying files.'
    for r in DATA:
        origfile = joinpath( r['path'], r['name'] + r['ext'] )
        newfile = joinpath( r['newpath'], r['newname'] + r['ext'] )
        if not exists( r['newpath'] ):
            makedirs( r['newpath'] )
        print origfile +' to '+ newfile
        # move the file.
        move( origfile, newfile )

    print 'Removing empty directories'
    DIRS = set( [ d['path'] for d in DATA ] )
    for d in DIRS:
        # if the directory is empty then delete it.
        if len( listdir( d ) ) == 0:
            print 'Deleting dir ' + d
            rmdir( d )

