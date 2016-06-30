# Change Log for RT

## 0.7.0 - unreleased

In progress...


## 0.6.0 - 2016-06-30

### Added

- Added support for multipart RT responses.
- Added support for multiple RT datetime formats because different types
  of RT responses may use different formats for datetime strings.
  XXX: There may be other formats.
  TODO: Make formats configurable?
  TODO: Add a configuration system.
- Added initial support for fetching ticket history.
- Added some initial doctests to `RTResponse`.

### Changed

- Switched to Python 3.3 instead of 3.5 in dev to ensure compatibility.
- Improved `RTConversionError`; added args that are specific to
  conversion errors.
- Preserve whitespace in values in RT responses, excluding the common
  whitespace at the beginning of continuation lines.
- Improved indentation of multiline values when serializing data for RT.
  Continuation lines now line up with their respective keys.
- Improved the regular expressions used to match header and detail lines
  in RT responses.

### Fixed

- Fixed parsing of multiline values in RT responses. Previously,
  multiline values would cause an error because we naively assumed that
  all non-blank, non-comment lines in RT responses were `Key: Value`
  pairs.
- Fixed handling of responses with multiple detail lines. All detail
  lines are now parsed out. Previously, responses with multiple detail
  lines would cause an error because we were expecting a blank line
  after a single detail line. Now, we expect that blank line after any
  number of contiguous detail lines.


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
