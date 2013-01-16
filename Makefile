YUICOMPRESS	?= yui-compressor
PYTHON		?= python2.6

CSS_PACK	= $(YUICOMPRESS) --charset utf-8 --nomunge
CSS_DIR		= src/osha/oira/browser/stylesheets
CSS_TARGETS	= $(CSS_DIR)/oira.min.css

JS_PACK		= $(YUICOMPRESS) --charset utf-8
JS_DIR		= src/osha/oira/browser/javascripts/
JS_TARGETS	= $(JS_DIR)/oira.min.js

EUPHORIE_POT	= src/osha/oira/locales/euphorie.pot
EUPHORIE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/euphorie.po)
PLONE_PO_FILES	= $(wildcard src/osha/oira/locales/*/LC_MESSAGES/plone.po)
MO_FILES	= $(EUPHORIE_PO_FILES:.po=.mo) $(PLONE_PO_FILES:.po=.mo)

TARGETS		= $(CSS_TARGETS) $(JS_TARGETS) $(MO_FILES)

all: ${TARGETS}

clean:
	-rm ${TARGETS}

bin/buildout: bootstrap.py
	$(PYTHON) bootstrap.py

bin/test: bin/buildout buildout.cfg devel.cfg setup.py
	bin/buildout -c devel.cfg
	touch bin/test

check:: bin/test $(MO_FILES)
	bin/test

jenkins: bin/test $(MO_FILES)
	bin/test --xml -s osha.oira

$(JS_DIR)/oira.min.js: $(JS_DIR)/oira.js
	set -e ; (for i in $^ ; do $(JS_PACK) $$i ; done ) > $@~ ; mv $@~ $@

pot: bin/buildout
	bin/pybabel extract -F babel.cfg \
		--copyright-holder='SYSLAB.COM GmbH' \
		--msgid-bugs-address='brand@syslab.com' \
		--charset=utf-8 \
		. > $(EUPHORIE_POT)~
	mv $(EUPHORIE_POT)~ $(EUPHORIE_POT)	

$(EUPHORIE_PO_FILES): src/osha/oira/locales/euphorie.pot
	msgmerge --update $@ $<

$(PLONE_PO_FILES): src/osha/oira/locales/plone.pot
	msgmerge --update $@ $<

$(CSS_DIR)/oira.min.css: $(CSS_DIR)/main.css 
	set -e ; (for i in $^ ; do $(CSS_PACK) $$i ; done ) > $@~ ; mv $@~ $@

.po.mo:
	msgfmt -c --statistics -o $@~ $< && mv $@~ $@

.PHONY: all clean check jenkins pot
.SUFFIXES:
.SUFFIXES: .po .mo .css .min.css
