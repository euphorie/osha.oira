EUPHORIE_POT	= src/osha/oira/locales/euphorie.pot
EUPHORIE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/euphorie.po)
PLONE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/plone.po)
MO_FILES	= $(EUPHORIE_PO_FILES:.po=.mo) $(PLONE_PO_FILES:.po=.mo)

TARGETS		= $(MO_FILES)

all: ${TARGETS}

clean:
	-rm ${TARGETS}

bin/buildout:
	python3.8 -m venv .
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
	i18ndude rebuild-pot --exclude="generated prototype examples" --pot $(EUPHORIE_POT) src/osha/oira --create euphorie
	$(MAKE) $(MFLAGS) $(EUPHORIE_PO_FILES)

$(EUPHORIE_PO_FILES): src/osha/oira/locales/euphorie.pot
	msgmerge --update -N --lang `echo $@ | awk -F"/" '{print ""$$5}'` $@ $<



.PHONY: all clean check jenkins pot buildout
.SUFFIXES:
.SUFFIXES: .po .mo
