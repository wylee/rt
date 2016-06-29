import re
from collections import MutableMapping, OrderedDict, Sequence
from datetime import datetime
from itertools import chain
from textwrap import dedent

from .exc import RTConversionError
from .patterns import CUSTOM_FIELD_RE, KEY_VALUE_LINE


DATETIME_FORMATS = (
    '%a %b %d %H:%M:%S %Y',
    '%Y-%m-%d %H:%M:%S',
)


def content_to_lines(content):
    return content.splitlines()


def parse_cf_name(name):
    """Parse custom field name from ``name``.

    Args:
        name (str): An RT field name

    Returns:
        str: 'XXX' if ``name`` is formatted as a custom field name like
            'CF.{XXX}'
        None: If ``name`` isn't formatted as a custom field name

    """
    cf_match = re.search(CUSTOM_FIELD_RE, name)
    if cf_match:
        cf_name = cf_match.group('name')
        return cf_name


def to_cf_name(name):
    """Format field name as a custom field name.

    If the field name is already formatted as a custom field name, it
    will be return as is.

    Args:
        name: A field name

    Returns:
        str: Custom field name like 'CF.{XXX}'


    """
    cf_name = parse_cf_name(name)
    return cf_name or 'CF.{%s}' % name


class RTData(OrderedDict):

    """Container for RT data.

    Custom fields can be set and retrieved in two ways::

        >>> data = RTData()

        >>> data.custom_fields['XYZ'] = 'xyz'
        >>> data.custom_fields['XYZ']
        'xyz'
        >>> data['CF.{XYZ}']
        'xyz'

        >>> data['CF.{ABC}'] = 'abc'
        >>> data['CF.{ABC}']
        'abc'
        >>> data.custom_fields['ABC']
        'abc'

        >>> data = RTData.from_lines(['ABC: abc'])
        >>> data['ABC']
        'abc'

        >>> data = RTData.from_lines(['ABC: abc', 'XYZ: x', ' y', ' z'])
        >>> data['ABC']
        'abc'
        >>> data['XYZ']
        'x\\ny\\nz'

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_fields = RTCustomFields(self)

    @classmethod
    def from_lines(cls, lines):
        """Create instance from lines of data.

        Args:
            lines (list): The content lines of an RT response. I.e., the
                part of the response text after the meta and detail lines.

                Note: line endings *should* be stripped from each line
                but other leading and trailing whitespace should *not*
                be stripped.

        Returns:
            RTData: Map of RT field name => raw field value.

        These are the types of lines we expect to encounter:

            - Blank lines (no content at all, including whitespace)
            - Comment lines (e.g., "# Comment")
            - Key lines (e.g., "Created: ABC")
            - Continuation lines (e.g., "    " or "    XYZ")

        Longest common whitespace is removed from continuation lines (on
        a per-value basis). Otherwise, leading and trailing whitespace
        is preserved.

        """
        data = []
        key_lines = []

        # Find & save lines containing keys
        for i, line in enumerate(lines):
            if not line or line.startswith('#'):
                continue
            match = re.match(KEY_VALUE_LINE, line)
            if match:
                key_lines.append((i, match.group('key'), match.group('value')))
            elif not line.startswith(' '):
                raise ValueError(
                    'Expected a continuation line starting with a space; got "%s"' % line)

        # Extract value for each key found above
        eof = (len(lines), None, None)
        for line, next_line in zip(key_lines, chain(key_lines[1:], [eof])):
            value = []
            i, key, start_value = line
            j, *rest = next_line
            continuation_lines = lines[(i + 1):j]
            if start_value:
                value.append(start_value)
            if continuation_lines:
                continuation_lines = dedent('\n'.join(continuation_lines))
                value.append(continuation_lines)
            data.append((key, '\n'.join(value).strip()))

        return cls(data)

    @classmethod
    def from_string(cls, content):
        """Create instance from string."""
        return cls.from_lines(content_to_lines(content))

    def serialize(self, serializer=None):
        """Convert from Python to RT content string."""
        if serializer is None:
            serializer = RTDataSerializer()
        return serializer.serialize(self)

    def deserialize(self, serializer=None):
        """Convert from raw RT to Python."""
        if serializer is None:
            serializer = RTDataSerializer()
        return serializer.deserialize(self)

    def __str__(self):
        return self.serialize()


class RTMultipartData(Sequence):

    def __init__(self, items):
        self._items = items

    @classmethod
    def from_lines(cls, lines):
        # TODO: Extract detail lines?
        parts = []
        current_part = []
        prev_iter = chain([None], lines[:-1])
        next_iter = chain(lines[1:], [None])
        for prev_line, line, next_line in zip(prev_iter, lines, next_iter):
            if not line or line.startswith('#'):
                continue
            if (prev_line, line, next_line) == ('', '--', ''):
                parts.append(current_part)
                current_part = []
            else:
                current_part.append(line)
        items = [RTData.from_lines(part) for part in parts]
        return RTMultipartData(items)

    @classmethod
    def from_string(cls, content):
        """Create instance from string."""
        return cls.from_lines(content_to_lines(content))

    def serialize(self, serializer=None):
        return '\n--\n\n'.join(item.serialize(serializer) for item in self)

    def deserialize(self, serializer=None):
        return RTMultipartData([item.deserialize(serializer) for item in self])

    def __getitem__(self, index):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return self.serialize()


class RTCustomFields(MutableMapping):

    """A container for RT custom fields.

    It provides a nicer way to access custom fields. Instead of::

        >>> data = RTData()
        >>> data['CF.{SomeField}'] = 'some value'
        >>> data['CF.{SomeField}']
        'some value'

    We can do this::

        >>> data = RTData()
        >>> data.custom_fields['SomeField'] = 'some value'
        >>> data.custom_fields['SomeField']
        'some value'

    It also provides an easy way to grab all of the custom fields from
    an :class:`RTData` container::

        >>> data = RTData()
        >>> data.custom_fields['SomeField'] = 'some value'
        >>> data.custom_fields['SomeOtherField'] = 'some other value'
        >>> for cf in data.custom_fields:
        ...     pass  # Do stuff with custom field

    Or see how many custom fields there are::

        >>> data = RTData()
        >>> data.custom_fields['SomeField'] = 'some value'
        >>> len(data.custom_fields)
        1

    Ordering is inherited from the parent container::

        >>> data = RTData()
        >>> data.custom_fields['First'] = 1
        >>> data.custom_fields['Second'] = 2
        >>> list(data.custom_fields.keys())
        ['First', 'Second']

    Args:
        container (RTData): The RTData instance these custom fields
            belong to.

    """

    def __init__(self, container):
        self.container = container

    def _cf_name(self, name):
        # 'name' => 'CF.{name}'
        cf_name = parse_cf_name(name)
        if cf_name:
            raise KeyError('When accessing a custom field, use just the name: %s' % cf_name)
        return to_cf_name(name)

    def __delitem__(self, name):
        cf_name = self._cf_name(name)
        try:
            return self.container.__delitem__(cf_name)
        except KeyError:
            raise KeyError(cf_name)

    def __getitem__(self, name):
        cf_name = self._cf_name(name)
        try:
            return self.container.__getitem__(cf_name)
        except KeyError:
            raise KeyError(cf_name)

    def __iter__(self):
        for name in self.container:
            cf_name = parse_cf_name(name)
            if cf_name:
                yield cf_name

    def __len__(self):
        return sum(1 for _ in self)

    def __setitem__(self, name, value):
        return self.container.__setitem__(self._cf_name(name), value)


class RTDataSerializer:

    # Map of RT field name => type to convert that field to
    conversion_map = {
        'Created': 'datetime',
        'LastUpdated': 'datetime',
        'Requestors': 'list',
    }

    multiline_fields = ('Text',)

    def deserialize(self, raw_data):
        """Convert raw string values returned from RT to Python.

        Args:
            raw_data (RTData): An RTData instance whose raw values have
                not yet been converted.

        Returns:
            RTData: A new RTData instance with converted values.

        """
        data = RTData()
        for name, value in raw_data.items():
            if name in self.conversion_map:
                type_name = self.conversion_map[name]
                converter_name = 'convert_to_%s' % type_name
                converter = getattr(self, converter_name)
                value = converter(raw_data.get(name))
            data[name] = value
        return data

    def serialize(self, data):
        """Convert Python data to a string for RT.

        Args:
            data (RTData): An RTData instance whose values will be
                converted to strings appropriate for RT.

        Returns:
            str: The converted data as an RT content string.

        """
        lines = []
        for name, value in data.items():
            if isinstance(value, Sequence) and not isinstance(value, str):
                value = ', '.join(value).strip()
            else:
                value = str(value).strip()
                if name in self.multiline_fields:
                    value = value.splitlines()
                    value = '\n '.join(value)
            lines.append('{name}: {value}'.format(name=name, value=value))
        lines.append('')
        content = '\n'.join(lines)
        return content

    def convert_to_datetime(self, string):
        """Convert a string as returned from RT to a ``datetime`` object.

        Args:
            string (str): Datetime string formatted according to
                :attr:`datetime_format`.

        Returns:
            datetime

        """
        if not string:
            return None
        for f in DATETIME_FORMATS:
            try:
                return datetime.strptime(string, f)
            except (TypeError, ValueError):
                pass
        raise RTConversionError('datetime', string, 'Formats: {}'.format(DATETIME_FORMATS))

    def convert_to_list(self, string):
        """Convert a list value as returned from RT to a ``list``.

        Args:
            string (str): String with list items separated by commas.
                Whitespace between items is ignored & stripped.

        Returns:
            list

        """
        if not string:
            return []
        items = string.split(',')
        items = [item.strip() for item in items]
        items = [item for item in items if item]  # XXX: Necessary?
        return items
