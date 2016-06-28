# Custom fields
CUSTOM_FIELD_RE = r'^CF\.\{(?P<name>[\w-]+)\}$'

# Responses
HEADER_RE = r'^RT/(?P<version>(\d+\.)+(\d+\.)*\d+)\s+(?P<status_code>\d{3})\s+(?P<reason>\w+)$'
DETAIL_RE = r'^#(?P<detail>[\w\s.]+)$'
