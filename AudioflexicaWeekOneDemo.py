import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
from opensimplex import OpenSimplex
import pyaudio
import struct
import wave

class Mesh(object):
    def __init__(self):
        """
        Create the view graphics and window
        """
        
        #set up the window
        self.app = QtGui.QApplication(sys.argv)
        self.view = gl.GLViewWidget()
        self.view.show()
        self.view.setWindowTitle("Audioflexica")
        # self.view.setCameraPosition(pos=(1000,0,0), elevation=30)
        # self.view.setCameraPosition(pos=(0,0,0), distance=200, elevation=30)
        # self.view.setGeometry(0, 0, 1280, 800)
        # self.view.opts['viewport'] = (0, 0, 2560, 1600)
        
        self.RATE = 24000
        self.CHUNK = 1024
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        self.noise = OpenSimplex()
        self.offSet = 0
        self.audioData = None
        
        verts = np.array([[x, y, 1.5 * self.noise.noise2d(i, j)] 
        for i, x in enumerate(range(-16, 16)) 
        for j, y in enumerate(range(-16, 16))], dtype=np.float32)
        
        faces = []
        for row in range(31):
            for col in range(31):
                faces.append([32 * row + col, 32 * row + col + 1, 32 * (row + 1) + col])
                faces.append([32 * (row + 1) + col + 1, 32 * row + col + 1, 32 * (row + 1) + col])
        
        colors = []
        for i in range(32):
            for j in range(32):
                colors.append([float(i) / float(32), float(j) / float(32), 1 - float(i) / float(32), 1])
                
        faces = np.array(faces)
        colors = np.array(colors)
        
        self.mesh = gl.GLMeshItem(
            vertexes=verts,faces=faces,
            smooth=True, drawEdges=True,
            vertexColors=colors
        )
        self.mesh.setGLOptions("additive")
        self.view.addItem(self.mesh)
    
    def update(self):
        """
        Updates the grid
        """
        self.audioData = self.stream.read(self.CHUNK, exception_on_overflow = False)
        
        if self.audioData is not None:
            self.audioData = struct.unpack(str(2 * self.CHUNK) + 'B', self.audioData)
            self.audioData = np.array(self.audioData, dtype='b')[::2] + 128
            self.audioData = np.array(self.audioData, dtype='int32') - 128
            self.audioData = self.audioData * 0.04
            self.audioData = self.audioData.reshape(32, 32)
        else:
            self.audioData = np.array([1] * 1024)
            self.audioData = self.audioData.reshape(32, 32)
        
        verts = np.array([[x, y, self.audioData[i][j] * self.noise.noise2d(i + self.offSet, j + self.offSet)] 
        for i, x in enumerate(range(-16, 16)) 
        for j, y in enumerate(range(-16, 16))], dtype=np.float32)
        
        faces = []
        for row in range(31):
            for col in range(31):
                faces.append([32 * row + col, 32 * row + col + 1, 32 * (row + 1) + col])
                faces.append([32 * (row + 1) + col + 1, 32 * row + col + 1, 32 * (row + 1) + col])
        
        colors = []
        for i in range(32):
            for j in range(32):
                colors.append([float(i) / float(32), float(j) / float(32), 1 - float(i) / float(32), 1])
                
        faces = np.array(faces)
        colors = np.array(colors)
        
        self.mesh.setMeshData(vertexes = verts, faces=faces, 
        vertexColors = colors, smooth = True, drawEdges = True)
        
        self.offSet -= 0.1
        
    
    def start(self):
        """
        Start off the screen
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
            
    def animation(self):
        """
        Animates mesh
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()
        self.update()
        

if __name__ == '__main__':
    mesh = Mesh()
    mesh.animation()
        
