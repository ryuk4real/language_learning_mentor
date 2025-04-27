# Language Learning Mentor

## Poetry Snippets

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

### Install Poetry:

You can use pip to install it globally:

```bash
pip install poetry
```

### Add dependencies:

You can add project dependencies using the add command:

```bash
poetry add package-name
```

### Define versions and constraints:

Poetry allows you to specify package versions and constraints. For example:

```bash
peotry add package-name@^1.0
```

### Install Dependencies

```bash
poetry install
```
### Update dependencies

```bash
poetry update
```

### Run the project
```bash
poetry env use python3.11      
poetry run python language_learning_mentor/main.py
```