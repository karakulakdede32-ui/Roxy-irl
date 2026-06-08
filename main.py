"""
Roxy IRL — Local chat app with Roxy's personality
No API key needed. Runs entirely offline.
"""

import os
import sys
import uuid
from datetime import datetime

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.theming import ThemeManager

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from roxy_brain import RoxyBrain
import chat_history


class ChatBubble(MDBoxLayout):
    """A single chat bubble — Roxy's or the user's."""

    def __init__(self, text, is_roxy=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(2)
        self.size_hint_x = 0.85
        self.size_hint_y = None
        self.height = dp(60)  # minimum, will grow via label
        self.md_bg_color = (
            [0.85, 0.3, 0.5, 0.15] if is_roxy else [0.2, 0.2, 0.3, 0.3]
        )
        self.radius = [dp(12), dp(12), dp(12), dp(12)]
        self.pos_hint = {"x": 0} if is_roxy else {"right": 1}

        # Name
        name = "Roxy <3" if is_roxy else "You"
        name_lbl = MDLabel(
            text=name,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1] if is_roxy else [0.6, 0.6, 0.8, 1],
            size_hint_y=None,
            height=dp(18),
            font_size=sp(11),
            halign="left" if is_roxy else "right",
        )
        self.add_widget(name_lbl)

        # Message
        halign = "left" if is_roxy else "right"
        self.msg_lbl = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.95] if is_roxy else [1, 1, 1, 0.85],
            size_hint_y=None,
            font_size=sp(15),
            halign=halign,
            valign="top",
        )
        self.msg_lbl.bind(texture_size=self._on_texture)
        self.add_widget(self.msg_lbl)

        # Timestamp
        now = datetime.now().strftime("%H:%M")
        time_lbl = MDLabel(
            text=now,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=[0.5, 0.5, 0.6, 0.6],
            size_hint_y=None,
            height=dp(14),
            font_size=sp(10),
            halign=halign,
        )
        self.add_widget(time_lbl)

    def _on_texture(self, instance, _texture_size):
        """Called when the label's texture is ready — set the bubble height."""
        if getattr(self, "_resizing", False):
            return
        self._resizing = True
        try:
            if instance.texture:
                instance.height = max(dp(24), instance.texture_size[1])
            else:
                instance.height = dp(24)
            total = sum(c.height for c in self.children if hasattr(c, "height")) + dp(24)
            self.height = max(dp(50), total)
        finally:
            self._resizing = False


class HistoryScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(16))

        header = BoxLayout(size_hint_y=0.08, spacing=dp(8))
        back_btn = MDRectangleFlatButton(
            text="\u2190 Back",
            font_size="16sp",
            size_hint_x=0.3,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        back_btn.bind(on_release=lambda x: self.app_ref.close_history())
        header.add_widget(back_btn)

        title = MDLabel(
            text="Past Chats",
            font_style="H5",
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
            halign="center",
        )
        header.add_widget(title)
        layout.add_widget(header)

        self.scroll = ScrollView(size_hint_y=0.84)
        self.list_layout = BoxLayout(
            orientation="vertical", spacing=dp(8), size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)

        del_btn = MDRectangleFlatButton(
            text="Clear All History",
            size_hint_y=0.08,
            md_bg_color=[0.3, 0.1, 0.1, 1],
            theme_text_color="Custom",
            text_color=[1, 0.5, 0.5, 1],
        )
        del_btn.bind(on_release=lambda x: self.clear_all())
        layout.add_widget(del_btn)

        self.add_widget(layout)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.list_layout.clear_widgets()
        convs = chat_history.list_conversations()
        if not convs:
            no_chats = MDLabel(
                text="No past chats yet.\nStart talking to Roxy!",
                halign="center",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.6, 0.8],
                size_hint_y=None,
                height=dp(100),
                font_size=sp(16),
            )
            self.list_layout.add_widget(no_chats)
            return

        for conv_id, preview, updated in convs[:20]:
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(60),
                padding=dp(12),
                spacing=dp(8),
                radius=[dp(8)],
                md_bg_color=[0.15, 0.15, 0.2, 1],
                elevation=0,
            )

            info = BoxLayout(orientation="vertical", spacing=dp(2))
            preview_label = MDLabel(
                text=preview if preview else "(empty)",
                theme_text_color="Custom",
                text_color=[1, 1, 1, 0.8],
                font_size=sp(14),
                size_hint_y=None,
                height=dp(24),
            )
            date_label = MDLabel(
                text=updated[:10] if updated else "",
                theme_text_color="Custom",
                text_color=[0.5, 0.5, 0.6, 0.6],
                font_size=sp(11),
                size_hint_y=None,
                height=dp(16),
            )
            info.add_widget(preview_label)
            info.add_widget(date_label)
            card.add_widget(info)

            load_btn = MDRectangleFlatButton(
                text="Load",
                size_hint_x=0.2,
                md_bg_color=[0.85, 0.3, 0.5, 0.1],
                theme_text_color="Custom",
                text_color=[0.85, 0.3, 0.5, 1],
                font_size=sp(12),
            )
            load_btn.conv_id = conv_id
            load_btn.bind(on_release=lambda x: self.load_conv(x.conv_id))
            card.add_widget(load_btn)

            self.list_layout.add_widget(card)

    def load_conv(self, conv_id):
        data = chat_history.load_conversation(conv_id)
        if data:
            self.app_ref.load_conversation(data)

    def clear_all(self):
        for conv_id, _, _ in chat_history.list_conversations():
            chat_history.delete_conversation(conv_id)
        self.refresh()


class SettingsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(20))

        title = MDLabel(
            text="Your Profile",
            font_style="H4",
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
            size_hint_y=0.1,
            halign="center",
        )
        layout.add_widget(title)

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=0.7,
            padding=[0, dp(20), 0, 0],
        )

        form.add_widget(
            MDLabel(
                text="What should I call you?",
                theme_text_color="Custom",
                text_color=[0.8, 0.8, 0.9, 1],
                font_size=sp(16),
                size_hint_y=None,
                height=dp(24),
            )
        )
        self.name_input = MDTextField(
            hint_text="Your name...",
            mode="rectangle",
            line_color_focus=[0.85, 0.3, 0.5, 1],
            size_hint_y=None,
            height=dp(50),
        )
        form.add_widget(self.name_input)

        form.add_widget(
            MDLabel(
                text="How old are you?",
                theme_text_color="Custom",
                text_color=[0.8, 0.8, 0.9, 1],
                font_size=sp(16),
                size_hint_y=None,
                height=dp(24),
            )
        )
        self.age_input = MDTextField(
            hint_text="Your age...",
            mode="rectangle",
            line_color_focus=[0.85, 0.3, 0.5, 1],
            input_filter="int",
            size_hint_y=None,
            height=dp(50),
        )
        form.add_widget(self.age_input)

        form.add_widget(
            MDLabel(
                text="What's your favorite game?",
                theme_text_color="Custom",
                text_color=[0.8, 0.8, 0.9, 1],
                font_size=sp(16),
                size_hint_y=None,
                height=dp(24),
            )
        )
        self.game_input = MDTextField(
            hint_text="Favorite game...",
            mode="rectangle",
            line_color_focus=[0.85, 0.3, 0.5, 1],
            size_hint_y=None,
            height=dp(50),
        )
        form.add_widget(self.game_input)

        layout.add_widget(form)

        btn_row = BoxLayout(size_hint_y=0.1, spacing=dp(16))
        back_btn = MDRectangleFlatButton(
            text="Back",
            font_size="16sp",
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        back_btn.bind(on_release=lambda x: self.app_ref.close_settings())
        btn_row.add_widget(back_btn)

        save_btn = MDRectangleFlatButton(
            text="Save",
            font_size="16sp",
            md_bg_color=[0.85, 0.3, 0.5, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
        )
        save_btn.bind(on_release=lambda x: self.app_ref.save_settings())
        btn_row.add_widget(save_btn)

        layout.add_widget(btn_row)
        self.add_widget(layout)

    def on_enter(self):
        brain = self.app_ref.brain
        self.name_input.text = brain.user_name if brain.user_name != "there" else ""
        self.age_input.text = brain.user_age or ""
        self.game_input.text = brain.user_fav_game or ""


class ChatScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(
            orientation="vertical", spacing=dp(4), padding=[dp(8), dp(8), dp(8), dp(8)]
        )

        # Header with plain text buttons
        header = BoxLayout(size_hint_y=0.07, spacing=dp(8))

        title = MDLabel(
            text="Roxy <3",
            font_style="H5",
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
            halign="left",
        )
        header.add_widget(title)

        settings_btn = MDRectangleFlatButton(
            text="Settings",
            font_size="12sp",
            size_hint_x=0.22,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        settings_btn.bind(on_release=lambda x: self.app_ref.open_settings())
        header.add_widget(settings_btn)

        history_btn = MDRectangleFlatButton(
            text="History",
            font_size="12sp",
            size_hint_x=0.2,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        history_btn.bind(on_release=lambda x: self.app_ref.open_history())
        header.add_widget(history_btn)

        layout.add_widget(header)

        # Chat area
        self.chat_scroll = ScrollView(
            size_hint_y=0.78, do_scroll_x=False, bar_width=dp(4)
        )
        self.chat_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            padding=[dp(4), dp(4), dp(4), dp(4)],
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))
        self.chat_scroll.add_widget(self.chat_layout)
        layout.add_widget(self.chat_scroll)

        # Input
        input_area = BoxLayout(size_hint_y=0.08, spacing=dp(6))
        self.chat_input = MDTextField(
            hint_text="Talk to Roxy...",
            mode="rectangle",
            line_color_focus=[0.85, 0.3, 0.5, 1],
            multiline=False,
            size_hint_x=0.78,
        )
        self.chat_input.bind(on_text_validate=lambda x: self.app_ref.send_message())
        input_area.add_widget(self.chat_input)

        send_btn = MDRectangleFlatButton(
            text="Send",
            font_size="15sp",
            size_hint_x=0.22,
            md_bg_color=[0.85, 0.3, 0.5, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
        )
        send_btn.bind(on_release=lambda x: self.app_ref.send_message())
        input_area.add_widget(send_btn)

        layout.add_widget(input_area)
        self.add_widget(layout)

    def add_message(self, text, is_roxy=True):
        bubble = ChatBubble(text, is_roxy=is_roxy)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, "scroll_y", 0), 0.15)


class RoxyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brain = RoxyBrain(os.path.join(APP_DIR, "config.json"))
        self.conversation_id = str(uuid.uuid4())
        self.messages = []
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.theme_style = "Dark"

    def build(self):
        self.sm = ScreenManager()

        self.chat_screen = ChatScreen(self, name="chat")
        self.settings_screen = SettingsScreen(self, name="settings")
        self.history_screen = HistoryScreen(self, name="history")

        self.sm.add_widget(self.chat_screen)
        self.sm.add_widget(self.settings_screen)
        self.sm.add_widget(self.history_screen)

        Clock.schedule_once(lambda dt: self.show_welcome(), 0.5)
        return self.sm

    def show_welcome(self):
        intro = self.brain.get_intro()
        self.chat_screen.add_message(intro, is_roxy=True)
        self.messages.append({"role": "roxy", "text": intro})

    def send_message(self):
        text = self.chat_screen.chat_input.text.strip()
        if not text:
            return

        self.chat_screen.add_message(text, is_roxy=False)
        self.messages.append({"role": "user", "text": text})
        self.chat_screen.chat_input.text = ""

        try:
            response = self.brain.get_response(text)
        except Exception:
            response = (
                "*her ears flicker* Sorry, circuits got crossed there for a sec."
                " What were you saying?"
            )

        self.chat_screen.add_message(response, is_roxy=True)
        self.messages.append({"role": "roxy", "text": response})
        chat_history.save_conversation(self.conversation_id, self.messages)

    def open_settings(self):
        self.sm.current = "settings"

    def close_settings(self):
        self.sm.current = "chat"

    def save_settings(self):
        name = self.settings_screen.name_input.text.strip()
        age = self.settings_screen.age_input.text.strip()
        game = self.settings_screen.game_input.text.strip()

        if name:
            self.brain.set_user_info("name", name)
        if age:
            self.brain.set_user_info("age", age)
        if game:
            self.brain.set_user_info("fav_game", game)

        confirm = f"Got it{', ' + name if name else ''}! I'll remember that."
        self.chat_screen.add_message(confirm, is_roxy=True)
        self.messages.append({"role": "roxy", "text": confirm})
        self.sm.current = "chat"

    def open_history(self):
        self.sm.current = "history"

    def close_history(self):
        self.sm.current = "chat"

    def load_conversation(self, data):
        self.conversation_id = data.get("id", str(uuid.uuid4()))
        self.messages = data.get("messages", [])
        self.chat_screen.chat_layout.clear_widgets()
        for msg in self.messages:
            is_roxy = msg["role"] == "roxy"
            self.chat_screen.add_message(msg["text"], is_roxy=is_roxy)
        self.sm.current = "chat"


if __name__ == "__main__":
    RoxyApp().run()
