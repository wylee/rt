import logging
import re

from .data import RTData
from .exc import RTTicketCreationError, RTTicketNotFoundError, RTTicketUpdateError
from .session import RTSession


log = logging.getLogger(__name__)


TICKET_NOT_FOUND_RE = r'^Ticket (?P<ticket_id>\d+) does not exist.$'
TICKET_CREATED_RE = r'^Ticket (?P<ticket_id>\d+) created.$'
TICKET_UPDATED_RE = r'^Ticket (?P<ticket_id>\d+) updated.$'


class RTInterface:

    """Wraps the RT "REST" API."""

    def __init__(self, url, username, password, default_queue=None):
        self.url = url
        self.username = username
        self.password = password
        self.default_queue = default_queue
        self.session = None
        self.new_session()

    def new_session(self):
        if self.session:
            self.session.close()
        self.session = RTSession(self.url)

    # Auth

    @property
    def logged_in(self):
        return self.session.logged_in

    def login(self):
        return self.session.login(self.username, self.password)

    def logout(self):
        result = self.session.logout()
        self.new_session()
        return result

    # Operations

    def get_ticket(self, ticket_id):
        f = locals()
        response = self.session.get('ticket/{ticket_id}/show'.format_map(f))
        if response.detail is not None:
            not_found_match = re.search(TICKET_NOT_FOUND_RE, response.detail)
            if not_found_match:
                raise RTTicketNotFoundError(ticket_id)
        return response.data

    def create_ticket(self, data):
        """Create a ticket in RT.

        Args:
            data (dict)

        Returns:
            int: Ticket ID

        Raises:
            RTTicketCreationError: Ticket can't be created in RT

        """
        path = 'ticket/new'
        rt_data = RTData((
            ('id', path),
            ('Queue', data.pop('Queue', self.default_queue)),
        ))
        rt_data.update(data)
        content = rt_data.serialize()
        response = self.session.post(path, data={'content': content})
        detail = response.detail
        if detail is not None:
            match = re.search(TICKET_CREATED_RE, detail)
            if match:
                ticket_id = match.group('ticket_id')
                return ticket_id
        raise RTTicketCreationError(content)

    def update_ticket(self, ticket_id, data):
        path = 'ticket/{ticket_id}/edit'.format(ticket_id=ticket_id)
        rt_data = RTData((
            ('id', path),
        ))
        rt_data.update(data)
        content = rt_data.serialize()
        response = self.session.post(path, data={'content': content})
        detail = response.detail
        if detail is not None:
            match = re.search(TICKET_UPDATED_RE, detail)
            if match:
                ticket_id = match.group('ticket_id')
                return ticket_id
        raise RTTicketUpdateError(content)

    def get_ticket_history(self, ticket_id, format='long'):
        """Get a ticket's transaction history.

        Args:
            ticket_id (int): An existing RT ticket ID.
            format (str|None):
                To get a list of history items with details, pass
                ``format='long'`` (the default); in this case, a list
                of :class:`RTData`s will be returned (one per history
                item).

                For a summary of history items, pass ``format='short'``;
                in this case, an :class:`RTData` will be returned with
                {ticket ID => description} pairs.

        """
        path = 'ticket/{ticket_id}/history'.format(ticket_id=ticket_id)
        params = {}
        if format in ('s', 'short'):
            multipart = False
            params['format'] = 's'
        elif format in ('l', 'long'):
            multipart = True
            params['format'] = 'l'
        else:
            raise ValueError('format must be one of "short" or "long"')
        response = self.session.post(path, params=params, multipart=multipart)
        if response.detail is not None:
            not_found_match = re.search(TICKET_NOT_FOUND_RE, response.detail)
            if not_found_match:
                raise RTTicketNotFoundError(ticket_id)
        return response.data
