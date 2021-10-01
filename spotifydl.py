#!/bin/python3

# Download an entire Spotify playlist using YouTube mp3s
# https://stackoverflow.com/questions/27473526/download-only-audio-from-youtube-video-using-youtube-dl-in-python-script

from __future__ import unicode_literals
import youtube_dl


def downloader():
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['https://youtu.be/CiyamJhSbBg'])

def get_song():
    print("Enter a YouTube Link to Download.")
    while True:
        try:
            song = input("Link: ")
        except ValueError:
            print("Enter a ")


def main():
    print("Hello World")

if __name__ == "__main__":
    main()
