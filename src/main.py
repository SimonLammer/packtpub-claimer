from threading import Timer
from packtpub import PacktpubController
import time, base64, json, cherrypy

config = dict();

class Root(object):
	def __init__(self):
		cherrypy.engine.subscribe('stop', self.stop)
		self.packtpub_controller = PacktpubController()
		self.status = ""
		self.timer = None

	def stop(self):
		if self.timer:
			self.timer.cancel()

	@cherrypy.expose
	def index(self):
		return """<!DOCTYPE html>
			<html>
				<head>
					<title>Packtpub Claimer</title>
				</head>
				<body>
					<form method="post" action="/register">
						<input type="email" name="email" placeholder="email" /><br />
						<input type="password" name="password" placeholder="password" /><br/>
						<input type="submit" value="Register" />
					</form>
					""" + self.status + """
				</body>
			</html>"""

	@cherrypy.expose
	def register(self, email, password):
		global config
		packtpub_controller = PacktpubController()
		if packtpub_controller.login(email, password):
			self.packtpub_controller = packtpub_controller
			config['email'] = email
			config['password'] = base64.b64encode(password)
			return 'registered as ' + email + '!<br><a href="/">back</a>'
		else:
			return 'Login with given credentials failed.'

	@cherrypy.expose
	def clear(self):
		self.status = ""
		return "Log cleared\n"

	@cherrypy.expose
	def claim(self):
		return self.pull([False]) + "\n"

	def pull(self, args):
		global config
		if args[0] == True: # rerun in 8h
			self.timer = Timer(60 * 60 * 8, self.pull, [True])
			self.timer.start()
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
