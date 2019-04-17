It's a Flask boilerplate for REST API projects. Works with [Flassger](https://github.com/rochacbruno/flasgger) and [SQLAlchemy](https://www.sqlalchemy.org/) from scratch.

## Getting started
Read prerequisites and installation guides, clone this project and perform all steps one by one.

### Basic requirements

- Python >= 3.63
- Editorconfig for your code editor
- python-venv module for creating virtual environments
- PostgreSQL >= 10.5
- NodeJS 10.x, npm and pm2

## Code style and contribution guide
- Install the [editorconfig](http://editorconfig.org/) plugin for your code editor.
- Do not copypaste, do not hack, always look for easiest solutions.
- Write tests for your code.
- For every task create a branch from current `develop`, when ready create a merge request back to `develop`.
- Prefer small commits and branches.

### Additional commands

To see additional commands run `flask` in project root directory.

### Helpful
Check Python code lines:
- `find dir_path/ -name "*.py" -type f -exec cat {} + | wc -l`

Check code coverage by tests (coverage must be installed):
- `coverage run --source apps/ -m unittest discover -s tests/`
- `coverage report -m`

