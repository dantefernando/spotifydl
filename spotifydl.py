#!/bin/python3

# Dante Fernando 2021
# Download an entire Spotify playlist using YouTube mp3s

# https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script

# - pytube module downloading getting streams of youtube

# TODO High Priority
# - Add support for adding a spotify playlist and getting a list of
# songs from the playlist
#       + make it so that the user can input an https link of their playlist
# - Fix: -> Special characters when spotify playlist desc.
#        -> Convert durations from ms for songs and total playlist runtime
# - Make folders inside music/ with time and date for different sessions

# TODO Medium Priority
# - Add a settings menu to choose from different defaults
# when downloading music. E.g. default to choose to download song
# with most views instead of the first index

# TODO Low Priority
# - Exceptions for having no internet connection
# - Delete partly downloaded music


# from __future__ import unicode_literals
import datetime
import youtube_dl
import os
import spotipy
from math import floor
from youtubesearchpython import VideosSearch
from spotipy.oauth2 import SpotifyClientCredentials
from secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


class SpotifyData:

    def __init__(self, clientID, clientSecret):
        """
        Constructor; Set authentication variables for Spotipy
        and create the spotipy instance for the rest
        of the SpotifyData class to use
        """

        self.__clientID = clientID
        self.__clientSecret = clientSecret
        self.__sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.__clientID,
                                                                        client_secret=self.__clientSecret))

    def __convertMilliseconds(self, playTime):
        """
        Convert milliseconds to a human readable
        format e.g. hours:minutes for display
        """

        d = datetime.timedelta(milliseconds=playTime)

        return d

    def getPlaylist(self, playlist_id):
        """
        Returns a list of dictionaries of songs with metadata
        and information about the playlist as well
        """

        # Requires: 
        # playlistData {Title,owner,Description, num of songs, total_playtime} TODO (need to append)
        # songs : {Title,Artists,followers,Duration_ms} TODO (need to append)

        # Get all data about spotify playlist
        results = self.__sp.playlist(playlist_id=playlist_id)

        songs = []
        playTime = 0
        for index, song in enumerate(results['tracks']['items'], start=1):  # Iterate through each song's data
            data = {}
            data['index'] = index
            data['title'] = song['track']['name']
            data['duration'] = self.__convertMilliseconds(song['track']['duration_ms'])
            playTime += song['track']['duration_ms']
            data['artists'] = [artist['name'] for artist in song['track']['artists']]
            songs.append(data)

        playlistData = {}
        playlistData['name'] = results['name']
        playlistData['owner'] = results['owner']['display_name']
        playlistData['description'] = results['description']
        playlistData['numSongs'] = results['tracks']['total']
        playTimeFormatted = self.__convertMilliseconds(playTime)
        playlistData['playTime'] = playTimeFormatted


        playlist = dict(playlistData = playlistData, songs = songs)

        return playlist


# Return True if the song exists in music/ , otherwise return False
def songExists(title, files):
    if f"{title}.mp3" in files:  # File is already downloaded
        return True
    else:  # File doesn't exist / hasn't been downloaded yet
        return False


# Make the music/ directory if it doesn't already exist
def makeMusicDir():
    cwd = os.getcwd()  # Get cwd
    path = os.path.join(cwd, "music")  # Path object

    # Try and make the music/ dir assuming it doesn't exist
    try:
        os.mkdir(path)  # Make the in the working directory
        files = []
    except FileExistsError:  # music/ exists already
        files = os.listdir(path)  # list of files in music/

    return path, files


# Download song using provided link
# Kwargs: redownload=BOOL
def downloader(songData, **kwargs):

    # Sets values using kwargs to determine
    # whether or not to redownload the song:
    redownload = kwargs.get("redownload")  # Either True or False

    # Extract the YouTube video's attributes from songData
    link = songData['link']
    title = songData['title']

    path, files = makeMusicDir()  # Make the music/ dir

    # Song doesn't exist, download the song or the user wants to redownload the song
    if not songExists(title, files) or redownload == True:

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            print("\n\n")

    else:  # Song exists in the folder
        print(f"\"{title}\" has been downloaded already.")
        while True:  # Loop until valid input has been receieved
            inp = input("(Default: Skip)\n(S)kip or (R)edownload song: ").lower()

            if inp == "" or inp == "s":  # User chose to skip download
                print("Song skipped!!\n\n")
                break
            elif inp == "r":  # User chose to redownload the song
                downloader(songData, redownload=True)
                break
            else:  # Invalid input
                print("Please enter a valid input, try again...\n")


# Display the songs from the YouTube search
# results in a readable format with title,
# channel, duration and views
def displaySongs(stripped_results):
    print("\n")
    for index, song in enumerate(stripped_results):
        title = song["title"]
        channel = song["channel"]
        duration = song["duration"]
        views = song["views"]
        print(f"{index+1}. {title}")
        print(f"Channel: {channel}")
        print(f"Duration: {duration}")
        print(f"Views: {views}\n")


# Get link of song to download chosen by
# the user
def getSongData(stripped_results):
    displaySongs(stripped_results)
    print("Enter the index of a song to download.")
    print("E.g. Enter '1' for Song 1.")
    print("(Default: 1)")
    while True:
        inp = input("Index of song: ")
        try:
            if inp == "":  # Default = 1 so 0th song
                songData = stripped_results[0]
                print("\n")
                return songData
            else:
                inp = int(inp)
                numSongs = len(stripped_results)
                if inp == 0 or inp > numSongs:
                    print(f"Please enter a valid index number between 1-{len(stripped_results)}.\nTry again...\n")
                else:  # Valid
                    songData = stripped_results[inp-1]
                    print("\n")
                    return songData
        except ValueError:
            print("Please enter a valid index, must be an integer.\nTry again...\n")


# Get YouTube Search Results on YouTube
# Based off of user's search query
def getResults(song_name, search_limit):

    # Get results from YouTube
    results = VideosSearch(song_name, limit=search_limit).result()["result"]

    stripped_results = []

    # Extract only important info from videos
    for video in results:
        data = {}
        data['title'] = video['title']
        data['channel'] = video['channel']["name"]
        data['duration'] = video['duration']
        data['views'] = video['viewCount']['short']
        data['link'] = video['link']

        stripped_results.append(data)

    return stripped_results


# Get song from user and limit of videos to search on YouTube
def getUserInput():
    while True:
        song_name = input("Enter song name (YouTube): ").replace(" ", "+")

        # Validation for song name
        if len(song_name) == 0:
            print("You need to enter a song title.\nTry again...\n")
        else:  # Validation for search_limit
            print("\nEnter the number of songs to show from YouTube (Max: 20). ")
            print("E.g. Entering \'3\' will only show the first 3 songs from YouTube.")
            print("(Default: 5)")
            while True:
                search_limit = input("Number of songs to show: ")
                try:
                    if search_limit == "":
                        search_limit = 5
                        return song_name, search_limit
                    else:
                        search_limit = int(search_limit)
                        if search_limit == 0 or search_limit > 20:
                            print("Enter a search result value between 1 and 20.\nTry again...\n")
                        else:  # Valid
                            return song_name, search_limit
                except ValueError:
                    print("Please input a valid number of search results to show.\nTry again...\n")


def main():

    spotify = SpotifyData(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
    playlist_id = input("playlist id here: ")
    playlist = spotify.getPlaylist(playlist_id)

    for song in playlist['songs']:  # print names
        print(song['title'], song['duration'])
    print(playlist['playlistData']['playTime'])

    # try:
    #     while True:  # Loop to keep downloading songs
    #         song_name , search_limit = getUserInput()
    #         stripped_results = getResults(song_name, search_limit)
    #         songData = getSongData(stripped_results)
    #         downloader(songData)
    # except KeyboardInterrupt:  # User hits ctrl-c on keyboard 
    #     print("\n\nExiting program...")


if __name__ == "__main__":
    main()

