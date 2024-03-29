test:
	# print difference as a warning
	autopep8 -r --diff .
	flake8 --ignore=E241,E501,W504
	pytest -n 4

format:
	autopep8 -r -a -a -a --in-place .

clean:
	find . -name '__pycache__' | xargs rm -rf {1}

setup:
	pip3 install -r requirements.txt

install:
	python3 -m pip install .

docs-init:
	mkdir -p docs
	cd docs && yes y | make sphinx-quickstart
	cd docs && make html
	cd docs && sphinx-apidoc -o source ../src

docs-generate:
	cd docs && make html
	make docs-show

docs-show:
	open docs/build/html/index.html

pydocs:
	cd src && pydoc -b
