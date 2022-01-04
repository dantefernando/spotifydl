import json


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

