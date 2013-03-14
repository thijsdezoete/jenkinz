import indicate
import jenkins
x = indicate.Indicatr()
x.hide_mac_dock_icon()
r = jenkins.Jenkins(indicatr=x)
r.run()
