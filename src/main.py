from threading import Timer
from packtpub import PacktpubController
import time, base64, cherrypy

class Root(object):
	def __init__(self, pull_delay):
		cherrypy.engine.subscribe('stop', self.stop)
		self.status = ""
		self.timer = None
		self.users = [];
		self.next_pull_time = 0
		self.pull_delay = pull_delay

	def __format_time(self, time_ = None):
		if time_ == None:
			time_ = time.time()
		res = ""
		if time_ < 0:
			res += "-"
			time_ = -time_
		res += time.strftime('%H:%M:%S', time.localtime(time_))	
		return res

	def __log(self, message):
		if self.status != "" :
			self.status += "\n"
		self.status += self.__format_time()
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
					<h1>Current time: """ + self.__format_time() + """</h1>
					<h2>Time until next pull: """ + self.__format_time(self.next_pull_time - time.time()) + """</h2>
				</body>
			</html>"""

	@cherrypy.expose
	def registered(self):
		return '\n'.join(user['email'] for user in self.users)

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
			is_new_user = True
			users_file = open("users.txt", "r")
			for username in users_file.readlines():
				if username == user['email']:
					is_new_user = False
					break
			users_file.close()
			if is_new_user:
				users_file = open("users.txt", "a")
				users_file.write(user['email'])
				users_file.close()
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
			self.next_pull_time = time.time() + self.pull_delay
			self.timer = Timer(self.pull_delay, self.pull, [True])
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
	r = Root(60 * 60 * 8) # pull every 8h
	r.pull(True)
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0',
		'server.socket_port': 8080,
	})
	cherrypy.quickstart(r)
