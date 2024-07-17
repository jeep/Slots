from .LuckyWealthCatPlay import LuckyWealthCatPlay
from .PowerPushPlay import PowerPushPlay
from .PinwheelPrizesPlay import PinwheelPrizesPlay
from .Machine import Machine
from .Play import Play


class PlayFactory:
    play_for_machine = {
        "Lucky Wealth Cat": LuckyWealthCatPlay,
        "Lucky Wealth Cat (Bingo)": LuckyWealthCatPlay,
        "Pinwheel Prizes": PinwheelPrizesPlay,
        "Pinwheel Prizes (Bingo)": PinwheelPrizesPlay,
        "Power Push": PowerPushPlay,
        "Power Push (Bingo)": PowerPushPlay}
        
    
    @staticmethod
    def get_play(machine_name: str) -> Play:
        if machine_name in PlayFactory.play_for_machine:
            return PlayFactory.play_for_machine[machine_name]()
        return Play(machine=Machine(machine_name))