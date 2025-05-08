

class ProgramException(Exception):
    """
    This kind of error will be intercepted by Program and print only the message. The stack trace will not be printed.
    """

    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return self.message