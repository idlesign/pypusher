Apple Push Notifications
========================

pypusher relies upon two classes to send Apple push notifications: ``ApplePushConnection`` and ``AppleNotification``.

``AppleFeedbackConnection`` class allows to get feedback information on stale device tokens from Apple.

Utilities
----------


.. warning::

    When troubleshooting please use ``lib_capn_version_satisfied()`` to check whether
    C library is found and has an appropriate version.


.. autoclass:: pypusher.pypusher.lib_capn_version_satisfied



.. _class-push_connection:

ApplePushConnection
-------------------


.. autoclass:: pypusher.pypusher.ApplePushConnection
    :members:
    :inherited-members:



.. _class-feedback_connection:


AppleFeedbackConnection
-----------------------

.. autoclass:: pypusher.pypusher.AppleFeedbackConnection
    :members:
    :inherited-members:



.. _class-notification:

AppleNotification
-----------------

.. autoclass:: pypusher.pypusher.AppleNotification
    :members:



Exceptions
==========

*pypusher* features te following exceptions to tackle with errors related to Apple Pushes.


.. _class-apple_exception:

AppleException
--------------

.. autoclass:: pypusher.pypusher.AppleException
    :members:

.. _class-capne_exception:


CapnLibraryCallException
------------------------

.. autoclass:: pypusher.pypusher.CapnLibraryCallException
    :members:
