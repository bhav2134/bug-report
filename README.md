## Bug Reporting System (BRS)

This system is designed to help users efficiently report and manage bugs or defects in various software components. This README.md file provides essential information for developers, contributors, and users to understand, contribute, and use the Bug Reporting System

## Getting Started

### Prerequisites

- Internet connection
- Web browser with network capabilities
- An email account

## Usage

### User Authentication

1. Open the BRS web form.
2. Log in with a valid username and password.

### Bug Submission

1. Click on the "Start New Bug Report" option.
2. Fill in the required details, including bug originator, type, and a short description.

### Bug Status and Priority

- Check the status and priority of a bug to understand its importance and progress.

### Graphical Representation

- View a graph illustrating the common trend of bugs found in each sprint for better sprint planning.

## Project Structure

**`/templates`** : This directory contains all the source code files of the Bug Reporting System.

* `/templates/home.html`: HTML file for the home page.
* `/templates/dashboard.html`: HTML file for the dashboard page.
* `/templates/login.html`: HTML file for the login page.
* `/templates/register.html`: HTML file for the registration page.

**`/static`** : This directory contains static assets such as stylesheets and client-side JavaScript files.

* `/static/home.css`: CSS file for styling the home page.
* `/static/dashboard.css`: CSS file for styling the dashboard page.
* `/static/login.css`: CSS file for styling the login page.
* `/static/register.css`: CSS file for styling the registration page.

**`/instance`** : This directory contains instance-specific configuration files (e.g., database configuration).

* `/instance/database.db`: SQLite3 database file.

**`/app.py`** : The app.py file is the entry point of the application, where the server is initialized, and routes are defined using Flask.

1. **`/README.md`** : The README file provides an overview of the Bug Reporting System, including installation instructions, usage guidelines, and support information.
2. **`/CONTRIBUTING.md`** : Guidelines for contributing to the Bug Reporting System.
3. **`/LICENSE`** : The license file (e.g., MIT License) specifying the terms and conditions for using the Bug Reporting System.
4. **`/tests`** : Contains test files for unit testing and integration testing.
5. **`/requirements.txt`** : File containing dependencies required for the Bug Reporting System (e.g., Flask).

We welcome contributions! Please follow the [contribution guidelines](CONTRIBUTING.md) to contribute to the Bug Reporting System.

## Contributors

Bhavdeep Arora, Hameez Iqbal, Mohammed Jama, Sarankan Srikaran, Kyle Teopiz

## License

This project is licensed under the [MIT License](LICENSE).
