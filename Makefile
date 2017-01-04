YUICOMPRESS	?= yui-compressor
PYTHON		?= bin/python

EUPHORIE_POT	= src/osha/oira/locales/euphorie.pot
EUPHORIE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/euphorie.po)
PLONE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/plone.po)
MO_FILES	= $(EUPHORIE_PO_FILES:.po=.mo) $(PLONE_PO_FILES:.po=.mo)

TARGETS		= $(MO_FILES)

all: ${TARGETS}

clean:
	-rm ${TARGETS}

buildout: bootstrap.py
	$(PYTHON) bootstrap.py
	./bin/buildout -c devel.cfg

bin/test: buildout devel.cfg setup.py
	touch bin/test
	touch bin/pybabel

check:: bin/test $(MO_FILES)
	bin/test -t '!robot'

check-robot:: bin/test $(MO_FILES)
	bin/test -t 'robot'

jenkins: bin/test $(MO_FILES)
	bin/test --xml -s osha.oira -t '!robot'


pot: bin/pybabel
	bin/pybabel extract -F babel.cfg \
		--copyright-holder='SYSLAB.COM GmbH' \
		--msgid-bugs-address='info@syslab.com' \
		--charset=utf-8 \
		src/osha > $(EUPHORIE_POT)~
	mv $(EUPHORIE_POT)~ $(EUPHORIE_POT)
	$(MAKE) $(MFLAGS) $(EUPHORIE_PO_FILES)

$(EUPHORIE_PO_FILES): $(EUPHORIE_POT)
	msgmerge --update -N $@ $<

.po.mo:
	msgfmt -c --statistics -o $@~ $< && mv $@~ $@


########################################################################
## Setup
## You don't run these rules unless you're a prototype dev

clean-proto:
	cd prototype && make clean

prototype: ## Get the latest version of the prototype
	@if [ ! -d "prototype" ]; then \
		git clone git@github.com:euphorie/oira.prototype.git prototype; \
	else \
		cd prototype && git pull; \
	fi;

jekyll: prototype
	@echo 'DO: rm prototype/stamp-bundler to force Jekyll re-install'
	@cd prototype && make jekyll

bundle: prototype
	cd prototype && make bundle

resources-install: bundle jekyll
	cp prototype/_site/bundles/oira.js src/osha/oira/browser/resources
	cp -R prototype/_site/style/* src/osha/oira/browser/resources


.PHONY: all clean check jenkins pot buildout
.SUFFIXES:
.SUFFIXES: .po .mo
