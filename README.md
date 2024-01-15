# CSV to JSON API Import Helper

## Installation

* Requires `python` version 3
* Requires `poetry` to install dependencies
* Clone the repository and run the following steps

```shell
poetry install
poetry run csv-to-json-api-import --help
```

or

```shell
poetry install
poetry shell
csv-to-json-api-import --help
```

## How to run

```shell
csv-to-json-api-import migrate-projects [OPTIONS] SNYK_TOKEN GROUP_ID SOURCE_ORG --csv-path=./path/to/file.csv
```
