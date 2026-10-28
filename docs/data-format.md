# Conference paper data format (version 1)

Each conference and year has its own UTF-8 JSON file in `data/`, for example `WWW-2026.json`. Every file uses the same top-level structure and contains exactly one conference-year object in its `collections` array.

After adding or editing a data file, run the following command from the website directory to validate the data and generate the offline assets:

```powershell
python update_data.py --sync
```

Run `python update_data.py` to validate without changing files. The script requires no third-party dependencies. Keep `index.html` and the `assets/` folder together to open the website offline.

## File structure

The top-level object contains `schema_version` (the integer `1`) and `collections` (an array containing exactly one conference-year object). Each conference-year object has these fields:

| Field | Type | Description |
| --- | --- | --- |
| `conference` | string | Uppercase conference abbreviation, such as `WWW`, `ICDE`, or `CVPR` |
| `year` | integer | Conference year; each conference and year combination must be unique |
| `name` | string | Chinese conference name |
| `scope` | string | Description of the data coverage |
| `source_url` | string | HTTP(S) URL of the source page |
| `papers` | array | Paper records for this conference and year |

Name each file `CONFERENCE-YEAR.json`, using the same conference abbreviation and year as its contents.

## Paper records

Every field below must be present; field order does not matter. Use an empty string (`""`) for missing text and an empty array (`[]`) for missing topics or links. Do not use `null` or placeholder text. Synchronization removes leading and trailing whitespace from strings.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Paper identifier, unique within the conference and year |
| `title` | string | English title |
| `title_zh` | string | Chinese title |
| `authors` | string | Display text for authors; separate multiple names with a comma and a space when possible |
| `abstract` | string | English abstract |
| `abstract_zh` | string | Chinese abstract |
| `topics` | array of strings | Chinese topic names, without duplicates |
| `kind` | string | Chinese paper type |
| `track` | string | Chinese track or more specific topic |
| `links` | array of objects | Each object contains only `label` and `url`; URLs must use HTTP(S) |
| `abstract_source` | string | Abstract source description |
| `search_extra` | string | Additional searchable keywords |

To add a conference or year, create a separate `CONFERENCE-YEAR.json` file with its single matching object in `collections`. For accurate display in English, add mappings for new conference names, topics, paper types, and link labels in `index.html`. Existing conferences and topics already have mappings.

[`papers.schema.json`](../papers.schema.json) provides a machine-readable JSON Schema. The synchronization script also checks for duplicate paper IDs within a conference year and duplicate conference-year combinations.

## Data and source files

`data/` contains the standardized paper data, split by conference and year. If the optional `原始资料归档/` directory is retained, it contains source materials and historical scripts. Historical collection scripts may use old absolute paths; check them before running.
