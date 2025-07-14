from PyQt5 import QtCore, QtGui, QtWidgets


class ClassCountWidget(QtWidgets.QListWidget):
    """Widget to display number of cached instances per class."""

    labelDoubleClicked = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._emit_label)
        self.setMinimumWidth(120)

    def _emit_label(self, item: QtWidgets.QListWidgetItem) -> None:
        label = item.data(QtCore.Qt.UserRole)
        if label:
            self.labelDoubleClicked.emit(label)

    def set_counts(self, counts: dict[str, int], color_func=None) -> None:
        """Update class counts.

        Parameters
        ----------
        counts: dict
            Mapping from label name to count.
        color_func: callable, optional
            Function that returns an ``(r, g, b)`` tuple for a label.
        """
        self.clear()
        for label in sorted(counts):
            count = counts[label]
            text = f"{label}: {count}"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, label)
            if color_func is not None:
                r, g, b = color_func(label)
                item.setForeground(QtGui.QColor(r, g, b))
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.addItem(item)
