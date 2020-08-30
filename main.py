
import kivy
kivy.require('1.0.6')

import json
import subprocess
from datetime import datetime, timedelta
from glob import glob
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty
from os.path import join, dirname
from random import randint


def clean_nmap_output(nmap_output):
    output = []
    for line in nmap_output.decode().split("\n"):
        if line.startswith("MAC Address"):
            # Remove "MAC Address:" str
            line = line.split(": ")[1]
            # Remove device name
            line = line.split(" (")[0]

            output.append(line)

    return output


def get_mac_addresses():
    cmd = "sudo nmap -sn 192.168.0.0/24"
    nmap_output = subprocess.check_output(cmd.split())
    return clean_nmap_output(nmap_output)


class Picture(RelativeLayout):
    '''Picture is the class that will show the image with a white border and a
    shadow. They are nothing here because almost everything is inside the
    picture.kv. Check the rule named <Picture> inside the file, and you'll see
    how the Picture() is really constructed and used.

    The source property will be the filename to show.
    '''

    source = StringProperty(None)


class PicturesApp(App):

    # key is mac address, value is data dict containing img paths
    # and last_active flag.
    pictures = {}
    DEACTIVATE_MIN_DELAY = 1

    def check_for_device_changes(self, dt):
        nmap_output = get_mac_addresses()

        print(nmap_output)

        for mac_address, data in self.pictures.items():
            is_active = mac_address in nmap_output
            last_active = data["last_active"]

            now = datetime.now()

            if is_active:
                data["last_active"] = now
                self.update_picture(data["picture"], data["active_picture_path"])
            elif last_active:
                if last_active + timedelta(minutes=self.DEACTIVATE_MIN_DELAY) < now:
                    self.update_picture(data["picture"], data["inactive_picture_path"])

    def update_picture(self, picture, path):
        picture.source = path

    def build(self):
        # the root is created in pictures.kv
        root = self.root

        with open('data.json', 'r') as json_file:
            data = json.load(json_file)

        picture_count = len(data.keys())

        base_left = 225
        base_bottom = 250

        # get any files into pictures directory
        for index, (mac_address, data) in enumerate(data.items()):
            try:
                # load the picture
                picture = Picture(source=data["inactive_picture_path"])
                picture.pos = (base_left + (index * picture.width), base_bottom)
                # add to the main field
                root.add_widget(picture)

                data["picture"] = picture
                data["last_active"] = None
                self.pictures.update({mac_address: data})

            except Exception as e:
                Logger.exception('Pictures: Unable to load <%s>' % picture_path)

        self.check_for_device_changes(None)
        Clock.schedule_interval(self.check_for_device_changes, 10)

    def on_pause(self):
        return True


class MainContainer:
    pass


if __name__ == '__main__':
    Window.maximize()
    PicturesApp().run()
