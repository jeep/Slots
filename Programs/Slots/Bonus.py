class Bonus:
    """Class to store bonus information"""
    def __init__(self, name):
        self.name = name
        self.sub_bonuses = []
        self.notable_events = []
        self.images = []
        self.value = "unknown"

    def add_bonus(self, bonus): 
        """Add a bonus to the sub bonuses"""
        self.sub_bonuses.append(bonus)

    def add_event(self, notable_event):
        """Add a note"""
        self.notable_events.append(notable_event)

    def add_image(self, image):
        """add an image"""
        self.images.append(image)

    def set_value(self, value):
        """set the ent state value"""
        self.value = value

    def __str__(self):
        bonus_str = ""
        for b in self.sub_bonuses:
            bonus_str += str(b)

        event_str = "["
        for e in self.notable_events:
            event_str = f"event: {e}"
        event_str += "]"

        imgs = ",".join(self.images)

        return "{" + f"BonusType: {self.name}, Sub-bonuses: [{bonus_str}], NotableEvents: [{event_str}], Images: [{imgs}], Value: {self.value}" + "}"