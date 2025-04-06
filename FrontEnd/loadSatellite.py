import sys
import pyassimp
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

class OpenGLWindow:
    def __init__(self, model_path, texture_path):
        self.model_path = model_path
        self.texture_path = texture_path
        self.angle = 0.0
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.texture = None

        # ✅ 相机控制变量
        self.camera_distance = 5.0
        self.rotation_y = 0.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        # ✅ 鼠标状态
        self.last_mouse_button = None
        self.last_mouse_pos = None

        # ✅ 模型缩放与居中
        self.model_center = np.array([0.0, 0.0, 0.0])
        self.auto_scale = 1.0

    def initialize(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        self.load_model(self.model_path)
        self.texture = self.load_texture(self.texture_path)
        print("Texture ID:", self.texture)

    def load_model(self, model_path):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        # 计算 bounding box
        min_bound = np.array([float("inf")] * 3)
        max_bound = np.array([-float("inf")] * 3)

        with pyassimp.load(model_path) as scene:
            for mesh in scene.meshes:
                for v in mesh.vertices:
                    min_bound = np.minimum(min_bound, v)
                    max_bound = np.maximum(max_bound, v)
                    self.vertices.append(v)
                self.normals.extend(mesh.normals)
                if len(mesh.texturecoords) > 0:
                    self.texcoords.extend(mesh.texturecoords[0])
                self.faces.extend(mesh.faces)

        # 模型中心
        center = (min_bound + max_bound) / 2.0
        self.model_center = center

        # 模型最大尺寸用于缩放
        size = max(max_bound - min_bound)
        self.auto_scale = 2.0 / size  # 统一缩放到大小约为 2
        self.camera_distance = 3.0

        print(f"[Model] Center: {center}, Size: {size:.3f}, Auto-scale: {self.auto_scale:.5f}")

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

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # ✅ 模型缩放 + 居中（固定变换）
        glScalef(self.auto_scale, self.auto_scale, self.auto_scale)
        glTranslatef(-self.model_center[0], -self.model_center[1], -self.model_center[2])

        # ✅ 相机操作（交互）
        glTranslatef(self.pan_x, self.pan_y, -self.camera_distance)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        glColor3f(1.0, 1.0, 1.0)
        self.draw_model()
        glutSwapBuffers()



    def update(self):
        self.angle += 0.5
        glutPostRedisplay()

    def draw_model(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_TRIANGLES)
        has_texcoord = len(self.texcoords) > 0
        for face in self.faces:
            for idx in face:
                if has_texcoord and idx < len(self.texcoords):
                    glTexCoord2f(self.texcoords[idx][0], self.texcoords[idx][1])
                glVertex3fv(self.vertices[idx])
        glEnd()

    def on_mouse(self, button, state, x, y):
        if state == GLUT_DOWN:
            self.last_mouse_button = button
            self.last_mouse_pos = (x, y)

        if button == 3:  # 滚轮上
            self.camera_distance = max(1.0, self.camera_distance - 0.5)
            print(f"[Zoom In] camera_distance = {self.camera_distance:.2f}")
        elif button == 4:  # 滚轮下
            self.camera_distance += 0.5
            print(f"[Zoom Out] camera_distance = {self.camera_distance:.2f}")

    def on_motion(self, x, y):
        if self.last_mouse_pos is None:
            return

        dx = x - self.last_mouse_pos[0]
        dy = y - self.last_mouse_pos[1]

        if self.last_mouse_button == GLUT_LEFT_BUTTON:
            self.rotation_y += dx * 0.5
            print(f"[Rotate] rotation_y = {self.rotation_y:.2f}")
        elif self.last_mouse_button == GLUT_RIGHT_BUTTON:
            self.pan_x += dx * 0.01
            self.pan_y -= dy * 0.01
            print(f"[Pan] pan_x = {self.pan_x:.2f}, pan_y = {self.pan_y:.2f}")

        self.last_mouse_pos = (x, y)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Satellite Model")

    window = OpenGLWindow(
        'models/satellite/10477_Satellite_v1_L3.obj',
        'models/satellite/10477_Satellite_v1_Diffuse.jpg'
    )
    window.initialize()

    glutDisplayFunc(window.draw)
    glutIdleFunc(window.update)
    glutMouseFunc(window.on_mouse)
    glutMotionFunc(window.on_motion)
    glutMainLoop()

if __name__ == "__main__":
    main()
