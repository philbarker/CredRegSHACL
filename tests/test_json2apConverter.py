import pytest
from json2ap import JSON2APConverter

ns_file_name = "inputData/namespaces.csv"
json_file_name = "inputData/policyBrowserData.json"

@pytest.fixture(scope = "module")
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
    with pytest.raises(TypeError) as e:
        c.read_json_file(2)
    assert str(e.value) == "filename must be a string"
    with pytest.raises(FileNotFoundError) as e:
        c.read_json_file("not_there.none")
    assert str(e.value) == "file named not_there.none does not exist"
