#!/bin/python3

# Dante Fernando 2021
# Download an entire Spotify playlist using YouTube mp3s

# https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script

# - pytube module downloading getting streams of youtube

# TODO High Priority
# - Add support for adding a spotify playlist and getting a list of
# songs from the playlist
# - Fix: -> only 100 results being returned when requesting playlist data
# - Fix: -> Special characters when spotify playlist desc.
# - Make folders inside music/ with time and date for different sessions

# TODO Medium Priority
# - Add a settings menu to choose from different defaults
# when downloading music. E.g. default to choose to download song
# with most views instead of the first index

# TODO Low Priority
# - Exceptions for having no internet connection
# - Delete partly downloaded music


# from __future__ import unicode_literals
# import datetime
import youtube_dl
import os
import spotipy
from youtubesearchpython import VideosSearch
from spotipy.oauth2 import SpotifyClientCredentials
from secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


class SpotifyData:
    """
    Return data from spotify using various methods
    """

    def __init__(self, clientID, clientSecret):
        """
        Constructor: Set authentication variables for Spotipy
        and create the spotipy instance for the rest
        of the SpotifyData class to use
        """

        self.__clientID = clientID
        self.__clientSecret = clientSecret
        self.__sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.__clientID,
                                                                        client_secret=self.__clientSecret))

    def __convertMilliseconds(self, milliseconds):
        """
        Convert milliseconds to a human readable
        format e.g. hours:minutes for display
        """

        milliseconds = int(milliseconds)
        seconds=(milliseconds/1000)%60
        seconds = int(seconds)
        minutes=(milliseconds/(1000*60))%60
        minutes = int(minutes)
        hours=(milliseconds/(1000*60*60))%24

        if len(str(seconds)) == 1:
            seconds = f"0{seconds}"

        if int(hours) > 0:
            durationFormatted = f"{int(hours)}:{int(minutes)}:{seconds}"
        else:
            durationFormatted = f"{int(minutes)}:{seconds}"

        return durationFormatted


    def getPlaylist(self, playlist_id):
        """
        Returns a list of dictionaries of songs with metadata
        and information about the playlist as well

        Bugs: a limit of only 100 songs from playlist are returned.
        """

        # Requires: 
        # playlistData {Title,owner,Description, num of songs, total_playtime} TODO (need to append)
        # songs : {Title,Artists,followers,Duration_ms} TODO (need to append)

        # Get all song data about spotify playlist
        results = self.__sp.playlist_tracks(playlist_id=playlist_id, limit=100)


        # Collect data about each song and store it in the songs list
        songs = []
        duration = 0  # Total duration of the playlist
        for index, song in enumerate(results['items'], start=1):  # Iterate through each song's data
            data = {}
            data['index'] = index
            data['title'] = song['track']['name']
            data['duration'] = self.__convertMilliseconds(song['track']['duration_ms'])
            duration += song['track']['duration_ms']
            data['artists'] = [artist['name'] for artist in song['track']['artists']]
            songs.append(data)

        results = self.__sp.playlist(playlist_id=playlist_id)

        # Collect data about the playlist and store it in the playlistData dict
        playlistData = {}
        playlistData['name'] = results['name']
        playlistData['owner'] = results['owner']['display_name']
        playlistData['description'] = results['description']
        playlistData['numSongs'] = results['tracks']['total']
        durationFormatted = self.__convertMilliseconds(duration)
        playlistData['duration'] = durationFormatted

        playlist = dict(playlistData = playlistData, songs = songs)
        return playlist


    def getPlaylistID(self):
        """
        Asks the user to enter a https link of the
        spotify playlist and the method will return
        the spotify playlist ID required to use with
        other methods involving fetching data of a playlist.
        """

        # https://open.spotify.com/playlist/6TqSxxmrNlrGQblCLlDj9S?si=94523af82e99433f
        link = input("Enter the link of the spotify playlist you want to download: ").split("/")

        playlistID = ""
        for letter in link[4]:
            if letter != "?":
                playlistID += letter
            else:
                break

        return playlistID


def songExists(title, files):
    """
    Return True if the song exists in music/ , otherwise return False
    """

    if f"{title}.mp3" in files:  # File is already downloaded
        return True
    else:  # File doesn't exist / hasn't been downloaded yet
        return False


def makeMusicDir():
    """
    Make the music/ directory if it doesn't already exist
    """

    cwd = os.getcwd()  # Get cwd
    path = os.path.join(cwd, "music")  # Path object

    # Try and make the music/ dir assuming it doesn't exist
    try:
        os.mkdir(path)  # Make the in the working directory
        files = []
    except FileExistsError:  # music/ exists already
        files = os.listdir(path)  # list of files in music/

    return path, files


def downloader(songData, **kwargs):
    """
    Download song using provided link
    Kwargs: redownload=BOOL
    """

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


def displaySongs(stripped_results):
    """
    Display the songs from the YouTube search
    results in a readable format with title,
    channel, duration and views
    """

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


def getSongData(stripped_results):
    """
    Get link of song to download chosen by the user
    """

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


def getResults(song_name, search_limit):
    """
    Get YouTube Search Results on YouTube
    Based off of user's search query
    """

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


def getUserInput():
    """
    Get song from user and limit of videos to search on YouTube
    """

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
    """
    Main (WIP)
    """

    spotify = SpotifyData(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
    playlist_id = spotify.getPlaylistID()
    playlist = spotify.getPlaylist(playlist_id)

    for song in playlist['songs']:  # print names
        print(song['title'], song['duration'])
    print(playlist['playlistData']['duration'])

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

