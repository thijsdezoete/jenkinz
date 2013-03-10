import requests
import indicate

import os
import gui
from PyQt4 import QtCore
from PyQt4 import QtGui
from math import floor as math_floor


class JenkinsConfig(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.url = 'http://da115.priv.spillgroup.org:8080'
        self.icon_map = ['red', 'green', 'blue', 'grey']
        self.icon_happy_map = {'red': 1, 'grey': 2, 'green': 3, 'blue': 4}
        self.mapped_states = {'blue_anime': 'blue', 'red_anime': 'red'}
        self.refresh_rate = 15
        self.micro_rate = self.calc_refresh_rate()

    def calc_refresh_rate(self):
        return self.refresh_rate * 1000

    def set_url(self, url):
        self.url = url

    def set_refresh_rate(self, rate):
        self.refresh_rate = int(rate)
        self.micro_rate = self.calc_refresh_rate()

    def get_refresh_rate(self):
        return self.micro_rate

    def refresh_now(self):
        self.parent.renew_entries()


class Jenkins(object):
    def __init__(self, indicatr):
        self.config = JenkinsConfig(parent=self)

        self.parent = indicatr
        self.icon_name = self.parent.favicon.get(self.config.url)
        self.icons = {}
        self.items = {}

        self.jenkinswindow = gui.JenkinsConfigWindow(parent=self.config)
        self.init_icons()
        self.refresh_timer = QtCore.QTimer()
        self._top_icon = 'blue'
        self.parent.change_icon(self.parent.top_icon, self.icons[self._top_icon])
        QtCore.QObject.connect(self.refresh_timer, QtCore.SIGNAL("timeout()"), self.renew_entries)

    def _change_top(self, icon_name):
        if icon_name == self._top_icon:
            return

        self.parent.change_icon(self.parent.top_icon, self.icons[icon_name])
        self._top_icon = icon_name

    def init_icons(self):
        for name in self.config.icon_map:
            self.icons[name] = QtGui.QIcon(os.path.abspath('images/weather_%s' % name))

    def set_url(self, url):
        self.config.set_url(url)

    def click_link(self, link):
        os.system('open %s' % link)

    def process_item(self, item, url, img):
        image = self.icons[img]

        self.parent.add_icon_to_menu(
            image,
            item,
            lambda: self.click_link(url)
        )

    def show_config_window(self):
        self.jenkinswindow.show()

    def add_refresh_btn(self):
        self.parent.add_to_menu('Refresh now', self.renew_entries)

    def add_config_btn(self):
        self.parent.add_to_menu('Configure...', self.show_config_window)

    def dertermine_top_icon(self):
        self._happiness = 0
        total = 0
        for i, item in enumerate(self.items):
            total += self.config.icon_happy_map[self.items[item]]

        end = int(math_floor(total / i))
        icon = [key for key, val in self.config.icon_happy_map.iteritems() if val == end][0]

        self._change_top(icon)

    def renew_entries(self):
        self.parent.reset_menu()
        self.add_config_btn()
        # self.add_refresh_btn()
        self.parent.add_separator()
        self.get_projects()
        self.parent.add_separator()

        self.parent.add_quit_btn()
        self.dertermine_top_icon()

        self.refresh_timer.start(self.config.get_refresh_rate())

    def get_projects(self):
        self.items = {}
        json_url = '{0}/api/json?'.format(self.config.url)
        posts = requests.get(json_url).json()
        for post in posts['jobs']:
            (name, url, img) = (str(post['name']), str(post['url']), str(post['color']))
            if img in self.config.mapped_states:
                name = name + ' - BUILDING'
                img = self.config.mapped_states[img]
            self.items[name] = img

            self.process_item(name, url, img)

    def run(self):
        self.parent.reset_menu()
        self.renew_entries()
        self.parent.run()


if __name__ == '__main__':
    x = indicate.Indicatr()
    x.hide_mac_dock_icon()
    r = Jenkins(indicatr=x)
    r.run()
