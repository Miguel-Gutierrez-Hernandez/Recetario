from utils.keywords import COMMANDS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from utils.listener import listen
from utils.talk import talk

class AsistenteLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)

        self.label = Label(
            text="Pulsa el botón y habla",
            font_size='20sp',
            size_hint=(1, 0.7)
        )

        self.btn = Button(
            text="🎤 Hablar",
            font_size='24sp',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)
        )

        self.btn.bind(on_press=self.on_listen)
        self.add_widget(self.label)
        self.add_widget(self.btn)

    def on_listen(self, instance):
        self.label.text = "Escuchando..."
        self.btn.disabled = True

        command = listen()

        if not command:
            self.label.text = "No te escuché, inténtalo de nuevo"
            self.btn.disabled = False
            return

        self.label.text = f"Comando: {command}"

        for keyword, func in COMMANDS.items():
            if keyword in command:
                func(command)
                break
        else:
            talk("No entendí el comando")
            self.label.text = "No entendí el comando"

        self.btn.disabled = False


class AsistenteApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return AsistenteLayout()


if __name__ == '__main__':
    AsistenteApp().run()