
## Requirements
- python: `3.10` or higher
- poetry: `1.8.0` or higher

---
## Getting started
1. Clone this reporitory.
2. Run: `poetry install`
3. Generate API key:
- Log in to TMetrics
- Click your name in the right top corner.
- Select My Profile in the drop-down list.
- On the My Profile page, click the Get new API token link.
- Copy the newly created token.

    _Note_: An API token will be valid for 1 year. If you generate a new token, the previous one becomes invalid.
4. Get TMetrics account id:

    Account ID can be found in TMetrics url, ex: https://app.tmetric.com/#/tracker/12345/ <br>
    Account ID of this workspace is **12345**

5. Initialize configuration:
```
poetry run tmetrics-wrapper init-config --account-id <account-id> --user-token <your-token> --out-file config.json
```
6. [Define your time entires](#defining-time-entries) in separate file.
7. Run:
```
poetry run tmetrics-wrapper run --tasks-file <task-definition-file> --config-file config.json --account-id <account-id> --user-token <your-token>
```

All cli commands support `--help` flag.

---

## Defining time entries
### Time entry definition format:
```
dd.mm.YYYY-dd.mm.YYYY
<task-duration(HH:MM)>|<note>|<project-key or alias>|<split into X time entries (default 1)>
<next-task>
<next-task>
---
dd.mm.YYYY-dd.mm.YYYY
<next-task>
...
```

### Example

Example config:
```
{
    "projects": {
            "Foo/Abc": {
                "id": 123,
                "alias": "foo"
        },
            "Bar/Xyz": {
                "id": 4567,
                "alias": "bar"
        },
            "FooBar/Alpha": {
                "id": 456987,
                "alias": "foo-bar"
        }
    }
}
```
Example time entries definiton:
```
12.07.2021-16.07.2021
2|Abc Meeting|Foo/Abc
5:20|Some Meeting|FooBar/Alpha|2
26|Some feature|Bar/Xyz
3|Code review|$bar|3
2:25|Code review|$foo-bar|5
```

Time entries will be scattered in between 12.07.2021(Mon) and 16.07.2021(Fri) (5 days)

- `2|Abc Meeting|Foo/Abc` will generate 1 time entry lasting `2` hours, with `Abc Meeting` note in Foo/Abc project.

- `5:20|Some Meeting|FooBar/Alpha|2` translates into `2` time entries lasting `5:20/2 = 2:40`, with `Some Meeting` note in `FooBar/Alpha` project

- `26|Some feature|Bar/Xyz` due to `26` hours cannot be a single time entry, so it will be split into `5` (daily) time entries lasting `26/5 = 5:12` with `Some feature` note in `Bar/Xyz` project.

- `3|Code review|$bar|3`: `3` time entires lasting `3/3 = 1` hour with `Code review` note in `Bar/Xyz` project.

- `2:25|Code review|$foo-bar|5`: `5` time entries lasting `29min` with `Code review` note in `FooBar/Alpha` project.
