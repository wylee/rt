distribution = psu.oit.rt
package = rt
egg_info = $(distribution).egg-info
sdist = dist/$(distribution)-$(version).tar.gz
upload_path = hrimfaxi:/vol/www/cdn/pypi/dist
venv = .env
venv_python ?= python3.5
version = $(shell cat VERSION)

sources = $(shell find . \
    -not -path '.' \
    -not -path '*/\.*' \
    -not -path './build' -not -path './build/*' \
    -not -path './dist' -not -path './dist/*' \
    -not -path './*\.egg-info' -not -path './*\.egg-info/*' \
    -not -path '*/__pycache__*' \
)

init: install test
reinit: clean-venv clean-install init

venv: $(venv)
$(venv):
	virtualenv -p $(venv_python) $(venv)
clean-venv:
	rm -rf $(venv)

install: venv $(egg_info)
reinstall: clean-install install
$(egg_info):
	$(venv)/bin/pip install -r requirements.txt
clean-install:
	rm -rf $(egg_info)

test: install
	$(venv)/bin/python -m unittest discover .
coverage:
	$(venv)/bin/coverage run --source $(package) -m unittest discover .  && coverage report

sdist: $(sdist)
$(sdist): $(sources)
	python setup.py sdist
clean-sdist:
	rm -f $(sdist)

upload: sdist
	scp $(sdist) $(upload_path)

clean: clean-pyc
clean-all: clean-install clean-pyc clean-sdist clean-venv
	rm -rf build dist
clean-pyc:
	find . -name __pycache__ -type d -print0 | xargs -0 rm -r

.PHONY = \
    init reinit venv install reinstall test coverage sdist upload \
    clean-venv clean-install clean-sdist \
    clean clean-all clean-pyc
