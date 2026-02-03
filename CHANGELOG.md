# Changelog

- new MAJOR version for incompatible API changes
- new MINOR version for added functionality in a backwards compatible manner
- new PATCH version for backwards compatible bug fixes

## [3.0.0] - 2026-02-03

- _Describe changes here._

## v2.1.9

**2024-09-29**
- Add graalpy tests

## v2.1.8

**2024-09-29**
- Add example for `/search/order` via POST request

## v2.1.7

**2023-10-18**
- Validator for `Criteria.ids` and `Criteria.limit`
- If `Criteria.ids` are passed, set `limits` to the number of ids
- Prevent that `Criteria.limits` and `Criteria.ids` are set simultaneous
- Bump up coverage

## v2.1.6

**2023-10-18**
- Correcting "Filter Aggregation", some typos correction

## v2.1.5

**2023-10-18**
- Get rid of special pretty printer version "pprint3x" for Python 3.7 and below
- Correcting type hint for filter `ContainsFilter`

## v2.1.4

**2023-10-18**
- Correct `EqualsAnyFilter`, thanks to Patrik Hofmann for finding that bug

## v2.1.3

**2023-07-14**
- Add codeql badge
- Move 3rd_party_stubs outside the src directory to `./.3rd_party_stubs`
- Add pypy 3.10 tests
- Add Python 3.12-dev tests

## v2.1.2

**2023-07-13**
- Require minimum Python 3.8
- Remove Python 3.7 tests

## v2.1.1

**2023-07-13**
- Introduce PEP517 packaging standard
- Introduce pyproject.toml build-system
- Remove setup.cfg
- Remove setup.py
- Update black config
- Clean `./tests/test_cli.py`

## v2.1.0

**2023-06-28**
- Introduce additional header fields
- Update black config
- Remove travis config
- Remove bettercodehub config
- Do not upload .egg files to pypi.org
- Update github actions: checkout@v3 and setup-python@v4
- Remove "better code" badges
- Remove Python 3.6 tests
- Adding Python 3.11 tests
- Update pypy tests to 3.9

## v2.0.9

**2022-07-04**
- Support additional query parameters for PATCH, POST, PUT and DELETE requests

## v2.0.8

**2022-07-04**
- Allow different content-types in order to be able to upload documents as octet-stream

## v2.0.7.3

**2022-06-30**
- Specify correct "attr" version in requirements

## v2.0.7.2

**2022-06-02**
- Update to github actions checkout@v3 and setup-python@v3

## v2.0.7.1

**2022-06-01**
- Update github actions test matrix

## v2.0.7

**2022-04-12**
- Retry the request (experimental, but not harmful at all) if failed
  - Issue: https://github.com/bitranox/lib_shopware6_api/issues/1
  - Sometimes (seldom, after about 10 minutes connected) we got: "error code: 9, status: 401 - The resource owner or authorization server denied the request, detail: Access token could not be verified."
  - It seems to work when retry the request

## v2.0.6

**2022-03-29**
- Remedy mypy "Untyped decorator makes function 'cli_info' untyped"

## v2.0.5

**2022-02-15**
- Documentation update

## v2.0.4

**2022-02-15**
- Documentation update

## v2.0.3

**2022-01-18**
- mypy type adjustments

## v2.0.2

**2022-01-09**
- Handle `dal.Criteria` 'ids' correctly
- Remove empty lists and dicts from `dal.Criteria`

## v2.0.1

**2022-01-06**
- Correct import for `dal.Criteria`

## v2.0.0

**2022-01-04**
- Make it possible to pass None values to Filters (Bug fix)
- Paginated request now respect limits

## v1.3.2

**2022-01-04**
- Improve detection of the `dal.Criteria` class

## v1.3.1

**2021-12-31**
- Implement testing for Python 3.6, 3.7

## v1.3.0

**2021-12-29**
- Add Sort, Group, Aggregations, Associations, etc.

## v1.2.0

**2021-12-28**
- Add Criteria, Filters

## v1.1.0

**2021-12-27**
- Add Store API DELETE/GET/GET LIST/PATCH/PUT methods

## v1.0.0

**2021-12-26**
- Initial release
