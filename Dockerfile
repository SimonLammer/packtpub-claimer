FROM simonlammer/rpi-python

LABEL maintainer "Simon Lammer <lammer.simon@gmail.com>"

RUN \
	apt-get update && \
	apt-get upgrade -y && \
	\
	pip install requests && \
	pip install Flask && \
	\
	true
	#apt-get clean && \
	#rm -rf /var/lib/apt/lists/*

VOLUME ["/handlers"]
VOLUME ["/code"]
ENTRYPOINT ["/bin/entrypoint.sh"]
