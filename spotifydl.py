#!/bin/python3

# Dante Fernando 2021
# Download an entire Spotify playlist using YouTube mp3s

# - pytube module downloading getting streams of youtube

# TODO High Priority
# - Add functionality to download metadata for each song?

# TODO Medium Priority
# - Fix: -> Special characters when spotify playlist desc.
# - Add a settings menu to choose from different defaults
# when downloading music. E.g. default to choose to download song
# with most views instead of the first index

# TODO Low Priority
# - Exceptions for having no internet connection
# - Delete partly downloaded music


import youtube_dl
import os
import json

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from youtubesearchpython import VideosSearch
from threading import Thread

from secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from cli import parse_arguments



class Settings:
    """
    Interact with the settings of the program
    for the user
    """

    def __init__(self):
        """
        Constructor for Settings class
        """

        self.__settings = self.__readSettings()


    def __readSettings(self):
        """
        Read settings from settings.json
        """

        # Default settings for the application
        defaultSettings = {'autoselect':'false'}

        try:  # Settings file already exists; read it

            with open("settings.json", "r") as json_file:
                settings = json.load(json_file)  # Read json from file

        except FileNotFoundError:  # Settings file doesn't exist; create it

            with open("settings.json", "w") as json_file:
                json.dump(defaultSettings, json_file)  # Write dict to to json file
            settings = defaultSettings

        return settings


    def menu(self):
        """
        Interactive menu for the user to change
        the settings of the app.
        """

        while True:

            print("\n-------Options Menu--------")
            print("1: Change Song Autoselect Settings\n"
                  "2: Exit to Main Menu\n")
            while True:  # Validates user input choice
                try:
                    inp = int(input("Your Choice: "))
                    if inp == 1:  # User wants to change autoselect settings
                        loop = True
                        while loop:
                            status = self.__settings['autoselect']  # Get current setting status from the file loaded
                            print("-" * 30)
                            print(f"Autoselect = {status} (Default: False)\n")
                            print("When Autoselect is set to *False*, the user will have to\n"
                                  "choose the correct youtube video each time before a song is downloaded.\n"
                                  "When Autoselect is set to *True*, the first youtube video will be chosen\n"
                                  "before choosing a song. This helps with saving time when downloading several songs\n"
                                  "from a playlist.\n")

                            print("\nTo change the setting, type \"True\" to change the Autoselect to True."
                                  "\nTo exit this menu, press ENTER or type \"exit\"")

                            accepted = ["true", "t", "false", "f"]
                            while True:  # Loop until valid input is entered
                                inp = input("Your choice: ").lower()

                                if inp in accepted:  # User wants to change the status
                                    if inp == status:  # Status is already changed to the desired setting
                                        break
                                    else:  # Status is different to the current status
                                        if inp == "t":
                                            inp = "true"
                                        elif inp == "f":
                                            inp = "false"

                                        self.__autoselect(inp)  # Change autoselect

                                        break

                                elif inp == "exit" or inp == "":  # User wants to exit
                                    loop = False
                                    break
                                else:
                                    print("Enter a valid input, try again...")
                        break


                    elif inp == 2:  # inp==2 | User Exits
                        print("Exiting...\n")
                        break
                    else:  # Not valid
                        print("Please enter either 1 or 2 as your choice.\n")
                except ValueError:  # User doesn't input numeric characters
                    print("Please enter numeric characters only, try again.\n")
            if inp == 2:
                break


    def __autoselect(self, status):
        """
        Change setting for autoselect
        and write to the settings.json file
        """

        if status == "true":
            self.__settings['autoselect'] = "true"  # Change status to true
        else:
            self.__settings['autoselect'] = "false"  # Change status to false

        # Write dict to to json file
        with open("settings.json", "w") as json_file:
            json.dump(self.__settings, json_file)


    def autoselectStatus(self):
        """
        Return the status of the autoselect setting
        Returns either True or False
        """

        if self.__settings['autoselect'] == "true":
            status = True
        else:
            status = False

        return status



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

        credential_manager = SpotifyClientCredentials(
            client_id=self.__clientID,
            client_secret=self.__clientSecret
        )

        self.__spotifyClient = Spotify(auth_manager=credential_manager)


    def isUserPlaylist(self, playlist):
        """
        Uses the playlist dict to display
        information about the playlist
        to the user.
        """

        # Playlist Information
        name = playlist['playlistData']['name']
        owner = playlist['playlistData']['owner']
        description = playlist['playlistData']['description']
        numSongs = playlist['playlistData']['numSongs']
        duration = playlist['playlistData']['duration']

        print(f"\nPlaylist Name: {name}\n"
              f"Owner: {owner}\n"
              f"Description: {description}\n"
              f"Num. of songs: {numSongs}\n"
              f"Playlist Duration: {duration}")

        print("\nIs this the correct playlist to download?")
        print("(Y)es or (N)o?")

        while True:
            inp = input("Your choice: ").lower()

            # User confirmed that it's the correct playlist
            if inp in ['y', 'yes', '']:
                return True

            # User confirmed that it's the incorrect playlist
            elif inp in ['n', 'no']:
                return False

            else:  # User entered invalid option
                print("Please enter a valid option, try again.")


    def __convertMilliseconds(self, milliseconds):
        """
        Convert milliseconds to a human readable
        format e.g. hours:minutes for display
        """

        milliseconds = int(milliseconds)
        seconds = (milliseconds/1000)%60
        seconds = int(seconds)
        minutes = (milliseconds/(1000*60))%60
        minutes = int(minutes)
        hours = (milliseconds/(1000*60*60))%24

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

        """

        # [[playlistData:{Title,owner,Description, num of songs, total_playtime}], [songs:{Title,Artists,followers,Duration_ms}]]

        # Get all song data about spotify playlist
        playlist_response = self.__spotifyClient.playlist_tracks(playlist_id=playlist_id, limit=100)


        # Collect data about each song and store it in the songs list
        songs = []
        duration = 0  # Total duration of the playlist
        for index, song in enumerate(playlist_response['items'], start=1):  # Iterate through each song's data
            data = {}
            data['index'] = index
            data['title'] = song['track']['name']
            data['duration'] = self.__convertMilliseconds(song['track']['duration_ms'])
            duration += song['track']['duration_ms']
            data['artists'] = [artist['name'] for artist in song['track']['artists']]
            songs.append(data)


        # Get all tracks from the playlist
        while playlist_response['next']:
            playlist_response = self.__spotifyClient.next(playlist_response)


            # Failed to get response, break the loop
            if playlist_response is None:
                break

            for index, song in enumerate(playlist_response['items'], start=int(songs[-1]['index'])):  # Iterate through each song's data
            # for index, song in enumerate(playlist_response, start=int(songs[-1]['index'])):  # Iterate through each song's data
                data = {}
                data['index'] = index
                data['title'] = song['track']['name']
                data['duration'] = self.__convertMilliseconds(song['track']['duration_ms'])
                duration += song['track']['duration_ms']
                data['artists'] = [artist['name'] for artist in song['track']['artists']]
                songs.append(data)



        results = self.__spotifyClient.playlist(playlist_id=playlist_id)

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

        Next Steps: Need to add validation for user
        """

        link = input("Enter the link of the spotify playlist you want to download: ")
        return link


def songExists(title, files):
    """
    Return True if the song exists in music/ , otherwise return False
    """

    if f"{title}.mp3" in files:  # File is already downloaded
        return True
    else:  # File doesn't exist / hasn't been downloaded yet
        return False


def makeMusicDir(spotifyData):
    """
    Make the music/ directory if it doesn't already exist
    and make a directory inside the music/ parent directory
    named after the name of the playlist.
    """

    cwd = os.getcwd()  # Get cwd
    path = os.path.join(cwd, f"music/{spotifyData['playlistData']['name']}")  # Path object

    # Try and make the music/ dir assuming it doesn't exist
    try:  # music/ dir doesn't exist
        os.makedirs(path)  # Make the dir in the working directory
        files = []
    except FileExistsError:  # music/ exists already
        files = os.listdir(path)  # list of files in music/

    return path, files


def downloader(youtubeData, spotifyData, settings, playlist, args, **kwargs):
    """
    Download song using provided link
    Kwargs: redownload=BOOL
    """

    # Sets values using kwargs to determine
    # whether or not to redownload the song:
    redownload = kwargs.get("redownload")  # Either True or False

    # Extract the YouTube video's attributes from youtubeData
    link = youtubeData['link']
    artists = ', '.join(spotifyData['artists'])
    title = f"{spotifyData['title']} - {artists}"
    title = title.replace("/", ".")

    path, files = makeMusicDir(playlist)  # Make the music/ dir and playlist dir

    # Song doesn't exist, download the song or the user wants to redownload the song
    if not songExists(title, files) or redownload == True:

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{path}/{title}.%(ext)s',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            print("\n\n")

    else:  # Song exists in the folder
        print(f"\"{title}\" has been downloaded already.")
        while True:  # Loop until valid input has been receieved
            if settings.autoselectStatus() or args.auto_select:  # Autoselect is set to true
                break
            else:
                inp = input("(Default: Skip)\n(S)kip or (R)edownload song: ").lower()

                if inp == "" or inp == "s":  # User chose to skip download
                    print("Song skipped!!\n\n")
                    break
                elif inp == "r":  # User chose to redownload the song
                    downloader(youtubeData, spotifyData, settings, playlist, args, redownload=True)
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


def getSongData(stripped_results, settings, args):
    """
    Get link of song to download chosen by the user
    """

    if settings.autoselectStatus() or args.auto_select:  # Autoselect is set to true
        return stripped_results[0]
    else:  # Auto select is disabled
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


# def getUserInput():
#     """
#     Get song from user and limit of videos to search on YouTube
#     """

#     while True:
#         song_name = input("Enter song name (YouTube): ").replace(" ", "+")

#         # Validation for song name
#         if len(song_name) == 0:
#             print("You need to enter a song title.\nTry again...\n")
#         else:  # Validation for search_limit
#             print("\nEnter the number of songs to show from YouTube (Max: 20). ")
#             print("E.g. Entering \'3\' will only show the first 3 songs from YouTube.")
#             print("(Default: 5)")
#             while True:
#                 search_limit = input("Number of songs to show: ")
#                 try:
#                     if search_limit == "":
#                         search_limit = 5
#                         return song_name, search_limit
#                     else:
#                         search_limit = int(search_limit)
#                         if search_limit == 0 or search_limit > 20:
#                             print("Enter a search result value between 1 and 20.\nTry again...\n")
#                         else:  # Valid
#                             return song_name, search_limit
#                 except ValueError:
#                     print("Please input a valid number of search results to show.\nTry again...\n")

def downloadSongs(settings, args):
    """
    Sequence of instructions to download the songs:

    1. Initializes the spotify API instance
    2. Gets the playlist link from the user
    3. Gets playlist response from API
    4. Downloads the songs from YouTube and saves to disk
    """

    print("PRESS CTRL-C TO EXIT TO MAIN MENU")

    try:
        # Initialize Spotify API
        spotify = SpotifyData(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)

        if args.playlistLink is None:  # User didn't parse a link as an argument

            # Validate that the user has entered the correct playlist
            while True:
                playlist_id = spotify.getPlaylistID()  # Get the playlist link from the user
                playlist = spotify.getPlaylist(playlist_id)  # get the playlist response from API

                # Ask user if the playlist is correct
                if spotify.isUserPlaylist(playlist) == True:
                    break

        else:  # user parsed in link as argument
            playlist_id = args.playlistLink
            playlist = spotify.getPlaylist(playlist_id)  # get the playlist response from API




        threads = []

        numSongs = len(playlist['songs'])
        numThreads = 20  # 20 concurrent threads running
        loops = numSongs // numThreads
        for i in range(0, numSongs-numThreads, numThreads):  # Iterates through each song

            for y in range(i, i+numThreads):
                song = playlist['songs'][y]  # Selects song
                songTitle = f"{song['title']} {song['artists']}"  # Formats title used to search on yt

                youtubeResults = getResults(songTitle, 5)  # Returns search results from YouTube
                songData = getSongData(youtubeResults, settings, args)  # Returns the song data from the YouTube search

                t = Thread(target=downloader, args=(songData, song, settings, playlist, args))
                threads.append(t)
                print(f"Appended thread #{y}")

            for x in range(i, i+numThreads):
                threads[x].start()
                print(f"Started thread #{x}")

            for x in range(i, i+numThreads):
                threads[x].join()

        for b in range(i+numThreads, numSongs):  # Iterates through each song

            song = playlist['songs'][b]  # Selects song
            songTitle = f"{song['title']} {song['artists']}"  # Formats title used to search on yt

            youtubeResults = getResults(songTitle, 5)  # Returns search results from YouTube
            songData = getSongData(youtubeResults, settings, args)  # Returns the song data from the YouTube search

            t = Thread(target=downloader, args=(songData, song, settings, playlist, args))
            threads.append(t)
            print(f"Appended thread #{b}")

        for x in range(i+numThreads, numSongs):
            threads[x].start()
            print(f"Started thread #{x}")

        for x in range(i+numThreads, numSongs):
            threads[x].join()

    except KeyboardInterrupt:  # User hits ctrl-c on keyboard 
        print("\n\nCancelling Downloads...")


def main_menu(settings, args):
    """
    Interactive main menu w/ options for the user

    (Program will loop inside here until the user decides to
    exit the program)
    """

    while True:
        print("\n----------Main Menu-----------")
        menu = {
            "1": [": Download playlist", downloadSongs],
            "2": [": Settings", settings.menu],
            "3": [": Quit to Desktop", quit]
        }


        # Prints each menu index and its corresponding functions description
        for key in sorted(menu.keys()):
            print(key + menu[key][0])

        if args.auto_select is not None:
            status = args.auto_select
        else:
            status = settings.autoselectStatus()

        print(f"\nMisc Settings: Autoselect={status}")

        while True:  # Loop until a valid index is received
            print("-" * 30)
            index = input("Select an index: ")
            try:  # Try to convert to an integer
                index = int(index)  # Converts to an integer
                if 1 <= index <= 3:  # In range
                    break
                else:  # Out of range
                    print("Out of range try again!")
            except ValueError:  # If it can't be converted to an integer
                print("Invalid index")
        print("-" * 30)

        if index == 1:
            menu[str(index)][1](settings, args)  # Select the menu option
        else:
            menu[str(index)][1]()  # Select the menu option


def main():
    """
    Main
    """

    settings = Settings()  # Initialize settings

    args = parse_arguments()

    if args.playlistLink is not None:  # User parsed playlist link as an arg
        downloadSongs(settings, args)

    else:  # User didn't parse any positional link arguments
        main_menu(settings, args)  # Enter the interactive main menu


if __name__ == "__main__":
    main()
