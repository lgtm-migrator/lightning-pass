from PyQt5 import QtCore


class MouseTracker(QtCore.QObject):
    positionChanged = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, widget):
        """Class contructor."""
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, o, e):
        """Event filter."""
        if o is self.widget and e.type() == QtCore.QEvent.MouseMove:
            self.positionChanged.emit(e.pos())
        return super().eventFilter(o, e)

    @staticmethod
    def setup_tracker(label, on_change):
        """Setup a mouse tracker over a specified label."""
        tracker = MouseTracker(label)
        tracker.positionChanged.connect(on_change)
