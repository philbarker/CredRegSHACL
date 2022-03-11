import pytest
from json2ap import JSON2APConverter

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
