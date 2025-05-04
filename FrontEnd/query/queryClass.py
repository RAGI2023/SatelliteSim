from FrontEnd.query.query import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QFileDialog

class QueryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.inputType = "TEXT"
        self.input_data = ""  # 用于存储输入的文本或音频路径

        # 初始绑定信号
        self.ui.submitButton.clicked.connect(self.submit_input)
        self.ui.comboBox.currentTextChanged.connect(self.changeInputType)
        self.ui.selectButton.clicked.connect(self.select_file)

        # 隐藏选择文件路径相关控件
        self.ui.Path.hide()
        self.ui.pathlabel.hide()
        self.ui.selectButton.hide()

    def changeInputType(self, value):
        if value == "TEXT":
            self.inputType = "TEXT"
            self.ui.textEdit.show()
            self.ui.Path.hide()
            self.ui.pathlabel.hide()
            self.ui.selectButton.hide()
        elif value == "VOICE":
            self.inputType = "VOICE"
            self.ui.textEdit.hide()
            self.ui.Path.show()
            self.ui.pathlabel.show()
            self.ui.selectButton.show()
            self.ui.pathlabel.setText("未选择文件")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 MP3 文件",
            "",
            "音频文件 (*.mp3);;所有文件 (*)"
        )
        if file_path:
            self.ui.pathlabel.setText(file_path)
            self.input_data = file_path  # 直接设置为音频路径
        else:
            self.ui.pathlabel.setText("未选择文件")

    def submit_input(self):
        if self.inputType == "TEXT":
            self.input_data = self.ui.textEdit.toPlainText()
        # 若是 voice 类型，input_text 已在 select_file 中设置为路径
        print(f"提交内容类型: {self.inputType}")
        print(f"提交内容: {self.input_data}")
        self.accept()  # 关闭窗口，返回 QDialog.Accepted
