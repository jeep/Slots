from .LuckyWealthCatPlay import LuckyWealthCatPlay
from .Machine import Machine
from .Play import Play


class PlayFactory:
    play_for_machine = {
        "Lucky Wealth Cat": LuckyWealthCatPlay,
    }

    @staticmethod
    def get_play(machine_name: str) -> Play:
        if machine_name in PlayFactory.play_for_machine:
            print("Making a LWC Play")
            return PlayFactory.play_for_machine[machine_name]()
        return Play(machine=Machine(machine_name))