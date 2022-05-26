# Get started

## Requirements
Python: `3.8` or higher


1. Clone this reporitory.
2. Run: `pip install -r requirements.txt`
3. Initialize configuration:
```
python3 tmetrics_wrapper/tmetrics_wrapper.py init-config --account-id <account-id> --user-token <your-token> --out-file config.json
```
4. [Define your time entires](#defining-time-entries) in separate file.
5. Run:
```
python3 tmetrics_wrapper/tmetrics_wrapper.py run --tasks-file <task-definition-file> --config-file config.json --account-id <account-id> --user-token <your-token>
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