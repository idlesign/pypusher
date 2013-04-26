"""
pypusher tests

NOTE: These tests rely on sandboxed connections.

"""

import unittest

try:
    from pypusher.pypusher import *
except ImportError:
    from pypusher import *


# set_log_level(logging.DEBUG)


DEV_CERT = '/home/idle/dev/pypusher/pypusher/apns-dev-cert.pem'
DEV_KEY = '/home/idle/dev/pypusher/pypusher/apns-dev-key.pem'
DEV_TOKENS = [
    '04C11AF19F8535381BC30D1F875EF9A0C626466932571C2AA2296B8C562D397C'
]


class TestAppleNotifications(unittest.TestCase):

    def test_apple_conn_establish(self):
        conn = ApplePushConnection(DEV_CERT, DEV_KEY)
        conn.establish()
        conn.close()

    def test_apple_conn_context_man(self):
        with ApplePushConnection(DEV_CERT, DEV_KEY) as conn:
            conn.use_sandbox()
            conn.send_notification(AppleNotification('Some text', DEV_TOKENS))

    def test_version_satisfied(self):
        status, ver = lib_capn_version_satisfied()
        self.assertTrue(status)
        self.assertIsNotNone(ver)

    def test_apple_conn_context(self):
        conn = AppleConnection(DEV_CERT, DEV_KEY)

    def test_apple_conn_set_mode(self):
        conn = AppleConnection(DEV_CERT, DEV_KEY)
        conn.use_sandbox(True)
        conn.use_sandbox(False)

    def test_apple_conn_set_cert(self):
        conn = AppleConnection(DEV_CERT, DEV_KEY)
        conn.set_certificate('pyapn.py')

    def test_apple_conn_set_private_key(self):
        conn = AppleConnection(DEV_CERT, DEV_KEY)
        conn.set_private_key('pyapn.py', 'somepass')

    def test_apple_notify_context(self):
        notification = AppleNotification()

    def test_apple_notify_set_badge(self):
        notification = AppleNotification()
        notification.set_badge(33)

    def test_apple_notify_set_expires_at(self):
        notification = AppleNotification()
        notification.set_expires_at(12345678)

    def test_apple_notify_set_text(self):
        notification = AppleNotification()
        notification.set_text('Volens nolens.')

    def test_apple_notify_set_l10n_msg_key(self):
        notification = AppleNotification()
        notification.set_l10n_msg_key('some-message-key')

    def test_apple_notify_set_l10n_btn_key(self):
        notification = AppleNotification()
        notification.set_l10n_btn_key('some-button-key')

    def test_apple_notify_set_sound(self):
        notification = AppleNotification()
        notification.set_sound('playit.ogg')

    def test_apple_notify_invalid(self):
        conn = ApplePushConnection(DEV_CERT, DEV_KEY)
        conn.use_sandbox()
        n = AppleNotification('Go gor it', ['invalidtoken'])
        self.assertRaises(CapnLibraryCallException, conn.send_notification, n)

    def test_apple_notify_send(self):
        notification = AppleNotification()
        conn = ApplePushConnection(DEV_CERT, DEV_KEY)
        conn.establish()
        self.assertRaises(CapnLibraryCallException, notification.send, conn)
        notification.add_recipient(DEV_TOKENS[0])
        notification.set_text('One potato, two potato.')
        conn.use_sandbox()
        notification.send(conn)

        notification.set_text('У самого синего моря.')
        notification.send(conn)

    def test_apple_notify_set_image(self):
        notification = AppleNotification()
        notification.set_image('showit.png')

    def test_apple_notify_add_target(self):
        notification = AppleNotification()
        notification.add_recipient(DEV_TOKENS[0])

    def test_apple_notify_add_custom_unsupported(self):
        notification = AppleNotification()
        self.assertRaises(PusherException, notification.add_custom_property, 'dict', {})

    def test_apple_notify_add_custom_int(self):
        notification = AppleNotification()
        notification.add_custom_property('int', 10)
        notification._set_custom_properties()

    def test_apple_notify_add_custom_str(self):
        notification = AppleNotification()
        notification.add_custom_property('str', 'some value')
        notification._set_custom_properties()

    def test_apple_notify_add_custom_double(self):
        notification = AppleNotification()
        notification.add_custom_property('double', 30.22)
        notification._set_custom_properties()

    def test_apple_notify_add_custom_bool(self):
        notification = AppleNotification()
        notification.add_custom_property('bool', True)
        notification._set_custom_properties()

    def test_apple_get_stale(self):
        conn = AppleFeedbackConnection(DEV_CERT, DEV_KEY)
        listing = conn.get_stale_recipients()
        self.assertTrue(type(listing), list)


if __name__ == '__main__':
    unittest.main()
