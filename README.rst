ReQLAstrology
=============

An Object-Document Mapper for RethinkDB modeled after the Declarative
SQLAlchemy extension.

Quick Start
-----------

Installation
************

This part is pretty standard

.. code-block:: bash
   $ pip install ReQLAstrology

Configuration
*************

Create a file called ``models.py``. This is where you'll configure
your models, surprisingly enough. Configuration should be the most
onerous part, but since it's something you won't interact with
constantly during normal development, we lean towards making
configuration more verbose, and avoiding lots of magical configuration
like selecting your 
