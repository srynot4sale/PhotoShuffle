"""Find duplicate files inside a directory tree."""

from os import walk, remove
from os.path import join as joinpath
from md5 import md5

def find_duplicates( rootdir ):
    """Find duplicate files in directory tree."""
    unique = set()
    duplicates = [] 
    for path, dirs, files in walk( rootdir ):
        for filename in files:
            filepath = joinpath( path, filename )
            filehash = md5( file( filepath ).read() ).hexdigest()
            if filehash not in unique:
                unique.add( filehash )
            else:
                duplicates.append( filepath )
    return duplicates

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    PARSER = ArgumentParser( description='Finds duplicate files.' )
    PARSER.add_argument( 'root', metavar='R', help='Dir to search.' )
    PARSER.add_argument( '-remove', action='store_true', 
                         help='Delete duplicate files.' )
    ARGS = PARSER.parse_args()

    DUPS = find_duplicates( ARGS.root )

    print '%d Duplicate files found.' % len(DUPS)
    for f in sorted(DUPS):
        if ARGS.remove == True:
            remove( f )
            print '\tDeleted '+ f
        else:
            print '\t'+ f
