from argparse import ArgumentParser


HELP_NOTICE = """CLI tool that downloads an entire
        Spotify playlist using YouTube and stores them locally as mp3 files.
        You can use this tool interactively with a menu or just call the command
        and provide it with the link of a playlist as a positional argument."""


def parse_arguments():
    """
    Initialize argument parser and
    return arguments called with the program
    """

    parser = ArgumentParser(
        prog="spotifydl",
        description=HELP_NOTICE
    )


    parser.add_argument(
        "playlistLink",
        nargs='?',
        default=None,
        type=str,
        help="URL for the spotify playlist you wish to download"
    )


    parser.add_argument(
        "-a", "--auto-select",
        action="store_true",
        default=False,
        help="Auto select and download the first song from the YouTube results."
    )


    return parser.parse_args()

