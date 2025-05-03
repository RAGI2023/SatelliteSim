from FrontEnd.query.query import Ui_Dialog
from PyQt5 import QtWidgets as Qt

class QueryWindow(Qt.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.input_text = "" # 用于存储输入的文本

        self.ui.submitButton.clicked.connect(self.submit_input)

    def submit_input(self):
        self.input_text = self.ui.textEdit.toPlainText()
        print(f"子窗口输入内容: {self.input_text}")
        self.accept()  # 提交并关闭窗口（exec_() 返回 QDialog.Accepted）