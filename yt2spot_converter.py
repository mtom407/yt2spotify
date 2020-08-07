import os
import json
import re
import requests
from secrets import user_id, oauth_token

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class PlaylistCreator:

    def __init__(self, youtube_link):

        if youtube_link:
            self.youtube_link = youtube_link
        else:
            self.youtube_link = None
        

    @staticmethod
    def print_menu():

        print("==================================")
        print("======= YouTube to Spotify =======")
        print("==================================")
        print()
        print(" ==> Options:")
        print("     Press [1] if you want to copy the link (make sure the tracklist is in the description)")
        print("     Press [2] if you want to copy the tracklist (make sure timestamps are included)")
        choice = input("Input your choice here: ")

        if choice not in ['1', '2']:
            print("Unknown option...")
            return -1
        else:
            return choice

    def get_youtube_compilation_songs(self):

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = [f for f in os.listdir('.') if 'client_secret' in f][0]
        my_api_key = " "

    
        bypassAuth = False
        if bypassAuth:
            # Don't bother getting credentials through web browser (development purposes)
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            youtube = googleapiclient.discovery.build( api_service_name, api_version, developerKey=my_api_key)
        else:
            # Get credentials and create an API client
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_console()
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)


        # Get YT video playlist URL from the user and extract id parameter
        if "&t" in self.youtube_link:
            video_id = self.youtube_link.split("=")[1].strip("&t")
        else:
            video_id = self.youtube_link.split("=")[1] 

        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )

        response = request.execute()

        return response

    def load_tracklist(self):
        
        tracklist = ""
        with open("tracklist.txt", "r") as fp: 
            for fp_line in fp:
                tracklist += fp_line

        return tracklist

    def extract_tracks(self, response):

        # check whether the user provided a youtube link or tracklist in a txt file
        if isinstance(response, dict):
            video_title = response["items"][0]["snippet"]["title"]
            video_description = response["items"][0]["snippet"]["localized"]["description"]
        elif isinstance(response, str):
            video_description = response
            video_title = input("Add a title to your playlist: ")
        else:
            print("What did you do?")
            return -1

        # try to extract artists and song names and put them in a list
        artists_and_tracks = []
        for line in video_description.split('\n'):
            if "-" in line and ':' in line and bool(re.search(r'\d', line)):
                songname_and_artist = line.split(':')[-1][3:]
                artists_and_tracks.append(songname_and_artist)

        return (video_title, artists_and_tracks)

    def create_spotify_playlist(self, playlist_title):

        if self.youtube_link:
            description = "Created from: " + self.youtube_link
        else:
            description = "Created from user supplied tracklist"
        
        request_body = json.dumps({
            "name":playlist_title,
            "description":description,
            "public":False
        })

        query = f"https://api.spotify.com/v1/users/{user_id}/playlists"

        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type":"application/json",
                "Authorization":f"Bearer {oauth_token}"
            }
        )

        response_json = response.json()

        return response_json["id"]

    def get_spotify_uri(self, search_string):
        
        query = f"https://api.spotify.com/v1/search?q={search_string}&type=track%2Cartist"

        response = requests.get(
            query,
            headers = {
                "Content-Type":"application/json",
                "Authorization":f"Bearer {oauth_token}"
            }
        )

        response_json = response.json()

        # list of results
        songs = response_json["tracks"]["items"]
        # first song on the list
        if songs:
            uri = songs[0]["uri"]
        else:
            uri = "unknown"

        return uri

    def add_songs_to_playlist(self):
        
        
        if self.youtube_link:
            response = self.get_youtube_compilation_songs()
        else:
            response = self.load_tracklist()
        
        title, tracks = self.extract_tracks(response)

        # collect all of uri
        uris = []
        for element in tracks:
            uri = self.get_spotify_uri(search_string=element)
            
            if uri != "unknown":
                uris.append(self.get_spotify_uri(search_string=element))
                print("Track {} : FOUND".format(element))
            else:
                print("Track {} : NOT FOUND".format(element))
                

        # create a new playlist
        playlist_id = self.create_spotify_playlist(playlist_title=title)

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(   
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(oauth_token)
            }
        )

        response_json = response.json()
        return response_json

if __name__ == "__main__":
    
    user_choice = PlaylistCreator.print_menu()

    if int(user_choice) == -1:
        print("Closing...")
    elif user_choice == '1':
        youtube_playlist = input("Copy the YouTube link here and press 'Enter': ")

        new_playlist = PlaylistCreator(youtube_playlist)
        new_playlist.add_songs_to_playlist()
    else:

        input("Copy the tracklist into 'tracklist.txt' file and press 'Enter': ")
    
        new_playlist = PlaylistCreator("")
        new_playlist.add_songs_to_playlist()


