BOWER 		?= node_modules/.bin/bower
BINDIR      ?= .bundle/bin
# XXX: See stamp-bundler below.
# BUNDLE      ?= $(BINDIR)/bundle
BUNDLE      ?= bundle

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
	# XXX This can be used to install bundler but doesn't work on Jenkins :(
	# mkdir -p $(BINDIR) && gem install --user-install bundler --bindir=$(BINDIR) --no-wrappers
	# $(BUNDLE) install --path .bundle --binstubs $(BINDIR)
	# Instead we now rely on Bundler being installed globally.
	$(BUNDLE) install --path .bundle --binstubs $(BINDIR)
	touch stamp-bundler

clean::
	rm -rf stamp-npm stamp-bower stamp-bundler node_modules src/bower_components bundles/*

extra-clean:: clean
	rm -rf ~/.cache/bower

check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

########################################################################
# For development (i.e. serving files)

serve: stamp-bower stamp-bundler
	bundle exec jekyll serve --watch --baseurl "" --host 0.0.0.0

.PHONY: all extra-clean clean check-clean serve
