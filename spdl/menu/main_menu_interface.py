from spdl.downloaders import downloadSongs

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

        if args.auto_select:  # User used --auto-select flag
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

