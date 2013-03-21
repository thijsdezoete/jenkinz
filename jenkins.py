import requests
import indicate
import types

import os
import gui
from PyQt4 import QtCore
from PyQt4 import QtGui
from math import floor as math_floor
import version


class JenkinsConfig(object):
    def __init__(self, parent=None):
        self.parent = parent
        self._url_flag_read = 0
        if not self.read_last_url():
            self.url = 'http://localhost'
        self.icon_map = ['red', 'green', 'blue', 'grey', 'rain', 'default']

        self.score_map = {20: 'red', 40: 'rain', 60: 'grey', 80: 'green', 100: 'blue', 0: 'red', 'default': 'default'}
        self.reverse_score_map = {'red': 20, 'rain': 40, 'grey': 60, 'green': 80, 'blue': 100, 'default': 'default'}

        self.refresh_rate = 60
        self.micro_rate = self.calc_refresh_rate()

    def calc_refresh_rate(self):
        return self.refresh_rate * 1000

    def needs_configuration(self):
        return True if self._url_flag_read is 0 else False
    def read_last_url(self):
        try:
            with open('url.txt', 'r') as f:
                test= f.read()
            self.url = test
            self._url_flag_read = 1
            return test
        except IOError:
            return None

    def set_url(self, url):
        self.url = url
        with open('url.txt', 'w') as f:
            f.write(url)

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
        self._top_icon = 'default'
        self.parent.change_icon(self.parent.top_icon, self.icons[self._top_icon])
        QtCore.QObject.connect(self.refresh_timer, QtCore.SIGNAL("timeout()"), self.renew_entries)

    def show_config_window(self):
        self.jenkinswindow.show()
        self.jenkinswindow.raise_()

    def add_refresh_btn(self):
        self.parent.add_to_menu('Refresh now', self.renew_entries)

    def add_about_btn(self):
        self.parent.add_to_menu('Version: %s' % version.VERSION, self.renew_entries)

    def add_config_btn(self):
        self.parent.add_to_menu('Configure...', self.show_config_window)
    def _change_top(self, icon_name):
        if icon_name == self._top_icon:
            return

        self.parent.change_icon(self.parent.top_icon, self.icons[icon_name])
        self._top_icon = icon_name

    def init_icons(self):
        for name in self.config.icon_map:
            self.icons[name] = QtGui.QIcon(os.path.abspath('images/health_%s' % name))

    def set_url(self, url):
        self.config.set_url(url)

    def click_link(self, link):
        os.system('open %s' % link)

    def process_item(self, item, url, img, long_text=None):
        image = self.icons[img]
        if not long_text:
            long_text = item

        action = self.parent.add_icon_to_menu(
            image,
            item,
            lambda: self.click_link(url)
        )
        action.setToolTip(long_text)
        return action


    def dertermine_top_icon(self):
        if not self.items:
            self._change_top('default')
            return

        total = 0
        for i, item in enumerate(self.items):
            if 'default' is self.config.reverse_score_map[self.items[item]]:
                continue
            total += self.config.reverse_score_map[self.items[item]]

        end = int(math_floor(total / i))
        icon = end / 20 * 20
        self._change_top(self.config.score_map[icon])

    def renew_entries(self):
        self.parent.reset_menu()
        
        self.add_config_btn()
        self.add_about_btn()
        self.parent.add_separator()

        self.get_projects()
        self.parent.add_separator()

        self.parent.add_quit_btn()

        self.dertermine_top_icon()
        self.refresh_timer.start(self.config.get_refresh_rate())

    def round_for_map(self, number):
        _t = number / 20 * 20
        return _t

    def handle_jenkins_report(self, report, post):
        score = self.round_for_map(report['score'])
        img = self.config.score_map[score]
        url = str(post['url'])
        name = str(post['name'])

        self.items[name] = img

        descr = str(report['description'])

        return self.process_item(name, url, img, descr)

    def handle_post(self, post):
        x = [self.handle_jenkins_report(b, post) for \
                b in post['healthReport'] \
                if str(b['description']).startswith('Build stability')\
            ]
        if len(x) < 1:
            return None

        return x[0]

    def get_projects(self):
        self.items = {}
        try:
            json_url = '{0}/api/json?depth=1'.format(self.config.url)
            posts = requests.get(json_url).json()
        except Exception:
            posts = {'jobs': []}

        for post in posts['jobs']:
            self.handle_post(post)

    def run(self):
        if self.config.needs_configuration():
            self.show_config_window()
        self.parent.reset_menu()
        self.renew_entries()
        self.parent.run()


if __name__ == '__main__':
    x = indicate.Indicatr()
    x.hide_mac_dock_icon()
    r = Jenkins(indicatr=x)
    r.run()
