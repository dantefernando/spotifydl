from youtubesearchpython import VideosSearch


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

