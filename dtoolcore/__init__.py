"""API for creating and interacting with dtool datasets.

"""

import datetime
import logging
import multiprocessing as mp
import shutil
import tempfile
import uuid

from pkg_resources import iter_entry_points
from collections import defaultdict

import dtoolcore.utils


__version__ = "3.14.0"

logger = logging.getLogger(__name__)


def _get_identifier_and_item_properties(d):
    """Return identifier and item properties dict.

    This is a helper function to make it possible to generate a dataset
    manifest using in parallel using the multiprocessing module.

    :param d: tuple containing dataset and handle
    :returns: identifier and item properties as a dict
    """
    dataset, handle = d
    key = dtoolcore.utils.generate_identifier(handle)
    value = dataset._storage_broker.item_properties(handle)
    return key, value


def _generate_storage_broker_lookup():
    """Return dictionary of available storage brokers."""
    storage_broker_lookup = dict()
    for entrypoint in iter_entry_points("dtool.storage_brokers"):
        StorageBroker = entrypoint.load()
        storage_broker_lookup[StorageBroker.key] = StorageBroker
    return storage_broker_lookup


def _get_storage_broker(uri, config_path):
    """Helper function to enable use lookup of appropriate storage brokers."""
    uri = dtoolcore.utils.sanitise_uri(uri)
    storage_broker_lookup = _generate_storage_broker_lookup()
    parsed_uri = dtoolcore.utils.generous_parse_uri(uri)
    StorageBroker = storage_broker_lookup[parsed_uri.scheme]
    return StorageBroker(uri, config_path)


def _admin_metadata_from_uri(uri, config_path):
    """Helper function for getting admin metadata."""
    uri = dtoolcore.utils.sanitise_uri(uri)
    storage_broker = _get_storage_broker(uri, config_path)
    admin_metadata = storage_broker.get_admin_metadata()
    return admin_metadata


def _is_dataset(uri, config_path):
    """Helper function for determining if a URI is a dataset."""
    uri = dtoolcore.utils.sanitise_uri(uri)
    storage_broker = _get_storage_broker(uri, config_path)
    return storage_broker.has_admin_metadata()


def generate_admin_metadata(name, creator_username=None):
    """Return admin metadata as a dictionary."""

    if not dtoolcore.utils.name_is_valid(name):
        raise(DtoolCoreInvalidNameError())

    if creator_username is None:
        creator_username = dtoolcore.utils.getuser()

    datetime_obj = datetime.datetime.utcnow()

    admin_metadata = {
        "uuid": str(uuid.uuid4()),
        "dtoolcore_version": __version__,
        "name": name,
        "type": "protodataset",
        "creator_username": creator_username,
        "created_at": dtoolcore.utils.timestamp(datetime_obj)
    }
    return admin_metadata


def _generate_uri(admin_metadata, base_uri):
    """Return dataset URI.

    :param admin_metadata: dataset administrative metadata
    :param base_uri: base URI from which to derive dataset URI
    :returns: dataset URI
    """
    name = admin_metadata["name"]
    uuid = admin_metadata["uuid"]
    # storage_broker_lookup = _generate_storage_broker_lookup()
    # parse_result = urlparse(base_uri)
    # storage = parse_result.scheme
    StorageBroker = _get_storage_broker(base_uri, config_path=None)
    return StorageBroker.generate_uri(name, uuid, base_uri)


def generate_proto_dataset(admin_metadata, base_uri, config_path=None):
    """Return :class:`dtoolcore.ProtoDataSet` instance.

    :param admin_metadata: dataset administrative metadata
    :param base_uri: base URI for proto dataset
    :param config_path: path to dtool configuration file
    """
    uri = _generate_uri(admin_metadata, base_uri)
    return ProtoDataSet(uri, admin_metadata, config_path)


def create_proto_dataset(
    name,
    base_uri,
    readme_content="",
    creator_username=None
):
    """Return :class:`dtoolcore.ProtoDataSet` instance.

    :param name: dataset name
    :param base_uri: base URI for proto dataset
    :param readme_content: content of README as a string
    :param creator_username: creator username
    """
    admin_metadata = generate_admin_metadata(name, creator_username)
    proto_dataset = generate_proto_dataset(admin_metadata, base_uri)
    proto_dataset.create()
    proto_dataset.put_readme(readme_content)
    return proto_dataset


def _copy_create_proto_dataset(
    src_dataset,
    dest_base_uri,
    config_path=None,
    progressbar=None
):
    if progressbar:
        progressbar.label = "Copying dataset"

    admin_metadata = src_dataset._admin_metadata
    admin_metadata["type"] = "protodataset"
    del admin_metadata["frozen_at"]

    proto_dataset = generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=dest_base_uri,
        config_path=config_path
    )

    # Ensure that this bug does not get re-introduced:
    # https://github.com/jic-dtool/dtoolcore/issues/1
    assert proto_dataset._admin_metadata["type"] == "protodataset"
    assert "frozen_at" not in proto_dataset._admin_metadata

    proto_dataset.create()

    return proto_dataset


def _copy_content(src_dataset, dest_proto_dataset, progressbar=None):

    # When using ``dtoolcore.copy`` there should be no handles in the
    # destination proto dataset so this funciton will return an empty
    # dictionary.
    # When using ``dtoolcore.copy_resume`` there may be handles in the
    # destination proto dataset. We therefore need to get the properties
    # of the item associated with the handle so that we can use the size
    # to ensure that the item has been copied across successfully.
    def get_dest_sizes(dest_proto_dataset):
        sizes = {}
        for handle in dest_proto_dataset._storage_broker.iter_item_handles():
            identifier = dtoolcore.utils.generate_identifier(handle)
            size = dest_proto_dataset._storage_broker.get_size_in_bytes(handle)
            sizes[identifier] = size
        return sizes

    dest_sizes = get_dest_sizes(dest_proto_dataset)
    dest_identifiers = set(dest_sizes.keys())
    for identifier in src_dataset.identifiers:
        src_properties = src_dataset.item_properties(identifier)

        # We don't want to redo the copy of the item if it has already been
        # done successfully.
        if identifier in dest_identifiers:
            src_size = src_properties["size_in_bytes"]
            dest_size = dest_sizes[identifier]
            if src_size == dest_size:
                if progressbar:
                    progressbar.update(1)
                continue

        src_abspath = src_dataset.item_content_abspath(identifier)
        relpath = src_properties["relpath"]
        dest_proto_dataset.put_item(src_abspath, relpath)
        if progressbar:
            progressbar.item_show_func = lambda x: relpath
            progressbar.update(1)

    dest_proto_dataset.put_readme(src_dataset.get_readme_content())

    for overlay_name in src_dataset.list_overlay_names():
        overlay = src_dataset.get_overlay(overlay_name)
        dest_proto_dataset._put_overlay(overlay_name, overlay)

    for annotation_name in src_dataset.list_annotation_names():
        annotation = src_dataset.get_annotation(annotation_name)
        dest_proto_dataset.put_annotation(annotation_name, annotation)


def copy(src_uri, dest_base_uri, config_path=None, progressbar=None):
    """Copy a dataset to another location.

    :param src_uri: URI of dataset to be copied
    :param dest_base_uri: base of URI for copy target
    :param config_path: path to dtool configuration file
    :returns: URI of new dataset
    """
    logger.debug("Copy {} -> {}".format(src_uri, dest_base_uri))
    dataset = DataSet.from_uri(src_uri)

    proto_dataset = _copy_create_proto_dataset(
        dataset,
        dest_base_uri,
        config_path,
        progressbar
    )
    _copy_content(dataset, proto_dataset, progressbar)
    proto_dataset.freeze(progressbar=progressbar)

    return proto_dataset.uri


def copy_resume(src_uri, dest_base_uri, config_path=None, progressbar=None):
    """Resume coping a dataset to another location.

    Items that have been copied to the destination and have the same size
    as in the source dataset are skipped. All other items are copied across
    and the dataset is frozen.

    :param src_uri: URI of dataset to be copied
    :param dest_base_uri: base of URI for copy target
    :param config_path: path to dtool configuration file
    :returns: URI of new dataset
    """
    logger.debug("Copy resume {} -> {}".format(src_uri, dest_base_uri))
    dataset = DataSet.from_uri(src_uri)

    # Generate the URI of the destination proto dataset.
    dest_uri = _generate_uri(dataset._admin_metadata, dest_base_uri)

    proto_dataset = ProtoDataSet.from_uri(dest_uri)

    _copy_content(dataset, proto_dataset, progressbar)
    proto_dataset.freeze(progressbar=progressbar)

    return proto_dataset.uri


class DtoolCoreTypeError(TypeError):
    pass


class DtoolCoreKeyError(KeyError):
    pass


class DtoolCoreValueError(ValueError):
    pass


class DtoolCoreInvalidNameError(ValueError):
    pass


class _BaseDataSet(object):
    """Base class for datasets."""

    def __init__(self, uri, admin_metadata, config_path=None):

        uri = dtoolcore.utils.sanitise_uri(uri)

        self._admin_metadata = admin_metadata
        self._storage_broker = _get_storage_broker(uri, config_path)
        self._uri = uri

    @classmethod
    def _from_uri_with_typecheck(cls, uri, config_path, type_name):
        # Make sure that the URI refers to a dataset.
        if not _is_dataset(uri, config_path):
            raise(DtoolCoreTypeError("{} is not a dataset".format(uri)))

        # Get the admin metadata out of the URI and type check.
        admin_metadata = _admin_metadata_from_uri(uri, config_path)
        if admin_metadata['type'] != type_name:
            raise DtoolCoreTypeError(
                "{} is not a {}".format(uri, cls.__name__))

        # Instantiate and return.
        return cls(uri, admin_metadata, config_path)

    @property
    def base_uri(self):
        """Return the base URI of the dataset."""
        return self._storage_broker.generate_base_uri(self.uri)

    @property
    def uri(self):
        """Return the URI of the dataset."""
        return self._uri

    @property
    def uuid(self):
        """Return the UUID of the dataset."""
        return self._admin_metadata["uuid"]

    @property
    def name(self):
        """Return the name of the dataset."""
        return self._admin_metadata['name']

    def update_name(self, new_name):
        """Update the name of the proto dataset.

        :param new_name: the new name of the proto dataset
        """
        logger.debug("Update name form '{}' to '{}' {}".format(
            self.name,
            new_name,
            self
        ))

        if not dtoolcore.utils.name_is_valid(new_name):
            raise(DtoolCoreInvalidNameError())

        self._admin_metadata['name'] = new_name
        if self._storage_broker.has_admin_metadata():
            self._storage_broker.put_admin_metadata(self._admin_metadata)

    def get_readme_content(self):
        """
        Return the content of the README describing the dataset.

        :returns: content of README as a string
        """
        logger.debug("Get readme content {}".format(self))
        return self._storage_broker.get_readme_content()

    def _put_overlay(self, overlay_name, overlay):
        """Store overlay so that it is accessible by the given name.

        :param overlay_name: name of the overlay
        :param overlay: overlay must be a dictionary where the keys are
                        identifiers in the dataset
        :raises: DtoolCoreTypeError if the overlay is not a dictionary,
                 DtoolCoreValueError if identifiers in overlay and dataset do
                 not match
                 DtoolCoreInvalidNameError if the overlay name is invalid
        """
        logger.debug("Put readme content {}".format(self))

        if not dtoolcore.utils.name_is_valid(overlay_name):
            raise(DtoolCoreInvalidNameError())

        if not isinstance(overlay, dict):
            raise DtoolCoreTypeError("Overlay must be dict")

        if set(self._identifiers()) != set(overlay.keys()):
            raise DtoolCoreValueError(
                "Overlay keys must be dataset identifiers"
            )

        self._storage_broker.put_overlay(overlay_name, overlay)

    def generate_manifest(self, progressbar=None):
        """Return manifest generated from knowledge about contents."""
        logger.debug("Generate manifest {}".format(self))
        items = dict()

        if progressbar:
            progressbar.label = "Generating manifest"

        # Determine the number of processes to use when generating the
        # manifest.
        num_processes = int(dtoolcore.utils.get_config_value(
            "DTOOL_NUM_PROCESSES",
            default=1
        ))
        logging.info(
            "Using {} process(es) to generate manifest".format(
                num_processes
            )
        )

        if num_processes > 1:

            # Create pool of processes.
            pool = mp.Pool(num_processes)

            # Create data structure to pass into the processing pool.
            handles = self._storage_broker.iter_item_handles()
            to_process = [(self, h) for h in handles]

            # Process items in parallel.
            results = pool.map(_get_identifier_and_item_properties, to_process)

            # Close the processing pool.
            pool.close()

            # Create the item dictionary for the manifest.
            for key, value in results:
                items[key] = value
                if progressbar:
                    progressbar.item_show_func = lambda x: value["relpath"]
                    progressbar.update(1)

        else:
            for handle in self._storage_broker.iter_item_handles():
                key = dtoolcore.utils.generate_identifier(handle)
                value = self._storage_broker.item_properties(handle)
                items[key] = value
                if progressbar:
                    progressbar.item_show_func = lambda x: handle
                    progressbar.update(1)

        manifest = {
            "items": items,
            "dtoolcore_version": __version__,
            "hash_function": self._storage_broker.hasher.name
        }

        return manifest

    def get_annotation(self, annotation_name):
        """Return annotation.

        :param annotation_name: name of the annotation
        :raises: DtoolCoreKeyError if the annotation does not exist
        :returns: annotation
        """
        if annotation_name not in self.list_annotation_names():
            raise(DtoolCoreKeyError())
        return self._storage_broker.get_annotation(annotation_name)

    def put_annotation(self, annotation_name, annotation):
        """Store annotation so that it is accessible by the given name.

        :param annotation_name: name of the annotation
        :param annotation: JSON serialisable value or data structure
        :raises: DtoolCoreInvalidNameError if the annotation name
                 is invalid
        """
        logger.debug("Put annotation {} {}".format(annotation_name, self))
        if not dtoolcore.utils.name_is_valid(annotation_name):
            raise(DtoolCoreInvalidNameError())
        self._storage_broker.put_annotation(annotation_name, annotation)

    def list_annotation_names(self):
        """Return list of annotation names."""
        logger.debug("List annotation names {}".format(self))
        return sorted(self._storage_broker.list_annotation_names())


class DataSet(_BaseDataSet):
    """
    Class for reading the contents of a dataset.
    """

    def __init__(self, uri, admin_metadata, config_path=None):
        super(DataSet, self).__init__(uri, admin_metadata, config_path)
        self._manifest_cache = None

    def _identifiers(self):
        return self._manifest["items"].keys()

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
        """Return iterable of dataset item identifiers."""
        logger.debug("Return identifiers {}".format(self))
        return self._identifiers()

    @property
    def _manifest(self):
        """Return manifest content."""
        logger.debug("Return manifest content {}".format(self))
        if self._manifest_cache is None:
            self._manifest_cache = self._storage_broker.get_manifest()

        return self._manifest_cache

    def item_properties(self, identifier):
        """Return properties of the item with the given identifier.

        :param identifier: item identifier
        :returns: dictionary of item properties from the manifest
        """
        logger.debug("Get item properties for {} {}".format(identifier, self))
        return self._manifest["items"][identifier]

    def item_content_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        logger.debug("Get item content abspath for {} {}".format(identifier, self))  # NOQA
        return self._storage_broker.get_item_abspath(identifier)

    def list_overlay_names(self):
        """Return list of overlay names."""
        logger.debug("List overlay names {}".format(self))
        return sorted(self._storage_broker.list_overlay_names())

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        logger.debug("Get overlay {} {}".format(overlay_name, self))
        if overlay_name not in self.list_overlay_names():
            raise(DtoolCoreKeyError())
        return self._storage_broker.get_overlay(overlay_name)

    def put_overlay(self, overlay_name, overlay):
        """Store overlay so that it is accessible by the given name.

        :param overlay_name: name of the overlay
        :param overlay: overlay must be a dictionary where the keys are
                        identifiers in the dataset
        :raises: DtoolCoreTypeError if the overlay is not a dictionary,
                 DtoolCoreValueError if identifiers in overlay and dataset do
                 not match
                 DtoolCoreInvalidNameError if the overlay name is invalid
        """
        logger.debug("Put overlay {} {}".format(overlay_name, self))
        self._put_overlay(overlay_name, overlay)

    def put_readme(self, content):
        """
        Update the README of the dataset and backup the previous README.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        self._storage_broker.update_readme(content)


class ProtoDataSet(_BaseDataSet):
    """
    Class for building up a dataset.
    """

    @classmethod
    def from_uri(cls, uri, config_path=None):
        """
        Return an existing :class:`dtoolcore.ProtoDataSet` from a URI.

        :params uri: unique resource identifier where the existing
                     :class:`dtoolcore.ProtoDataSet` is stored
        :returns: :class:`dtoolcore.ProtoDataSet`
        """
        return cls._from_uri_with_typecheck(uri, config_path, "protodataset")

    def _identifiers(self):
        """Return iterable of dataset item identifiers."""
        for handle in self._storage_broker.iter_item_handles():
            yield dtoolcore.utils.generate_identifier(handle)

    def create(self):
        """Create the required directory structure and admin metadata."""
        logger.debug("Create structure and admin metadata {}".format(self))
        self._storage_broker.create_structure()
        self._storage_broker.put_admin_metadata(self._admin_metadata)

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        logger.debug("Put readme {}".format(self))
        self._storage_broker.put_readme(content)

    def put_item(self, fpath, relpath):
        """
        Put an item into the dataset.

        :param fpath: path to the item on disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        :returns: the handle given to the item
        """
        logger.debug("Put item with handle {} {}".format(relpath, self))
        return self._storage_broker.put_item(fpath, relpath)

    def add_item_metadata(self, handle, key, value):
        """
        Add metadata to a specific item in the :class:`dtoolcore.ProtoDataSet`.

        :param handle: handle representing the relative path of the item in the
                       :class:`dtoolcore.ProtoDataSet`
        :param key: metadata key
        :param value: metadata value
        """
        logger.debug("Add item metadata {} {} {}".format(handle, key, self))
        self._storage_broker.add_item_metadata(handle, key, value)

    def _generate_overlays(self):
        """Return dictionary of overlays generated from added item metadata."""
        overlays = defaultdict(dict)
        for handle in self._storage_broker.iter_item_handles():
            identifier = dtoolcore.utils.generate_identifier(handle)
            item_metadata = self._storage_broker.get_item_metadata(handle)
            for k, v in item_metadata.items():
                overlays[k][identifier] = v

        return overlays

    def freeze(self, progressbar=None):
        """
        Convert :class:`dtoolcore.ProtoDataSet` to :class:`dtoolcore.DataSet`.
        """
        logger.debug("Freeze dataset {}".format(self))
        # Call the storage broker pre_freeze hook.
        self._storage_broker.pre_freeze_hook()

        if progressbar:
            progressbar.label = "Freezing dataset"

        # Generate and persist the manifest.
        manifest = self.generate_manifest(progressbar=progressbar)
        self._storage_broker.put_manifest(manifest)

        # Generate and persist overlays from any item metadata that has been
        # added.

        overlays = self._generate_overlays()
        for overlay_name, overlay in overlays.items():
            self._put_overlay(overlay_name, overlay)

        # Change the type of the dataset from "protodataset" to "dataset" and
        # add a "frozen_at" time stamp to the administrative metadata.
        datetime_obj = datetime.datetime.utcnow()
        metadata_update = {
            "type": "dataset",
            "frozen_at": dtoolcore.utils.timestamp(datetime_obj)
        }
        self._admin_metadata.update(metadata_update)
        self._storage_broker.put_admin_metadata(self._admin_metadata)

        # Clean up using the storage broker's post freeze hook.
        self._storage_broker.post_freeze_hook()


class DataSetCreator(object):
    """Context manager for creating a dataset.

    Inside the context manager one works on a proto dataset.  When exiting the
    context manager the proto dataset is automatically frozen into a dataset,
    unless an exception has been raised in the context manager.
    """

    def __init__(
        self,
        name,
        base_uri,
        readme_content="",
        creator_username=None
    ):
        base_uri = dtoolcore.utils.sanitise_uri(base_uri)
        self.proto_dataset = create_proto_dataset(
            name=name,
            base_uri=base_uri,
            readme_content=readme_content,
            creator_username=creator_username
        )
        self._tmpdir = None

    def __enter__(self):

        tmpdir_prefix = dtoolcore.utils.get_config_value(
            "DTOOL_TMPDIR_PREFIX",
            None
        )
        if tmpdir_prefix is None:
            self._tmpdir = tempfile.mkdtemp()
        else:
            self._tmpdir = tempfile.mkdtemp(prefix=tmpdir_prefix)

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.proto_dataset.freeze()

        # Remove the staging directory.
        shutil.rmtree(self._tmpdir)

    @property
    def uri(self):
        """Return the dataset URI."""
        return self.proto_dataset.uri

    @property
    def staging_directory(self):
        """Return the staging directory.

        An ephemeral directory that only exists within the
        DataSetCreator context manger. It can be used as
        a location to write output files that need to be
        added to the dataset.

        The easiest way to add a file here is to use the
        :func:`dtoolcore.DataSetCreator.get_staging_fpath`
        method to get a path to write content to.

        If you write files directly to the staging directory
        you will need to register them using the
        :func:`dtoolcore.DataSetCreator.register_output_file`
        method.
        """
        return self._tmpdir

    def put_item(self, fpath, relpath):
        """
        Put an item into the dataset.

        :param fpath: path to the item on disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        :returns: the handle given to the item
        """
        return self.proto_dataset.put_item(fpath, relpath)
