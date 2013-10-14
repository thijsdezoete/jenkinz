import jenkins
import esky
import sys


if getattr(sys, 'frozen', False):
    try:
        app = esky.Esky(sys.executable, 'http://traypi.com/secret/')
        # TODO if we're going to auto update, we better copy the config file
        app.auto_update()
    except Exception as e:
        print 'Error updating!!!', e

r = jenkins.Jenkins()
r.run()
