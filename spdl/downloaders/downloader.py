from spdl.providers import SpotifyData, getResults, getSongData
from spdl.providers.secrets import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

from threading import Thread
import youtube_dl
import os


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

