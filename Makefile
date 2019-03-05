EUPHORIE_POT	= src/osha/oira/locales/euphorie.pot
EUPHORIE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/euphorie.po)
PLONE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/plone.po)
MO_FILES	= $(EUPHORIE_PO_FILES:.po=.mo) $(PLONE_PO_FILES:.po=.mo)

TARGETS		= $(MO_FILES)

all: ${TARGETS}

clean:
	-rm ${TARGETS}

bin/buildout: bootstrap.py
	virtualenv -p python2.7 --clear --no-site-packages .
	bin/pip install -r requirements.txt

bin/i18ndude bin/test bin/sphinx-build: bin/buildout buildout.cfg versions.cfg devel.cfg setup.py
	bin/buildout -c devel.cfg -t 10
	touch bin/i18ndude
	touch bin/sphinx-build
	touch bin/test


check:: bin/test $(MO_FILES)
	bin/test -t '!robot'

check-robot:: bin/test $(MO_FILES)
	bin/test -t 'robot'

jenkins: bin/test $(MO_FILES)
	bin/test --xml -s osha.oira -t '!robot'


pot: bin/i18ndude
	i18ndude rebuild-pot --exclude="generated prototype examples" --pot $(EUPHORIE_POT) src/osha/oira --merge src/Euphorie/src/euphorie/deployment/locales/euphorie.pot --create euphorie
	$(MAKE) $(MFLAGS) $(EUPHORIE_PO_FILES)

$(EUPHORIE_PO_FILES): src/osha/oira/locales/euphorie.pot
	msgmerge --update -N --lang `echo $@ | awk -F"/" '{print ""$$5}'` $@ $<



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
	@cd prototype && make osha

bundle: prototype
	cd prototype && make bundle

resources-install: bundle jekyll
	cp prototype/_site/bundles/bundle.js src/osha/oira/browser/resources/oira.js
	cp -R prototype/_site/style/* src/osha/oira/browser/resources


.PHONY: all clean check jenkins pot buildout
.SUFFIXES:
.SUFFIXES: .po .mo
