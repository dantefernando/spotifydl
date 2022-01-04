from spdl.settings import Settings
from spdl.parsers import parse_arguments
from spdl.downloaders import downloadSongs
from spdl.menu import main_menu

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

