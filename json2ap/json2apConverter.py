from AP import AP, PropertyStatement
from csv import DictReader

class JSON2APConverter:
    """Class comprising Credential Engine JSON code and python AP, with methods to read the former and convert it into the latter."""
    def __init__(self):
        self.ap = AP()
        self.cr_json = dict()
        # need to hard-code some info not in JSON AP data
        self.dont_repeat = [
            "ceterms:ctid",
            "ceterms:name",
            "ceterms:description",
            "ceterms:subjectWebpage",
        ]
