import cv2
import dlib
import numpy as np
import sqlite3
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from datetime import datetime
import random
from pygrabber.dshow_graph import FilterGraph

class videoFeed(QDialog):

    def __init__(self):                                                                                                 #constructor
        super(videoFeed,self).__init__()
        loadUi("videoFeed.ui", self)
        self.startVid.clicked.connect(self.startfeed)
        self.markin.clicked.connect(lambda: self.registerstudent("In"))                                                 #button connects to "registerstudent"
        self.markout.clicked.connect(lambda: self.registerstudent("Out"))                                               #button connects to "registerstudent"
        self.infobar.setText("Hey, Please Begin When Ready!")
        self.label.setPixmap(QPixmap("LogoSmall.png"))
        timer = QTimer(self)
        timer.timeout.connect(self.Clock)
        timer.start(1000)
        now = datetime.now()
        day = now.strftime("%d-%m-%Y")
        self.datebar.setText(day)
        self.back.clicked.connect(self.goback)
        self.updatecamlist()
    def startfeed(self):
        self.name = None
        cam = int(self.camselect.currentText().split(" ")[-1].strip("()"))
        capturing = cv2.VideoCapture(cam)
        faceDetection =dlib.get_frontal_face_detector()                                                                 #loads the face detector
        faceshaper = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")                                      #face recognition model file, has numbers for different points on face
        modeltwo = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")                          #face recognition model file
        self.infobar.setText("I Am Analysing Your Face Now...")
        self.startVid.setText("PRESS 'x' TO STOP VIDEO")
        while True:
            ret,frame = capturing.read()                                                                                #captures frame from video feed
            frame = cv2.flip(frame, 1)
            if not ret:
                break                                                                                                   #breaks out of loop when video feed ends
            grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)                                                               #converts frame to greyscale
            matches =faceDetection(grey,0)                                                                              #rectangles of interest of face are returned
            for i in matches:
                assigner = faceshaper(grey,i)                                                                           #assigns numbers for different points of face
                face_descriptor = modeltwo.compute_face_descriptor(frame,assigner)
                studentname =self.studentfaces(face_descriptor)                                                         #connects to "studentfaces" method to recognise a student's face from database
                cv2.putText(frame,studentname,(i.left(),i.top()-10),cv2.FONT_HERSHEY_DUPLEX,0.9,(0,0,180),2)            #displays name of student

            cv2.imshow("Video Feed",frame)                                                                              #shows video feed
            cv2.moveWindow("Video Feed",633,110)                                                                        #centres video feed
            cv2.setWindowProperty("Video Feed",cv2.WND_PROP_TOPMOST,1)                                                  #pins video feed window
            if cv2.waitKey(1) &0xFF == ord("x"):                                                                        #video feed closes when "x" is pressed
                self.infobar.setText("Start the Video When You Are Ready Again!")
                self.startVid.setText("START REGISTRY")
                break
        capturing.release()
        cv2.destroyAllWindows()
    def studentfaces(self,faceprint):
        connection =sqlite3.connect("system.db")
        query = connection.cursor()
        query.execute("SELECT * FROM embeddings")                                                                       #selects all faces in database
        results =query.fetchall()
        minimumdistance= float("inf")                                                                                   #sets minimum face distance to infinity
        self.name = None
        for i in results:
            systemfaceprint =np.fromstring(i[2],dtype=float,sep=",")                                                    #converts face embeddings in database to array of floats to use
            distance = np.linalg.norm(faceprint -systemfaceprint)                                                       #calculates distance between faceprint in video feed and existing faceprint
                                                                                                                        #if distance is small, they are similar
            if distance < minimumdistance:
                minimumdistance = distance
                studentid = i[1]
                self.name = self.studentnamefind(studentid)

        thresholdValue = 0.4                                                                                            #face recognition threshold value (how small does distance have to be)
        if minimumdistance > thresholdValue:
            self.name = "Unknown"                                                                                       #assigns "Unknown" to a student not on the system
        connection.close()
        return self.name
    def registerstudent(self,status):
        if self.name is None:
            self.infobar.setText("No Face Has Been Recognised")                                                         #sets error message if there is no face but button is pressed
            return
        elif self.name == "Unknown":
            self.infobar.setText("You Are Not In The System")                                                           #sets error message if an unknown student presses the button
            return
        else:
            registerid = random.randint(500,599)
            studentid = self.studentidfind(self.name)
            connection =sqlite3.connect("system.db")                                                                    #connects to register database
            query = connection.cursor()
            current = datetime.now()
            date =current.strftime("%Y-%m-%d")                                                                          #retrieves current date
            time = current.strftime("%H:%M:%S")                                                                         #retrieves current time
            record = [str(registerid),studentid,time,date,status]
            query.execute("INSERT INTO register (RegisterID,StudentID,Time,Date,Status) VALUES (?,?,?,?,?)",record)     #update the register
            connection.commit()
            connection.close()
            if status == "In":
                self.infobar.setText("You Have Marked In "+self.name)
            elif status == "Out":
                self.infobar.setText("You Have Marked Out "+self.name)
    def studentnamefind(self,id):
        connection = sqlite3.connect("system.db")
        cursor = connection.cursor()
        query = "SELECT Name FROM student WHERE StudentID = ?"
        cursor.execute(query,(id,))
        name = cursor.fetchone()
        connection.close()
        return name[0]

    def studentidfind(self,name):
        connection = sqlite3.connect("system.db")
        cursor = connection.cursor()
        query = "SELECT StudentID FROM student WHERE Name = ?"
        cursor.execute(query,(name,))
        id = cursor.fetchone()
        connection.close()
        return id[0]

    def Clock(self):
        currenttime = QTime.currentTime()
        clocklabel = currenttime.toString("hh:mm:ss")
        self.clock.setText(clocklabel)

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


#if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #welcome = videoFeed()
    #widget = QStackedWidget()
    #widget.addWidget(welcome)
    #widget.setFixedHeight(750)
    #widget.setFixedWidth(1500)
    #widget.show()
    #sys.exit(app.exec_())