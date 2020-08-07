# yt2spotify
A script to turn a YouTube music compilation video into a Spotify playlist 

HUGELY INSPIRED BY (a chonky chunk of code has been taken from this video/repository, go show some support):

 https://www.youtube.com/watch?v=7J_qcttfnJA
 https://github.com/TheComeUpCode/SpotifyGeneratePlaylist

Step 1: Obtain YouTube API credentials from https://developers.google.com/youtube/registering_an_application

Step 2: Fill required information in secrets.py file - your Spotify user id (username) can be grabbed from your Spotify Account Overiew.
        Grab the oauth_token from [here](https://developer.spotify.com/console/delete-playlist-tracks/?playlist_id=&body=%7B%22tracks%22%3A%5B%7B%22uri%22%3A%22spotify%3Atrack%3A2DB2zVP1LVu6jjyrvqD44z%22%2C%22positions%22%3A%5B0%5D%7D%2C%7B%22uri%22%3A%22spotify%3Atrack%3A5ejwTEOCsaDEjvhZTcU6lg%22%2C%22positions%22%3A%5B1%5D%7D%5D%7D)

Step 3: Run yt2spot_converter.py

REMEMBER - not every song can be found on Spotify, if you see that some songs are missing that is probably why.
