# RT REST API Wrapper

This packages provides a wrapper for the Request Tracker (RT) REST API.
Whether or not RT's "REST" API is truly RESTful is debatable, but we
won't get into that here.

## Installation Options

- Add `psu.oit.rt` to `install_requires` in your project's `setup.py`;
  this assumes you're project *has* a setup.py and that it utilizes
  `setuptools` instead of plain `distutils`.
- Add `psu.oit.rt` to your project's `pip` requirements files (e.g.,
  `requirements.txt` ). If your project uses `setup.py`, this is only
  necessary if you want to install this package in development mode
  (e.g., you'd add something like `-e ../psu.oit.rt` to your project's
  `requirements.txt`).
- `pip install -f https://cdn.research.pdx.edu/pypi/dist/ psu.oit.rt`.
  The `-f` (`--find-links`) is necessary because this package isn't
  currently published to PyPI.

## Basic Usage

    >>> from rt import RTInterface
    >>> rest_url = 'https://example.com/rt/REST/1.0/'
    >>> rt = RTInterface(rest_url, username, password)
    >>> rt.login()
    True
    >>> rt.get_ticket(1)
    RTData(...)

`RTData` is an `OrderedDict` of `{field name => value}` parsed from the
plain-text RT response.

## RT Websites

- Main: https://www.bestpractical.com/rt/
- GitHub: https://github.com/bestpractical/rt/ (RT is GPL-licensed)

## RT REST API Documentation

http://requesttracker.wikia.com/wiki/REST

I looked through the documentation on the RT site and couldn't find
documentation for the REST API there. Instead, it's on a third-party
wiki that's *loaded* with ads. I installed NoScript on my work computer
just for this site! Otherwise, it's barely usable.

## RT REST API Responses

Given a request such as:

    https://support.oit.pdx.edu/NoAuthCAS/REST/1.0/ticket/1

A response from the REST API looks something like this:

    RT/4.0.5 200 Ok

    id: ticket/1
    Queue: rt-test
    [Other fields elided]

The API always returns an HTTP 200 response as far as I can tell. The
response text *also* includes an HTTP-ish status line starting with the
RT version, as shown above. I think it's possible that this status line
may sometimes contain a value other than 200, but the status is usually
200, even when something isn't found.

A not-found response looks something like this:

    RT/4.0.5 200 Ok

    # Ticket NNN does not exist.

Notice that RT claims this is a 200 response, so the only way to tell
that the ticket wasn't found is to parse the line starting with "#".

## Other RT Packages

There are two other RT libraries for Python on PyPI: `rt` and
`python-rtkit`.

`python-rtkit` actually seems fairly decent in terms of code quality,
but there's no Python 3 version. `rt` supports most of RT's REST
operations, but it has some issues that were tricky to work around.

## This RT package

I was putting a lot of effort into working around various issues with
the `rt` library. In addition, we (PSU) need robust support for
multi-threaded environments (e.g., in web apps). It got to the point
where it made more sense to write and maintain a new wrapper with the
extra functionality we need.

This package:

- Has centralized, robust response parsing/serialization capabilities
- Can parse the string values returned from RT into any Python type
- Returns consistent, intuitive values for the various operations
- Consistently raises exceptions for exceptional conditions
- Provides and exception hierarchy that makes it easy to diagnose errors
- Provides a thread-safe wrapper that utilizes multiple worker threads;
  this is intended for use in, e.g., web apps (or anywhere that
  performance and/or thread-safety are a concern)

## License

MIT. See the LICENSE file.

## History

This package was developed at Portland State University (PSU) by the
Office of Information Technology (OIT) for use in various internal
applications. As such, the current version only contains the minimal
functionality needed to support OIT applications.
