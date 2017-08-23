from dtoolcore.storage_broker import DiskStorageBroker

__version__ = "0.1.0"


def _get_storage_broker(uri, config_path):
    """Helper function to enable use lookup of appropriate storage brokers."""
    return DiskStorageBroker(uri, config_path)


def _admin_metadata_from_uri(uri, config_path):
    """Helper function for getting admin metadata."""
    storage_broker = _get_storage_broker(uri, config_path)
    admin_metadata = storage_broker.get_admin_metadata()
    return admin_metadata


class _BaseDataSet(object):
    """Base class for datasets."""

    def __init__(self, uri, admin_metadata, config_path=None):
        self._admin_metadata = admin_metadata
        self._storage_broker = _get_storage_broker(uri, config_path)

    @classmethod
    def _from_uri_with_typecheck(cls, uri, config_path, type_name):
        # Get the admin metadata out of the URI and type check.
        admin_metadata = _admin_metadata_from_uri(uri, config_path)
        if admin_metadata['type'] != type_name:
            raise TypeError("{} is not a {}".format(uri, cls.__name__))

        # Instantiate and return.
        return cls(uri, admin_metadata, config_path)

    @property
    def uuid(self):
        """Return the UUID of the dataset."""
        return self._admin_metadata["uuid"]

    @property
    def name(self):
        """Return the name of the dataset."""
        return self._admin_metadata['name']

    def get_readme_content(self):
        """
        Return the content of the README describing the dataset.

        :returns: content of README as a string
        """
        return self._storage_broker.get_readme_content()

    def put_overlay(self, overlay_name, overlay):
        """Store overlay so that it is accessible by the given name.

        :param overlay_name: name of the overlay
        :param overlay: overlay must be a dictionary where the keys are
                        identifiers in the dataset
        :raises: TypeError if the overlay is not a dictionary,
                 ValueError if identifiers in overlay and dataset do not match
        """
        if not isinstance(overlay, dict):
            raise TypeError("Overlay must be dict")

        if set(self.identifiers) != set(overlay.keys()):
            raise ValueError("Overlay keys must be dataset identifiers")

        self._storage_broker.put_overlay(overlay_name, overlay)


class DataSet(_BaseDataSet):
    """
    Class for reading the contents of a dataset.
    """

    def __init__(self, uri, admin_metadata, config_path=None):
        super(DataSet, self).__init__(uri, admin_metadata, config_path)
        self._manifest_cache = None

    @classmethod
    def from_uri(cls, uri, config_path=None):
        """
        Return an existing :class:`dtoolcore.DataSet` from a URI.

        :params uri: unique resource identifier where the existing
                     :class:`dtoolcore.DataSet` is stored
        :returns: :class:`dtoolcore.DataSet`
        """
        return cls._from_uri_with_typecheck(uri, config_path, "dataset")

    @property
    def identifiers(self):
        """Return list of dataset item identifiers."""
        return self._manifest["items"].keys()

    @property
    def _manifest(self):
        """Return manifest content."""
        if self._manifest_cache is None:
            self._manifest_cache = self._storage_broker.get_manifest()

        return self._manifest_cache

    def item_properties(self, identifier):
        """Return properties of the item with the given identifier.

        :param identifier: item identifier
        :returns: dictionary of item properties from the manifest
        """
        return self._manifest["items"][identifier]

    def item_content_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        return self._storage_broker.get_item_abspath(identifier)

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        return self._storage_broker.get_overlay(overlay_name)
