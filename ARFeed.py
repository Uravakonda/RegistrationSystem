import cv2
import cv2.aruco as aruco
import numpy as np
from PyQt5.uic import loadUi
from pygrabber.dshow_graph import FilterGraph
from PyQt5.QtWidgets import QDialog

class ARFeature(QDialog):

    def __init__(self):
        super(ARFeature,self).__init__()
        loadUi("ARFeed.ui",self)
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters()
        self.impulsebtn.clicked.connect(self.showimpulse)
        self.pendbtn.clicked.connect(self.showpendulum)
        self.circuitbtn.clicked.connect(self.showcircuits)
        self.template = None
        self.runbtn.clicked.connect(self.run)
        self.back.clicked.connect(self.goback)
        self.updatecamlist()

    def showimpulse(self):
        self.template = cv2.imread("Images/wallball.png")
    def showpendulum(self):
        self.template = cv2.imread("Images/pendulum.png")
    def showcircuits(self):
        self.template = cv2.imread("Images/Circuits.png")

    def run(self):
        cam = int(self.camselect.currentText().split(" ")[-1].strip("()"))                                              #camera chosen from menu box is used
        self.cap = cv2.VideoCapture(cam)
        self.runbtn.setText("PRESS 'x' TO STOP VIDEO")
        while True:
            ret,frame =self.cap.read()                                                                                  #each frame is read
            grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)                                                               #frame is converted to greyscale for algorithm
            corners,ids,rejectedImgPoints = aruco.detectMarkers(grey,self.aruco_dict,parameters=self.parameters)        #ArUco marker is detected (correct marker from 6x6_250 markers is used)

            if np.all(ids is not None) and self.template is not None:                                                   #checks to see if a marker is detected
                for i in corners:
                    cv2.polylines(frame,[np.int32(i)],True,(0,255,0),3)                                                 #identifies box to put image in

                    #The diagram image is fitted to the marker
                    dst_pts = i[0].astype("float32")
                    src_pts = np.array([[0,0],[self.template.shape[1] -1,0],[self.template.shape[1]-1,self.template.shape[0]-1],[0,self.template.shape[0]-1]],dtype="float32")
                    M, _ = cv2.findHomography(src_pts,dst_pts)
                    warped = cv2.warpPerspective(self.template,M,(frame.shape[1],frame.shape[0]))
                    mask = np.zeros((frame.shape[0],frame.shape[1]),dtype="uint8")
                    cv2.fillConvexPoly(mask,dst_pts.astype("int32"),(255,))

                    frame = cv2.bitwise_and(frame,frame,mask=cv2.bitwise_not(mask))                                     #the frame of the image created is loaded on the screen
                    frame = cv2.bitwise_or(frame,warped)
            cv2.imshow("Teacher's Diagram",frame)                                                                       #Display the video frame
            cv2.moveWindow("Teacher's Diagram",633,110)                                                                 #centres video feed
            cv2.setWindowProperty("Teacher's Diagram",cv2.WND_PROP_TOPMOST,1)                                           #pins video feed window

            if cv2.waitKey(1)& 0xFF == ord("x"):                                                                        #Video stops if "x" is pressed
                break
        self.cap.release()
        cv2.destroyAllWindows()
        self.runbtn.setText("SHOW VIDEO")

    def list_ports(self):
        fg = FilterGraph()
        devices =fg.get_input_devices()
        resultcams = {}
        for i,device_name in enumerate(devices):
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                is_reading,img = cam.read()
                if is_reading:
                    resultcams[i] =device_name
            cam.release()
        return resultcams

    def updatecamlist(self):
        resultcams = self.list_ports()                                                                                  #lists available cameras to use
        for port,name in resultcams.items():                                                                            #adds name of cameras to menu box
            self.camselect.addItem(f"{name} ({port})")

    def goback(self):
        self.close()