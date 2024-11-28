from Programs.Slots.LuckyWealthCatPlay import LuckyWealthCatPlay
from Programs.Slots.Play import Play
from Programs.Slots.PlayFactory import PlayFactory


class TestPlayFactory:
    def test_DefaultPlay(self):
        play = PlayFactory.get_play("Simple Machine")
        assert type(play) is Play

    def test_LuckyWealthCatPlay(self):
        play = PlayFactory.get_play("Lucky Wealth Cat")
        assert type(play) is LuckyWealthCatPlay
