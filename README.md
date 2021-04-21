# Lightning Pass

Lightning Pass is a GUI application build with PyQt. Passoword generation, account management and password manager are the main features of this project.

## Preview

* [This is how loading looks like!](https://gitlab.com/Lkms19/lightning-pass/-/blob/master/docs/loading.gif/)
* [This is how password generation looks like!](https://gitlab.com/Lkms19/lightning-pass/-/blob/master/docs/password_generator.gif)
* [This is how login looks like!](https://gitlab.com/Lkms19/lightning-pass/-/blob/master/docs/login.gif)
* [This is how the vault looks like!](https://gitlab.com/Lkms19/lightning-pass/-/blob/master/docs/vault.gif)

## Tech/framework used

*   Python 3.9
*   PyQt5
*   MySQL

## Features

*   Random password generation based on mouse movement
*   Account manager
*   Password manager
*   Secure password storage in database

## What I've learned

*   Python - factory for decorator factories, coroutines, contextlib, functools and strengthened knowledge in many other areas
*   PyQT - QSS files and stylesheets, QtDesigner, QtSlots - mouse tracking, QStackedWidget, QInputDialog and many more...
*   Cryptography - hashing and symmetric encryption by deriving a key from "master password"
*   SQL/MySQL - table relationships, unique keys, proper way to handle SQL injection
*   VCS and Gitlab - pre-commit hooks, continuous integration, git rollbacks,...

## Installation

*   Clone the repository
*   Run `poetry build` in the cloned folder. [Poetry](https://python-poetry.org/) for more information.
*   Add your credentiuals into the `.env` file

## How to use?

*   Head over to the location of the repo in your machine.
*   Run the lightning_pass module or the python file in the bin folder.

## License

Developed under the [MIT](https://gitlab.com/Lkms19/lightning-pass/-/blob/master/LICENSE) license.
