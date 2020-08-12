# Isotherm digitizer for NIST Adsorption Database

## Installation

```
pip install -e .[pre-commit]
pre-commit install
```

## Local testing

```
panel serve digitizer --dev digitizer/*.py
```

## Configuration

Use the following environment variables to configure the digitizer

 * `DIGITIZER_SUBMISSION_FOLDER`: Absolute path to submission folder (defaults to `./submissions`)
