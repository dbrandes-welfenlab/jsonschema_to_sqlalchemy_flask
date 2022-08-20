JSON Schema to Flask SQLAlchemy / Flask Admin converter
=======================================================

Idea
----

The main idea behind this project is to get a simple web based cruid
interface for given JSON Schema files without the need of manual convert
these data structures to other formats and handle this redundancy. As
JSON seems to be the defacto standard data exchange format for different
programming languages and JSON Schema is the natual extension to specify
the content of the data, in many cases these are anyway exists, or could
easily be generated, these two are the choosen ones.

What it does
------------

This script converts a couple of connected (with filenames $ref) flat
(without neested objects) JSON Schema files to a few python scripts:

-  one containing the flask admin / SQLAlchemy data,
-  one to create data in database,
-  one to get all unique names of data (see above),
-  one to convert an object from the database to a python dict,
-  and one to get an order in which new entries in the database should
   constructed (cause of unique name fields, see above).

Each JSON schema description should contain one variable that is marked
with “uniqueName”: true that contains a unique name for this entry. This
name should be used to reference this datafield from other JSON Schemas
with “$ref”:“FILENAME.schema.json” (see
jsonschema_to_sqlalchemy_flask/test/data folder for a simple example).
The scripts could be used in the process when the JSON schemas are
generated (if they are generated), so the interface is updated
accordingly. The default location of the database is the “/tmp”
directory, so data should be read and saved elsewhere after creation.

For use this project, create a dir, for example test_js2sf, create an
empty **init**.py file there, insert the following in your code:

.. code:: python

   from jsonschema_to_sqlalchemy_flask.src import convert_to_sqlalchemy_flask
   from jsonschema_to_sqlalchemy_flask.src import convert_to_json_loader
   from jsonschema_to_sqlalchemy_flask.src import convert_to_json_dump
   from jsonschema_to_sqlalchemy_flask.src import convert_to_unique_name_list_getter
   from jsonschema_to_sqlalchemy_flask.src.get_order import get_order
   from jsonschema_to_sqlalchemy_flask.src.convert_from_json_schema import convert_flask_admin

to import all stuff and

.. code:: python

   schema_filename_list = ["filename1.schema.json", "filename2.schema.json"]
   flask_filename_without_extension = "flask_main_file"
   flask_filename = "test_js2sf/flask_main_file.py"

   data = convert_flask_admin(schema_filename_list, flask_filename_without_extension)

to get an intermediate data structure for getting the python code (with
existing JSON Schema files filename1.schema.json and
filename2.schema.json), and after:

.. code:: python

   flask_file = convert_to_sqlalchemy_flask.insert_in_template(data)
   with open(flask_filename, "w") as fh:
       fh.write(flask_file)

and

.. code:: python

   json_load_file = convert_to_json_loader.insert_in_template(data)
   json_dump_from_database_file = convert_to_json_dump.insert_in_template(data)
   unique_name_list_file = convert_to_unique_name_list_getter.insert_in_template(data)
   order_list = get_order(data)

to get the python code from. After saving these files (for example
“test_js2sf/json_load.py”, “test_js2sf/json_dump.py” and
“test_js2sf/name_list.py”), they could be called from commandline as
follows:

.. code:: bash

   python -m test_js2sf.json_load --input_filename filename1.json --modelname filename1

with existing filename1.json contains data that fits the
filename1.schema.json and its unique name contains “name1” and

.. code:: bash

   python -m test_js2sf.json_dump.py --modelname filename1 --uniquename "name1" --output_filename "equal_to_filename1.json"

or

.. code:: bash

   python -m test_js2sf.name_list.py --modelname filename1

to get all unique names for filename1.schema.json data in database.

Install
-------

install with pip (python 3.10 and new pip version needed):

.. code:: bash

   pip install jsonschema-to-sqlalchemy-flask

Links
-----

-  `Github
   Repo <https://github.com/dbrandes-welfenlab/jsonschema_to_sqlalchemy_flask>`__
-  `example
   Repo <https://github.com/dbrandes-welfenlab/test_jsonschema_to_sqlalchemy_flask>`__
