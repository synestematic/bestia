### generic exceptions ###################
class MissingBinary(Exception):
    pass

### output module exceptions #############
class InvalidColor(Exception):
    pass

class InvalidFx(Exception):
    pass

class UndefinedAnsiSequence(Exception):
    pass

class UndefinedAlignment(Exception):
    pass

### connect module exceptions ############
class CUrlFail(Exception):
    pass
