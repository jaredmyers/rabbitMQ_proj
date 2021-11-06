import os, sys, re, requests, json
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
USERNAME2="TestUser"
#AUTH_TOKEN

def main():
    token = util.prompt_for_user_token(USERNAME1, scope)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    currentUserProfileObj = sp.current_user()
    SPOTIFY_USER_ID=currentUserProfileObj["id"]
    playlistName=(USERNAME1+"&"+USERNAME2+"'s Mesh")
    nwPlaylistObj=createPlaylist(playlistName,token,SPOTIFY_USER_ID)
    print("Playlist "+nwPlaylistObj[1]+" Created")
    #call data puller function
    sampleSongIds=["4TYEIckMi7PTCh1kiknKSy","0lj4hDaua3ezKyLJ2oXFWw"]
    
    addToPlaylist(sampleSongIds,sp,nwPlaylistObj[1])


def createPlaylist(name, tokenIn,userID):
        data = json.dumps({
            "name": name,
            "description": "Test Playlist 1",
            "public": True
        })
        url = "https://api.spotify.com/v1/users/"+userID+"/playlists"
        response = place_post_api_request(url, data, tokenIn)
        response_json = response.json()
        # create playlist
        playlist_id = response_json["id"]
        playlist = [name, playlist_id]
        return playlist

def place_post_api_request(url, data,inToken):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {inToken}"
            }
        )
        return response

def pullTrackIDsFromFile(filePath):
    print("pulling track IDs from file and pushing them back as a list")


def addToPlaylist(listOfTrackIDs,spooter,playlist_id):
    spooter.playlist_add_items(playlist_id, listOfTrackIDs)
    print("adding tracks")


if __name__ == "__main__":
    main()
