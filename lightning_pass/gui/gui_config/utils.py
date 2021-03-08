class Utils:
    def __init__(self, parent, *args, **kwargs):
        """Buttons constructor"""
        super().__init__(*args, **kwargs)
        self.main_win = parent
        self.ui = parent.ui
