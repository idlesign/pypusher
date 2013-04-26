Getting started with pypusher
=============================

.. note::

    Please install *libcapn* http://libcapn.org/ to use pypusher.



.. code-block:: python

    from pypusher.pypusher import *

    # Check whether capn library version is supported by pypusher.
    if lib_capn_version_satisfied():

        # Create a notification for device `DEVICE_01_TOKEN_HEXSTRING`.
        notification = AppleNotification('This notification is brought to you by pypusher.', ['DEVICE_01_TOKEN_HEXSTRING'])

        # Add another recipient.
        notification.add_recipient('DEVICE_02_TOKEN_HEXSTRING')
        # Set badge number to show 10.
        notification.set_badge(10)
        # Set expiration timestamp to 2014-10-10 10:10:10
        notification.set_expires_at(1412921410)

        # Send the notification using the connection data. And handle possible exceptions.
        try:
            # Set connection parameters: connection certificate and private key.
            with ApplePushConnection('/home/idle/my_cert.pem', '/home/idle/my_key.pem') as connection:
                # Let's use Apple sandbox servers for tests.
                connection.use_sandbox()
                connection.send_notification(notification)
        except AppleException as e:
            print('Pusher failed his mission: %s' % e)


        # Let's hunt stale device tokens if any.
        try:
            with AppleFeedbackConnection('/home/idle/my_cert.pem', '/home/idle/my_key.pem') as connection:
                stale_tokens = connection.get_stale_recipients()
                print(stale_tokens)
        except AppleException as e:
            print('Pusher failed on feedback: %s' % e)

