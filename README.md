# SCOAP3

**WIP version of SCOAP3**


Current live version available at: [www.scoap3.org](www.scoap3.org)

SCOAP3 is a one-of-its-kind partnership of over three-thousand libraries, key funding agencies and research centers in 43 countries and 3 intergovernmental organizations. Working with leading publishers, SCOAP3 has converted key journals in the field of high-energy physics to open access at no cost for authors. SCOAP3 centrally pays publishers for costs involved in providing their services, publishers, in turn, reduce subscription fees to all their customers, who can redirect these funds to contribute to SCOAP3. Each country contributes in a way commensurate to its scientific output in the field. In addition, existing open access journals are also centrally supported, removing any existing financial barrier for authors.

SCOAP3 journals are open for any scientist to publish without any financial barriers. Copyright stays with authors, and a permissive CC-BY license allows text- and data-mining. SCOAP3 addresses open access mandates at no burden for authors. All articles appear in the SCOAP3 repository for further distribution, as well as being open access on publishers’ websites.

License: MIT

---

## Pre requirements

### Python

Python `3.11`

You can also use [pyenv](https://github.com/pyenv/pyenv) for your python installations.
Simply follow the [instructions](https://github.com/pyenv/pyenv#installation) and set the global version to 3.8.

### poetry

install `poetry` https://poetry.eustace.io/docs/

```bash
$ curl -sSL https://install.python-poetry.org | python3 - --version 1.1.14
```

### pre-commit

install `pre-commit` https://pre-commit.com/

```bash
$ curl https://pre-commit.com/install-local.py | python -
```

And run

```bash
$ pre-commit install
```

### Docker & Docker Compose

Follow the guide https://docs.docker.com/compose/install/

---

## Run with docker

### Start
```bash
$ docker-compose up
```

### Usage

After startup, the application should be avaiable at [localhost:3000](localhost:3000)

---

## How to test

### Docker
```bash
$ docker-compose run --rm django pytest
```
### Local
For running the tests you only need the django, db, redis and mq service.
You can start only the needed services using
```bash
$ docker-compose run django
```
To run the tests, use:
```bash
$ poetry run pytest
```
