TRANS_FOLDER=enkel/translations
DOMAIN=default
NB_FOLDER=$(TRANS_FOLDER)/nb/LC_MESSAGES
EN_FOLDER=$(TRANS_FOLDER)/en/LC_MESSAGES
POT=$(TRANS_FOLDER)/$(DOMAIN).pot
EX_OUT=examples/out
EX_XML=examples/xml
EX_THEMES=examples/themes
RNGDATA=enkel/rngdata
LATEST_RELEASE=$(shell git tag | sort | tail -n 1)

apidoc: clean-apidoc
	epydoc --config epydoc.html.cfg -v --exclude="enkel\.scripts" \
			--exclude="enkel\.batteri\.staticcms\.cli"
clean-apidoc:
	@echo "*** remving generated api documentation"
	rm -rf apidoc/

doc:
	enkel/batteri/staticcms/cli.py -c src-docs/markup.cfg --validate --create -v
clean-doc:
	@echo "*** removing generated documentation"
	rm -rf docs/markup


example-xml: clean-example-xml
	xmllint --noout --relaxng $(RNGDATA)/admin.rng $(EX_XML)/admin.xml
	xsltproc $(EX_THEMES)/admin/html-default/admin.xsl $(EX_XML)/admin.xml > $(EX_OUT)/admin.html
clean-example-xml:
	@echo "*** removing example output"
	rm -rf examples/out/*


clean-pyc:
	@echo "*** removing *.pyc files from tree"
	rm -f `find ./ -iname "*.pyc"`
clean-setuptools:
	@echo "*** cleaning up after setuptools"
	rm -rf dist/ build/ Enkel.egg-info/
clean: clean-example-xml clean-pyc clean-apidoc clean-doc clean-setuptools


pot:
	@echo "*** updating pot-file from sources"
	xgettext -o $(POT) --keyword="N_:1" `find enkel/ -name "*.py"`

merge:
	@echo "*** merging changes is pot-file into existing po-files"
	msgmerge -U $(NB_FOLDER)/$(DOMAIN).po $(POT) --suffix=.bak
	msgmerge -U $(EN_FOLDER)/$(DOMAIN).po $(POT) --suffix=.bak

potmerge: pot merge

mo:
	@echo "*** compiling po-files to *.mo"
	msgfmt -o $(NB_FOLDER)/$(DOMAIN).mo $(NB_FOLDER)/$(DOMAIN).po
	msgfmt -o $(EN_FOLDER)/$(DOMAIN).mo $(EN_FOLDER)/$(DOMAIN).po


dist:
	@echo "*** creating latest release: $(LATEST_RELEASE)"
	git archive --format=tar --prefix=enkel-$(LATEST_RELEASE)/ $(LATEST_RELEASE) \
	| gzip > install/enkel-$(LATEST_RELEASE).tar.gz

head:
	@echo "*** creating latest release: HEAD"
	git archive --format=tar --prefix=enkel-head/ HEAD \
	| gzip > install/enkel-head.tar.gz
