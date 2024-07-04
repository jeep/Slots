from Programs.Slots.LuckyWealthCatPlay import LuckyWealthCatPlay
from Programs.Slots.Machine import Machine
from Programs.Slots.Play import Play


class PlayFactory:
    play_for_machine = {
        "Lucky Wealth Cat": LuckyWealthCatPlay(),
    }

    @staticmethod
    def get_play(machine_name: str) -> Play:
        if machine_name in PlayFactory.play_for_machine:
            return PlayFactory.play_for_machine[machine_name]
        return Play(Machine(machine_name))