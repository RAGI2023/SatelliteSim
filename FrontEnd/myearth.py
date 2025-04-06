import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from myearthui import Ui_MainWindow  # Qt Designer 转换出来的 UI 文件

class OpenGLWindow(QOpenGLWidget):
    def __init__(self, texture_image, parent=None):
        super().__init__(parent)
        self.texture_image = texture_image
        self.angle = 0.0
        self.texture = None

        # 设置 OpenGL 渲染窗口透明，仅透明 OpenGL 背景，不会覆盖 widget 背景
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # 不让 OpenGL 背景完全透明
        self.setAutoFillBackground(False)  # 不填充背景，允许父窗口背景显示
        self.setStyleSheet("background: transparent;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 0.0)  # 背景透明，白色背景，alpha为0
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.texture = self.load_texture(self.texture_image)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h != 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -4.5)
        glRotatef(self.angle, 0.0, -1.0, 0.0)
        glRotatef(-20, 1.0, 0.0, 1.0)
        glRotatef(250, 0.0, 0.0, 1.0)
        glRotatef(320.0, 0.0, 1.0, 0.0)          # 加一个初始偏转，让中国面向你
        self.draw_textured_sphere(1.5, 32, 32)

    def update_frame(self):
        self.angle += 0.5
        self.update()

    def load_texture(self, image_file):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        image = Image.open(image_file)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return texture_id

    def draw_textured_sphere(self, radius, slices, stacks):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        quad = gluNewQuadric()
        gluQuadricTexture(quad, GL_TRUE)
        gluSphere(quad, radius, slices, stacks)
        gluDeleteQuadric(quad)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: white;")  # 设定主窗口背景

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 不设置 widget 透明，只是不主动填充背景
        self.ui.widget.setAutoFillBackground(False)

        # OpenGL 渲染窗口设置为透明
        self.opengl_widget = OpenGLWindow("texture/8k_earth_daymap.jpg", parent=self.ui.widget)
        self.opengl_widget.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self.ui.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.opengl_widget)

        palette = self.ui.widget.palette()
        palette.setColor(self.ui.widget.backgroundRole(), self.palette().color(self.backgroundRole()))
        self.ui.widget.setPalette(palette)
        self.ui.widget.setAutoFillBackground(True)

def main():
    # 启用 OpenGL alpha 通道，支持透明
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
