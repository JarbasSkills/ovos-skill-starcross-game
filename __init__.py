from pyfrotz.ovos import FrotzSkill
from ovos_workshop.decorators import conversational_intent, intent_handler


class StarCrossSkill(FrotzSkill):
    def __init__(self, *args, **kwargs):

        # Game specific init
        def intro_parser(game):
            intro = """you are sound asleep in your bunk aboard the deep-space black hole prospecting ship "starcross," operating out of ceres.
            just as your sleep becomes deep and comfortable, an alarm bell begins ringing! it's the mass detector! instantly you awake.
            this hasn't been a profitable trip so far, and you don't even have the cash for repairs.
            this could be the break you've been waiting for."""
            game._frotz_read()
            return intro

        # game is english only, apply bidirectional translation
        super().__init__(game_id="starcross",
                         game_lang="en-us",
                         game_data=f'{self.root_dir}/res/{self.game_id}.z5',
                         intro_parser=intro_parser,
                         *args, **kwargs)

    @intent_handler("play.intent")
    def handle_play(self, message=None):
        self.start_game(load_save=True)

    # intents
    @conversational_intent("exit.intent")
    def handle_exit(self, message=None):
        self.exit_game()

    @conversational_intent("restart_game.intent")
    def handle_restart(self, message=None):
        self.start_game(load_save=False)

    @conversational_intent("save.intent")
    def handle_save(self, message=None):
        self.save_game()
