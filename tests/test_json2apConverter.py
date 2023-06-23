import pytest
from json2ap import JSON2APConverter
from AP import AP, PropertyStatement, ShapeInfo

ns_file_name = "inputData/namespaces.csv"
json_file_name = "inputData/policyBrowserData.json"


@pytest.fixture(scope="module")
def test_converter():
    c = JSON2APConverter()
    return c


def test_init(test_converter):
    c = test_converter
    assert c.cr_json == {}
    assert c.ap.propertyStatements == []
    assert c.ap.namespaces == {}
    assert c.ap.metadata == {}
    assert c.ap.shapeInfo == {}


def test_read_namespaces(test_converter):
    c = test_converter
    c.read_namespaces(ns_file_name)
    assert len(c.ap.namespaces) == 26
    assert c.ap.namespaces["ceterms"] == "https://purl.org/ctdl/terms/"
    with pytest.raises(TypeError) as e:
        c.read_namespaces(2)
    assert str(e.value) == "filename must be a string"
    with pytest.raises(FileNotFoundError) as e:
        c.read_namespaces("not_there.none")
    assert str(e.value) == "file named not_there.none does not exist"


def test_read_json_file(test_converter):
    c = test_converter
    c.read_json_file(json_file_name)
    assert len(c.cr_json) == 6
    assert len(c.cr_json["Policy"]["Classes"]) == 55
    with pytest.raises(TypeError) as e:
        c.read_json_file(2)
    assert str(e.value) == "filename must be a string"
    with pytest.raises(FileNotFoundError) as e:
        c.read_json_file("not_there.none")
    assert str(e.value) == "file named not_there.none does not exist"


def test_convert_metadata(test_converter):
    c = test_converter
    class_data = c.cr_json["Policy"]["Classes"][22]
    c.convert_metadata(class_data, level="required")
    assert c.ap.metadata["dct:title"] == "Credential Organization (required)"
    assert (
        c.ap.metadata["dct:description"]
        == "Required properties for Organization that plays one or more key roles in the lifecycle of a credential."
    )


def test_convert_shape(test_converter):
    c = test_converter
    class_data = c.cr_json["Policy"]["Classes"][22]
    c.convert_shape(class_data, "required")
    info = c.ap.shapeInfo["CredentialOrganizationShape"]
    assert info.id == "CredentialOrganizationShape"
    assert info.label == {"en": "Credential Organization"}
    assert info.comment == {
        "en": "Shape for organization that plays one or more key roles in the lifecycle of a credential."
    }
    assert info.targets == {"class": "ceterms:CredentialOrganization"}
    assert info.closed == False
    assert info.mandatory == True
    assert info.severity == "violation"
    with pytest.raises(ValueError) as e:
        c.build_ap(class_data, level="important")
    assert (
        str(e.value)
        == "Importance level must be one of required, recommended, or optional."
    )
    c.ap.dump()
    assert False


def test_convert_property_statement(test_converter):
    c = test_converter
    agentPurposeData = {
        "Label": "Agent Purpose",
        "Definition": "A description of the organization's primary purpose.",
        "ImportanceLevel": "constraintType:RecommendsProperty",
        "StatusURI": "vs:stable",
        "PropertyURIs": ["ceterms:agentPurpose"],
    }
    expected_ps = PropertyStatement(
        shapes=["test_shape"],
        properties=["ceterms:agentPurpose"],
        labels={"en": "Agent Purpose"},
        mandatory=True,
        repeatable=True,
        valueNodeTypes=["IRI"],
        valueDataTypes=[],
        valueShapes=[],
        valueConstraints=[],
        valueConstraintType="",
        notes={},
        severity="violation",
    )
    ps = c.convert_property_statement(agentPurposeData, "test_shape")
    assert ps == expected_ps
    nameData = {
        "Label": "Name",
        "Definition": "Name or title of the resource.",
        "ImportanceLevel": "constraintType:RequiresProperty",
        "StatusURI": "vs:stable",
        "PropertyURIs": ["ceterms:name"],
    }
    expected_ps = PropertyStatement(
        shapes=["test_shape"],
        properties=["ceterms:name"],
        labels={"en": "Name"},
        mandatory=True,
        repeatable=True,
        valueNodeTypes=["Literal"],
        valueDataTypes=["rdf:langString"],
        valueShapes=[],
        valueConstraints=[],
        valueConstraintType="",
        notes={},
        severity="violation",
    )
    ps = c.convert_property_statement(nameData, "test_shape")
    assert ps == expected_ps
    accreditedInData = {
        "Label": "Accredited In",
        "Definition": "Region or political jurisdiction such as a state, province or locale in which the credential, learning opportunity or assessment is accredited.",
        "Comment": "",
        "ImportanceLevel": "constraintType:RequiresProperty",
        "StatusURI": "vs:stable",
        "PropertyURIs": ["ceterms:accreditedIn"],
    }
    expected_ps = PropertyStatement(
        shapes=["test_shape"],
        properties=["ceterms:accreditedIn"],
        labels={"en": "Accredited In"},
        mandatory=True,
        repeatable=True,
        valueNodeTypes=[],  # to fix, should be BNode / BNode or IRI
        valueDataTypes=[],
        valueShapes=[],  # to fix, enforce range
        valueConstraints=[],
        valueConstraintType="",
        notes={},
        severity="violation",
    )
    ps = c.convert_property_statement(accreditedInData, "test_shape")
    assert ps == expected_ps


def test_get_class_data(test_converter):
    c = test_converter
    (cd, node_type) = c.get_class_data("ceterms:ApprenticeshipCertificate")
    assert node_type == "IRI"
    assert cd["Label"] == "Apprenticeship Certificate"
    (cd, node_type) = c.get_class_data("schema:QuantitativeValue")
    assert node_type == "BNode"
    assert cd["Label"] == "Quantitative Value"
