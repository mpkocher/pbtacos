.PHONY: all clean install
SHELL = /bin/bash -e

all: install

install:
	@which pip > /dev/null
	@pip freeze|grep 'pbtacos=='>/dev/null \
      && pip uninstall -y pbtacos \
      || echo -n ''
	@pip install ./

clean:
	rm -rf build/;\
	find . -name "*.egg-info" | xargs rm -rf;\
	find . -name "*.pyc" | xargs rm -f;\
	find . -name "*.err" | xargs rm -f;\
	find . -name "*.log" | xargs rm -f;\
	rm -rf dist;\
	rm -rf docs/_build

