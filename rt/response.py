import logging
import re


from .data import content_to_lines, RTData
from .exc import RTMalformedResponseHeaderError, RTMissingResponseHeaderError
from .patterns import DETAIL_RE, HEADER_RE


log = logging.getLogger(__name__)


class RTResponse:

    def __init__(self, content, serializer=None):
        self.content = content
        self.lines = content_to_lines(content)

        lines = self.lines

        if not lines:
            raise RTMissingResponseHeaderError(content)

        line = lines[0]
        meta = self.get_meta(line)
        if meta is None:
            raise RTMalformedResponseHeaderError(content)
        self.version = meta['version']
        self.status_code = meta['status_code']
        self.reason = meta['reason']
        lines = lines[1:]

        line = lines[0]
        if line:
            error_detail = 'Expected a blank line following the meta line'
            raise RTMalformedResponseHeaderError(content, error_detail)
        lines = lines[1:]

        # Detail line is optional.
        line = lines[0]
        self.detail = self.get_detail(line)
        if self.detail is not None:
            lines = lines[1:]

        self.data = RTData.from_lines(lines).deserialize(serializer)

    @classmethod
    def from_raw_response(cls, response):
        """Create an instance from a "raw" response object.

        Args:
            response: A "raw" response object as returned from the
                requests library.

        Returns:
            RTResponse

        """
        rt_response = cls(response.text)
        rt_response.raw_response = response
        return rt_response

    def get_meta(self, line):
        match = re.search(HEADER_RE, line)
        if match:
            return match.groupdict()

    def get_detail(self, line):
        match = re.search(DETAIL_RE, line)
        if match:
            return match.group('detail').strip()
