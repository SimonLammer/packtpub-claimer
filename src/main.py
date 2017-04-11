from threading import Timer
import time, cherrypy

pulltime = time.time()

class Root(object):
	@cherrypy.expose
	def index(self):
		global pulltime
		print "route: /"
		return "Hello World!" + time.strftime('%H:%M:%S', time.localtime(pulltime))

	@cherrypy.expose
	def pull(self):
		global pulltime
		pulltime = time.time()
		print "pulled"
		Timer(10, self.pull, ()).start()

if __name__ == "__main__":
	r = Root()
	r.pull()
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0',
		'server.socket_port': 80,
	})
	cherrypy.quickstart(r)
