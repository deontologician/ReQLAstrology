from setuptools import setup, find_packages

VERSION = 0.1
README = open('README.rst')

setup(
    name="ReQLAstrology",
        version=VERSION,
    description="An Object-D_ocument Mapper for RethinkDB",
    author="Josh Kuhn",
    author_email="deontologician@gmail.com",
    url="deontologician.github.io/ReQLAstrology",
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    license="MIT License",
    tests_require=['pytest == 2.5.2', 'mock'],
    long_description=README,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "rethinkdb==1.12.0-2",
    ],
    scripts=[
        'tests/test_reqlastrology.py',
    ],
)