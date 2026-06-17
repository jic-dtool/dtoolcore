# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`dtoolcore` is the dependency-free Python core API for creating and reading
**dtool datasets** — packages of data plus structural and descriptive metadata
for managing (scientific) data. It is a library only (no CLI here; the CLI lives
in separate `dtool` packages). Storage backends (disk, iRODS, Azure, S3, …) are
pluggable via setuptools entry points; this repo ships only the disk backend.

## Commands

```bash
# Run the full test suite (pytest config + coverage in pyproject.toml)
pytest

# Run a single test file / test
pytest tests/test_copy_dataset.py
pytest tests/test_copy_dataset.py::test_copy

# Lint
ruff check .
ruff check . --fix   # auto-fix

# Run tests across all supported environments (py39..py314, lint)
tox
tox -e lint          # lint only

# Install for development
pip install -e ".[test,lint]"

# Build sdist + wheel (flit_scm backend)
python -m build
```

Tests live in `tests/`, are pytest-based, and rely on shared fixtures defined in
`tests/__init__.py` (`tmp_uri_fixture`, `tmp_dir_fixture`, `chdir_fixture`,
`tmp_env_var`, etc.). Most tests are "functional": they create real datasets in
temporary directories and read them back.

## Architecture

The codebase has two layers with a deliberate separation of concerns:

1. **`dtoolcore/__init__.py`** — the storage-agnostic public API (dataset
   lifecycle, metadata orchestration). It never touches the filesystem directly.
2. **`dtoolcore/storagebroker.py`** — storage backends. All I/O happens here,
   behind the `BaseStorageBroker` interface.

These communicate through two key abstractions:

- **handle**: a Unix-style relative path identifying an item *within* a dataset.
- **identifier**: the SHA-1 hexdigest of a handle (`utils.generate_identifier`).
  Identifiers are the canonical keys used throughout the manifest and overlays.

### Dataset lifecycle: ProtoDataSet → DataSet

A dataset is built as a **`ProtoDataSet`** (writable, `type: "protodataset"`),
then **frozen** into a read-only **`DataSet`** (`type: "dataset"`). Both subclass
`_BaseDataSet`. The `freeze()` method is the pivotal transition: it generates and
persists the manifest, converts accumulated per-item metadata fragments into
overlays, flips the `type` in admin metadata, and stamps `frozen_at`.

`freeze_with_manifest(manifest, frozen_at=None)` is an alternative that freezes
using a **client-supplied** manifest (pre-computed hashes) instead of hashing
server-side. It validates that the README and every manifest item exist in
storage but trusts the provided hashes — intended for server applications.

`DataSetCreator` (and `DerivedDataSetCreator`) are context managers wrapping the
normal flow: enter → work in a staging tempdir → exit auto-freezes (unless an
exception propagated). Prefer these for new code over manual proto/freeze
handling.

Construct datasets from a URI via `DataSet.from_uri(uri)` /
`ProtoDataSet.from_uri(uri)`, which type-check the admin metadata. Top-level
helpers: `create_proto_dataset`, `create_derived_proto_dataset`, `copy`,
`copy_resume`, `iter_datasets_in_base_uri`, `iter_proto_datasets_in_base_uri`.

### Metadata model

Four distinct metadata categories — do not conflate them:

- **admin metadata** (`.dtool/dtool`): uuid, name, type, creator, timestamps.
- **README** (`README.yml`): free-form descriptive metadata; client ensures
  valid YAML. `update_readme` backs up the prior version with a timestamp suffix.
- **manifest** (`.dtool/manifest.json`): per-item structural metadata
  (size, hash, mtime, relpath), keyed by identifier. Generated at freeze.
- **overlays** (`.dtool/overlays/*.json`): per-item key/value metadata, keyed by
  identifier. On a frozen dataset, overlays must have exactly the dataset's
  identifiers as keys. Pre-freeze, use `add_item_metadata(handle, key, value)`,
  which writes fragment files that `freeze()` aggregates into overlays.
- **annotations** (`.dtool/annotations/*.json`) and **tags** (`.dtool/tags/`):
  dataset-level (not per-item) metadata.

### Storage brokers (pluggable backends)

`_get_storage_broker(uri, config_path)` parses the URI scheme and looks up the
broker registered under the `dtool.storage_brokers` entry point group (see
`pyproject.toml`). The scheme (e.g. `file`) maps to a broker's `key` attribute.

To add a backend, subclass `BaseStorageBroker` and implement its
`NotImplementedError` interface methods (`get_text`/`put_text`/`delete_key`, the
`get_*_key` methods, `iter_item_handles`, `get_size_in_bytes`/`get_utc_timestamp`/
`get_hash`, `has_admin_metadata`, `pre_freeze_hook`/`post_freeze_hook`, etc.).
The base class provides reusable JSON serialization logic on top of the
text/key primitives — most higher-level methods (`get_manifest`, `put_overlay`,
…) are already implemented in terms of `get_text`/`put_text`. `DiskStorageBroker`
(`key = "file"`) is the reference implementation; its on-disk layout is defined
by `_STRUCTURE_PARAMETERS`.

`pre_freeze_hook` is also a validation point: `DiskStorageBroker` rejects "rogue"
files in the dataset root that aren't part of the known structure.

### Cross-platform paths & URIs (`utils.py`)

URIs are central. `generous_parse_uri` turns relative paths into fully-qualified
`file://` URIs (and handles Windows drive letters); `sanitise_uri` normalizes any
input. Handles are always Unix-style; `handle_to_osrelpath` / `relpath_to_handle`
convert to/from OS-native paths. When editing path logic, preserve the
`IS_WINDOWS` branches — Windows support is a maintained feature.

### Configuration (`utils.get_config_value`)

Lookup precedence: **environment variable → JSON config file → default**. Config
file defaults to `~/.config/dtool/dtool.json`. Notable keys: `DTOOL_NUM_PROCESSES`
(parallelize manifest hashing for `file`/`symlink` brokers via multiprocessing)
and `DTOOL_STAGING_PREFIX` (staging tempdir location for `DataSetCreator`).

## Conventions

- **No runtime dependencies** — keep it that way; the dependency-free promise is
  a core feature. Version discovery uses stdlib `importlib.metadata`.
- **Python 3.9+** only (`requires-python = ">=3.9"`). CI in
  `.github/workflows/test.yml` tests 3.9–3.14. Note the one remaining version
  branch: `entry_points().select(...)` (3.10+) vs `.get(...)` (3.9) in
  `_generate_storage_broker_lookup`.
- **Build backend is `flit_scm`** (flit + setuptools_scm). The version is derived
  from git tags and written to `dtoolcore/version.py` (generated, do not edit).
  Releases are git tags; tagging triggers PyPI publish.
- **Timestamps**: `utils.timestamp()` returns seconds since the Unix epoch and
  treats naive datetimes as UTC. Pass timezone-aware UTC datetimes from new code.
- Update `CHANGELOG.rst` (keep-a-changelog format, semantic versioning) for
  user-facing changes.
- The library raises `DtoolCore*` exception subclasses (`DtoolCoreTypeError`,
  `DtoolCoreKeyError`, `DtoolCoreValueError`, `DtoolCoreInvalidNameError`,
  `DtoolCoreBrokenStagingPromise`) — use these rather than bare builtins.
