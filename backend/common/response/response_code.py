#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses

from enum import Enum

from backend.common.i18n import t


class CustomCodeBase(Enum):
    """Custom status code base class"""

    @property
    def code(self) -> int:
        """Get status code"""
        return self.value[0]

    @property
    def msg(self) -> str:
        """Get status code information"""
        message = self.value[1]
        return t(message)


class CustomResponseCode(CustomCodeBase):
    """Custom response status code"""

    HTTP_200 = (200, 'response.success')
    HTTP_400 = (400, 'response.error')
    HTTP_500 = (500, 'Server Internal Error')


class CustomErrorCode(CustomCodeBase):
    """Custom Error Status Code"""

    CAPTCHA_ERROR = (40001, 'error.captcha.error')


@dataclasses.dataclass
class CustomResponse:
    """
    Provide open response status codes instead of enumerations, which can be useful if you want to customize response information
    """

    code: int
    msg: str


class StandardResponseCode:
    """Standard response status code"""

    """
    HTTP codes
    See HTTP Status Code Registry:
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml

    And RFC 2324 - https://tools.ietf.org/html/rfc2324
    """
    HTTP_100 = 100 # CONTINUE: Continue
    HTTP_101 = 101 # SWITCHING_PROTOCOLS: Protocol Switching
    HTTP_102 = 102 # PROCESSING: Processing
    HTTP_103 = 103 # EARLY_HINTS: Prompt message
    HTTP_200 = 200 # OK: The request was successful
    HTTP_201 = 201 # CREATED: Created
    HTTP_202 = 202 # ACCEPTED: Accepted
    HTTP_203 = 203 # NON_AUTHORITATIVE_INFORMATION: Non-authoritative information
    HTTP_204 = 204 # NO_CONTENT: No content
    HTTP_205 = 205 # RESET_CONTENT: Reset content
    HTTP_206 = 206 # PARTIAL_CONTENT: Partial content
    HTTP_207 = 207 # MULTI_STATUS: Multi-state
    HTTP_208 = 208 # ALREADY_REPORTED: Reported
    HTTP_226 = 226 # IM_USED: Used
    HTTP_300 = 300 # MULTIPLE_CHOICES: Multiple Choices
    HTTP_301 = 301 # MOVED_PERMANENTLY: Permanently Moved
    HTTP_302 = 302 # FOUND: Temporary Move
    HTTP_303 = 303 # SEE_OTHER: View other locations
    HTTP_304 = 304 # NOT_MODIFIED: Not modified
    HTTP_305 = 305 # USE_PROXY: Using Proxy
    HTTP_307 = 307 # TEMPORARY_REDIRECT: Temporary redirection
    HTTP_308 = 308 # PERMANENT_REDIRECT: Permanent redirect
    HTTP_400 = 400 # BAD_REQUEST: Request error
    HTTP_401 = 401 # UNAUTHORIZED: Unauthorized
    HTTP_402 = 402 # PAYMENT_REQUIRED: Payment is required
    HTTP_403 = 403 # FORBIDDEN: Access is prohibited
    HTTP_404 = 404 # NOT_FOUND: Not found
    HTTP_405 = 405 # METHOD_NOT_ALLOWED: Method not allowed
    HTTP_406 = 406 # NOT_ACCEPTABLE: Not acceptable
    HTTP_407 = 407 # PROXY_AUTHENTICATION_REQUIRED: Proxy authentication is required
    HTTP_408 = 408 # REQUEST_TIMEOUT: Request timeout
    HTTP_409 = 409 # CONFLICT: Conflict
    HTTP_410 = 410 # GONE: Deleted
    HTTP_411 = 411 # LENGTH_REQUIRED: Content length required
    HTTP_412 = 412 # PRECONDITION_FAILED: Prerequisite failed
    HTTP_413 = 413 # REQUEST_ENTITY_TOO_LARGE: The request entity is too large
    HTTP_414 = 414 # REQUEST_URI_TOO_LONG: Request URI is too long
    HTTP_415 = 415 # UNSUPPORTED_MEDIA_TYPE: Unsupported media types
    HTTP_416 = 416 # REQUESTED_RANGE_NOT_SATISFIABLE: The request scope does not meet the requirements
    HTTP_417 = 417 # EXPECTATION_FAILED: Expectation failed
    HTTP_418 = 418 # UNUSED: Idle
    HTTP_421 = 421 # MISDIRECTED_REQUEST: Request that was wrongly directed
    HTTP_422 = 422 # UNPROCESSABLE_CONTENT: Unprocessable entity
    HTTP_423 = 423 # LOCKED: Locked
    HTTP_424 = 424 # FAILED_DEPENDENCY: Dependency failed
    HTTP_425 = 425 # TOO_EARLY: Too early
    HTTP_426 = 426 # UPGRADE_REQUIRED: Requires upgrade
    HTTP_427 = 427 # UNASSIGNED: Not allocated
    HTTP_428 = 428 # PRECONDITION_REQUIRED: Prerequisites required
    HTTP_429 = 429 # TOO_MANY_REQUESTS: Too many requests
    HTTP_430 = 430 # Unassigned: Not allocated
    HTTP_431 = 431 # REQUEST_HEADER_FIELDS_TOO_LARGE: The request header field is too large
    HTTP_451 = 451 # UNAVAILABLE_FOR_LEGAL_REASONS: Not available due to legal reasons
    HTTP_500 = 500 # INTERNAL_SERVER_ERROR: Server internal error
    HTTP_501 = 501 # NOT_IMPLEMENTED: Not implemented
    HTTP_502 = 502 # BAD_GATEWAY: Error gateway
    HTTP_503 = 503 # SERVICE_UNAVAILABLE: The service is not available
    HTTP_504 = 504 # GATEWAY_TIMEOUT: Gateway timeout
    HTTP_505 = 505 # HTTP_VERSION_NOT_SUPPORTED: HTTP version does not support
    HTTP_506 = 506 # VARIANT_ALSO_NEGOTIATES: Variants will also be negotiated
    HTTP_507 = 507 # INSUFFICIENT_STORAGE: Insufficient storage space
    HTTP_508 = 508 # LOOP_DETECTED: Loop detected
    HTTP_509 = 509 # UNASSIGNED: Not allocated
    HTTP_510 = 510 # NOT_EXTENDED: Not extended
    HTTP_511 = 511 # NETWORK_AUTHENTICATION_REQUIRED: Requires network authentication

    """
    WebSocket codes
    https://www.iana.org/assignments/websocket/websocket.xml#close-code-number
    https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
    """
    WS_1000 = 1000 # NORMAL_CLOSURE: Normally closed
    WS_1001 = 1001 # GOING_AWAY: Leaving
    WS_1002 = 1002 # PROTOCOL_ERROR: Protocol Error
    WS_1003 = 1003 # UNSUPPORTED_DATA: Unsupported data types
    WS_1005 = 1005 # NO_STATUS_RCVD: No status received
    WS_1006 = 1006 # ABNORMAL_CLOSURE: Exception closed
    WS_1007 = 1007 # INVALID_FRAME_PAYLOAD_DATA: Invalid frame load data
    WS_1008 = 1008 # POLICY_VIOLATION: Policy Violation
    WS_1009 = 1009 # MESSAGE_TOO_BIG: The message is too big
    WS_1010 = 1010 # MANDATORY_EXT: Required extension
    WS_1011 = 1011 # INTERNAL_ERROR: Internal error
    WS_1012 = 1012 # SERVICE_RESTART: Service restart
    WS_1013 = 1013 # TRY_AGAIN_LATER: Please try again later
    WS_1014 = 1014 # BAD_GATEWAY: Error gateway
    WS_1015 = 1015 # TLS_HANDSHAKE: TLS handshake error
    WS_3000 = 3000 # UNAUTHORIZED: Unauthorized
    WS_3003 = 3003 # FORBIDDEN: Access is prohibited
