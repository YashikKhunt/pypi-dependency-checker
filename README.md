# pypi-dependency-checker

Checks every pinned line of a requirements file against the [PyPI JSON API](https://docs.pypi.org/api/json/) and reports:

1. **Dependencies checked** – number of dependency lines
2. **Packages not on PyPI** – the package name does not exist
3. **Versions not on PyPI** – the package exists, but the pinned version does not
4. **Oldest pinned release** – among valid pins, the oldest release (by `upload_time` of its first file)

Uses only the Python standard library (`urllib`, `json`), so no installation is needed.

## Usage

```bash
python3 check_pypi.py req.txt              # one file
python3 check_pypi.py req.txt task2.txt    # several files
python3 check_pypi.py                      # defaults to requirements.txt
```

## Example

```
$ python3 check_pypi.py req.txt
Dependencies checked: 5
Packages not on PyPI: requessts, huggingface-cli
Versions not on PyPI: flask==1.3.0
Oldest pinned release: numpy == 1.16.0 (2019)
```
