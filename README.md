# Python repo template

This is a template for making repositories using python.
It includes some of the boilerplate we need for running tests,
and optionally for connecting to a database.

## Usage:

Either fork or just copy the content of this repo.
Once you see how the tests work, and how the fixtures are defined,
you can delete the examples and add your own code instead.

## Requirements

The `requirements.txt` file should contain all the packages that are needed to run the code.

To install requirements, (e.g., using venv):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database

We used postgres as the example database, as it is a little bit trickier to set up.
When running locally, you should set up a postgres server and have it listen on
port 5432. You should also create a database with a new name and update that name
in the `models/base.py` file.

In the .github/workflows folder, there is a file called `run-tests.yml` which sets up
the automated tests on github actions. To enable use of the database,
go in that file and uncomment the service that sets up the postgres database.

The `models` folder should have files for all the different classes that
you'd like to be mapped unto the database tables using the `sqlalchemy` library.

## tests

To run the tests, just do `pytest` in the root of the repo.
You must have a database set up first, unless you are not using this feature
(i.e., if you don't import anything to do with `models/base.py` in your code.)

The tests should run automatically on every commit.

## pre-commit hooks

To set up the precommit hooks, do:

```bash
pip install pre-commit
pre-commit install
```

From now on, each commit will be preceeded by automatic formatting and linting checks.

## License

This project is licensed under the MIT License,
which means it is distributed as open source software.
See the [LICENSE.md](LICENSE.md) file for details.

# Documentation:

For more information than fits in a README, see the [docs](docs) folder,
or check out the same content on our
[readthedocs page](https://guysawesomepythontemplate.readthedocs.io/en/latest/index.html).
