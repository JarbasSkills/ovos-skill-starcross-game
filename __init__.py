from pyfrotz.ovos import FrotzSkill
from pyfrotz.parsers import starcross_intro_parser


class StarCrossSkill(FrotzSkill):
    def __init__(self, *args, **kwargs):
        # game is english only, apply bidirectional translation
        super().__init__(*args,
                         game_id="starcross",
                         game_lang="en-us",
                         game_data=f'{self.root_dir}/res/{self.game_id}.z5',
                         intro_parser=starcross_intro_parser,
                         **kwargs)
