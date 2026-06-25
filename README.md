# Git URL Generator

Generates a website URL for a path that's part of a repo hosted on a GitHub, BitBucket or GitLab git forge.

Supports github.com, bitbucket.org & gitlab.com by default.

Can be easily confgured to support your company's self-hosted instance.

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

## Installation

(From the root of a local clone of this repo)
```
pip install --user .
```
The directory where `pip` installs modules may need to be added to your PATH environment variable - (`pip` will report if this is the case).

**Uninstall**

```
pip uninstall giturl
```

## Configuration

The tool can be configured to support self hosted instances of one of the supported git forges.

The expected location of the configuration file depends on which OS you're using:

* **Linux**: `${XDG_CONFIG_HOME:-~/.config}/giturl/config.toml`
* **MacOS**: `$HOME/Library/Application Support/giturl/config.toml`
* **Windows**: `%APPDATA%\giturl\config.toml`

Configure your self-hosted git forge instances as follows:

```toml
[forges]
# "hostname" = "GitHub|GitLab|BitBucket"
"github.acme.corp" = "GitHub"
"gitlab.acme.corp" = "GitLab"
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

* Install using pipx.
* Add option to open the URL in the user's browser.
* Replace `-l` option with `path[:line_number]`.
