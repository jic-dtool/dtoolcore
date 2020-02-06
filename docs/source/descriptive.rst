Descriptive documentation
=========================


Quickstart
----------

The easiest way to create a dataset is to use the
:class:`dtoolcore.DataSetCreator` context manager.

The code below creates a frozen dataset without any metadata or data.

.. code-block:: python

    >>> from dtoolcore import DataSetCreator
    >>> with DataSetCreator("my-awesome-dataset", "/tmp") as ds_creator:
    ...     uri = ds_creator.uri

Clearly, this dataset is not very interesting. However, we can use it to show
how one can load a :class:`dtoolcore.DataSet` instance from a dataset's URI,
using the :func:`dtoolcore.DataSet.from_uri` method.

    
.. code-block:: python

    >>> from dtoolcore import DataSet
    >>> dataset = DataSet.from_uri(uri)
    >>> print(dataset.name)
    my-awesome-dataset
       

..  clean up

    >>> import shutil
    >>> shutil.rmtree("/tmp/my-awesome-dataset")


Creating a dataset
------------------

A dtool dataset packages data and metadata. Descriptive metadata is stored
in a "README" file at the top level of the dataset. It is best practise to
use the YAML file format for the README.

The code below creates a variable that holds a string with descriptive metadata
in YAML format.

.. code-block:: python

    >>> readme_content = "---\ndescription: three text files with animals"

The ``readme_content`` can be added to the dataset when creating a
:class:`dtoolcore.DataSetCreator` context manager.

.. code-block:: python

    >>> with DataSetCreator("animal-dataset", "/tmp", readme_content) as ds_creator:
    ...     animal_ds_uri = ds_creator.uri
    ...     for animal in ["cat", "dog", "parrot"]:
    ...         handle = animal + ".txt"  # Unix-like relpath
    ...         fpath = ds_creator.prepare_staging_abspath_promise(handle)
    ...         with open(fpath, "w") as fh:
    ...             fh.write(animal)
    ...

The code above does several things. It stores the URI of the dataset in the
variable ``animal_ds_uri``. It loops over the strings ``cat``, ``dog``,
``parrot`` and creates a so called "handle" for each one of them. A handle is a
human readable label of an item in a dataset. It has to be unique and look like
a Unix-style relpath. The handle is then passed into the
:func:`dtoolcore.DataSetCreator.prepare_staging_abspath_promise` method which
returns the absolute path to a file that needs to be created within the
lifetime of the context manager. Otherwise a
``dtoolcore.DtoolCoreBrokenStagingPromise`` exception is raised. The code then
uses these absolute paths to create files in these locations. When the context
manager exits these files are added to the dataset, the temporary location
where the files were created is deleted and the dataset is frozen.


Working with items in a dataset
-------------------------------

Below a dataset is loaded from the ``animal_ds_uri``.

.. code-block:: python

    >>> animal_dataset = DataSet.from_uri(animal_ds_uri)

The readme content can be accessed using the
:func:`dtoolcore.DataSet.get_readme_content()` method.

.. code-block:: python

    >>> print(animal_dataset.get_readme_content())
    ---
    description: three text files with animals

Items in a dataset are accessed using their identifiers. The item identifiers
can be accessed using the :attr:`dtoolcore.DataSet.identifiers` property.
 
.. code-block:: python

    >>> for i in animal_dataset.identifiers:
    ...     print(i)
    ...
    e55aada093b34671ec2f9467fe83f0d3d8c31f30
    d25102a700e072b528db79a0f22b3a5ffe5e8f5d
    26f0d76fb3c3e34f0c7c8b7c3461b7495761835c

To view information about each item one can use the
:func:`dtoolcore.DataSet.item_properties` method that returns a dictionary with
the items ``hash``, ``size_in_bytes``, ``relpath`` (also known as "handle").

    >>> for i in animal_dataset.identifiers:
    ...     item_props = animal_dataset.item_properties(i)
    ...     info_str = "{hash} {size_in_bytes} {relpath}".format(**item_props)
    ...     print(info_str)
    ...
    d077f244def8a70e5ea758bd8352fcd8 3 cat.txt
    68238cd792d215bdfdddc7bbb6d10db4 6 parrot.txt
    06d80eb0c50b49a509b49f2424e8c805 3 dog.txt

To get the content of an item one can use the
:func:`dtoolcore.DataSet.item_content_abspath` method. The method guarantees
that the content of the item will be available in the abspath provided. This is
important when working with datasets stored in the cloud, for example
in an AWS S3 bucket.

.. code-block:: python

    >>> for i in animal_dataset.identifiers:
    ...     fpath = animal_dataset.item_content_abspath(i)
    ...     with open(fpath, "r") as fh:
    ...         print(fh.read())
    ...
    cat
    parrot
    dog


Annotating a dataset with key/value pairs
-----------------------------------------

The descriptive metadata in the readme is not ideally suited for
programatic access to metadata. If one needs to interact with
metadata programatically it is much easier to do so using so
called "annotations". These are key/value pairs that can be added
to a dataset.

In the code below the :func:`dtoolcore.DataSet.put_annotation` method is used
to add add the key/value pair "category"/"pets" to the dataset.

.. code-block:: python

    >>> animal_dataset.put_annotation("category", "pets")

The :func:`dtoolcore.DataSet.get_annotation` can then be used to access the
value of the "category" annotation.

.. code-block:: python

    >>> print(animal_dataset.get_annotation("category"))
    pets

It is also possible to add an annotation to a dataset inside a
:class:`dtoolcore.DataSetCreator` conext manager using the
:func:`dtoolcore.DataSetCreator.put_annotation` method.


Working with item metadata
--------------------------

It is also possible to add per item metadata. This is, for example, useful if
one wants to access only a subset of items from a dataset. Below is a
dictionary that can be used to look up the family of a set of animals.

.. code-block:: python

    >>> family = {
    ...     "tiger": "felidae",
    ...     "lion": "felidae",
    ...     "horse": "equidae"
    ... }

The code below creates a new dataset and adds the "family" of the animal
as a piece of metadata to each item using the
:func:`dtoolcore.DataSetCreator.add_item_metadata` method.

.. code-block:: python

    >>> with DataSetCreator("animal-2-dataset", "/tmp") as ds_creator:
    ...     animal2_ds_uri = ds_creator.uri
    ...     for animal in ["tiger", "lion", "horse"]:
    ...         handle = animal + ".txt"  # Unix-like relpath
    ...         fpath = ds_creator.prepare_staging_abspath_promise(handle)
    ...         with open(fpath, "w") as fh:
    ...             fh.write(animal)
    ...         ds_creator.add_item_metadata(handle, "family", family[animal])
    ...

Per item metadata are stored in what is referred to as "overlays". It is
possible to get back the content of an overlay using the
:func:`dtoolcore.DataSet.get_overlay` method.

.. code-block:: python

    >>> animal2_dataset = DataSet.from_uri(animal2_ds_uri)
    >>> family_overlay = animal2_dataset.get_overlay("family")

The ``family_overlay`` is a Python dictonary, where they keys correspond to the
item identifiers.

    >>> for key, value in family_overlay.items():
    ...     print("{} {}".format(key, value))
    ...
    85b263904920cc18caa5630e4124f4311847e6b8 felidae
    433635d53dae167009941349491abf7aae9becbd felidae
    f480009aa5a5c43d09f40f39df7a5a3ec5f42237 equidae

The code below uses this per item metadata to only process the cats ("felidae"). 

.. code-block:: python

    >>> for i in animal2_dataset.identifiers:
    ...     if family_overlay[i] != "felidae":
    ...         continue
    ...     fpath = animal2_dataset.item_content_abspath(i)
    ...     with open(fpath, "r") as fh:
    ...         print(fh.read())
    ... 
    lion
    tiger

To add an overlay to an existing dataset one can use the
`dtoolcore.DataSet.put_overlay` method. This takes as input a dictonary where
each item has a keyed entry.


Creating a derived dataset
--------------------------

In data processing it can be useful to track the provenance of the input.  This
is most easily done by making use of the ``dtoolcore.DerivedDataSetCreator``
context manager.

.. code-block:: python

    >>> from dtoolcore import DerivedDataSetCreator

Suppose we wanted to transfor the animals from the ``animal_dataset`` into the
sounds that they make. Let's create a dictionary to help us do this.

.. code-block:: python

    >>> animal_sounds = {
    ...     "dog": "bark",
    ...     "cat": "meow",
    ...     "parrot": "squak"
    ... }
    ...

The code below creates a dataset derived from the ``animal_dataset``.

.. code-block:: python

    >>> with DerivedDataSetCreator("animal-sounds-dataset", "/tmp", animal_dataset) as ds_creator:
    ...     animal_sounds_ds_uri = ds_creator.uri
    ...     for i in animal_dataset.identifiers:
    ...         input_abspath = animal_dataset.item_content_abspath(i)
    ...         with open(input_abspath, "r") as fh:
    ...             animal = fh.read()
    ...         handle = animal_dataset.item_properties(i)["relpath"]
    ...         output_abspath = ds_creator.prepare_staging_abspath_promise(handle)
    ...         with open(output_abspath, "w") as fh:
    ...             fh.write(animal_sounds[animal])
    ...

The derived dataset has now been created and it can be loaded using the
:class:`dtoolcore.DataSet.from_uri` method.

.. code-block:: python

    >>> animal_sounds_dataset = DataSet.from_uri(animal_sounds_ds_uri)

This has been automatically annotated with ``source_dataset_name``,
``source_dataset_uuid``, and ``source_dataset_uri``.

.. code-block:: python

    >>> print(animal_sounds_dataset.get_annotation("source_dataset_name"))
    animal-dataset

The code example below looks at the data in the  ``animal-sounds-dataset``
dataset.

    >>> for i in animal_sounds_dataset.identifiers:
    ...     handle = animal_sounds_dataset.item_properties(i)["relpath"]
    ...     fpath = animal_sounds_dataset.item_content_abspath(i)
    ...     with open(fpath, "r") as fh:
    ...         content = fh.read()
    ...     print("{} - {}".format(handle, content))
    ...
    cat.txt - meow
    parrot.txt - squak
    dog.txt - bark


..  clean up

    >>> import shutil
    >>> shutil.rmtree("/tmp/animal-dataset")
    >>> shutil.rmtree("/tmp/animal-2-dataset")
    >>> shutil.rmtree("/tmp/animal-sounds-dataset")
