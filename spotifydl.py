#!/bin/python3

# Download an entire Spotify playlist using YouTube mp3s
# https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script


# pytube module downloading getting streams of youtube

from __future__ import unicode_literals
from youtubesearchpython import VideosSearch
import youtube_dl
import urllib.request
import re


# Download song using provided link
def downloader(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


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
    while True:
        try:
            inp = int(input("Index of song: "))
            numSongs = len(stripped_results)
            if inp == 0 or inp > numSongs:
                print("Please enter a valid index number.\nTry again...")
            else:
                songData = stripped_results[inp-1]
                return songData
        except ValueError:
            print("Please enter a valid index, must be a number.\nTry again...")


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
            print("You need to enter a song title.\n Try again...")
        else:  # Validation for search_limit
            print("Enter the number of songs to show from YouTube: ")
            print("E.g. '5' will show only the first 5 songs from YouTube.")
            while True:
                try:
                    search_limit = int(input("Number of songs to show: "))
                    if search_limit == 0 or search_limit > 20: print("Enter a search result value between 1 and 20.\nTry again...")
                    else:  # Valid
                        return song_name, search_limit
                except ValueError:
                    print("Please input a valid number of search results to show.\nTry again...")


def main():
    song_name , search_limit = getUserInput()
    stripped_results = getResults(song_name, search_limit)
    songData = getSongData(stripped_results)
    print(songData)
    link = songData['link']
    downloader(link)


if __name__ == "__main__":
    main()


