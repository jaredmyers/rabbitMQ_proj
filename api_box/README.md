# SpotifyProjectBackEnd-APImachine

Moved my development work off my personal repo to Jared's so that there would be less confusion between having two repos.

<h3>Main Overview of my work so far:</h3>

1.) The "mixer" feature
  Info: This feature takes the top tracks of two users, saves them to our database locally and then synthesizes a new "combo" list locally. After this a playlist is created and added to the user's library using the "combo" file we have locally in the DB to make an API call(s).
  
    UserInfoPullerTracks.py [v 0.3 Completed]- Script that pulls a user's top tracks from spotify. Requires the user to be logged in with their spotify account to operate sucessfully. The puller currently saves the track metadata to a local csv file in the same directory. This wil be used by the "Diff" feature as well.
  
    PlaylistMerger.py [v 0.5 Completed]- Basic parser that was created to merge things. It takes two "User Info" files made by the previous script and merges them. Currently it saves the output to another local csv file titled "COMBOLIST.csv" in the same directory. It has been constructed so that we should be able to process JSON objects with it as well with minimal tweaking.
  
    SynthesizePlaylist.py [Not Yet Started]- Publishes a playlist to a user's profile, needs user to be logged in (& spotify OAuth2 to work) to complete successfully! The SynthesizePlaylist.py will be used by the "Diff" feature as well.
  
  2.) The "diff" feature
    Info: This feature takes two user's artist and top track information to produce a "diff" showing said users how their tastes are similar and where said tastes differ. Another use case for the "diff" feature is comparing a user's taste (via top tracks from different periods) between "time frames". Such a tool could be useful for demoing how one's music taste evolves over time. Right now I just want to compare artists and top tracks for the first use case but theoretically you could compare a few other interesting datapoints but alas my resources are very finite as of the moment.
    
    UserInfoPullerTracks.py [v 0.3 Completed]- See previous feature, is used to fetch top tracks of a given period.
    
    UserInfoPullerArtists.py [Not Yet Started]- Pulls a user's top artists to a local file like the previous script/function does for tracks.
    
    DiffGenerator.py [Not Yet Started] - Compares user's information and puts it into a transportable dataformat for django/html or whatever
    
    SynthesizePlaylist.py [Not Yet Started]- Publishes a playlist to a user's profile, needs user to be logged in (& spotify OAuth2 to work) to complete successfully!
