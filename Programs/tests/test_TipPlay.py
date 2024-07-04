import pytest
import datetime
import pathlib
from decimal import Decimal

from Programs.Slots.Machine import Machine
from Programs.Slots.TipPlay import TipPlay


machine_for_test = Machine("Test Machine")
class TestTipPlay():
    @pytest.fixture
    def play(self):
        return TipPlay(casino = "ilani", start_time = datetime.datetime(2024, 1, 2), _cash_in = [Decimal(10.00)])

    def test_initial_cash_in(self, play):
        assert play.initial_cash_in == Decimal(10.00)
    
    def test_play_type(self, play):
        assert play.play_type == "Tip"
    
    def test_cash_out(self, play):
        assert play.cash_out == Decimal(0.0)
        with pytest.raises(Exception):
            play.cash_out = Decimal("1.23")
    
    def test_set_bet_raises(self, play):
        with pytest.raises(Exception):
            play.bet = Decimal('1.23')

    def test_set_state_raises(self, play):
        with pytest.raises(Exception):
            play.state = "This is a state"

    def test_set_playtype_raises(self, play):
        with pytest.raises(Exception):
            play.play_type = "AP"

    def test_play_as_str(self, play):
        expected = r"""ilani,01/02/2024,Tip,$10.00,,Tip,,$0.00,-$10.00,,Non-AP,,,"""

        assert str(play) == expected