from ubuntu:14.04
maintainer guido.stevens@cosent.net
run apt-get update
run apt-get install -y make git-core ruby ruby-dev nodejs jed
run locale-gen en_US.UTF-8
run gem install bundler
run useradd -m -d /app app
run echo thunderbolt > /etc/debian_chroot
cmd ["/bin/bash"]
