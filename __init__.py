import time
from os.path import join, expanduser, exists

from mycroft.skills.core import intent_file_handler
from mycroft.skills.intent_service_interface import IntentQueryApi
from mycroft_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.skills.decorators import layer_intent, enables_layer, \
    resets_layers
from pyfrotz import Frotz
from quebra_frases import sentence_tokenize


class StarCross(OVOSSkill):
    def __init__(self):
        super().__init__()
        self.playing = False
        self.game = None
        self.last_interaction = time.time()
        # TODO xdg path
        self.save_file = expanduser("~/starcross.save")
        self.game_data = join(self.root_dir, 'starcross.z5')
        # built by requirements.sh
        self.frotz_path = expanduser("~/frotz/dfrotz")

    def initialize(self):
        # start skill in "not_playing" layer
        self.intent_layers.disable()
        self.intent_layers.activate_layer("not_playing")
        # async commands due to converse timeout!
        self.add_event("frotz.starcross.cmd", self._handle_cmd)

    def will_trigger(self, utterance, lang):
        # will an intent from this skill trigger ?
        skill_id = IntentQueryApi(self.bus).get_skill(utterance, lang)
        if skill_id and skill_id == self.skill_id:
            return True
        return False

    def speak_output(self, line):
        # replace type with say because its voice game
        lines = sentence_tokenize(line.replace("type", "say"))

        for line in lines:
            # TODO nice background picture
            self.gui["text"] = line
            self.gui.show_page("text.qml")
            self.speak(line.strip(), wait=True)

        self.speak("", expect_response=True)  # start listening for user input
        self.last_interaction = time.time()
        self.maybe_end_game()

    @enables_layer("playing")
    def start_game(self):
        self.playing = True
        if self.game is None:
            self.game = Frotz(self.game_data, interpreter=self.frotz_path,
                              save_file=self.save_file)
        self.last_interaction = time.time()

        # starcross says intro before credits and pyfroz misses it
        def intro_parser(game):
            intro = """you are sound asleep in your bunk aboard the deep-space black hole prospecting ship "starcross," operating out of ceres.
            just as your sleep becomes deep and comfortable, an alarm bell begins ringing! it's the mass detector! instantly you awake.
            this hasn't been a profitable trip so far, and you don't even have the cash for repairs.
            this could be the break you've been waiting for."""
            game._frotz_read()
            return intro

        self.speak_output(self.game.get_intro(intro_parser))
        self.current_room = self.do_command("look")

    @layer_intent("play.intent", layer_name="not_playing")
    def handle_play(self, message=None):
        self.start_game()

    @layer_intent("restart_game.intent", layer_name="playing")
    def handle_restart(self, message=None):
        # shorter intent that doesnt require game name in utt
        self.start_game()

    @layer_intent("save.intent", layer_name="playing")
    def handle_save(self, message=None):
        if not self.playing:
            self.speak_dialog("save.not.found")
        else:
            self.game.save()
            self.speak_dialog("game.saved", {"name": self.name})

    @layer_intent("resume_game_short.intent", layer_name="playing")
    def handle_resume(self, message=None):
        # shorter intent that doesnt require game name in utt
        self.handle_restore(message)

    @intent_file_handler("restore.intent")
    def handle_restore(self, message):
        if exists(self.save_file):
            self.playing = True
            if self.game is None:
                self.game = Frotz(self.game_data, interpreter=self.frotz_path,
                                  save_file=self.save_file)
            self.game.restore()
            self.speak_dialog("restore.game", {"name": self.name})
            self.enable_intent("Save")
        else:
            self.speak_dialog("save.not.found")
            new_game = self.ask_yesno("new.game", {"name": self.name})
            if new_game:
                self.handle_play()

    @resets_layers()
    def game_over(self):
        self.playing = False
        self.game = None
        self.speak_dialog("game.ended")

    def maybe_end_game(self):
        # end game if no interaction for 10 mins
        if self.playing:
            timed_out = time.time() - self.last_interaction > 10 * 3600
            if timed_out:
                self.handle_save()
            if timed_out or self.game.game_ended():
                self.game_over()

    def do_command(self, utterance):
        if self.game.game_ended():
            self.game_over()
            return
        # this may return empty string if the game ended
        data = self.game.do_command(utterance)
        if not data:
            self.playing = False
            return None
        else:
            room = data[0]
            description = data[1]
            self.speak_output(room)
            self.speak_output(description)
        return room

    def _handle_cmd(self, message):
        utt = message.data["utterance"]
        self.do_command(utt)
        # check for game end
        if self.game.game_ended():
            self.game_over()

    def converse(self, utterances, lang="en-us"):
        """ Handle conversation.

        This method gets a peek at utterances before the normal intent
        handling process after a skill has been invoked once.

        To use, override the converse() method and return True to
        indicate that the utterance has been handled.

        Args:
            utterances (list): The utterances from the user
            lang:       language the utterance is in

        Returns:
            bool: True if an utterance was handled, otherwise False
        """
        # check if game was abandoned mid conversation and we should clean it up
        self.maybe_end_game()
        if self.playing:
            ut = utterances[0]
            # if self will trigger do nothing and let intents handle it
            if self.will_trigger(ut, lang):
                # save / restore will trigger
                return False
            # capture speech and pipe to the game
            # NOTE this is too slow, converse times out and we get double
            # intents, delay execution and return now!
            self.bus.emit(Message("frotz.starcross.cmd", {"utterance": ut}))
            return True
        return False


def create_skill():
    return StarCross()
