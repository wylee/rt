# Custom fields
CUSTOM_FIELD_RE = r'^CF\.\{(?P<name>[\w-]+)\}$'

# Responses
HEADER_RE = r'^RT/(?P<version>(\d+\.)+(\d+\.)*\d+)\s+(?P<status_code>\d{3})\s+(?P<reason>.+?)\s*$'
DETAIL_RE = r'^#\s*(?P<detail>.+?)\s*$'
# Values may be empty
KEY_VALUE_LINE = r'^(?P<key>[A-Za-z0-9{}._-]+):\s*(?P<value>.*)$'
