import sys
import signal
from PyQt5.QtWidgets import QApplication
from pyqt_ui.main_window import MainWindow


if __name__ == '__main__':
    # 允许 Ctrl+C 终止应用
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())