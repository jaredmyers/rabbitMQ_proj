import os, sys, re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util

#TODO this should publish playlists to a user's account
scope = "user-library-read,user-top-read,playlist-modify-public"

#Step 1: Create playlist
#Step 2: Read source file for playlist content
#Step 3: Iteratively loop through each object in the source file and add the associated songs to the playlist published in step 1

PULL_FILE_PATH="/comboLists/"
USERNAME1="wizzywizzard"
USERNAME2="Test"


def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def createPlaylist():
    print("creating playlist")
    return("playlist_ID")

def pullTrackIDsFromFile(filePath):
    print("pulling track IDs from file and pushing them back as a list")


def addToPlaylist(listOfTrackIDs):
    print("adding tracks")


if __name__ == "__main__":
    main()