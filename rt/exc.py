"""RT exception hierarchy."""


# Base


class RTError(Exception):

    """Base RT exception type.

    Args:
        content (str): Typically, this would be the content of an RT
            response, but it can be any string (as appropriate).
        detail (str): Optional string providing extra detail about the
            error.

    Both ``content`` and ``detail`` (if provided) are passed up to
    :exc:`Exception` to complete initialization.

    """

    def __init__(self, content, detail=None):
        self.content = content
        self.detail = detail
        args = (content, detail) if detail else (content,)
        super().__init__(*args)


# Auth


class RTAuthenticationError(RTError):

    pass


# Response


class RTResponseError(RTError):

    pass


class RTUnexpectedStatusCodeError(RTResponseError):

    def __init__(self, status_code, content, detail=None):
        self.status_code = status_code
        super().__init__(content, detail)


class RTMissingResponseHeaderError(RTResponseError):

    pass


class RTMalformedResponseHeaderError(RTResponseError):

    pass


# Ticket


class RTTicketError(RTError):

    pass


class RTTicketNotFoundError(RTTicketError):

    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        super().__init__(ticket_id)


# Operation


class RTOperationError(RTError):

    """Indicates an RT operation failure."""


class RTTicketRetrievalError(RTOperationError, RTTicketError):

    pass


class RTTicketCreationError(RTOperationError, RTTicketError):

    pass


class RTTicketUpdateError(RTOperationError, RTTicketError):

    pass


# Conversion


class RTConversionError(RTError, ValueError):

    def __init__(self, type_, value, detail=None):
        content = 'Could not convert {value!r} to {type_}'.format(**locals())
        super().__init__(content, detail)
