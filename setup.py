from setuptools import setup, find_packages


setup(
    author="Will Gaggioli",
    author_email="wgaggioli@gmail.com",
    name='intervalfield',
    version="0.1",
    description='IntervalField for Django Models and Forms',
    license='Beerware',
    platforms=['OS Independent'],
    install_requires=[
        'Django',
        'python-dateutil'
    ],
    tests_require=['mock'],
    packages=find_packages(exclude=[]),
    include_package_data=True,
)
