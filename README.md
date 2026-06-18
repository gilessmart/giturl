# Git URL Generator

Generates a website URL for a file or folder that's part of a repo hosted on GitHub, BitBucket or GitLab.

## Usage

```
giturl [-l line_number] [-b] <path>
```

### Options

- `-l line_number`: Specify a line number to include in the URL.
- `-b`: Use the current branch name instead of the commit hash in the URL.

### Examples

1. Generate the URL for a file:
   ```sh
   $ giturl tests/test-files/example.txt
   https://github.com/gilessmart/giturl/blob/e8f4df3/test-files/example.txt
   ```

2. Generate the URL for a file with a specific line number:
   ```sh
   $ giturl -l 5 tests/test-files/example.txt
   https://github.com/gilessmart/giturl/blob/e8f4df3/test-files/example.txt#L42
   ```

3. Generate the URL for a file using the current branch name instead of the current commit hash:
   ```sh
   $ giturl -b tests/test-files/example.txt
   https://github.com/gilessmart/giturl/blob/main/test-files/example.txt
   ```

## Requirements

* Python 3

## End User Installation

(From the root of a local clone of this repo)
```
pip install --user .
```
The directory where `pip` installs modules may need to be added to your PATH environment variable - (`pip` will report if this is the case).

**Uninstall**

```
pip uninstall giturl
```

## Development Setup

* Setup Python virtual environment:
  ```sh
  python -m venv .venv
  ```
* Activate virtual environment:
  ```
  source .venv/bin/activate
  ```
  Or on Windows:  
  * Git Bash: `source .venv/Scripts/activate`  
  * Command Prompt: `.venv\Scripts\activate.bat`  
  * Powershell: `.\.venv\Scripts\Activate.ps1`
* Install module into venv:
  ```
  pip install -e ".[dev]"
  ```

### Tests

```
pytest -v
```

## Potential Enhancements

* Extract the config into a config file.
* Install using pipx.
* Add option to open the URL in the user's browser.
* If no path is supplied, produce the URL of the repository root.
* Replace `-l` option with `path[:line_number]`.
