import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
from opensimplex import OpenSimplex

class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh
        """

        # setup the view window
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setGeometry(500, 1000, 1280, 800)
        print(self.w.width(), self.w.rect())
        # self.w.resizeGL(1080, 720)
        self.w.show()
        self.w.setWindowTitle('Terrain')
        self.w.setCameraPosition(distance=30, elevation=8)
        
        # constants and arrays
        self.nsteps = 1
        self.ypoints = range(-20, 22, self.nsteps)
        self.xpoints = range(-20, 22, self.nsteps)
        self.nfaces = len(self.ypoints)
        self.offset = 0
        self.smoothness = 100
        self.colorVal = 0
        
        # perlin noise object
        self.tmp = OpenSimplex()

        # create the veritices array
        verts = np.array([
            [
                x, y, 1.5 * self.tmp.noise2d(x=n / self.smoothness, y=m / self.smoothness)
            ] for n, x in enumerate(self.xpoints) for m, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        # create the faces and colors arrays
        faces = []
        colors = []
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([1, 1, 1, 0.7])
                colors.append([1, 0, 1, 0.8])

        faces = np.array(faces)
        colors = np.array(colors)

        # create the mesh item
        self.m1 = gl.GLMeshItem(
            vertexes=verts,
            faces=faces, faceColors=colors,
            smooth=True, drawEdges=True,
        )
        self.m1.setGLOptions('additive')
        self.w.addItem(self.m1)
        
        grid = gl.GLGridItem()
        grid.scale(2, 2, 2)
        self.w.addItem(grid)
        
    def update(self):
        """
        update the mesh and shift the noise each time
        """
        verts = np.array([
            [
                x, y, 2.5 * self.tmp.noise2d(x=n / self.smoothness + self.offset, y=m / self.smoothness + self.offset)
            ] for n, x in enumerate(self.xpoints) for m, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        faces = []
        colors = []
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([self.colorVal, self.colorVal, self.colorVal, 0.7])
                colors.append([self.colorVal, self.colorVal, self.colorVal, 0.8])
                
                # print([float(n) / self.nfaces, float(1 - n) / self.nfaces, float(m) / self.nfaces, 0.7])
                # print([self.colorVal, float(1 - n) / self.nfaces, float(m) / self.nfaces, 0.7])
        
        self.colorVal += 0.01
        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)
        print([self.colorVal, self.colorVal, self.colorVal, 0.7])

        self.m1.setMeshData(
            vertexes=verts, faces=faces, faceColors=colors
        )
        self.offset -= 0
        
        print(self.colorVal)
        # self.smoothness = (self.smoothness + 1) % 100 + 1
    
    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
            
    def animation(self):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1000)
        self.start()
        self.update()
            
if __name__ == '__main__':
    t = Terrain()
    t.animation()
