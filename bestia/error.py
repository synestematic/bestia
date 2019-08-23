### generic exceptions ###################
class MissingBinary(Exception):
    pass

### output module exceptions #############
class InvalidColor(Exception):
    pass

class InvalidFx(Exception):
    pass

class InvalidMode(Exception):
    pass

class InvalidAnsiSequence(Exception):
    pass

class InvalidAlignment(Exception):
    pass

### connect module exceptions ############
class CurlFail(Exception):
    pass
