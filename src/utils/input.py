
class Input:
    """Gets command line input with prompts and input validation."""

    def getBool(prompt):
        """
            Prompts the user for a Y/n boolean value with validation.
        """

        response = input(f"{prompt} y/n: ")
        if(response == "y"): return True
        if(response == "n"): return False

        print("Must enter Y/n value.")
        return Input.getBool(prompt)
    
    def getString(prompt):
        return input(prompt)
    
    def getChoice(prompt, options):
        optionsText = " / ".join([
            f"({option[0]}){option[1:]}"
            for option in options
        ])
        response = input(f"{prompt} {optionsText}: ")
        for option in options:
            if(response == option[0]):
                return option

        return Input.getChoice(prompt, options)

    def getInt(prompt):
        """
            Prompts the user for an integer value with validation.
        """

        response = input(f"{prompt} int: ")
        ret = int(response) if response.isdecimal() else None

        if(ret != None): return ret

        print("Must enter integer value.")
        return Input.getInt(prompt)
    