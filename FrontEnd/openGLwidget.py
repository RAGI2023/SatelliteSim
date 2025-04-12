import math
from PIL import Image
import numpy as np
import pyassimp
import time
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Satellite:
    def __init__(self, name, index, r, inclination_deg, angle_deg, delta_deg, callback):
        """初始化卫星对象

        Args:
            name (str): 卫星名称，可重复
            index (int): 编号，不可重复
            r (float): 轨道半径
            inclination_deg (_type_): 轨道倾角，单位为度（°），表示卫星轨道与赤道的夹角
            angle_deg (_type_): 初始相位角，单位为度（°），表示卫星在轨道上的位置
            delta_deg (_type_): 每帧旋转的角度，单位为度（°）
            callback (function): 点击卫星触发的回调函数（未启用）
        """
        self.name = name
        self.index = index
        self.r = r
        self.inclination = math.radians(inclination_deg)
        self.angle = angle_deg
        self.x = 0
        self.y = 0
        self.z = 0
        self.delta_deg = delta_deg
        self.callback = callback


    def update_position(self):
        self.angle = (self.angle + self.delta_deg) % 360
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

        # 定时器控制更新帧率
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.update_delta_t = 16
        self.timer.start(self.update_delta_t)  # 每16毫秒更新一次

        # 初始轨道队列
        self.orbitQueue = []
        # self.orbitArray = [0, 2, 1]

        self.clickQueue = []

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
        # index一定要按顺序来
        self.satellites = [
            Satellite("Sat-A", 0, 2.5, 45, 0, 0.2, self.on_satellite_clicked),
            Satellite("Sat-B", 1, 2.8, 60, 90, 0.2, self.on_satellite_clicked),
            Satellite("Sat-C", 2, 3.0, 30, 180, 0.2, self.on_satellite_clicked),
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
        glTranslatef(0.0, 0.0, -7.0)  # 移动到适当的位置
        glRotatef(-20, 1.0, 0.0, 1.0)
        glRotatef(250, 0.0, 0.0, 1.0)
        glRotatef(320.0, 0.0, 1.0, 0.0)

        glColor3f(1.0, 1.0, 1.0)
        self.draw_textured_sphere(1.5, 32, 32)  # 绘制地球

        # 绘制卫星轨道和卫星模型
        for sat in self.satellites:
            self.draw_orbit(sat.r, sat.inclination)
            self.draw_satellite_model(sat.x, sat.y, sat.z)

        # 添加闪烁轨道
        for i in range(len(self.orbitQueue) - 1):
            self.draw_blinking_arc_between(self.satellites[self.orbitQueue[i]], self.satellites[self.orbitQueue[i+1]])
        # self.draw_blinking_arc_between(self.satellites[0], self.satellites[1])

    def update_frame(self):
        for sat in self.satellites:
            sat.update_position()
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

    def get_blink_alpha(self, speed=5.0):
            """
            计算一个在 0~1 之间循环变化的 alpha 值，用于控制闪烁透明度。
            参数 speed 控制闪烁速度，值越大越快。
            """
            return (math.sin(time.time() * speed) + 1.0) * 0.5

    def draw_blinking_arc_between(self, sat1, sat2, segments=100):
    # 计算闪烁的透明度
        alpha = (math.sin(self.timer.remainingTime() * 0.001) + 1.0) * 0.5  # 时间控制透明度，控制闪烁频率

        # 设置线条的颜色与透明度（红色闪烁）
        glColor4f(1.0, 0.2, 0.2, alpha)
        glLineWidth(3.0)

        # 将卫星的位置作为球面坐标单位向量
        p1 = np.array([sat1.x, sat1.y, sat1.z])
        p2 = np.array([sat2.x, sat2.y, sat2.z])
        
        # 计算半径
        r1 = np.linalg.norm(p1)
        r2 = np.linalg.norm(p2)
        r = (r1 + r2) / 2.0
        
        # 防止除以零的情况
        if r < 1e-6:
            return  # 如果距离太小，直接返回，避免除以零

        v1 = p1 / r
        v2 = p2 / r

        # 球面插值：slerp（球面线性插值）
        glBegin(GL_LINE_STRIP)
        for i in range(segments + 1):
            t = i / segments
            omega = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
            if omega < 1e-5:
                interp = v1  # 如果角度非常小，直接使用第一个位置
            else:
                sin_omega = np.sin(omega)
                interp = (np.sin((1 - t) * omega) * v1 + np.sin(t * omega) * v2) / sin_omega
            interp_pos = interp * r
            glVertex3f(*interp_pos)
        glEnd()
        glLineWidth(1.0)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.makeCurrent()  # 确保当前 OpenGL 上下文活跃
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
        print(f"[Clicked] Satellite selected: {sat.name}:{sat.index}")
        self.clickQueue.append(sat.index)
        
