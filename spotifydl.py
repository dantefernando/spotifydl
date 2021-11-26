#!/bin/python3

# Download an entire Spotify playlist using YouTube mp3s
# https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script


# pytube module downloading getting streams of youtube
# youtubesearchpython module

from __future__ import unicode_literals
import youtube_dl
import urllib.request
import re


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
        print("Link downloaded!")


# def get_song():
#     print("Enter a YouTube Link to Download: ")
#     while True:
#         try:
#             link = input("Link: ")
#             return link
#         except ValueError:
#             print("Please enter a valid URL link, try again...")


def get_song():
    name = input("enter song name: ").replace(" ", "+")
    html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={name}")
    video_ids = re.findall(r"watch\?v=(\s{11})", html.read().decode())
    print(video_ids)
    print(f"youtube.com/watch?v={video_ids[0]}")

def main():
    link = get_song()
    downloader(link)


if __name__ == "__main__":
    main()


