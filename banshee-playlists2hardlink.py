#!/usr/bin/python
# Export playlists from the banshee database to folder/files tree
# files are not duplicated but hardlinks so it don't take more storage place
# run this script as cron command to automaticly update teh trees
# i did it to be able to sync files from playlists between devices with syncthing

print("Exporting banshee playlists")

import os
from urllib.parse import unquote
import sqlite3
import argparse
import shutil

# Variables
playlistsOut = []

# Parse arguments
parser = argparse.ArgumentParser(description='Extract playlists from the banshee music database')
parser.add_argument('-l','--list-playlists', action="store_true", default=False,
                    help='List playlists and exit')
parser.add_argument('-u','--user-playlists', action="store_true", default=False,
                    help='Extract user playlists (default)')
parser.add_argument('-s','--smart-playlists', action="store_true", default=False,
                    help='Extract smart playlists')
parser.add_argument('-r','--remove-old', action="store_true", default=False,
                    help='Remove existing *.m3u files in --output-dir')
parser.add_argument('-p','--playlists', action="store", default="",
                    help='Specify which playlists to export by name. Delimit using "|"')
parser.add_argument('-o','--output-dir', action="store",
                    default=os.path.join(os.path.expanduser('~'), '.config/banshee-1/export-playlist'),
                    help='Specify where to put the playlist files')
parser.add_argument('-d','--database', action="store",
                    default=os.path.join(os.path.expanduser('~'), '.config/banshee-1/banshee.db'),
                    help='Specify where the database is')
args = parser.parse_args()

# Format paths
args.output_dir = os.path.realpath(args.output_dir)
# create playlist dir if not existing
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir);

args.database = os.path.realpath(args.database)

# Connect to the banshee database
connection = sqlite3.connect(args.database)
c = connection.cursor()

# Gather CorePlaylist names if required
if args.user_playlists == True or args.smart_playlists == False:
    playlistsSQL = 'Select Name from CorePlaylists Where PrimarySourceID = 1'
    for x in c.execute(playlistsSQL):
        playlistsOut.append([x, 'Playlist'])

# Gather CoreSmartPlaylist names if required
if args.smart_playlists == True or args.user_playlists == False:
    smartplaylistsSQL = 'Select Name from CoreSmartPlaylists Where PrimarySourceID = 1'
    for x in c.execute(smartplaylistsSQL):
        playlistsOut.append([x, 'SmartPlaylist'])

# Remove playlists not present in args.playlists if args.playlists != ""
if args.playlists != "":
    playlistsIn = args.playlists.split("|")
    i = 0
    n = len(playlistsOut)
    while i < n:
        if playlistsOut[i][0][0] not in playlistsIn:
            playlistsOut.pop(i)
            n -= 1
        else:
            i += 1

# List playlists and exit if required
if args.list_playlists == True:
    for x in playlistsOut:
        print(x[0][0])
    exit()

# Remove old playlists if required
flatPlaylists = []
for x in playlistsOut:
    flatPlaylists.append(x[0][0])

if args.remove_old:
    for x in sorted(os.listdir(args.output_dir)):
        print(os.path.isdir(os.path.join(args.output_dir,x)))
        if os.path.isdir(os.path.join(args.output_dir,x)) == True and x not in flatPlaylists:
            print('Removing "' + x + '"...')
            shutil.rmtree(os.path.join(args.output_dir,x))

# Loop through CorePlaylists
for x in sorted(playlistsOut):
    playlistName = x[0][0]
    playlistType = x[1]
    playlistInfoSQL = 'Select round(t.Duration/1000.0,0), a.Name, t.Title, t.Uri '+\
                      'From Core'+ playlistType +'s p, Core'+ playlistType +'Entries e, '+\
                           'CoreTracks t, CoreArtists a '+\
                      'Where p.'+ playlistType +'ID = e.'+ playlistType +'ID and '+\
                            'e.TrackID = t.TrackID and '+\
                            't.ArtistID = a.ArtistID and '+\
                            't.PrimarySourceID = 1 and '+\
                            'p.Name = "' + playlistName +\
                      '" Group By p.Name, a.Name, t.Title, t.Uri'

    print('Exporting ' + playlistName),

    playlistOutputDir = os.path.join(args.output_dir,playlistName)

    # create playlist dir if not existing
    if not os.path.exists(playlistOutputDir):
        os.makedirs(playlistOutputDir);

    # Loop through CorePlaylistEntries for the current CorePlaylist
    flatFilesOut = []
    for y in c.execute(playlistInfoSQL):
        srcPath = unquote(y[3][7:])
        srcPath = os.path.realpath(srcPath)
        filename = os.path.basename(srcPath)
        destPath = os.path.join(playlistOutputDir, filename)

        #record file list for later purge
        flatFilesOut.append(filename)

        # if hard link do not alredy exists create it
        if not os.path.exists(destPath):
          os.link(srcPath, destPath)

    # Remove old files from playlist if required
    if args.remove_old:
        for x in sorted(os.listdir(playlistOutputDir)):
            if x not in flatFilesOut:
                os.remove(os.path.join(playlistOutputDir, x))


print('Done')