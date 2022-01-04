
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


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

