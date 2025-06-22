import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f7fa;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLabel {
            font-size: 11pt;
        }
        QDoubleSpinBox, QSpinBox {
            padding: 5px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #ecf0f1;
            color: #2c3e50;
            font-size: 10pt;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()