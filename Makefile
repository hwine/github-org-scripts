VENV_NAME=venv3

# we assume python3 available
venv3:
	python3 -m venv $@
	. $(VENV_NAME)/bin/activate && echo req*.txt | xargs -n1 pip install -r
	@echo "Virtualenv created in $(VENV_NAME). You must activate before continuing."
	false

# we assume python2 available
venv2:
	python2 -m virtualenv --python=python2.7 $@
	. $(VENV_NAME)/bin/activate && echo req*.txt | xargs -n1 pip install -r
	@echo "Virtualenv created in $(VENV_NAME). You must activate before continuing."
	false

# vim: noet ts=8
