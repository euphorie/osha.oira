BOWER 		?= node_modules/.bin/bower
BINDIR      ?= .bundle/bin
BUNDLE      ?= $(BINDIR)/bundle
# XXX: See stamp-bundler below.
# BUNDLE      ?= bundle

.PHONY: all
all:: serve
default: all

########################################################################
## Install dependencies

bundle bundle.js: build.js stamp-bower
	node_modules/.bin/r.js -o build.js

cmsbundle bundles/oira.cms.js: build-cms.js stamp-bower
	cp ../../oira.private/src/oira/private/browser/static/redactor.js redactor/
	cp ../../oira.private/src/oira/private/browser/static/redactor.css redactor/
	node_modules/.bin/r.js -o build-cms.js
	node_modules/.bin/grunt uglify
	node_modules/.bin/grunt cssmin
	cp bundles/oira.cms* ../../oira.private/src/oira/private/browser/static/
	cp redactor/redactor.min.css ../../oira.private/src/oira/private/browser/static/

stamp-npm: package.json
	npm install
	touch stamp-npm

stamp-bower: stamp-npm
	$(BOWER) install
	touch stamp-bower

stamp-bundler:
	mkdir -p $(BINDIR) && gem install --user-install bundler --bindir=$(BINDIR) --no-wrappers
	$(BUNDLE) install --path .bundle --binstubs $(BINDIR)
	touch stamp-bundler

.PHONY: clean
clean::
	rm -rf stamp-npm stamp-bower stamp-bundler node_modules src/bower_components bundles/*

.PHONY: extra-clean
extra-clean:: clean
	rm -rf ~/.cache/bower

.PHONY: check-clean
check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

########################################################################
# For development (i.e. serving files)

.PHONY: serve
serve: stamp-bower stamp-bundler
	$(BUNDLE) exec jekyll serve --watch --baseurl "" --host 0.0.0.0

