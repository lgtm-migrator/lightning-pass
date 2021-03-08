class Collector:
    """The Collector class contains functionality for recording current mouse position."""

    def __init__(self):
        """Class contructor."""
        self.randomness_lst = []

    def __repr__(self):
        """Provide information about this class."""
        return f"Collector({self.randomness_lst})"

    def collect_position(self, pos):
        """Collect mouse position.

        :param QPoint pos: current cursor position

        :returns True: If current number of position can be divided by 10 without any remainder.
        :rtype bool

        :returns "Done": If 1000 position have been collected.
        :rtype str

        """
        if len(self.randomness_lst) <= 999:
            self.randomness_lst.append("(%d, %d)" % (pos.x(), pos.y()))
            if len(self.randomness_lst) % 10 == 0:
                return True
        else:
            return "Done"
