class Collector:
    def __init__(self):
        self.randomness_lst = []

    def collect_position(self, pos):
        if len(self.randomness_lst) <= 999:
            self.randomness_lst.append("(%d, %d)" % (pos.x(), pos.y()))
            if len(self.randomness_lst) % 10 == 0:
                return True
        else:
            return "Done"
