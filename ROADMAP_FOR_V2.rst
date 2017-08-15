ROADMAP for version 2
=====================

The top level package will only have two helper function::

    from dtoolcore import dataset_from_uri, proto_dataset_from_uri

This can be used on URIs pointing at datasets on disk and in the cloud.
It will return an object that has a dataset interface. For a dataset on
disk it will return a ``dtoolcore.DataSet``.

The ``dtoolcore`` package supports plugins, so if the ``dtool_irods``
package is installed and one points the ``dataset_from_uri`` function
at an iRODS URI it will also return a ``dtoolcore.DataSet``. The differnece
between the disc and the iRODS instances will be the content of the
private property ``dtoolcore.DataSet._storage_broker``.

It is the responsibility of the ``dataset_from_uri`` to set the correct
storage broker on the dataset instance.

The same pattern and responsibilities are also true for the proto datasets.

The next step is to examine the validity of the above by writing a
DiscStorageBroker and see how differnt it is to the AzureStorageBroker.
