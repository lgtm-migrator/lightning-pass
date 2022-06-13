# Lightning Pass

---

Lightning Pass is using Python, PyQt and MySQL

---

## Installation

### Install instructions

1. Install Python https://www.python.org/
2. Install Poetry https://python-poetry.org/docs/
3. Install MySQL https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/
4. Clone this repository

```sh
git clone git@github.com:kucera-lukas/lightning-pass.git
```

5. Install dependencies

```sh
poetry install
```

### Create the `.env` file

Create a `.env` file and copy the contents of `.env.example` file into the `.env` file

```sh
cp .env.example .env
```

### Initialize database

```sh
mysql -u user -e "CREATE DATABASE lightning_pass";
```

## Development

### GUI window

```sh
python ligtning_pass
```

### Tests

```sh
pytest
```

### Qt Creator

```sh
qtcreator lightning_pass/gui/static/qt_designer/*.ui
```

```sh
# generate python code from `main.ui`
pyuic5 lightning_pass/gui/static/qt_designer/main.ui -o lightning_pass/gui/static/qt_designer/output/main.py
````

### Qt Style Sheets

Both light and dark mode stylesheets are located in the [static](https://github.com/kucera-lukas/lightning-pass/tree/master/lightning_pass/gui/static) folder

## Features

*   Random password generation based on mouse movement
*   Account manager
*   Password manager
*   Secure password storage in database

## What I've learned

*   Python - Advanced decorator, descriptor and context manager usage. Gained more familiarity with standard library modules like functools or contextlib
*   PyQT - QSS files and stylesheets, QtDesigner, QtSlots - mouse tracking, QStackedWidget, QInputDialog and many more...
*   Cryptography - hashing and symmetric encryption by deriving a key from "master password"
*   SQL/MySQL - table relationships, unique keys, proper way to handle SQL injection
*   VCS and GitLab - pre-commit hooks, continuous integration, git rollbacks,...

## Preview

* [This is how loading looks like!](https://github.com/kucera-lukas/lightning-pass/blob/master/docs/loading.gif)
* [This is how password generation looks like!](https://github.com/kucera-lukas/lightning-pass/blob/master/docs/password_generator.gif)
* [This is how login looks like!](https://github.com/kucera-lukas/lightning-pass/blob/master/docs/login.gif)
* [This is how the vault looks like!](https://github.com/kucera-lukas/lightning-pass/blob/master/docs/vault.gif)

## OS Support
Tested on Linux and Windows 10

## Contributing

```sh
pre-commit install
```

## License

Developed under the [MIT](https://github.com/kucera-lukas/lightning-pass/blob/master/LICENSE) license
