from threading import Timer
from packtpub import PacktpubController
import time, base64, json, cherrypy

config = dict();

class Root(object):
	def __init__(self):
		self.packtpub_controller = PacktpubController()
		self.status = ""

	@cherrypy.expose
	def index(self):
		return self.status + "\n"

	@cherrypy.expose
	def clear(self):
		self.status = ""
		return "Log cleared\n"

	@cherrypy.expose
	def claim(self):
		return self.pull([False]) + "\n"

	def pull(self, args):
		global config
		if args[0] == True:
			Timer(60 * 60 * 8, self.pull, [True]).start() # rerun in 8h
		status = time.strftime('%H:%M:%S', time.localtime(time.time()))
		if self.packtpub_controller.login(config['email'], base64.b64decode(config['password'])):
			status += "\n\tLogin as " + config['email'] + " successful."
		result = self.packtpub_controller.claim_free_ebook()
		if result == True:
			status += "\n\t\tNo new ebook to be claimed"
		elif result == False:
			status += "\n\t\tERROR@pull"
		else:
			status += "\n\t\tNew ebook claimed: " + result
		if self.status != "":
			self.status += "\n"
		self.status += status 
		return status

if __name__ == "__main__":
	with open('config.json') as json_data:
		config = json.load(json_data)
	r = Root()
	r.pull([True])
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0',
		'server.socket_port': 8080,
	})
	cherrypy.quickstart(r)
