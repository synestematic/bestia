################################
### output module exceptions ###
################################

class InvalidAnsi(Exception):
    pass

class InvalidSgr(InvalidAnsi):
    pass

class InvalidColor(InvalidSgr):
    pass

class InvalidFx(InvalidSgr):
    pass

class InvalidMode(Exception):
    pass

class InvalidAlignment(Exception):
    pass


##############################
### proc module exceptions ###
##############################

class InvalidCommand(Exception):
    pass
