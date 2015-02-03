PROJECT=thunderbolt

default:
	@echo "make < docker-build | docker-run | jekyll-build | jekyll-run>"
docker-build: 
	docker build -t $(PROJECT) .

# re-uses ssh agent
# presupposes your buildout cache is in /var/tmp as configured in .buildout
# also loads your standard .bashrc
docker-run:
	docker run -i -t \
		--net=host \
		-v $(SSH_AUTH_SOCK):/tmp/auth.sock \
		-v /var/tmp:/var/tmp \
		-v $(HOME)/.bashrc:/.bashrc \
		-v $(HOME)/.gitconfig:/.gitconfig \
		-e SSH_AUTH_SOCK=/tmp/auth.sock \
		-v $(PWD):/app -w /app -u app $(PROJECT)

jekyll-build:
	mkdir -p gemfiles
	bundle install --path .bundle/gemfiles

jekyll-run:
	export LC_ALL=en_US.UTF-8
	export LANG=en_US.UTF-8
	bundle exec jekyll serve --watch --baseurl ""
