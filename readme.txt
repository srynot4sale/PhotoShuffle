This script will programmatically reorganise photographs from an ad-hoc mess to something structured: using the EXIF information from each file and use the creation time of each image as key to organise each image into the directory structure Year/Month/Day.  If an image file is missing EXIF data then the file’s creation time can be used instead via an option.

An example of running this script to reoranise the photos folder and leave the original files in place would be:
    python PhotoShuffle.py -copy /Users/Daniel/Pictures /Users/Daniel/OrganisedPictures

An example of running this script to reoranise the photos folder would be:
    python PhotoShuffle.py /Users/Daniel/Pictures /Users/Daniel/OrganisedPictures

The ExifScan.py script can also be ran directly to scan and harvest EXIF data from image files in a directory tree and write a CSV formatted report for analysis.  For example to find the creation time for all files in the photos folder, run the following:
    python ExifScan.py DateTimeOriginal DateTime

To find only the files without the DateTimeOriginal tag run the following:
    python ExifScan.py -nodata DateTimeOriginal

