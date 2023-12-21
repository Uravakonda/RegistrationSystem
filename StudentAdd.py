import cv2
import dlib
import sqlite3
import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from datetime import datetime
from pygrabber.dshow_graph import FilterGraph

class StudentAdd(QDialog):

    def __init__(self):
        super(StudentAdd,self).__init__()
        loadUi("studentAdd.ui",self)
        self.registerbtn.clicked.connect(self.startFeed)
        self.infobar.setText("Hey! Add the Student's Information To Begin")
        now = datetime.now()
        day = now.strftime("%d-%m-%Y")
        self.datebar.setText(day)
        self.back.clicked.connect(self.goback)
        self.updatecamlist()
    def startFeed(self):
        name = self.studentname.text()
        ID = self.ID.text()
        DOB = self.DOB.text()
        form = self.Form.text()
        house = self.House.text()
        subone = self.subone.text()
        subtwo = self.subtwo.text()
        subthree = self.subthree.text()
        subfour = self.subfour.text()
        if name == "" or ID == "" or DOB =="" or form == "" or house =="" or subone == ""or subtwo == ""or subthree == ""or subfour == "":
            self.infobar.setText("Please Fill In All The Information, Thank You!")
        else:
            idlist = self.getsubjectid(subone,subtwo,subthree,subfour)
            subjectids = [item[0] for item in idlist]
            connection = sqlite3.connect("system.db")
            query = connection.cursor()
            record = [ID,name,DOB,form,house]
            query.execute("INSERT INTO student (StudentID,Name,DOB,Form,House) VALUES (?,?,?,?,?)",record)
            idone = str(subjectids[0])+str(ID)
            query.execute("INSERT INTO studentsubject VALUES (?,?,?)",(idone, ID,subjectids[0]))
            idtwo = str(subjectids[1])+str(ID)
            query.execute("INSERT INTO studentsubject VALUES (?,?,?)",(idtwo, ID,subjectids[1]))
            idthree = str(subjectids[2])+str(ID)
            query.execute("INSERT INTO studentsubject VALUES (?,?,?)",(idthree, ID,subjectids[2]))
            idfour = str(subjectids[3])+str(ID)
            query.execute("INSERT INTO studentsubject VALUES (?,?,?)",(idfour, ID,subjectids[3]))
            connection.commit()
            connection.close()

            cam = int(self.camselect.currentText().split(" ")[-1].strip("()"))
            capturing = cv2.VideoCapture(cam)
            facedetection =dlib.get_frontal_face_detector()                                                                 #loads face detector
            shaper = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")                                          #face recognition model file, has numbers for different points on face
            modeltwo = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")                          #face recognition model file
            embeddingid = 0
            positions = ["front","right","left","up","down","smile"]                                                        #this is the beginning of the head positioning instructions
            for i in positions:
                if i =="up" or i== "down":
                    self.infobar.setText("Please look "+i)
                elif i == "front":
                    self.infobar.setText("Please face the front")
                elif i =="right" or i == "left":
                    self.infobar.setText("Please turn to your "+i)
                elif i =="smile":
                    self.infobar.setText("Please Look Front and "+i)
                for a in range(2):                                                                                          #loop to take 2 pictures of each position of student
                    ret,frame = capturing.read()
                    if not ret:
                        break
                    cv2.imshow("Video Feed",frame)                                                                          #displays feed
                    cv2.moveWindow("Video Feed",983,381)
                    grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)                                                           #converts image to greyscale in order to detect faces
                    matches = facedetection(grey,0)
                    embeddingid = embeddingid + 1
                    for j in matches:
                        shape =shaper(grey,j)
                        faceprint =modeltwo.compute_face_descriptor(frame,shape)
                        ID = self.ID.text()
                        self.saveStudent(embeddingid,int(ID),faceprint)                                                     #calls method "saveStudent"
                    cv2.waitKey(3000)
            capturing.release()
            cv2.destroyAllWindows()
            self.infobar.setText("Student Registered. You Can Now Add Another!")
    def saveStudent(self,value,ID,faceprint):
        connection = sqlite3.connect("system.db")
        query = connection.cursor()
        stringfaceprint = ",".join(map(str,faceprint))                                                                      #converts faceprint embedding to string and joins with comma
        query.execute("INSERT INTO embeddings VALUES (?,?,?)",(value,ID,stringfaceprint))                                   #inserts faceprints into database
        connection.commit()
        connection.close()

    def getsubjectid(self,subone,subtwo,subthree,subfour):
        connection = sqlite3.connect("system.db")
        cursor = connection.cursor()
        query = ("SELECT SubjectID FROM subject WHERE SubjectName = ? OR SubjectName = ? OR SubjectName = ? OR SubjectName = ?")
        cursor.execute(query,(subone,subtwo,subthree,subfour,))
        results = cursor.fetchall()
        connection.close()
        return results

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
        # Get the list of available ports
        resultcams = self.list_ports()
        # Add the available ports to the dropdown
        for port,name in resultcams.items():
            self.camselect.addItem(f"{name} ({port})")

    def goback(self):
        self.close()

#if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #welcome = StudentAdd()
    #widget = QStackedWidget()
    #widget.addWidget(welcome)
    #widget.setFixedHeight(750)
    #widget.setFixedWidth(1500)
    #widget.show()
    #sys.exit(app.exec_())