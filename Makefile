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

bin/buildout: bootstrap.py
	$(PYTHON) bootstrap.py

bin/test bin/pybabel: bin/buildout buildout.cfg setup.py
	bin/buildout
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
		src > $(EUPHORIE_POT)~ && mv $(EUPHORIE_POT)~ $(EUPHORIE_POT)	

$(EUPHORIE_PO_FILES): $(EUPHORIE_POT)
	msgmerge --update -N $@ $<

.po.mo:
	msgfmt -c --statistics -o $@~ $< && mv $@~ $@

.PHONY: all clean check jenkins pot
.SUFFIXES:
.SUFFIXES: .po .mo
