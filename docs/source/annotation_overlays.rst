Annotation overlays
===================

A DataSet can be augmented with additional annotation overlays. These provide extra key/value pair information for items in the DataSet. These are freeform, i.e. different data items can have different key/value pairs.

To create an overlay, first request an empty overlay:

.. code-block:: python

    >>> from dtool import DataSet
    >>> my_dataset = DataSet.from_path('my_dataset/')
    >>> my_overlay = my_dataset.empty_overlay()

At this point, ``my_overlay`` is a dictionary, the keys of which are the hashes in the dataset, and the values are empty dictionaries.

Then update the dictionaries with key/value pairs:

.. code-block:: python

    >>> item_hash = "a250369afb3eeaa96fb0df99e7755ba784dfd69c"
    >>> my_overlay[item_hash]["latitude"] = 57.4
    >>> my_overlay[item_hash]["longitude"] = 0.3

To save the overlay:

.. code-block:: python

    >>> my_dataset.persist_overlay(name="geo_locations", my_overlay)

To retrieve an item from an overlay:

.. code-block:: python

    >>> my_dataset.overlays["geo_locations"][item_hash]
    {"latitude": 57.4, "longitude": 0.3}

.. warning::

    You can only annotate DataSets that have been persisted to path.

