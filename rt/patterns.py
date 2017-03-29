# Custom fields keys. These consist of 'CF.{name}' where `name` can
# contain letters, numbers, underscores, spaces, and dashes and may end
# with a question mark.
CUSTOM_FIELD_RE = r'^CF\.\{(?P<name>[\w -]+)\??\}$'

# Response header & detail lines.
HEADER_RE = r'^RT/(?P<version>(\d+\.)+(\d+\.)*\d+)\s+(?P<status_code>\d{3})\s+(?P<reason>.+?)\s*$'
DETAIL_RE = r'^#\s*(?P<detail>.+?)\s*$'

# Response lines consisting of a 'key: value' pair where `value` may be
# empty and `key` can be one of 'CF.{name}' or 'name' where `name` can
# contain letters, numbers, underscores, spaces, and dashes and may end
# with a question mark.
KEY_VALUE_LINE = (
    r'^'
    r'(?P<key>('
    r'CF\.\{[\w -]+\??\}'
    r'|'
    r'[\w -]+\??'
    r'))'
    r':'
    r'\s*'
    r'(?P<value>.*)'
    r'$'
)
