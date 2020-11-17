################################
### output module exceptions ###
################################

class InvalidSgr(Exception):
    pass

class InvalidColor(InvalidSgr):
    pass

class InvalidFx(InvalidSgr):
    pass

class InvalidMode(Exception):
    pass

class InvalidAlignment(Exception):
    pass
