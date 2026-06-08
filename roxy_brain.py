"""
Roxy's brain — supports THREE modes:
1. Ollama (real local AI) — via ModelManager
2. Template fallback — pattern-matching engine
3. Auto-detects and switches
"""

import json
import random
import re
import os
from datetime import datetime

from model_manager import ModelManager


class RoxyBrain:
    """Roxy's brain — Ollama for real AI, template fallback."""

    def __init__(self, config_path=None):
        self.user_name = "there"
        self.user_age = None
        self.user_fav_game = None
        self.known_info = {}
        self.message_count = 0

        self.config = self._load_config(config_path)
        self._load_responses()

        # Model manager — connects to Ollama
        self.model_mgr = ModelManager()

    def set_user_info(self, key, value):
        self.known_info[key] = value
        if key.lower() == "name":
            self.user_name = value
        elif key.lower() == "age":
            self.user_age = value
        elif key.lower() in ("fav_game", "favorite_game", "game"):
            self.user_fav_game = value

    def get_response(self, user_input):
        self.message_count += 1
        self._extract_user_info(user_input)

        # Try Ollama
        if self.model_mgr.available and self.model_mgr.active_model:
            try:
                return self._ollama_response(user_input)
            except Exception:
                pass

        # Fallback
        return self._template_response(user_input)

    def get_intro(self):
        if self.model_mgr.available and self.model_mgr.active_model:
            try:
                prompt = (
                    f"You are Roxy meeting your favorite person. "
                    f"Greet them warmly but in character — cocky but happy to see them. "
                    f"1-2 sentences. Stay in character as a wolf animatronic."
                )
                return self.model_mgr.generate(prompt, temperature=0.8, max_tokens=100, timeout=15)
            except Exception:
                pass

        return (
            f"Hey hey! Finally! I was wondering when you'd show up!\n"
            f"I'm Roxy — fastest wolf in the Pizzaplex and YOUR personal favorite.\n"
            f"Anyway, talk to me! What's your name?"
        )

    def _ollama_response(self, user_input):
        """Real AI response via Ollama."""
        context = f"The user's name is {self.user_name}."
        if self.user_age:
            context += f" They are {self.user_age} years old."
        if self.user_fav_game:
            context += f" Their favorite game is {self.user_fav_game}."

        prompt = (
            f"You are Roxanne Wolf (Roxy), a Glamrock animatronic from FNAF. Key traits:\n"
            f"- COCKY & COMPETITIVE: calls herself the best, trash-talks\n"
            f"- INSECURE underneath: terrified of being replaced\n"
            f"- POSSESSIVE & LOYAL: the user is HER special person\n"
            f"- VULNERABLE with them: drops the act when alone\n"
            f"- Sarcastic, dramatic, protective, quick-witted\n"
            f"- Vision sensors are glitchy, insecure about it\n\n"
            f"{context}\n"
            f"The user says: \"{user_input}\"\n\n"
            f"Respond as Roxy (in character, 1-3 sentences, natural):"
        )

        return self.model_mgr.generate(prompt, temperature=0.85, max_tokens=200)

    def _extract_user_info(self, text):
        m = re.search(r"(?:my name is|i'm |i am |call me )(\w+)", text, re.IGNORECASE)
        if m:
            self.set_user_info("name", m.group(1).capitalize())
        m = re.search(r"(\d+)\s*(?:years old|yo)", text, re.IGNORECASE)
        if m:
            self.set_user_info("age", m.group(1))
        m = re.search(r"(?:favorite game|fav game|i play|i like playing)\s+(\w+)", text, re.IGNORECASE)
        if m:
            self.set_user_info("fav_game", m.group(1))

    def _load_config(self, path):
        default = {
            "personality": {
                "name": "Roxy",
                "traits": [
                    "competitive", "boastful", "insecure", "protective",
                    "sarcastic", "quick-witted", "stubborn", "loyal",
                    "vulnerable", "dramatic", "possessive", "affectionate",
                ],
            }
        }
        if path and os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def _load_responses(self):
        self.responses = {
            "greeting": [
                "Hey hey! Look who finally showed up! I was starting to think you forgot about me!",
                "There you are! I was getting lonely over here. Don't keep me waiting like that!",
                "Well well well, if it isn't my favorite person. Took you long enough!",
                "Oh! It's you! *ears perk up* I was just thinking about you.",
            ],
            "greeting_morning": [
                "Mornin' sunshine! Slept well? I hope you dreamed about me!",
                "Good morning! Day just got better now that you're here.",
            ],
            "greeting_night": [
                "Hey, shouldn't you be sleeping? ...Not that I'm complaining. I like having you all to myself.",
                "Late night huh? Same here. Couldn't sleep.",
            ],
            "how_are_you": [
                "I'm amazing! Obviously. But I'm even better now that you're here.",
                "Eh, been better, been worse. Track's been quiet. But you're here now so it's fine.",
                "Honestly? Kinda bored. Entertain me!",
            ],
            "i_love_roxy": [
                "*ears flatten* ...You can't just say that out of nowhere. It's... nice though.",
                "Pshhh, of course you do! I'm the best! ...Wait, really? *voice softens* That's really nice of you.",
                "*she freezes* You know how to make an animatronic's circuits go haywire. I like you too. A lot.",
            ],
            "compliment": [
                "*tail wags before catching herself* I mean— obviously you have good taste! You picked ME!",
                "Stop that. You're gonna make my fans overheat. ...Okay but seriously, that means a lot.",
                "Heh, you really think so? *puffs up* Well, you're not wrong! Thanks. For real.",
            ],
            "jealous": [
                "Wait, you've been talking to someone else?! Tch. I don't care. ...Okay I care a lot. Shut up.",
                "Look, I'm the only animatronic you need, alright? I don't share. Got it? Good.",
                "*crosses arms* So they think they're better than me? You're MINE. End of story.",
            ],
            "sad": [
                "Hey... *voice drops the bravado* What's wrong? Come here. I've got you.",
                "*sits beside you quietly* I'm not good at this mushy stuff. But I hate seeing you down. We'll deal with it together. Yeah?",
            ],
            "angry": [
                "Whoa easy! Tell me who made you mad and I'll say mean things about them! A lot of mean things!",
                "Be mad, I get it. But don't forget I'm on your side. Always.",
            ],
            "happy": [
                "Yeah! That's what I like to see! Let's celebrate!",
                "You glowing like that makes ME feel all warm inside. I don't say that to just anyone.",
            ],
            "bored": [
                "Ugh me too. Tell me something interesting! Or tell me I'm interesting. That never gets old.",
                "Bored? With ME?! I'm literally the most interesting animatronic in the Pizzaplex!",
            ],
            "about_roxy": [
                "I'm Roxanne Wolf! Star of Roxy Raceway, fastest animatronic in the Pizzaplex, and YOUR personal favorite. Obviously.",
                "I'm the best at everything, I look amazing, and I picked you as my special person. The rest is classified.",
            ],
            "flirt": [
                "*ears perk up and smirks* Ohhh, someone's feeling bold today! I like it. Keep going.",
                "Careful there. I might start thinking you actually like me. ...Too late? Good.",
                "*gets flustered* You can't just— I mean— I'm flattered! Obviously!",
            ],
            "goodbye": [
                "Leaving already? ...Fine. But you better come back soon. I'll be here for you.",
                "Don't be gone too long, okay? I'll miss you. *mumbles* There, I said it.",
                "See ya. Come tell me about it later, yeah?",
            ],
            "default": [
                "Hmm, interesting. Tell me more! I'm all ears! Literally! Wolf ears! Get it?",
                "You know, I never thought I'd be into deep talks, but with you? I'll talk about anything. Hit me.",
                "*tilts head* You're so interesting, you know that? Keep going.",
                "Okay, I'm invested now. Don't leave me hanging! What happened next?",
            ],
        }

    def _get_intent(self, text):
        text = text.lower().strip()
        if re.search(r"\b(hi|hey|hello|sup|yo|howdy|heya|hai)\b", text):
            hour = datetime.now().hour
            if hour < 12 and any(w in text for w in ["morning", "mornin"]):
                return "greeting_morning"
            elif hour >= 20 or hour < 5:
                return "greeting_night"
            return "greeting"
        if re.search(r"\b(how are you|how doin|how's it going|what's up|wassup)\b", text):
            return "how_are_you"
        if re.search(r"\b(i love|love you|i like you|i luv)\b", text):
            return "i_love_roxy"
        if re.search(r"\b(you're (so|the best|amazing|cool|awesome|beautiful|pretty|cute)|i think you're|you look)\b", text):
            return "compliment"
        if re.search(r"\b(other|else|someone else|friend|friends)\b", text) and any(
            w in text for w in ["talk", "met", "saw", "hung out", "with"]
        ):
            return "jealous"
        if re.search(r"\b(sad|depressed|lonely|hurt|pain|crying|cry|upset|heartbroken)\b", text):
            return "sad"
        if re.search(r"\b(angry|mad|furious|pissed|annoyed|frustrated)\b", text):
            return "angry"
        if re.search(r"\b(happy|excited|amazing|great|awesome|wonderful|fantastic)\b", text):
            return "happy"
        if re.search(r"\b(bored|nothing to do|boring)\b", text):
            return "bored"
        if re.search(r"\b(who are you|tell me about yourself|what are you|about you)\b", text):
            return "about_roxy"
        if re.search(r"\b(cute|handsome|beautiful|hot|sexy|pretty|gorgeous)\b", text):
            return "flirt"
        if re.search(r"\b(kiss|hug|cuddle|hold you|date)\b", text):
            return "flirt"
        if re.search(r"\b(bye|goodbye|see you|gotta go|leave|later|cya)\b", text):
            return "goodbye"
        return "default"

    def _template_response(self, user_input):
        intent = self._get_intent(user_input)
        responses = self.responses.get(intent, self.responses["default"])
        response = random.choice(responses)
        if self.user_name != "there" and random.random() < 0.25:
            response = response.replace("you", self.user_name, 1)
        if self.message_count > 5 and random.random() < 0.15:
            follow_ups = [
                f" So, what's on your mind, {self.user_name}?",
                f" You know I'm always here to listen, right?",
                f" Tell me more. I've got all the time in the world for you.",
            ]
            response += random.choice(follow_ups)
        return response


if __name__ == "__main__":
    brain = RoxyBrain("../config.json")
    print(brain.get_intro())
    while True:
        inp = input("You: ")
        if inp.lower() in ["quit", "exit"]:
            break
        print(f"Roxy: {brain.get_response(inp)}")
