from AP import AP, PropertyStatement, ShapeInfo
from csv import DictReader
from os.path import exists
from urllib.parse import quote
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
        """read the namespace prefix:url info from a csv file"""
        if type(filename) is not str:
            msg = "filename must be a string"
            raise TypeError(msg)
        if not exists(filename):
            msg = "file named %s does not exist" % filename
            raise FileNotFoundError(msg)
        self.ap.load_namespaces(filename)

    def read_json_file(self, filename):
        """read a JSON file and use it to populate cr_json dict"""
        if type(filename) is not str:
            msg = "filename must be a string"
            raise TypeError(msg)
        if not exists(filename):
            msg = "file named %s does not exist" % filename
            raise FileNotFoundError(msg)
        with open(filename, "r") as json_file:
            json_data = json_file.read()
        self.cr_json = json.loads(json_data)

    def convert_class(self, class_data, level="required"):
        levels = {
            "required": "constraintType:RequiresProperty",
            "recommended": "constraintType:RecommendsProperty",
            "optional": "constraintType:OptionalProperty",
        }
        if level not in levels.keys():
            print(level)
            msg = "Importance level must be one of required, recommended, or optional."
            raise ValueError(msg)
        # first the populate the metadata
        title = class_data["Label"] + " (" + level + ")"
        description = "%s properties for %s" % (
            level.capitalize(),
            class_data["Definition"],
        )
        print(description)
        self.ap.add_metadata("dct:title", title)
        self.ap.add_metadata("dct:description", description)
        # add top shape for main class
        shape_id = quote(class_data["Label"].title().replace(" ", "") + "Shape")
        shapeInfo = ShapeInfo()
        shapeInfo.set_id(shape_id)
        shapeInfo.add_label("en", class_data["Label"])
        shapeInfo.add_comment("en", "Shape for " + class_data["Definition"].lower())
        shapeInfo.append_target(class_data["URI"], "class")
        shapeInfo.set_closed("false")
        shapeInfo.set_mandatory("true")
        shapeInfo.set_severity("violation")
        self.ap.add_shapeInfo(shape_id, shapeInfo)
        # add properties for main shape
        for p in class_data["PropertySets"]:
            if p["ImportanceLevel"] == levels[level]:
                ps = PropertyStatement
                ps.add_shape(shape_id)
                ps.add_label("en", p["label"])
                ps.add_severity("violation")
