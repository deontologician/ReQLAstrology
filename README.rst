ReQLAstrology
=============

An Object-Document Mapper for RethinkDB modeled after the Declarative
SQLAlchemy extension.

Principles
----------

- ReQLAstrology leans towards making model and schema definitions
  explicit and declarative because they'll be referred to many times,
  but created and modified only seldomly. This means it takes a bit
  more typing to create a "hello world" with ReQLAstrology, but in
  real apps the explicitness in model definitions will pay for itself
  in reduced frustration quickly.

- Much or even most of your schema is probably known. ReQLAstrology
  should make it easy to express the part of your schema that you
  know, while letting you leave the parts that aren't defined flexible
  and adaptable.

- Expose the full power of ReQL through a thin query layer that adds
  some convenience features for querying with model objects. (Which
  makes sense, ReQLA knows a bit more about your data, so it can
  eliminate a bit of boilerplate for you). You spend more time writing
  queries, so this is where ReQLAstrology optimizes for developer
  convenience.


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
your models, surprisingly enough. Create a couple of models for
superheroes:

.. code-block:: python
    

Future Work
-----------

- Provide a schema inference tool that can suggest models from an
  existing RethinkDB database.
    - List fields as "Maybe" if they're ever null or not present
- Provide a tool for doing migrations.
