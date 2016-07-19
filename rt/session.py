import logging
import textwrap
from urllib.parse import urljoin

from requests import Session as BaseSession

from .exc import RTAuthenticationError, RTUnexpectedStatusCodeError
from .response import RTResponse


log = logging.getLogger(__name__)


class RTSession(BaseSession):

    """An RT session handles logging in & out and making requests."""

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.logged_in = False

    def request(self, method, path, acceptable_status_codes=(200,), parse_response=True,
                require_auth=True, multipart=False, **kwargs):
        """Perform a request in the current RT session.

        Args:
            method: The uppercase HTTP method name. Passed directly
                through to requests.
            path: Path relative to base RT REST URL. This will be
                combined with the base URL to get the full URL/path.
            acceptable_status_codes (tuple): Only 200 responses are
                acceptable by default.
            parse_response: By default, an :class:`RTResponse` is
                returned, which knows how to parse RT REST responses.
                The "raw" response object--as returned from the requests
                library--will be returned if this is ``False``.
            require_auth: By default, authentication is required.
                Generally speaking, only login & logout requests don't
                require auth.
            multipart: Whether the RT response contains multiple parts.
            kwargs: The remaining keyword args are passed as-is to the
                super method.

        Returns:
            RTResponse

        """
        url = self.url_for_path(path)

        if require_auth and not self.logged_in:
            raise RTAuthenticationError('Login required for {method} {url}'.format_map(locals()))

        # Never follow redirect responses because that isn't useful
        # here, mainly because redirects are the only way we can detect
        # that authentication is required (or expired).
        kwargs['allow_redirects'] = False
        response = super().request(method, url, **kwargs)

        status_code = response.status_code
        response_text = response.text

        if status_code not in acceptable_status_codes:
            if status_code == 302:
                # We don't pass the response content here because it's a
                # big lump of HTML, and that's not very helpful.
                raise RTAuthenticationError('Not authorized (session probably expired)')
            raise RTUnexpectedStatusCodeError(status_code, response_text)

        if parse_response:
            response = RTResponse.from_raw_response(response, multipart=multipart)

        log_level = log.getEffectiveLevel()
        log_args = (method, url, response.status_code, response.reason)
        if log_level == logging.DEBUG:
            indented_text = textwrap.indent(response_text, ' ')
            log_args = log_args + (indented_text,)
            log.debug('%s %s %s "%s"\n%s', *log_args)
        else:
            log.info('%s %s %s "%s"', *log_args)

        return response

    def url_for_path(self, path):
        return urljoin(self.url, path)

    # Auth

    auth_request_args = {
        'acceptable_status_codes': (200, 302),
        'parse_response': False,
        'require_auth': False,
    }

    def login(self, username, password):
        """Log in to RT.

        RT returns a 200 response on success and a 302 when the username
        and/or password is incorrect.

        Args:
            username (str): RT username
            password (str): RT password

        Returns:
            bool: ``True`` if not already logged in & login succeeds;
                ``False`` if already logged in.

        """
        if self.logged_in:
            return False
        data = {'user': username, 'pass': password}
        response = self.post('', data=data, **self.auth_request_args)
        if response.status_code == 302:
            self.close()  # Clear anonymous session state
            raise RTAuthenticationError('Could not log in with the supplied credentials')
        self.logged_in = True
        return True

    def logout(self):
        """Log out of RT.

        RT returns a 200 response on successful logout or a 302 if not
        logged in.

        Returns
            bool: ``True`` if not already logged out & logout succeeds;
                ``False`` if already logged out.

        """
        if not self.logged_in:
            return False
        response = self.post('logout', **self.auth_request_args)
        self.close()
        self.logged_in = False
        return response.status_code == 200
