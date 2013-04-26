pypusher
========
http://github.com/idlesign/pypusher



What's that
-----------

*pypusher pushes stuff from Python*

This module allows you to send Apple Push Notifications to various Apple devices from your Python code.

It relies on *libcapn* to feature *Apple Push Notification Service* support.



Requirements
------------

1. Python 3
2. capn library - http://libcapn.org/



Quick example
-------------

.. code-block:: python

    # Create a notification.
    notification = AppleNotification('This notification is brought to you by pypusher.', ['DEVICE_01_TOKEN_HEXSTRING', 'DEVICE_02_TOKEN_HEXSTRING'])

    # Set connection parameters.
    with ApplePushConnection('/home/idle/my_cert.pem', '/home/idle/my_key.pem') as connection:
        # Send the notification using the connection data.
        connection.send_notification(notification)


**Documentation**: http://pypusher.readthedocs.org/
