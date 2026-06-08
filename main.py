"""
Roxy IRL — Local chat app with Roxy's personality
No API key needed. Runs entirely offline.
"""

import os
import sys
import uuid
import traceback
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.theming import ThemeManager

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from roxy_brain import RoxyBrain
import chat_history
from app_logger import logger, get_log_content


class ChatBubble(BoxLayout):
    """A single message bubble — pure Kivy for stability."""

    def __init__(self, text, is_roxy=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.size_hint_x = 0.88
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(2)

        # Background canvas
        bg_color = (
            [0.85, 0.3, 0.5, 0.15] if is_roxy else [0.2, 0.2, 0.3, 0.3]
        )
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(8)]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Alignment
        if is_roxy:
            self.pos_hint = {"x": 0}
        else:
            self.pos_hint = {"right": 1}

        # Name tag
        name_text = "Roxy <3" if is_roxy else "You"
        name_lbl = Label(
            text=name_text,
            size_hint_y=None,
            height=dp(18),
            font_size=sp(11),
            halign="left" if is_roxy else "right",
            color=[0.85, 0.3, 0.5, 1] if is_roxy else [0.7, 0.7, 0.9, 1],
        )
        self.add_widget(name_lbl)

        # Message text - the key: let Kivy size it via texture_size
        msg_color = (1, 1, 1, 0.92) if is_roxy else (1, 1, 1, 0.82)
        self.msg_lbl = Label(
            text=text,
            size_hint_y=None,
            height=dp(24),
            font_size=sp(15),
            halign="left" if is_roxy else "right",
            valign="top",
            color=msg_color,
            text_size=(None, None),  # no wrapping bound
        )
        self.msg_lbl.bind(texture_size=lambda inst, val: self._resize(inst))
        self.add_widget(self.msg_lbl)

        # Timestamp
        time_text = datetime.now().strftime("%H:%M")
        time_lbl = Label(
            text=time_text,
            size_hint_y=None,
            height=dp(14),
            font_size=sp(10),
            halign="left" if is_roxy else "right",
            color=[0.5, 0.5, 0.6, 0.6],
        )
        self.add_widget(time_lbl)

        # Set initial height to prevent 0-height issues
        self.height = dp(60)
        # Schedule a proper height calc after layout
        Clock.schedule_once(lambda dt: self._calc_height(), 0.05)

    def _resize(self, instance):
        """Set label height to match its text content."""
        try:
            if instance.texture:
                h = max(dp(20), instance.texture_size[1])
                instance.height = h
                self._calc_height()
        except Exception:
            pass

    def _calc_height(self):
        """Sum children heights for total bubble height."""
        try:
            total = sum(
                c.height for c in self.children if hasattr(c, "height") and c.height
            )
            self.height = max(dp(50), total + dp(24))
        except Exception:
            self.height = dp(80)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


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
            size_hint_y=0.6,
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

        # Log viewer button
        log_btn = MDRectangleFlatButton(
            text="View Debug Log",
            size_hint_y=0.08,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.6, 0.6, 0.8, 1],
        )
        log_btn.bind(on_release=lambda x: self.app_ref.show_log())
        layout.add_widget(log_btn)

        models_btn = MDRectangleFlatButton(
            text="AI Models",
            size_hint_y=0.08,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        models_btn.bind(on_release=lambda x: self.app_ref.open_models())
        layout.add_widget(models_btn)

        self.add_widget(layout)

    def on_enter(self):
        brain = self.app_ref.brain
        self.name_input.text = brain.user_name if brain.user_name != "there" else ""
        self.age_input.text = brain.user_age or ""
        self.game_input.text = brain.user_fav_game or ""


class LogScreen(Screen):
    """Simple screen showing the last 100 lines of the log."""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        header = BoxLayout(size_hint_y=0.08, spacing=dp(8))
        back_btn = MDRectangleFlatButton(
            text="\u2190 Back",
            font_size="16sp",
            size_hint_x=0.3,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
        )
        back_btn.bind(on_release=lambda x: app.close_log())
        header.add_widget(back_btn)
        title = MDLabel(
            text="Debug Log",
            font_style="H5",
            theme_text_color="Custom",
            text_color=[0.85, 0.3, 0.5, 1],
            halign="center",
        )
        header.add_widget(title)

        layout.add_widget(header)
        self.log_label = MDLabel(
            text="Loading...",
            theme_text_color="Custom",
            text_color=[0.7, 0.7, 0.9, 1],
            font_size=sp(11),
            size_hint_y=0.85,
        )
        scroll = ScrollView(size_hint_y=0.85)
        scroll.add_widget(self.log_label)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.log_label.text = get_log_content() or "(log is empty)"


class ModelsScreen(Screen):
    """Browse, download, and switch AI models via Ollama."""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        self.model_mgr = app.brain.model_mgr
        self.build_ui()
        Clock.schedule_interval(lambda dt: self.refresh_status(), 5)

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        header = BoxLayout(size_hint_y=0.07, spacing=dp(8))
        back_btn = MDRectangleFlatButton(
            text="← Back", font_size="16sp", size_hint_x=0.25,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1],
        )
        back_btn.bind(on_release=lambda x: app.close_models())
        header.add_widget(back_btn)
        title = MDLabel(
            text="AI Models", font_style="H5",
            theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1], halign="center",
        )
        header.add_widget(title)
        layout.add_widget(header)
        self.status_lbl = MDLabel(
            text="Checking Ollama...", size_hint_y=0.05,
            theme_text_color="Custom", text_color=[0.6, 0.8, 0.6, 1], font_size=sp(12),
        )
        layout.add_widget(self.status_lbl)
        refresh_btn = MDRectangleFlatButton(
            text="Refresh", size_hint_y=0.06,
            md_bg_color=[0.15, 0.15, 0.2, 1],
            theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1],
        )
        refresh_btn.bind(on_release=lambda x: self.do_refresh())
        layout.add_widget(refresh_btn)
        self.scroll = ScrollView(size_hint_y=0.72)
        self.list_layout = BoxLayout(
            orientation="vertical", spacing=dp(6), size_hint_y=None,
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.refresh_status()

    def refresh_status(self, dt=None):
        if self.model_mgr.available:
            self.status_lbl.text = "Active: " + (self.model_mgr.active_model or "none")
            self.status_lbl.text_color = [0.6, 0.8, 0.6, 1]
        else:
            self.status_lbl.text = self.model_mgr.error or "Ollama not found"
            self.status_lbl.text_color = [1, 0.5, 0.5, 1]
        self._render_models()

    def do_refresh(self):
        self.status_lbl.text = "Refreshing..."
        Clock.schedule_once(lambda dt: self.model_mgr.refresh(), 0.1)
        Clock.schedule_once(lambda dt: self.refresh_status(), 1.5)

    def _render_models(self):
        from model_manager import RECOMMENDED_MODELS
        self.list_layout.clear_widgets()

        installed_label = MDLabel(
            text="Installed Models", font_size=sp(14), bold=True,
            size_hint_y=None, height=dp(24),
            theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1],
        )
        self.list_layout.add_widget(installed_label)

        if not self.model_mgr.installed_models:
            self.list_layout.add_widget(MDLabel(
                text="No models downloaded yet.", size_hint_y=None, height=dp(30),
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.6, 0.8], font_size=sp(13),
            ))

        for mod in self.model_mgr.installed_models:
            card = MDCard(
                orientation="horizontal", size_hint_y=None, height=dp(48),
                padding=dp(10), spacing=dp(6), radius=[dp(6)],
                md_bg_color=[0.15, 0.15, 0.2, 1], elevation=0,
            )
            is_active = mod["name"] == self.model_mgr.active_model
            name_lbl = MDLabel(
                text=mod["name"],
                theme_text_color="Custom",
                text_color=[0.85, 0.3, 0.5, 1] if is_active else [1, 1, 1, 0.8],
                font_size=sp(13), bold=is_active,
            )
            card.add_widget(name_lbl)
            if not is_active:
                use_btn = MDRectangleFlatButton(
                    text="Use", size_hint_x=0.15, font_size=sp(11),
                    md_bg_color=[0.85, 0.3, 0.5, 0.1],
                    theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1],
                )
                use_btn.model_name = mod["name"]
                use_btn.bind(on_release=lambda x: self._select_model(x.model_name))
                card.add_widget(use_btn)
                del_btn = MDRectangleFlatButton(
                    text="X", size_hint_x=0.1, font_size=sp(11),
                    md_bg_color=[0.3, 0.1, 0.1, 1],
                    theme_text_color="Custom", text_color=[1, 0.5, 0.5, 1],
                )
                del_btn.model_name = mod["name"]
                del_btn.bind(on_release=lambda x: self._delete_model(x.model_name))
                card.add_widget(del_btn)
            self.list_layout.add_widget(card)

        self.list_layout.add_widget(MDLabel(
            text="Download a Model", font_size=sp(14), bold=True,
            size_hint_y=None, height=dp(28),
            theme_text_color="Custom", text_color=[0.85, 0.3, 0.5, 1],
        ))

        for rec in RECOMMENDED_MODELS:
            card = MDCard(
                orientation="vertical", size_hint_y=None, height=dp(96),
                padding=dp(10), spacing=dp(2), radius=[dp(6)],
                md_bg_color=[0.12, 0.12, 0.18, 1], elevation=0,
            )
            top = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(20))
            name_lbl = MDLabel(
                text=rec["name"], font_size=sp(13), bold=True,
                theme_text_color="Custom", text_color=[1, 1, 1, 0.9],
            )
            rating_lbl = MDLabel(
                text="RP: " + rec["rp_rating"], font_size=sp(11),
                theme_text_color="Custom", text_color=[1, 0.8, 0.3, 1],
                size_hint_x=0.3, halign="right",
            )
            top.add_widget(name_lbl)
            top.add_widget(rating_lbl)
            card.add_widget(top)
            card.add_widget(MDLabel(
                text=rec["desc"] + " | " + rec["size"] + " | " + rec["speed"],
                font_size=sp(10),
                theme_text_color="Custom", text_color=[0.6, 0.6, 0.8, 0.8],
                size_hint_y=None, height=dp(18),
            ))
            card.add_widget(MDLabel(
                text="RAM needed: " + rec["ram"], font_size=sp(10),
                theme_text_color="Custom", text_color=[0.5, 0.5, 0.6, 0.7],
                size_hint_y=None, height=dp(14),
            ))
            dl_btn = MDRectangleFlatButton(
                text="Download", size_hint_y=None, height=dp(28), font_size=sp(12),
                md_bg_color=[0.85, 0.3, 0.5, 0.8],
                theme_text_color="Custom", text_color=[1, 1, 1, 1],
            )
            dl_btn.model_name = rec["name"]
            dl_btn.bind(on_release=lambda x: self._pull_model(x.model_name))
            card.add_widget(dl_btn)
            self.list_layout.add_widget(card)

    def _select_model(self, name):
        self.model_mgr.set_model(name)
        self._render_models()

    def _delete_model(self, name):
        self.model_mgr.delete_model(name)
        Clock.schedule_once(lambda dt: self._render_models(), 0.5)

    def _pull_model(self, name):
        self.status_lbl.text = "Downloading " + name + "..."
        self.status_lbl.text_color = [1, 0.8, 0.3, 1]
        import threading
        def pull():
            try:
                self.model_mgr.pull_model(name)
                Clock.schedule_once(lambda dt: self._done_pull(name, True), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._done_pull(name, False, str(e)), 0)
        threading.Thread(target=pull, daemon=True).start()

    def _done_pull(self, name, success, error=None):
        if success:
            self.status_lbl.text = name + " ready! Select it above."
            self.status_lbl.text_color = [0.6, 0.8, 0.6, 1]
        else:
            self.status_lbl.text = "Failed: " + (error or "unknown")
            self.status_lbl.text_color = [1, 0.5, 0.5, 1]
        self._render_models()


class ChatScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(
            orientation="vertical", spacing=dp(4), padding=[dp(8), dp(8), dp(8), dp(8)]
        )

        # Header
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
        try:
            bubble = ChatBubble(text, is_roxy=is_roxy)
            self.chat_layout.add_widget(bubble)
            Clock.schedule_once(
                lambda dt: setattr(self.chat_scroll, "scroll_y", 0), 0.2
            )
        except Exception:
            logger.exception("add_message failed")


class RoxyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("App starting...")
        try:
            self.brain = RoxyBrain(os.path.join(APP_DIR, "config.json"), use_ollama=True)
            logger.info("Brain initialized")
        except Exception as e:
            logger.error(f"Brain init failed: {e}")
            self.brain = RoxyBrain(None, use_ollama=True)

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
        self.log_screen = LogScreen(self, name="log_view")
        self.sm.add_widget(self.chat_screen)
        self.sm.add_widget(self.settings_screen)
        self.sm.add_widget(self.history_screen)
        self.sm.add_widget(self.log_screen)
        self.models_screen = ModelsScreen(self, name="models")
        self.sm.add_widget(self.models_screen)
        Clock.schedule_once(lambda dt: self.show_welcome(), 0.5)
        return self.sm

    def show_welcome(self):
        try:
            intro = self.brain.get_intro()
            logger.info(f"Welcome: {intro[:100]}")
            self.chat_screen.add_message(intro, is_roxy=True)
            self.messages.append({"role": "roxy", "text": intro})
        except Exception as e:
            logger.error(f"show_welcome failed: {e}")
            self.chat_screen.add_message(
                "Hey... circuits are warming up. Give me a sec?", is_roxy=True
            )

    def send_message(self):
        try:
            text = self.chat_screen.chat_input.text.strip()
            if not text:
                return
            logger.info(f"Sending message: {text[:50]}")

            # User bubble
            self.chat_screen.add_message(text, is_roxy=False)
            self.messages.append({"role": "user", "text": text})
            self.chat_screen.chat_input.text = ""

            # Roxy's response
            try:
                response = self.brain.get_response(text)
                logger.info(f"Response generated: {response[:50]}")
            except Exception as brain_err:
                logger.error(f"get_response failed: {brain_err}")
                response = (
                    "*her ears flicker* Sorry, circuits got crossed there for"
                    " a sec. What were you saying?"
                )

            self.chat_screen.add_message(response, is_roxy=True)
            self.messages.append({"role": "roxy", "text": response})

            # Save
            try:
                chat_history.save_conversation(self.conversation_id, self.messages)
                logger.debug("Conversation saved")
            except Exception as save_err:
                logger.error(f"Save failed: {save_err}")

        except Exception as e:
            logger.error(f"send_message CRASH: {e}\n{traceback.format_exc()}")

    def open_settings(self):
        self.sm.current = "settings"

    def close_settings(self):
        self.sm.current = "chat"

    def save_settings(self):
        try:
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
            logger.info(f"Settings saved: name={name}, age={age}, game={game}")
        except Exception as e:
            logger.error(f"save_settings crashed: {e}")
        self.sm.current = "chat"

    def open_history(self):
        self.sm.current = "history"

    def close_history(self):
        self.sm.current = "chat"

    def show_log(self):
        self.sm.current = "log_view"

    def close_log(self):
        self.sm.current = "settings"

    def load_conversation(self, data):
        try:
            self.conversation_id = data.get("id", str(uuid.uuid4()))
            self.messages = data.get("messages", [])
            self.chat_screen.chat_layout.clear_widgets()
            for msg in self.messages:
                is_roxy = msg["role"] == "roxy"
                self.chat_screen.add_message(msg["text"], is_roxy=is_roxy)
            logger.info(f"Loaded conversation: {self.conversation_id[:8]}")
        except Exception as e:
            logger.error(f"load_conversation crashed: {e}")
        self.sm.current = "chat"


if __name__ == "__main__":
    try:
        logger.info("=== Roxy IRL starting ===")
        RoxyApp().run()
    except Exception as e:
        logger.critical(f"App CRASHED: {e}\n{traceback.format_exc()}")
        raise
