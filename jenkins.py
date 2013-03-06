import requests
import indicate
# from indicate import Favicon
from urlparse import urlparse
# import sys
import os
import gui
from PyQt4 import QtCore
from PyQt4 import QtGui


class Jenkins(object):
    def __init__(self, indicatr):
        self.url = 'http://da115.priv.spillgroup.org:8080'
        self.icon_map = ['red', 'green', 'blue', 'grey']
        self.parent = indicatr
        self.icon_name = self.parent.favicon.get(self.url)
        self.icons = {}
        self.items = {}

        self.jenkinswindow = gui.JenkinsConfigWindow(parent=self)
        self.init_icons()
        self.parent.change_icon(self.parent.top_icon, self.icons['blue'])

        # self.loginwindow = gui.LoginWindow(parent=self)

    def init_icons(self):
        for name in self.icon_map:
            # with open(os.path.abspath('images/weather_%s.png' % name), 'rb') as f:
            #     dataBuffer = QtCore.QByteArray(f.read())
            #     print dataBuffer
            #     icn = QtGui.QIcon(pm.loadFromData(dataBuffer))
            #     print icn.availableSizes()
            self.icons[name] = QtGui.QIcon(os.path.abspath('images/weather_%s' % name))

    def set_url(self, url):
        self.url = url

    def click_link(self, link):
        os.system('open %s' % link)

    def process_item(self, item, url, img=None, long_text=None):
        if long_text is None:
            long_text = item

        if img is None:
            base_url = str(urlparse(url).netloc)
        else:
            base_url = self.icons[img]

        # if not item in self.items:
        #     self.items[item] = url
        #     self.parent.favicon.get(base_url)

        action = self.parent.add_icon_to_menu(
            base_url,
            item,
            lambda: self.click_link(self.items[item])
        )
        action.setToolTip(long_text)

    def add_refresh_btn(self):
        self.parent.add_to_menu('Renew entries', self.renew_entries)

    def renew_entries(self):
        self.parent.reset_menu()
        self.add_refresh_btn()
        self.parent.add_separator()
        self.get_projects()
        self.parent.add_separator()

        self.parent.add_quit_btn()

    def get_projects(self):
        json_url = '{0}/api/json?'.format(self.url)  # , sub, reddit_type, '10')
        posts = requests.get(json_url).json()
        for post in posts['jobs']:
            (name, url, img) = (str(post['name']), str(post['url']), str(post['color']))

            self.process_item(name, url, img)
            print post
            print


    def run(self, subreddit="python"):
        self.parent.reset_menu()
        self.get_projects()
        # self.add_subreddit('python')
        # self.add_subreddit('php')
        self.renew_entries()
        # self.get_subreddit(subreddit)
        # self.parent.add_separator()
        # self.get_subreddit('php')

        self.parent.run()


if __name__ == '__main__':
    x = indicate.Indicatr()
    # x.hide_mac_dock_icon()
    r = Jenkins(indicatr=x)
    r.run()
