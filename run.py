import indicate
import jenkins
try:
    import esky
except:
    pass
import sys

if getattr(sys, 'frozen', False):
    try:
        app = esky.Esky(sys.executable, 'http://traypi.com/secret/')
        app.auto_update()
    except Exception as e:
        print 'Error updating!!!', e
else:
    print 'vanilla run'

x = indicate.Indicatr()
x.hide_mac_dock_icon()
r = jenkins.Jenkins(indicatr=x)
r.run()
