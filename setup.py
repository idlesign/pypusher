import os
from setuptools import setup
from pypusher import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='pypusher',
    version='.'.join(map(str, VERSION)),
    description='pypusher pushes stuff from Python',
    long_description=readme,
    author="Igor 'idle sign' Starikov",
    author_email='idlesign@yandex.ru',
    url='http://github.com/idlesign/pypusher',
    packages=['pypusher'],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
