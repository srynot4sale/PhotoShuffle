"""Scans a folder and builds a date sorted tree based on image creation time."""

if __name__ == '__main__':
    from os import makedirs, listdir, rmdir
    from os.path import join as joinpath, exists, getmtime
    from datetime import datetime
    from shutil import move, copy2 as copy
    from ExifScan import scan_exif_data
    from argparse import ArgumentParser
    import hashlib

    PARSER = ArgumentParser(description='Builds a date sorted tree of images.')
    PARSER.add_argument( 'orig', metavar='O', help='Source root directory.')
    PARSER.add_argument( 'dest', metavar='D',
                         help='Destination root directory' )
    PARSER.add_argument( '-filetime', action='store_true',
                         help='Use file time if missing EXIF' )
    PARSER.add_argument( '-copy', action='store_true',
                         help='Copy files instead of moving.' )
    ARGS = PARSER.parse_args()

    config_newpath = '%Y/%m'
    config_keepname = True

    print 'Gathering & processing EXIF data.'

    # Get creation time from EXIF data.
    DATA = scan_exif_data( ARGS.orig )

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
        elif ARGS.filetime == True:
            ctime = getmtime( joinpath( r['path'], r['name'] + r['ext'] ))
            r['ftime'] = datetime.fromtimestamp( ctime )
        else:
            print 'No EXIF data available for %s' % (joinpath( r['path'], r['name'] + r['ext'] ))

    # Remove any files without datetime info.
    DATA = [ f for f in DATA if 'ftime' in f.keys() ]

    # Generate new path YYYY/MM/DD/ using EXIF date.
    for r in DATA:
        r['newpath'] = joinpath( ARGS.dest, r['ftime'].strftime(config_newpath) )

    # Generate filenames per directory: 1 to n+1 (zero padded) with DDMMMYY.
    print 'Generating filenames.'
    for newdir in set( [ i['newpath'] for i in DATA ] ):
        files = [ r for r in DATA if r['newpath'] == newdir ]
        pad = len( str( len(files) ) )
        usednames = []
        for i in range( len(files) ):
            datestr = files[i]['ftime'].strftime('%d%b%Y')

            if config_keepname:
                newname = files[i]['name']
                j = 0
            else:
                newname = '%0*d_%s' % (pad, i+1, datestr)
                j = i + 1

            # if filename exists keep looking until it doesn't. Ugly!
            while ( exists( joinpath( newdir, newname + files[i]['ext'] ) ) or
                newname in usednames ):
                # Check if these are the same image
                hash_old = hashlib.md5(file(joinpath( newdir, newname + files[i]['ext'] ), 'rb').read())
                hash_new = hashlib.md5(file(joinpath( files[i]['path'], files[i]['name'] + files[i]['ext'] ), 'rb').read())
                if hash_old.hexdigest() == hash_new.hexdigest():
                    break

                j += 1

                if config_keepname:
                    newname = '%s_%d' % (newname, j)
                else:
                    jpad = max( pad, len( str( j ) ) )
                    newname = '%0*d_%s' % (jpad, j, datestr)

            usednames.append( newname )
            files[i]['newname'] = newname

    # Copy the files to their new locations, creating directories as requried.
    print 'Copying files.'
    for r in DATA:
        origfile = joinpath( r['path'], r['name'] + r['ext'] )
        newfile = joinpath( r['newpath'], r['newname'] + r['ext'] )
        if not exists( r['newpath'] ):
            makedirs( r['newpath'] )
        if not exists( newfile ):
            if ARGS.copy:
                print 'Copying '+ origfile +' to '+ newfile
                copy( origfile, newfile )
            else:
                print 'Moving '+ origfile +' to '+ newfile
                move( origfile, newfile )
        else:
            print newfile +' already exists!'

    if ARGS.copy:
        print 'Removing empty directories'
        DIRS = set( [ d['path'] for d in DATA ] )
        for d in DIRS:
            # if the directory is empty then delete it.
            if len( listdir( d ) ) == 0:
                print 'Deleting dir ' + d
                rmdir( d )

