from .LuckyWealthCatPlay import LuckyWealthCatPlay
from .LuckyBuddhaPlay import LuckyBuddhaPlay
from .PowerPushPlay import PowerPushPlay
from .PinwheelPrizesPlay import PinwheelPrizesPlay
from .FrankensteinPlay import FrankensteinPlay
from .Machine import Machine
from .Play import Play


class PlayFactory:
    play_for_machine = {
        "Lucky Wealth Cat": LuckyWealthCatPlay,
        "Lucky Wealth Cat (Bingo)": LuckyWealthCatPlay,
        "Lucky Buddha": LuckyBuddhaPlay,
        "Lucky Buddha (Bingo)": LuckyBuddhaPlay,
        "Frankenstein": FrankensteinPlay,
        "Frankenstein (Bingo)": FrankensteinPlay,
        "Pinwheel Prizes": PinwheelPrizesPlay,
        "Pinwheel Prizes (Bingo)": PinwheelPrizesPlay,
        "Power Push": PowerPushPlay,
        "Power Push (Bingo)": PowerPushPlay}
        
    
    @staticmethod
    def get_play(machine_name: str) -> Play:
        if machine_name in PlayFactory.play_for_machine:
            return PlayFactory.play_for_machine[machine_name]()
        return Play(machine=Machine(machine_name))