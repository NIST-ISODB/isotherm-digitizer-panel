# Isotherm digitizer for NIST Adsorption Database

Find the digitizer at digitizer.matscreen.com

## Installation

```
pip install -e .[pre-commit]
pre-commit install
```

## Local testing

```
panel serve digitizer --dev digitizer/*.py
```

## Deployment via docker
```
docker build . -t digitizer
docker run --name digitizer -p 5006:5006 digitizer
```

## Configuration

Use the following environment variables to configure the digitizer

 * `DIGITIZER_SUBMISSION_FOLDER`: Absolute path to submission folder (defaults to `./submissions`)
