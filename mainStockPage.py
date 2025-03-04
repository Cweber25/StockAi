from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config
# Turn cursor back on with sudo mv /usr/share/icons/PiXflat/cursors/left_ptr.bak /usr/share/icons/PiXflat/cursors/left_ptr
Config.set('graphics', 'fullscreen', 'auto')

class HelloWorldApp(App):
    def build(self):
        return Label(text="Kill yourself", font_size='48sp')

if __name__ == '__main__':
    HelloWorldApp().run()
