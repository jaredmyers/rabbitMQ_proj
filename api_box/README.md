# SpotifyProjectBackEnd-APImachine

Moved my development work off my personal repo to Jared's so that there would be less confusion between having two repos.
There shouldn't be any API secrets in there (I've declared them as environment variables on my local machine, put yours in their places)
TASK: Played around with the spotify API using some demo code and making it my own. Broke some stuff.
TASK: Used the credential manager to get non-user information
TASK: Spotify OAuth Authentication for local machine using localhost address.
TASK: Made script that makes an API call for user's top tracks within a specified time frame (short, medium, long) and saves the data locally to a file. Right now it just creates a CSV but I think I'll change it to JSON once everything is working ay okay.
TASK: Created a data type agnostic (JSON friendly) list merger (see MergePlaylists.py) A sample file "COMBOLIST.csv" shows the output of it. Ideally this output will be piped to the forthcoming "Synthesize" script which is planned to create a playlist in the user's library via the API. The SYNTHESIZE and Merge scripts are separate because the SYNTHESIZE script will be used to process the "diff functionality" in subsequent commits.
NOTE: This is just a (working) proof of concept. Yes the code is messy but I'll be sure to give it a brush up once I have all my API stuff working flawlessly on it's own independent basis.
NOTE: Django implementation is also forthcoming tbh I'm not 100% how I'm gonna handle it right now. More research required.

