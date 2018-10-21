import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
from opensimplex import OpenSimplex
import pyaudio

class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh
        """

        # setup the view window
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        print(1, self.w.width(), self.w.height())
        self.w.show()
        self.w.setWindowTitle('Terrain')
        self.w.setCameraPosition(pos=(0,0,0), distance=200, elevation=30)
        self.w.setGeometry(0, 0, 1280, 800)
        self.w.pan(-70, -15, 0)
        self.w.opts['viewport'] =  (0, 0, 2560, 1600)
        # self.w.setFixedSize(WidthOfParent, HeightOfParent)
        
        # constants and arrays
        self.nsteps = 1
        self.ypoints = range(-20, 22, self.nsteps)
        self.xpoints = range(-20, 22, self.nsteps)
        self.nfaces = len(self.ypoints)
        self.offset = 0
        self.smoothness = 1000
        self.colorVal = 0
        
        # perlin noise object
        self.tmp = OpenSimplex()

        # create the veritices array
        verts = np.array([
            [
                x, y, 1.5 * self.tmp.noise2d(x=float(n) / float(self.smoothness), y=float(m) / float(self.smoothness))
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
        
        # grid = gl.GLGridItem()
        # # grid.setSize(10, 10, 10)
        # grid.scale(2, 2, 2)
        # self.w.addItem(grid)
        # print(grid.size())
        
    def update(self):
        """
        update the mesh and shift the noise each time
        """
        verts = np.array([
            [
                x, y, 2.5 * self.tmp.noise2d(x=n / 3 + self.offset, y=m / 3 + self.offset)
            ] for n, x in enumerate(self.xpoints) for m, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        faces = []
        colors = []
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([1,0,0,0.7])
                colors.append([0,1,0,0.7])
                # colors.append([float(n) / float(self.nfaces), float(1 - n) / float(self.nfaces), float(m) / float(self.nfaces), 0.7])
                # colors.append([float(n) / float(self.nfaces), float(1 - n) / float(self.nfaces), float(m) / float(self.nfaces), 0.8])
                
                # print([float(n) / self.nfaces, float(1 - n) / self.nfaces, float(m) / self.nfaces, 0.7])
                # print([self.colorVal, float(1 - n) / self.nfaces, float(m) / self.nfaces, 0.7])
        
        self.colorVal += 0.01
        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)
        # print([self.colorVal, self.colorVal, self.colorVal, 0.7])

        self.m1.setMeshData(
            vertexes=verts, faces=faces, faceColors=colors
        )
        
        # print(self.colorVal)
        # self.smoothness = (self.smoothness + 1) % 100 + 1
        # self.offset -= 0.18
    
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
        timer.start(10)
        self.start()
        self.update()
            
if __name__ == '__main__':
    t = Terrain()
    t.animation()
    # CHUNK_SIZE = 1024
    # FORMAT = pyaudio.paInt16
    # RATE = 80000
    # 
    # p = pyaudio.PyAudio()
    # output = p.open(format=FORMAT,
    #                         channels=1,
    #                         rate=RATE,
    #                         input=True,
    #                         output=True,
    #                         frames_per_buffer=CHUNK_SIZE) # frames_per_buffer=CHUNK_SIZE
    # with open('Redbone.wav', 'rb') as fh:
    #     while fh.tell() != 50000: # get the file-size from the os module
    #         AUDIO_FRAME = fh.read(CHUNK_SIZE)
    #         print(len(AUDIO_FRAME))
    #         output.write(AUDIO_FRAME)
