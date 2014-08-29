YUICOMPRESS	?= yui-compressor
PYTHON		?= python2.7

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

bin/test bin/pybabel: buildout devel.cfg setup.py
	touch bin/test
	touch bin/pybabel

check:: bin/test $(MO_FILES)
	bin/test

jenkins: bin/test $(MO_FILES)
	bin/test --xml -s osha.oira

pot: bin/pybabel
	bin/pybabel extract -F babel.cfg \
		--copyright-holder='SYSLAB.COM GmbH' \
		--msgid-bugs-address='info@syslab.com' \
		--charset=utf-8 \
		src/osha > $(EUPHORIE_POT)~ && mv $(EUPHORIE_POT)~ $(EUPHORIE_POT)	

$(EUPHORIE_PO_FILES): $(EUPHORIE_POT)
	msgmerge --update -N $@ $<

.po.mo:
	msgfmt -c --statistics -o $@~ $< && mv $@~ $@

.PHONY: all clean check jenkins pot buildout
.SUFFIXES:
.SUFFIXES: .po .mo
