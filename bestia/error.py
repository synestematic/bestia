################################
### output module exceptions ###
################################

class InvalidAnsiSequence(Exception):
    pass

class InvalidColor(InvalidAnsiSequence):
    pass

class InvalidFx(InvalidAnsiSequence):
    pass

class InvalidMode(Exception):
    pass

class InvalidAlignment(Exception):
    pass
