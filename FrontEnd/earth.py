import sys
import math
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
from earthui import Ui_MainWindow
import pyassimp


class Satellite:
    def __init__(self, name, r, inclination_deg, angle_deg, callback):
        self.name = name
        self.r = r
        self.inclination = math.radians(inclination_deg)
        self.angle = angle_deg
        self.x = 0
        self.y = 0
        self.z = 0
        self.callback = callback

    def update_position(self, delta_deg):
        self.angle = (self.angle + delta_deg) % 360
        angle_rad = math.radians(self.angle)
        self.x = self.r * math.cos(angle_rad)
        self.y = self.r * math.sin(angle_rad) * math.cos(self.inclination)
        self.z = self.r * math.sin(angle_rad) * math.sin(self.inclination)


class OpenGLWindow(QOpenGLWidget):
    def __init__(self, earth_texture, sat_model_path, sat_texture_path, parent=None):
        super().__init__(parent)
        self.earth_texture_file = earth_texture
        self.sat_model_path = sat_model_path
        self.sat_texture_path = sat_texture_path

        self.earth_texture = None
        self.sat_texture = None

        self.sat_vertices = []
        self.sat_texcoords = []
        self.sat_faces = []
        self.sat_center = np.array([0.0, 0.0, 0.0])
        self.sat_scale = 1.0
        self.sat_display_list = None

        self.satellites = []

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background: transparent;")
        self.setUpdateBehavior(QOpenGLWidget.PartialUpdate)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.earth_texture = self.load_texture(self.earth_texture_file)
        self.sat_texture = self.load_texture(self.sat_texture_path)
        self.load_satellite_model(self.sat_model_path)

        # Init multiple satellites
        self.satellites = [
            Satellite("Sat-A", 2.5, 45, 0, self.on_satellite_clicked),
            Satellite("Sat-B", 2.8, 60, 90, self.on_satellite_clicked),
            Satellite("Sat-C", 3.0, 30, 180, self.on_satellite_clicked),
        ]

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h != 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -7.0)
        glRotatef(-20, 1.0, 0.0, 1.0)
        glRotatef(250, 0.0, 0.0, 1.0)
        glRotatef(320.0, 0.0, 1.0, 0.0)

        glColor3f(1.0, 1.0, 1.0)
        self.draw_textured_sphere(1.5, 32, 32)

        for sat in self.satellites:
            self.draw_orbit(sat.r, sat.inclination)
            self.draw_satellite_model(sat.x, sat.y, sat.z)

    def update_frame(self):
        for sat in self.satellites:
            sat.update_position(0.2)
        self.update()

    def load_texture(self, texture_file):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        image = Image.open(texture_file)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return texture_id

    def draw_textured_sphere(self, radius, slices, stacks):
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        quad = gluNewQuadric()
        gluQuadricTexture(quad, GL_TRUE)
        gluSphere(quad, radius, slices, stacks)
        gluDeleteQuadric(quad)

    def draw_orbit(self, r=2.5, inclination=math.radians(45)):
        glColor3f(0.5, 0.5, 1.0)
        glBegin(GL_LINE_LOOP)
        for i in range(360):
            angle = math.radians(i)
            x = r * math.cos(angle)
            y = r * math.sin(angle) * math.cos(inclination)
            z = r * math.sin(angle) * math.sin(inclination)
            glVertex3f(x, y, z)
        glEnd()

    def load_satellite_model(self, model_path):
        self.sat_vertices = []
        self.sat_texcoords = []
        self.sat_faces = []

        min_bound = np.array([float("inf")] * 3)
        max_bound = np.array([-float("inf")] * 3)

        with pyassimp.load(model_path) as scene:
            for mesh in scene.meshes:
                for v in mesh.vertices:
                    min_bound = np.minimum(min_bound, v)
                    max_bound = np.maximum(max_bound, v)
                    self.sat_vertices.append(v)
                if len(mesh.texturecoords) > 0:
                    self.sat_texcoords.extend(mesh.texturecoords[0])
                self.sat_faces.extend(mesh.faces)

        self.sat_center = (min_bound + max_bound) / 2.0
        size = max(max_bound - min_bound)
        self.sat_scale = 0.8 / size

        self.sat_display_list = glGenLists(1)
        glNewList(self.sat_display_list, GL_COMPILE)
        self._draw_satellite_raw()
        glEndList()

    def _draw_satellite_raw(self):
        glBegin(GL_TRIANGLES)
        has_tex = len(self.sat_texcoords) > 0
        for face in self.sat_faces:
            for idx in face:
                if has_tex and idx < len(self.sat_texcoords):
                    glTexCoord2f(self.sat_texcoords[idx][0], self.sat_texcoords[idx][1])
                glVertex3fv(self.sat_vertices[idx])
        glEnd()

    def draw_satellite_model(self, x, y, z):
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(self.sat_scale, self.sat_scale, self.sat_scale)
        glTranslatef(-self.sat_center[0], -self.sat_center[1], -self.sat_center[2])
        glBindTexture(GL_TEXTURE_2D, self.sat_texture)
        glCallList(self.sat_display_list)
        glPopMatrix()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.makeCurrent()  # ✅ 加这行，确保当前 OpenGL 上下文活跃
            # print("Mouse Pressed at:", event.x(), event.y())
            x = event.x()
            y = self.height() - event.y()
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)

            ray_start = gluUnProject(x, y, 0.0, modelview, projection, viewport)
            ray_end = gluUnProject(x, y, 1.0, modelview, projection, viewport)
            ray_dir = np.subtract(ray_end, ray_start)
            ray_dir = ray_dir / np.linalg.norm(ray_dir)

            for sat in self.satellites:
                sat_pos = np.array([sat.x, sat.y, sat.z])
                to_sat = sat_pos - ray_start
                proj_len = np.dot(to_sat, ray_dir)
                closest = ray_start + ray_dir * proj_len
                dist = np.linalg.norm(closest - sat_pos)
                if dist < self.sat_scale * 3000:  # 放宽命中半径
                    sat.callback(sat)
                    break


    def on_satellite_clicked(self, sat):
        print(f"[Clicked] Satellite selected: {sat.name}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.widget.setAutoFillBackground(False)

        self.opengl_widget = OpenGLWindow(
            "texture/8k_earth_daymap.jpg",
            "models/satellite/10477_Satellite_v1_L3.obj",
            "models/satellite/10477_Satellite_v1_Diffuse.jpg",
            parent=self.ui.widget
        )

        layout = QVBoxLayout(self.ui.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.opengl_widget)

        palette = self.ui.widget.palette()
        palette.setColor(self.ui.widget.backgroundRole(), self.palette().color(self.backgroundRole()))
        self.ui.widget.setPalette(palette)
        self.ui.widget.setAutoFillBackground(True)


def main():
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
