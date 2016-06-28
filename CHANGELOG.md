# Change Log for RT

## 0.5.0 - 2016-06-28

This package was originally part of an internal Portland State
University project. It has been extracted for use in other PSU projects
and potentially for use by third parties.

The initial version number is somewhat arbitrary; it's intended to
indicated that the project isn't feature complete but that it's somewhat
stable.

This initial version supports only the following operations:

- Get ticket
- Create ticket
- Update ticket

Other operations will be added as needed to support PSU applications.

### Known Issues

Responses with fields containing multiline values aren't parsed
correctly. This is because RT indicates multiline responses using
indentation, but the current code assumes each line is a separate
key/value pair.
