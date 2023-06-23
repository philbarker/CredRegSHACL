from AP import AP, PropertyStatement, ShapeInfo
from csv import DictReader
from os.path import exists
from urllib.parse import quote
import json

# map importance levels to terms in json data
levels = {
    "required": "constraintType:RequiresProperty",
    "recommended": "constraintType:RecommendsProperty",
    "optional": "constraintType:OptionalProperty",
}

# used to decide how to create property constraints
literals = [
    "xsd:data",
    "xsd:string",
    "rdf:langString",
    "xsd:boolean",
    "xsd:integer",
    "xsd:language",
    "xsd:float",
    "xsd:decimal",
    "xsd:dateTime",
    "xsd:date",
]


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

    def build_ap(self, class_data, level="required"):
        """Build an AP based on data about a class and its property sets."""
        if type(class_data) is not dict:
            print(class_data)
            raise TypeError("class data must be a dict.")
        elif type(level) is not str:
            print(level)
            raise TypeError("level must be a string.")
        self.convert_metadata(class_data, level)
        self.convert_shape(class_data, level)

    def convert_metadata(self, class_data, level):
        """Convert metadata about the AP from the data for the first class."""
        if level not in levels.keys():
            print(level)
            msg = "Importance level must be one of required, recommended, or optional."
            raise ValueError(msg)
        title = class_data["Label"] + " (" + level + ")"
        description = "%s properties for %s" % (
            level.capitalize(),
            class_data["Definition"],
        )
        self.ap.add_metadata("dct:title", title)
        self.ap.add_metadata("dct:description", description)
        self.ap.add_metadata("level", level)

    def convert_shape(self, class_data, level, objectOf=None):
        """Convert class data from JSON into AP ShapeInfo."""
        if level not in levels.keys():
            print(level)
            msg = "Importance level must be one of required, recommended, or optional."
            raise ValueError(msg)
        if objectOf is None:
            shape_id = quote(class_data["Label"].title().replace(" ", "") + "Shape")
            target = (class_data["URI"], "class")
        else:
            property_name = objectOf.split(":")[1]
            shape_id = quote(
                property_name.title()
                + class_data["Label"].title().replace(" ", "")
                + "Shape"
            )
            target = (objectOf, "objectsOf")
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
                self.convert_property_statement(p, shape_id)
        return shape_id

    def convert_property_statement(self, property_data, shape_id):
        """Convert data about a property into PropertyStatement."""
        # recursively deals with shapes for objects of properties
        ps = PropertyStatement()
        ps.add_shape(shape_id)
        for p in property_data["PropertyURIs"]:
            ps.add_property(p)
        ps.add_label("en", property_data["Label"])
        ps.add_mandatory(True)
        ps.add_severity("violation")
        if len(property_data["PropertyURIs"]) == 1:
            p_uri = property_data["PropertyURIs"][0]
            range = self.find_range(p_uri)  # returns a list of CURIEs
            for r in range:
                if r == "xsd:anyURI":
                    # handle as rdf:resource with node_type IRI
                    ps.add_valueNodeType("IRI")
                    self.ap.add_propertyStatement(ps)
                elif r in literals:
                    # add appropriate data
                    ps.add_valueNodeType("Literal")
                    ps.add_valueDataType(r)
                    self.ap.add_propertyStatement(ps)
                elif r.split(":")[0] in ["ceterms", "schema"]:
                    (range_data, node_type) = self.get_class_data(r)
                    level = self.ap.metadata["level"]
                    if range_data is not None:
                        shape_id = self.convert_shape(range_data, level, p_uri)
                        # recurse it baby
                        # welcome back
                        ps.add_valueNodeType(node_type)
                        ps.add_valueShape(shape_id)
                        self.ap.add_propertyStatement(ps)
                    else:
                        # create a shape that enforces only range
                        self.create_range_shape(p_uri, r)
                        self.ap.add_propertyStatement(ps)
                else:
                    # treat as URI ref,
                    pass
        elif len(property_data["PropertyURIs"]) > 1:
            # need property shapes for each as options
            pass
        else:
            # probably shouldn't get here
            print(ps)
            raise ValueError("No property URIs in property set.")
        return ps  # useful for testing

    def find_range(self, property_uri):
        if type(property_uri) is not str:
            print(property_uri)
            raise TypeError("URI must be passed as a string")
        elif property_uri.split(":")[0] != "ceterms":
            print(property_uri)
            raise ValueError("URI must be CURIE in ceterms namespace")
        for pd in self.cr_json["PropertyData"]:
            if pd["URI"] == property_uri:
                return pd["Range"]
        raise ValueError("No info on range of property uri " + property_uri)

    def get_class_data(self, class_uri):
        if type(class_uri) is not str:
            print(class_uri)
            raise TypeError("URI must be passed as a string")
        elif class_uri.split(":")[0] not in ["ceterms", "schema"]:
            print(class_uri)
            raise ValueError("URI is CURIE in unrecognised namespace")
        for c in self.cr_json["Policy"]["Classes"]:
            if c["URI"] == class_uri:
                if self.is_ctid_required(c):
                    node_type = "IRI"
                else:
                    node_type = "BNode"
                return (c, node_type)
        return (None, None)

    def is_ctid_required(self, class_data):
        """Return boolean True/False for whether ctid is a required property."""
        for p in class_data["PropertySets"]:
            if "ceterms:ctid" in p["PropertyURIs"]:
                if p["ImportanceLevel"] == "constraintType:RequiresProperty":
                    return True
        return False

    def create_range_shape(self, property_uri, range_uri):
        """Return a shape which expresses range r for property p_uri."""
        if type(property_uri) is not str:
            print(property_uri)
            raise TypeError("URI must be passed as a string")
        # to do: work out what the shape should be and what to return from this
        # shape_id will be something like PropertyNameRangeShape
        # target will be objects of property_uri
        shapeInfo = ShapeInfo()
        property_name = property_uri.split(":")[1]
        range_name = range_uri.split(":")[1]
        shape_id = quote(property_name.title() + range_name.title() + "Shape")
        shapeInfo.set_id(shape_id)
        shapeInfo.add_label("en", "Objects of " + property_uri)
        shapeInfo.add_comment("en", "Shape for objects of " + property_uri)
        shapeInfo.append_target(property_uri, "objectsOf")
        shapeInfo.set_closed("false")
        shapeInfo.set_mandatory("true")
        shapeInfo.set_severity("violation")
        typeProperty = PropertyStatement()
        typeProperty.add_shape(shape_id)
        typeProperty.add_property("rdf:type")
        typeProperty.add_mandatory(True)
        typeProperty.add_label("en","Specify type property.")
        typeProperty.add_repeatable(False)
        typeProperty.add_valueNodeType("iri")
        typeProperty.add_valueConstraint(range_uri)
        self.ap.add_propertyStatement(typeProperty)
        self.ap.add_shapeInfo(shape_id, shapeInfo)
