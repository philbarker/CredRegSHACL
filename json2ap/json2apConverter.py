from AP import AP, PropertyStatement
from csv import DictReader
from os.path import exists
import json

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

    def read_namespaces(self, filename):
        """read the namespace prefix:url info from the csv file"""
        if type(filename) is not str:
            msg = "filename must be a string"
            raise TypeError(msg)
        if not exists(filename):
            msg = "file named %s does not exist" % filename
            raise FileNotFoundError(msg)
        self.ap.load_namespaces(filename)

    def read_json_file(self, filename):
        if type(filename) is not str:
            msg = "filename must be a string"
            raise TypeError(msg)
        if not exists(filename):
            msg = "file named %s does not exist" % filename
            raise FileNotFoundError(msg)
        with open(filename, "r") as json_file:
            json_data = json_file.read()
        self.cr_json = json.loads(json_data)
