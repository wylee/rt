# Change Log for RT

## 0.9.0 - unreleased

In progress...

## 0.8.0 - 2017-03-29

- Improved regular expressions used to parse key/value pairs from RT
  response lines and custom field names. Custom field names and keys may
  now end with a question mark.

## 0.7.0 - 2016-10-06

### Added

- Added `data_type` keyword arg to `RTResponse` so custom data types can
  be specified instead of always using `RTData` and `RTMultipartData`.
- Added context manager interface to `RTInterface`. This is nice for
  simple use cases to ensure the RT session is closed without a bunch of
  tedious boilerplate.
- Added `search` operation to `RTIntferface` and `RTFrontEnd`.
- Added `RTLinesData` and related `RTIDSerializer`. These are for use
  with RT data that's returned as a sequence of lines like `xyz/n`
  (e.g., what gets returned from the `search/ticket` endpoint when the
  `format` query parameter is set to `i` (for `id`?)).

### Changed

- Upgraded requests 2.10.0 => 2.11.1.
- Switched from using `re.match()` to `re.search()` when
  parsing/matching key/value lines.
- `RTSession.request()` now accepts *all* `RTResponse` args.
- All detail lines are now included in the `detail` attribute of
  `RTResponse` instances (instead of just the first detail line).
- The detail lines of an RT response are now *always* passed to the data
  type from `RTResponse`. Previously, they were only passed for
  multipart responses.
- Cleaned up some things.

### Fixed

- Added missing `RTFrontEnd.get_ticket_history()` method. The
  corresponding method was added to `RTInterface` in 3aa43d2, but I
  forgot to add it to `RTFrontEnd` then.
- Fixed key/value matching to account for the fact that custom field
  names may include spaces.


## 0.6.0 - 2016-06-30

### Added

- Added support for multipart RT responses.
- Added support for multiple RT datetime formats because different types
  of RT responses may use different formats for datetime strings.
  - XXX: There may be other formats.
  - TODO: Make formats configurable?
  - TODO: Add a configuration system.
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
indicate that the project isn't feature complete but that it's somewhat
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
