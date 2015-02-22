# Export your banshee playlists into folder/files tree

This python script is my attempt to get exported my banshee playlist into a folder/files tree    
Files are not duplicated but hard linked instead.

## install it
just colne thiss repo
```git clone https://github.com/bachy/banshee-playlists2hardlinks.git```

## run it
you can run it ponctualy with the command ```./banshee-plalists2hardlink.py```

or you can setup a cron job to run it automaticly


## options
you can run ```./banshee-plalists2hardlink.py -h``` to read all aptional arguments   

  -h, --help show this help message and exit    
  -l, --list-playlists  List playlists and exit   
  -a, --absolute        Use absolute paths (relative by default)    
  -u, --user-playlists  Extract user playlists (default)     
  -s, --smart-playlists  Extract smart playlists     
  -r, --remove-old  Remove existing *.m3u files in --output-dir
  -p PLAYLISTS, --playlists PLAYLISTS Specify which playlists to export by name. Delimit using "|"
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR Specify where to put the playlist files
  -d DATABASE, --database DATABASE Specify where the database is


## thanks
thanks to (jarretgilliam)[https://github.com/jarrettgilliam] for his (banshee-playlists)[https://github.com/jarrettgilliam/banshee-playlists] script.




