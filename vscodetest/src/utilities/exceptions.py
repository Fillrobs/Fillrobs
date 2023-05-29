from __future__ import unicode_literals

from urllib.parse import urlparse

from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy


class CloudBoltException(Exception):
    """Abstract base class for all exceptions defined by CloudBolt.

    CloudBolt exceptions require a normal message string, but can define
    a 'details' attribute which can be read by logging and error-handling logic.
    """

    def __init__(self, message, details=""):
        super().__init__(message)
        self.details = details


class BadColorException(CloudBoltException):
    """
    Raised when one of the colors defined within CB (ex. for the portal background color) is not a
    proper hexidecimal value.
    """


class CancelJobException(BaseException):
    """
    Exception raised in order to cancel a job.

    This inherits from BaseException because we don't want `except Exception`
    to catch it. Raising this exception should always cause the program to
    exit, similar to KeyboardInterrupt and SystemExit, so it should not be
    caught in an except block unless you have a really good reason.
    """


class NoLicensesAvailableException(CloudBoltException):
    """
    Exception raised when server(s) need licenses, there is a hard limit,
    and none are available
    """


class OperationNotAllowed(CloudBoltException):
    """
    Exception raised when a given operation is not allowed.
    """


class PermissionDeniedException(CloudBoltException):
    """
    Exception raised when any user attempts an operation outside
    their perms.
    """


class VMCreationException(CloudBoltException):
    """
    Exception raised by resource handlers when VM Creation fails for some
    reason.
    """

    def __init__(self, *args, **kwargs):
        self.original_exception = kwargs.pop("original_exception", None)
        super().__init__(*args, **kwargs)


class NameInUseException(VMCreationException):
    """
    Exception raised by resource handlers when the chosen name is already
    in use.
    """


class NotFoundException(CloudBoltException):

    """
    Exception raised when an object is not found in the CloudBolt DB or an
    external DB.

    `object_type` is an optional argument used to represent the type of object
    that was being searched for. It should be a string. For example,
    object_type='Server'.
    """

    def __init__(self, *args, **kwargs):
        self.object_type = kwargs.pop("object_type", None)
        super().__init__(*args, **kwargs)


class HookFileNotFoundException(CloudBoltException):
    """
    Raised when trying to load a ClodBoltHook that is either missing a
    hook_file attribute, or the actual file referenced in the attribute is not
    found in the cloudbolt appliance filesystem.
    """


class TimeoutException(CloudBoltException):

    """
    Raised when a job or other process fails to complete within some time
    limit.
    """


class CommandExecutionException(CloudBoltException):

    """Exception raised when an executed command returns non-zero

    Attributes:
        message
        rv
        command
        output
    """

    def __init__(self, message="", rv="", command="", output="", *args, **kwargs):
        self.rv = rv
        self.command = command
        self.output = output
        det_str = "{}. Return value: {}. Command: {}. Output: {}"
        self.details = det_str.format(message, self.rv, self.command, self.output)
        super().__init__(message, *args, **kwargs)


class IllegalStateException(CloudBoltException):

    """
    Exception raised when something happens when we don't want it to,
    such as when items that should happen in a specific order don't
    get executed properly.
    """


class MethodNotImplementedException(CloudBoltException):

    """
    Exception raised when a method that should not be called is.
    """


class LicenseViolationException(CloudBoltException):

    """
    User has exceeded or violated some portion of their license (e.g., creating
    more servers than they've licensed; using some un-licensed feature; etc
    """


class InvalidConfigurationException(CloudBoltException):

    """
    User has mis-configured the installation; or the configuration is
    somehow incomplete.
    """


class ConnectionError(CloudBoltException):

    """
    Connection to a service failed due to authorization or other errors.
    """


class InvalidCartException(CloudBoltException):

    """
    An error while updating or modifying the Cart (e.g., conflicting orders,
    multiple groups, etc)
    """


class RADIUSTimeoutException(CloudBoltException):

    """
    When connection to RADIUS server times out
    """


class RADIUSAccessRejected(CloudBoltException):

    """
    User authentication denied by RADIUS server
    """


class RADIUSException(CloudBoltException):

    """
    General RADIUS exception
    """


class ChecksumIncorrect(CloudBoltException):
    """
    For when a file is found to be corrupt.
    """


class CloudBoltIllegalURLError(Exception):
    """
    Exception for if we try to connect to an external URL that is not covered by
    GlobalPreferences.external_url_whitelist
    """

    def __init__(self, url, *args, **kwargs):
        """Just track the URL for the __str__ method"""
        super().__init__(*args, **kwargs)
        self.url = None
        # try to get just the domain of the URL using urlparse so that the error message
        # is better for the end user b/c the External URL Whitelist only takes domains and
        # not full URLs
        try:
            self.url = urlparse(url).netloc
        # if urlparse fails, it raises a ValueError
        except ValueError:
            pass
        # if urlparse failed or it could not determine the domain of the given URL
        if not self.url:
            self.url = url

    def __str__(self):
        """Verbose error description"""
        return ugettext_lazy(
            "Cannot send a request to {url} as it is not in the External URL Whitelist"
        ).format(url=self.url)


# These are mostly used by run_script stuff:
class MissingArgumentError(ValueError):
    """An argument was required but was not provided or was None."""

    pass


class MutuallyExclusiveArgumentsError(ValueError):
    """Two (or more) arguments cannot both be provided, but were."""

    pass


class IllegalArgument(ValueError):
    """For use in validating arguments in our internal methods and functions."""

    pass


class MissingAttributeValueError(ValueError):
    """The requested functionality requires an attribute to be set on a class, but it wasn't."""

    pass


class OptionIsNotUnique(ValueError):
    """
    Raised when a Preconfiguration option (PreconfigurationValueSet.value) is not unique for a given
    Preconfiguration to which is belongs. Could also be used for CustomField options.
    """

    pass


class ConditionalEscapeError(Exception):
    """ Unspecified run-time error that is marked safe and can pass html. """

    def __str__(self):
        return conditional_escape(self.args[0])


class NamingSequenceRangeExceededError(Exception):
    """
    Raised when the sequence limit has been reached when generating a custom name for Fuse.
    Non-reuse scenario
    """

    def __init__(self, *args, **kwargs):
        self.sequence_name = kwargs.pop("sequence_name", None)
        self.sequence_value = kwargs.pop("sequence_value", None)
        super().__init__(*args, **kwargs)


class InstanceIsHibernating(ValueError):
    """
    Raised to indicate when a ServiceNow Instance is in hibernation.
    Inherits from ValueError so it gets caught with other connection issues
    for ServiceNow.
    """

    pass


class ObjectInUseException(CloudBoltException):
    """
    Raised when a request/action is in conflict with the current state of
    the server, such as deleting an object which is used within other objects
    """


class InvalidCredentialsException(CloudBoltException):
    """Raised to indicate that the supplied credentials were invalid."""

    def __init__(self, message, details=""):
        super().__init__(message)
        self.message = message
        self.details = details
