FROM simonlammer/rpi-python

LABEL maintainer "Simon Lammer <lammer.simon@gmail.com>"

RUN \
	apt-get update && \
	apt-get upgrade -y && \
	\
	pip install requests && \
	pip install cherrypy && \
	\
	true
	#apt-get clean && \
	#rm -rf /var/lib/apt/lists/*

RUN \
	apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev && \
	pip install lxml

VOLUME ["/handlers"]
VOLUME ["/code"]
ENTRYPOINT ["/bin/entrypoint.sh"]
