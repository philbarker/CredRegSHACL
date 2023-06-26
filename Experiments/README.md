shacl.ttl can be used to validate against what is  *required* by the Registry Profile.

## to do
- [ ] add in Benchmark as Warnings.
- [ ] conside making a closed shape to give info when non-CTDL terms are used.

## Example usage

* Use with the [Joinup ITB shack validator](https://www.itb.ec.europa.eu/shacl/any/upload) -- make sure the "Load imports defined in the input" option is checked.
* Use with [pyshacl](https://pypi.org/project/pyshacl/)
  `pyshacl -s shacl.ttl -i rdfs -e https://credreg.net/ctdl/schema/encoding/turtle s_cred_ex.ttl`

## Notes
Some checks fail because range of property is declared as xsd:anyURI but published value node kinds are IRI.