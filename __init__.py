from pyfrotz.ovos import FrotzSkill
from pyfrotz.parsers import starcross_intro_parser


class StarCrossSkill(FrotzSkill):
    def __init__(self, *args, **kwargs):
        # TODO - dedicated icon, use pyfrotz icon for now
        skill_icon = "https://raw.githubusercontent.com/TigreGotico/pyFrotz/refs/heads/dev/pyfrotz/gui/all/pyfrotz.png"
        bg = "http://infocom.elsewhere.org/gallery/starcross/starcross1.jpg"
        # game is english only, apply bidirectional translation
        super().__init__(*args,
                         game_id="starcross",
                         game_lang="en-us",
                         game_data=f'{self.root_dir}/res/{self.game_id}.z5',
                         intro_parser=starcross_intro_parser,
                         skill_icon=skill_icon,
                         game_image=bg,
                         **kwargs)
