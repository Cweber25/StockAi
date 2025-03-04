from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config

Config.set('graphics', 'fullscreen', 'auto')

class HelloWorldApp(App):
    def build(self):
        return Label(text="Hello test", font_size='48sp')

if __name__ == '__main__':
    HelloWorldApp().run()
