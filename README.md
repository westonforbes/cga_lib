# Introduction
This is a package of tools used by myself, Weston Forbes, for the CG Automation Toolkit.

# Using This Package
To install this package in a project, within its venv run:
```shell
pip install git+https://github.com/westonforbes/cga_lib.git
```

# Standard Project Setup

### Virtual Environment Setup

#### Windows
```shell
python -m venv venv
venv\\Scripts\\Activate
pip install -r requirements.txt
```

#### Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Visual Studio Code Interpreter Setup
To set up the interpreter for the editor in VS Code.
1. Ctrl+Shift+P.
2. Search for `Python: Select Interpreter`.
3. Select the interpreter that points to the virtual environment.

```
\.venv\\Scripts\\python.exe (Windows)
/.venv/bin/python (Linux)
```

### Cleanup Requirements.txt

```
pip install pipreqs
pipreqs --force
```