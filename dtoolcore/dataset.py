from dtoolcore.storage_broker import DiskStorageBroker

__version__ = "0.1.0"


class DataSet(object):

    @classmethod
    def from_uri(cls, uri):

        storage_broker = DiskStorageBroker(uri)

        admin_metadata = storage_broker.get_admin_metadata()

        if admin_metadata['type'] != 'dataset':
            raise TypeError("{} is not a dataset".format(uri))

        dataset = cls(
            admin_metadata=admin_metadata
        )

        dataset._storage_broker = storage_broker

        return dataset

    def __init__(self, admin_metadata, config_path=None):
        self._admin_metadata = admin_metadata
        self._storage_broker = None
        self._manifest_cache = None

    @property
    def uuid(self):
        """Return the proto dataset's UUID."""
        return self._admin_metadata["uuid"]

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

    @property
    def readme_content(self):
        return self._storage_broker.get_readme_contents()

    @property
    def name(self):
        """Return the name of the dataset."""

        return self._admin_metadata['name']

    def item_properties(self, identifier):
        """Return properties of the item with the given identifier."""

        return self._manifest["items"][identifier]

    def item_contents_abspath(self, identifier):
        """Return absolute path at which item contents can be accessed."""
        return self._storage_broker.get_item_abspath(identifier)

    def access_overlay(self, overlay_name):

        return self._storage_broker.get_overlay(overlay_name)

    def put_overlay(self, overlay_name, overlay):
        """Store the given overlay so that it is accessible by the given name.
        The overlay must be a dictionary where the keys are identifiers in the
        dataset."""

        if not isinstance(overlay, dict):
            raise TypeError("Overlay must be dict")

        if set(self.identifiers) != set(overlay.keys()):
            raise ValueError("Overlay keys must be dataset identifiers")

        self._storage_broker.store_overlay(overlay_name, overlay)
