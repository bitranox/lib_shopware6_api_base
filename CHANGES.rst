Changelog
=========

- new MAJOR version for incompatible API changes,
- new MINOR version for added functionality in a backwards compatible manner
- new PATCH version for backwards compatible bug fixes

v2.1.2
---------
2023-07-13:
    - require minimum python 3.8
    - remove python 3.7 tests

v2.1.1
---------
2023-07-13:
    - introduce PEP517 packaging standard
    - introduce pyproject.toml build-system
    - remove setup.cfg
    - remove setup.py
    - update black config
    - clean ./tests/test_cli.py

v2.1.0
---------
2023-06-28:
    - introduce additional header fields
    - update black config
    - remove travis config
    - remove bettercodehub config
    - do not upload .egg files to pypi.org
    - update github actions : checkout@v3 and setup-python@v4
    - remove "better code" badges
    - remove python 3.6 tests
    - adding python 3.11 tests
    - update pypy tests to 3.9

v2.0.9
---------
2022-07-04: support additional query parameters for patch, post ,put and delete requests

v2.0.8
---------
2022-07-04: allow different content-types in order to be able to upload documents as octet-stream

v2.0.7.3
---------
2022-06-30: specify correct "attr" version in requirements

v2.0.7.2
---------
2022-06-02: update to github actions checkout@v3 and setup-python@v3

v2.0.7.1
--------
2022-06-01: update github actions test matrix

v2.0.7
--------
2022-04-12: retry the request (experimental, but not harmful at all) if failed.
  - issue https://github.com/bitranox/lib_shopware6_api/issues/1
  - sometimes (seldom, after about 10 minutes connected) we got: "error code: 9, status: 401
    The resource owner or authorization server denied the request, detail: Access token could not be verified."
  - it seems to work when retry the request

v2.0.6
--------
2022-03-29: remedy mypy Untyped decorator makes function "cli_info" untyped

v2.0.5
------
2022-02-15: documentation update

v2.0.4
------
2022-02-15: documentation update

v2.0.3
------
2022-01-18: mypy type adjustments

v2.0.2
------
2022-01-09:
    - handle dal.Criteria 'ids' correctly
    - remove empty lists and dicts from dal.Criteria

v2.0.1
------
2022-01-06: correct import for dal.Criteria

v2.0.0
------
2022-01-04:
    - make it possible to pass None Values to Filters (Bug)
    - paginated request now respect limits

v1.3.2
------
2022-01-04: improve detection of the dal.Criteria Class

v1.3.1
------
2021-12-31: implement testing for python 3.6, 3.7

v1.3.0
--------
2021-12-29: add Sort, Group, Aggregations, Associations, etc ..

v1.2.0
--------
2021-12-28: add Criteria, Filters

v1.1.0
--------
2021-12-27: add Store Api DELETE/GET/GET LIST/PATCH/PUT methods

v1.0.0
--------
2021-12-26: initial release
