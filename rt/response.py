import logging
import re


from .data import content_to_lines, RTData, RTMultipartData
from .exc import RTMalformedResponseHeaderError, RTMissingResponseHeaderError
from .patterns import DETAIL_RE, HEADER_RE


log = logging.getLogger(__name__)


class RTResponse:

    def __init__(self, content, serializer=None, multipart=False):
        self.content = content
        self.lines = lines = content_to_lines(content)

        if not lines:
            raise RTMissingResponseHeaderError(content)

        meta = self.get_meta(lines[0])
        if meta is None:
            raise RTMalformedResponseHeaderError(content)
        self.version = meta['version']
        self.status_code = meta['status_code']
        self.reason = meta['reason']
        lines = lines[1:]

        if lines[0]:
            error_detail = 'Expected a blank line following the meta line'
            raise RTMalformedResponseHeaderError(content, error_detail)
        lines = lines[1:]

        # A detail line or lines is optional. For multipart responses,
        # the detail line of the first part will be used.
        self.details = []
        i = 0
        detail = self.get_detail(lines[i])
        while detail:
            self.details.append(detail)
            i += 1
            detail = self.get_detail(lines[i])

        # Use the first detail as the "main" detail.
        self.detail = self.details[0] if self.details else None

        if self.details:
            if lines[len(self.details)]:
                error_detail = 'Expected a blank line following detail line(s)'
                raise RTMalformedResponseHeaderError(content, error_detail)

        if multipart:
            self.data = RTMultipartData.from_lines(lines).deserialize(serializer)
        else:
            if self.details:
                # Skip detail line(s) and following blank line
                lines = lines[len(self.details):]
            self.data = RTData.from_lines(lines).deserialize(serializer)

    @classmethod
    def from_raw_response(cls, response, **kwargs):
        """Create an instance from a "raw" response object.

        Args:
            response: A "raw" response object as returned from the
                requests library.
            kwargs: Keyword args passed through to constructor.

        Returns:
            RTResponse

        """
        rt_response = cls(response.text, **kwargs)
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
