from flask import Flask
from threading import Timer
import time

app = Flask(__name__)
pulltime = time.time()

@app.route("/")
def main():
	global pulltime
	print "route: /"
	return "Hello World!" + time.strftime('%H:%M:%S', time.localtime(pulltime))

def pull():
	global pulltime
	pulltime = time.time()
	print "pulled"
	Timer(10, pull, ()).start()

if __name__ == "__main__":
	pull()
	app.run()
