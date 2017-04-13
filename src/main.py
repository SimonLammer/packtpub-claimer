from threading import Timer
from packtpub import PacktpubController
import time, base64, cherrypy

class Root(object):
	def __init__(self):
		cherrypy.engine.subscribe('stop', self.stop)
		self.status = ""
		self.timer = None
		self.users = [];

	def __log(self, message):
		if self.status != "" :
			self.status += "\n"
		self.status += time.strftime('%H:%M:%S', time.localtime(time.time()))
		if self.status[-1:] != "\n" and message[0] != "\n":
			self.status += "\n"
		self.status += message

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
		packtpub_controller = PacktpubController()
		if packtpub_controller.login(email, password):
			user = {
				'email': email,	
				'password': base64.b64encode(password),
				'controller': packtpub_controller,
			}
			self.users.append(user)
			self.__log("New user registered: " + email)
			return 'registered as ' + email + '!<br><a href="/">back</a>'
		else:
			return 'Login with given credentials failed.'

	@cherrypy.expose
	def clear(self):
		self.status = ""
		return "Log cleared\n"

	@cherrypy.expose
	def claim(self):
		return self.pull() + "\n"

	def pull(self, rerun_pull = False):
		if rerun_pull:
			self.timer = Timer(8, self.pull, [True])
			self.timer.start()
		status = ""
		if len(self.users) == 0:
			status += "\n\tNo user registered"
		else:
			for user in self.users:
				if user['controller'].login(user['email'], base64.b64decode(user['password'])):
					status += "\n\tLogin as " + user['email'] + " successful."
				result = user['controller'].claim_free_ebook()
				if result == True:
					status += " - No new ebook to be claimed"
				elif result == False:
					status += " - ERROR@pull"
				else:
					status += " - New ebook claimed: " + result
		self.__log(status)
		return status

if __name__ == "__main__":
	r = Root()
	r.pull(True)
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0',
		'server.socket_port': 8080,
	})
	cherrypy.quickstart(r)
