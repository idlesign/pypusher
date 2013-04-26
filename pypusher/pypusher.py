"""
pypusher pushes stuff from Python

This module relies on libcapn to feature Apple Push Notification Service support.

"""
import logging
import ctypes
from ctypes.util import find_library


LIB_CAPN = ctypes.CDLL(find_library('capn'))
if LIB_CAPN._name is None:
    LIB_CAPN = None

LIB_CAPN_VERSION_EXPECTED = b'1.1'


class PusherException(Exception):
    """Generic pypusher exception."""

class LibraryCallException(PusherException):
    """Basic exception for external libraries calls."""


class AppleException(PusherException):
    """Basic exception for Apple services."""


class CapnLibraryCallException(LibraryCallException, AppleException):
    """Exception for libcapn calls."""


def lib_capn_version_satisfied():
    """Helper function. Checks whether found in the system libcapn
    version can be used by pypusher.

    :return: Tuple (version_satisfied_bool, found_version_number)
    """
    if LIB_CAPN is None:
        raise PusherException('Unable to find libcapn in the system. Verify it exists and registered (ldconfig).')

    version = LIB_CAPN.apn_version_string
    version.restype = ctypes.c_char_p
    version = version()
    if version.startswith(LIB_CAPN_VERSION_EXPECTED):
        return True, version

    return False, None


def set_log_level(lvl):
    """Helper function. Quickly configures logging."""
    logging.basicConfig(level=lvl, format='%(asctime)s - %(name)s - %(levelname)s\n%(message)s\n')


class PushLogger():
    """Descriptor class for logging capabilities."""

    def __init__(self):
        self._logger = None

    def __get__(self, instance, owner):
        if self._logger is None:
            self._logger = logging.getLogger(owner.__module__ + '.' + owner.__name__)
        return self._logger


def to_bytes(val):
    """Converts unicode to bytestring accepted by external C libraries."""
    return bytes(val, 'utf8')


class LibUtils():
    """Basic class with helpers for interaction with C libraries."""

    logger = PushLogger()
    lib = None
    prefix = None

    def _call_basic(self, func_short, args_list=None, restype=None):
        """Performs C library call.

        :param func_short: Library function name w/o prefix. E.g: `close` will call `apn_close`, when prefix = apn_
        :param args_list: List of arguments to be passed to function
        :param restype: Function result type to cast the result to
        :return: Function result
        """
        if args_list is None:
            args_list = []

        func_name = '%s%s' % (self.prefix, func_short)
        attrib = getattr(self.lib, func_name)
        if restype is not None:
            attrib.restype = restype

        self.logger.debug('"%s" called with %s.' % (func_name, args_list))
        result = attrib(*args_list)
        self.logger.debug('"%s" result: %s' % (func_name, result))

        return result


class CapnLib(LibUtils):
    """Helper class to ease libcapn calls."""

    def __init__(self):
        self.lib = LIB_CAPN
        self.prefix = 'apn_'

    def call(self, func_short, args_list=None, restype=None):
        """Performs lbcapn function call.

        :param func_short: Library function name w/o prefix. E.g: `close` will call `apn_close`, when prefix = apn_
        :param args_list: List of arguments to be passed to function
        :param restype: Function result type to cast the result to
        :return: Library function result
        """
        if args_list is None:
            args_list = []

        err_handle = ctypes.c_void_p()
        args_list.append(ctypes.byref(err_handle))
        result = self._call_basic(func_short, args_list, restype)
        if result == 1:
            err_msg = self.call('error_message', [err_handle], ctypes.c_char_p)
            self.call('error_free', [ctypes.byref(err_handle)])
            raise CapnLibraryCallException(err_msg)
        return result


class AppleConnection():
    """Basic connection class for Apple notification services."""

    _established = False

    def __init__(self, cert_path, private_key_path, passphrase=None):
        """Initializes connection data.

        :param cert_path: Absolute path to certificate file
        :param private_key_path: Absolute path to private key file
        :param passphrase: A passphrase for a private key
        """
        self.lib = CapnLib()
        self.certificate = cert_path
        self.private_key = private_key_path

        self.ctx_handle = ctypes.c_void_p()
        self.lib.call('init', [ctypes.byref(self.ctx_handle), None, None, None])

        self.set_certificate(cert_path)
        self.set_private_key(private_key_path, passphrase)

    def __enter__(self):
        self.establish()
        return self

    def __exit__(self, *exc_data):
        self.close()

    def establish(self):
        raise NotImplementedError()

    def use_sandbox(self, val=True):
        """Toggles sandbox mode.

        .. note::

            Certificate and private key for sandbox connection may differ
            from that used for production.

        :param val: boolean to toggle
        """
        self.lib.call('set_mode', [self.ctx_handle, int(val)])

    def set_certificate(self, path):
        """Sets absolute path to certificate used for connection."""
        self.lib.call('set_certificate', [self.ctx_handle, to_bytes(path)])

    def set_private_key(self, path, passphrase=None):
        """Sets absolute path to private key, and optionally key's passphrase
        used for connection."""
        if passphrase is not None:
            passphrase = to_bytes(passphrase)
        self.lib.call('set_private_key', [self.ctx_handle, to_bytes(path), passphrase])

    def is_established(self):
        """Returns boolean whether a connection is already established."""
        return self._established

    def close(self):
        """Closes open connection."""
        if self._established:
            self.lib.call('close', [self.ctx_handle])
            self._established = False


class ApplePushConnection(AppleConnection):
    """Used to connect to Apple Push Notification service."""

    def establish(self):
        """Establishes a connection."""
        self.lib.call('connect', [self.ctx_handle])
        self._established = True

    def send_notification(self, notification):
        """Sends the given push notification.

        :param notification: :class:`AppleNotification`
        """
        if not self.is_established():
            self.establish()

        self.lib.call('send', [self.ctx_handle, notification.ctx_handle])


class AppleFeedbackConnection(AppleConnection):
    """Used to connect to Apple Feedback service."""

    def establish(self):
        """Establishes a connection."""
        self.lib.call('feedback_connect', [self.ctx_handle])
        self._established = True

    def get_stale_recipients(self):
        """Returns a list of device tokens considered stale by Apple."""
        if not self.is_established():
            self.establish()

        listing = []

        tokens_arr = ctypes.c_void_p()
        tokens_arr_count = ctypes.c_uint32()
        self.lib.call('feedback', [self.ctx_handle, ctypes.byref(tokens_arr), ctypes.byref(tokens_arr_count)])

        if tokens_arr_count:
            arr = ctypes.c_char_p * tokens_arr_count
            array = ctypes.cast(tokens_arr, ctypes.POINTER(arr))
            listing = [item for item in array.contents]

        self.lib.call('feedback_tokens_array_free', [tokens_arr, tokens_arr_count])
        return listing


class AppleNotification():
    """Describes Apple push notification."""

    _allowed_custom_props = {
        int: ('integer', None),
        str: ('string', None),
        float: ('double', ctypes.c_double),
        bool: ('bool', None),
        # TODO array str
    }

    def __init__(self, text=None, recipients=None):
        """Initializes a notification.

        :param text: Optional notification text.
        :param recipients: List of recipients (device tokens)

        .. note:

            Either notification text or localization message key
            is required. Use `set_text` or `set_l10n_msg_key` methods
            to provide them later.

        """
        self.lib = CapnLib()
        self.custom_props = {}

        self.ctx_handle = ctypes.c_void_p()
        self.lib.call('payload_init', [ctypes.byref(self.ctx_handle)])

        if text is not None:
            self.set_text(text)

        if recipients is not None:
            for recipient in recipients:
                self.add_recipient(recipient)

    def set_badge(self, num):
        """Sets a number to be shown on notification badge.

        :param num: Integer or None to reset
        """
        if num is None:
            num = 0
        self.lib.call('payload_set_badge', [self.ctx_handle, num])

    def set_expires_at(self, ts=None):
        """Sets an expiration timestamp. Apple will try to deliver
         the notification till that date. After that it will be dismissed.

        :param ts: Timestamp or None to reset
        """
        if ts is None:
            ts = 0
        self.lib.call('payload_set_expiry', [self.ctx_handle, ts])

    def set_text(self, text):
        """Sets main text of notification.

        :param text: Text or None to reset
        """
        if text is None:
            text = ''
        self.lib.call('payload_set_body', [self.ctx_handle, to_bytes(text)])

    def set_sound(self, sound_name):
        """Sets the name of a sound file in application package
        to be played on notification.

        .. note:

            Use `default` to use the default sound.

        :param sound_name: Name or None to reset
        """
        if sound_name is None:
            sound_name = ''
        self.lib.call('payload_set_sound', [self.ctx_handle, to_bytes(sound_name)])

    def set_image(self, image_name):
        """Sets the name of an image file in application package
        to be shown on application load from notification.

        :param image_name: Name or None to reset
        """
        if image_name is None:
            image_name = ''
        self.lib.call('payload_set_launch_image', [self.ctx_handle, to_bytes(image_name)])

    def set_l10n_msg_key(self, key):
        """Sets an identifier (key) used to get certain application localization
        string for main text.

        :param key: Identifier or None to reset
        """
        if key is None:
            key = ''
        self.lib.call('payload_set_localized_key', [self.ctx_handle, to_bytes(key), None, 0])

    def set_l10n_btn_key(self, key):
        """Sets an identifier (key) used to get certain application localization
        string for notification button.

        :param key: Identifier or None to reset
        """
        if key is None:
            key = ''
        self.lib.call('payload_set_localized_action_key', [self.ctx_handle, to_bytes(key)])

    def add_custom_property(self, name, value):
        """Add custom user-defined parameter and it's value to notification.

        :param name: Property name
        :param value: Property value
        """
        t = type(value)
        if t not in self._allowed_custom_props.keys():
            raise PusherException('Unsupported value type "%s" is given for "%s" custom property. Allowed types: %s' % (t, name, list(self._allowed_custom_props.keys())))
        self.custom_props[name] = value

    def add_recipient(self, device_token):
        """Adds a recipient (token_device) to notification.

        :param device_token: Device token as a hexstring. E.g.: 04C11AF19F8535381BC30D1F875EF9A0C626466932571C2AA2296B8C562D398C
        """
        self.lib.call('payload_add_token', [self.ctx_handle, to_bytes(device_token)])

    def send(self, push_connection):
        """Performs a notification send using the given connection."""
        self._set_custom_properties()
        push_connection.send_notification(self)

    def _set_custom_properties(self):
        for name, val in self.custom_props.items():
            type_name, caster = self._allowed_custom_props[type(val)]
            if caster is not None:
                val = caster(val)

            func_short = 'payload_add_custom_property_%s' % type_name
            self.lib.call(func_short, [self.ctx_handle, to_bytes(name), val])
