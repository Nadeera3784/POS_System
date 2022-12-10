from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSplitter, QWidget, QVBoxLayout, QMainWindow, QGridLayout, QLayout
from PyQt5.QtWidgets import QToolBar, QPushButton, QLabel


class QPanedWidget(QWidget):

    def __init__(self, first_pane: QWidget, second_pane: QWidget, orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__()

        left_pane = first_pane
        right_pane = second_pane

        splitter = QSplitter(orientation)
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)

        layout = QGridLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)


# noinspection PyMethodMayBeStatic
class SplitWindow(QMainWindow):

    def __init__(self, parent=None):
        super(SplitWindow, self).__init__(parent)
        self.statusBar().showMessage("Ready")
        self.resize(800, 600)
        self.setCentralWidget(self.build_layout())

    def build_layout(self):
        return QPanedWidget(
            self.create_pane(self.create_pane_content('left')),
            self.create_pane(self.create_pane_content('right')),
            Qt.Horizontal  # This is optional, defaults to horizontal
        )

    def create_pane(self, content: QLayout) -> QWidget:
        # Container widget for pane layout
        pane_layout_container = QWidget()
        pane_layout_container.setLayout(content)
        return pane_layout_container

    def create_pane_content(self, identifier) -> QLayout:
        content = QVBoxLayout()  # Layout widget for pane content

        # FROM HERE you create your own content

        toolbar = QToolBar()
        toolbar.addWidget(QPushButton("Do Something"))
        content.addWidget(toolbar)  # Don't forget this! ^_^

        label = QLabel(identifier)
        label.setAutoFillBackground(True)
        p = label.palette()
        p.setColor(label.backgroundRole(), Qt.lightGray)
        label.setPalette(p)
        label.setAlignment(Qt.AlignCenter)

        content.addWidget(label)  # Don't forget this! ^_^

        # UNTIL HERE you populate your content

        return content


if __name__ == '__main__':
    app = QApplication([])
    win = SplitWindow()
    win.show()
    app.exec_()