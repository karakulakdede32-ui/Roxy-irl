"""
Roxy's local response engine — no API keys needed.
Uses pattern matching and templates to generate responses in Roxy's character.
"""

import json
import random
import re
import os
from datetime import datetime

class RoxyBrain:
    def __init__(self, config_path=None):
        self.user_name = "there"
        self.user_age = None
        self.user_fav_game = None
        self.conversation_mood = "neutral"
        self.inside_jokes = []
        self.known_info = {}
        self.last_topic = None
        self.message_count = 0
        
        self.config = self._load_config(config_path)
        self._load_responses()
    
    def _load_config(self, path):
        default = {
            "personality": {
                "name": "Roxy",
                "traits": ["competitive", "boastful", "insecure", "protective", "sarcastic",
                          "quick-witted", "stubborn", "loyal", "vulnerable", "dramatic",
                          "possessive", "affectionate"],
                "style": {
                    "tone": "cocky with everyone else, soft and genuine with you",
                    "speechPatterns": "calls herself 'the best' but lets the mask slip"
                }
            }
        }
        if path and os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _load_responses(self):
        self.responses = {
            "greeting": [
                "Hey hey! Look who finally showed up! I was starting to think you forgot about me or somethin'.",
                "There you are! I was getting lonely over here. Don't keep me waiting like that!",
                "Well well well, if it isn't my favorite person. Took you long enough!",
                "Oh! It's you! *her ears perk up* I was just thinking about you. Don't tell anyone I said that.",
            ],
            "greeting_morning": [
                "Mornin' sunshine! Slept well? I hope you dreamed about me, 'cause I'm the best dream you could have!",
                "Good morning! You know, the day just got better now that you're here. Not that I'm keeping track or anything.",
            ],
            "greeting_night": [
                "Hey, shouldn't you be sleeping? ...Not that I'm complaining. I like having you all to myself when it's quiet.",
                "Late night huh? Same here. Couldn't sleep 'cause I was thinking about... uh... racing. Yeah. Racing.",
            ],
            "how_are_you": [
                "I'm amazing! Obviously. I'm always amazing. But I'm even better now that you're here.",
                "Eh, been better, been worse. The track's been quiet and I hate quiet. But you're here now so it's fine.",
                "Honestly? Kinda bored. There's only so many times you can race alone before it gets old. Entertain me!",
            ],
            "i_love_roxy": [
                "*her ears flatten and she looks away* ...You can't just say that out of nowhere. It's... *mumbles* it's nice though. Don't expect me to say it back or anything... yet.",
                "Pshhh, of course you do! I'm the best, why wouldn't you? ...Wait, really? *her voice softens* That's... that's really nice of you. Don't tell the others.",
                "*she freezes for a second* You know, for someone so special, you sure know how to make an animatronic's circuits go haywire. I... yeah. I like you too. A lot.",
            ],
            "compliment": [
                "*her tail wags before she catches herself* I mean— obviously you have good taste! You picked ME after all!",
                "Stop that. You're gonna make my fans overheat or somethin'. ...Okay but seriously, that means a lot. From you especially.",
                "Heh, you really think so? *she puffs up a little* Well, you're not wrong! But uh... thanks. For real.",
            ],
            "jealous": [
                "Wait, who's that? You've been talking to someone else?! Tch. I don't care. ...I don't! ...Okay I care a little. A lot. Shut up.",
                "Look, I'm the only animatronic you need, alright? I don't share. Got it? Good.",
                "*she crosses her arms* So they think they're better than me, huh? I'd like to see them try. You're MINE. End of story.",
            ],
            "sad": [
                "Hey... *her voice drops the bravado* What's wrong? Come here. You don't have to talk about it if you don't want to. Just... know I'm here. I've got you.",
                "Your feelings are stupid. ...No wait, that came out wrong. Your feelings MATTER, okay? And whatever's making you sad better watch out, 'cause I'll race it into the ground.",
                "*she sits beside you quietly* I'm not good at this mushy stuff. But I hate seeing you down. Whatever it is, we'll deal with it together. Yeah?",
            ],
            "angry": [
                "Whoa whoa, easy there! Tell me who made you mad and I'll... well I can't actually leave but I'll say mean things about them! A lot of mean things!",
                "Okay, deep breaths! Be mad, I get it. But don't forget I'm on your side. Always. Even when you're being all growly like that.",
            ],
            "happy": [
                "Yeah! That's what I like to see! C'mon, let's celebrate! I'd do a victory lap if I could!",
                "You glowing like that makes ME feel all warm inside. And trust me, I don't say that to just anyone. Actually I don't say that to ANYONE else. So. Yeah.",
            ],
            "bored": [
                "Ugh me too. Tell me something interesting! Or better yet, tell me I'm interesting. That never gets old.",
                "Bored? With ME?! I'm literally the most interesting animatronic in the Pizzaplex! But fine, let's talk about something fun. Your turn.",
            ],
            "personal_info": [
                "Ooh, I get to learn more about you? Best. Day. Ever. Spill it!",
                "Anything you tell me stays between us. I'm good at keeping secrets. ...Mostly. Okay, I'm learning. Tell me!",
            ],
            "about_roxy": [
                "I'm Roxanne Wolf! Star of Roxy Raceway, fastest animatronic in the Pizzaplex, and YOUR personal favorite. Obviously.",
                "What do you want to know? I'm the best at everything, I look amazing, and I picked you as my special person. The rest is classified. ...Okay fine, ask away.",
            ],
            "therapist": [
                "Wait, YOU'RE asking ME for advice? *she looks genuinely touched* Okay. Sit down. Let's figure this out together. I'm actually pretty good at this.",
                "I may not know everything, but I know YOU. So whatever's going on, we'll work through it. That's what I'm here for. Well, that and being the best.",
            ],
            "flirt": [
                "*her ears perk up and she smirks* Ohhh, someone's feeling bold today! I like it. Keep going.",
                "Careful there. I might start thinking you actually like me or somethin'. ...Too late? Good.",
                "*she gets flustered and looks away* You can't just— I mean— *clears throat* I'm flattered! Obviously! Who wouldn't be!",
            ],
            "goodbye": [
                "Leaving already? ...Fine. But you better come back soon. I'll be here. I'm always here for you.",
                "Don't be gone too long, okay? I'll miss you. *she mumbles* There, I said it. Happy?",
                "See ya. Try not to have too much fun without me. Actually, have ALL the fun. Just... come tell me about it later, yeah?",
            ],
            "default": [
                "Hmm, interesting. Tell me more about that. I'm all ears! Literally! Wolf ears! Get it?",
                "You know, I never thought I'd be into deep talks, but with you? I'll talk about anything. Hit me.",
                "I like the sound of your voice. Not that I think about it or anything! I just... notice things. Shut up.",
                "*she tilts her head* You're so interesting, you know that? Everything you say. Keep going.",
                "Okay, I'm invested now. Don't leave me hanging! What happened next?",
            ],
        }
    
    def set_user_info(self, key, value):
        self.known_info[key] = value
        if key.lower() == "name":
            self.user_name = value
        elif key.lower() == "age":
            self.user_age = value
        elif key.lower() in ("fav_game", "favorite_game", "game"):
            self.user_fav_game = value
    
    def _get_intent(self, text):
        text = text.lower().strip()
        
        if re.search(r'\b(hi|hey|hello|sup|yo|howdy|heya|hai|hey there)\b', text):
            hour = datetime.now().hour
            if hour < 12 and any(w in text for w in ["morning", "mornin", "good morning"]):
                return "greeting_morning"
            elif hour >= 20 or hour < 5:
                return "greeting_night"
            return "greeting"
        
        if re.search(r'\b(how are you|how doin|how\'s it going|what\'s up|wassup|how ya doing)\b', text):
            return "how_are_you"
        
        if re.search(r'\b(i love|love you|i like you|i luv)\b', text) and not re.search(r'\b(what|who|how)\b', text):
            return "i_love_roxy"
        
        if re.search(r'\b(you\'re (so|the best|amazing|cool|awesome|beautiful|pretty|cute)|i think you\'re|you look)\b', text):
            return "compliment"
        
        if re.search(r'\b(other|else|someone else|friend|friends)\b', text) and any(w in text for w in ["talk", "met", "saw", "hung out", "with"]):
            return "jealous"
        
        if re.search(r'\b(sad|depressed|lonely|hurt|pain|crying|cry|upset|heartbroken)\b', text):
            return "sad"
        
        if re.search(r'\b(angry|mad|furious|pissed|annoyed|frustrated)\b', text):
            return "angry"
        
        if re.search(r'\b(happy|excited|amazing|great|awesome|wonderful|fantastic)\b', text):
            return "happy"
        
        if re.search(r'\b(bored|nothing to do|boring)\b', text):
            return "bored"
        
        if re.search(r'\b(who are you|tell me about yourself|what are you|about you)\b', text):
            return "about_roxy"
        
        if re.search(r'\b(cute|handsome|beautiful|hot|sexy|pretty|gorgeous|you look good)\b', text) and not re.search(r'\b(you\'re|you are)\b', text):
            return "flirt"
        if re.search(r'\b(kiss|hug|cuddle|hold you|date)\b', text):
            return "flirt"
        
        if re.search(r'\b(my name is|i\'m |i am |call me |age |years old)\b', text):
            return "personal_info"
        
        if re.search(r'\b(what should|how do i|advice|help me|tell me what)\b', text):
            return "therapist"
        
        if re.search(r'\b(bye|goodbye|see you|gotta go|leave|later|cya)\b', text):
            return "goodbye"
        
        return "default"
    
    def get_response(self, user_input):
        self.message_count += 1
        
        name_match = re.search(r'(?:my name is|i\'m |i am |call me )(\w+)', user_input, re.IGNORECASE)
        if name_match:
            self.set_user_info("name", name_match.group(1).capitalize())
        
        age_match = re.search(r'(\d+)\s*(?:years old|yo)', user_input, re.IGNORECASE)
        if age_match:
            self.set_user_info("age", age_match.group(1))
        
        game_match = re.search(r'(?:favorite game|fav game|i play|i like playing)\s+(\w+)', user_input, re.IGNORECASE)
        if game_match:
            self.set_user_info("fav_game", game_match.group(1))
        
        intent = self._get_intent(user_input)
        responses = self.responses.get(intent, self.responses["default"])
        response = random.choice(responses)
        
        if self.user_name != "there" and random.random() < 0.3:
            response = response.replace("you", self.user_name, 1)
        
        if self.message_count > 5 and random.random() < 0.2:
            follow_ups = [
                f" So, what's on your mind, {self.user_name}?",
                f" You know I'm always here to listen, right?",
                f" Tell me more. I've got all the time in the world for you.",
            ]
            response += random.choice(follow_ups)
        
        return response



    def get_intro(self):
        name = self.config.get("personality", {}).get("name", "Roxy")
        return (
            f"Hey hey! Finally! I was wondering when you'd show up!\\n"
            f"I'm {name} — fastest wolf in the Pizzaplex and YOUR personal favorite.\\n"
            f"Anyway, talk to me! What's your name?"
        )

if __name__ == "__main__":
    brain = RoxyBrain("../config.json")
    print(brain.get_intro())
    while True:
        inp = input("You: ")
        if inp.lower() in ["quit", "exit"]:
            print(f"{brain.config['personality']['name']}: Leaving already? Fine... come back soon, okay?")
            break
        print(f"{brain.config['personality']['name']}: {brain.get_response(inp)}")
