from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtWidgets import QApplication, QTableView
import sqlite3
from PyQt5 import QtWidgets
from datetime import datetime
import hashlib
import speech_recognition as sr


class addTeacher(QDialog):
    def __init__(self):
        super(addTeacher,self).__init__()
        loadUi("teacherAdd.ui",self)
        now = datetime.now()
        day = now.strftime("%d-%m-%Y")
        self.datebar.setText(day)
        self.infobar.setText("You Can Add A Teacher Below!")
        self.micbox.addItems(self.getmics())
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.addteach.clicked.connect(self.createTeacher)
        self.back.clicked.connect(self.goback)


    def createTeacher(self):
        teacherid = self.teacherid.text()
        username = self.username.text()
        password = self.password.text()
        confirmpass = self.confirmpass.text()
        hashval = hashlib.sha256()
        hashval.update(password.encode())
        hashpassword = hashval.hexdigest()

        if len(teacherid) ==0 or len(username) == 0 or len(password)==0 or len(confirmpass)== 0:
            self.infobar.setText("Please Fill In All Details of the Teacher...")
            return
        elif password != confirmpass:
            self.infobar.setText("Please Make Sure The Passwords Match!")
            return
        else:
            self.verror.setText("Say Something, I Am Listening...")
            voiceprint = self.getvoice(self.micbox.currentIndex())
            connection = sqlite3.connect("system.db")
            cursor = connection.cursor()
            teacherinfo = [int(teacherid),username,hashpassword,voiceprint]
            cursor.execute("INSERT INTO teacher (TeacherID,Username,Password,VoicePrint) VALUES (?,?,?,?)",teacherinfo)
            connection.commit()
            connection.close()
            self.infobar.setText("I Have Added The Teacher's Details!")
            self.verror.setText("")
            return

    def goback(self):
        self.close()

    def getmics(self):
        list = sr.Microphone.list_microphone_names()
        return list

    def getvoice(self,index):
        self.verror.setText("Say Something, I Am Listening...")
        r = sr.Recognizer()
        with sr.Microphone(device_index=index) as j:
            self.verror.setText("Say Something, I Am Listening...")
            audio = r.record(j,duration=5)
        try:
            self.verror.setText("Say Something, I Am Listening...")
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            self.verror.setText("Sorry, I Did Not Understand That")
        except sr.RequestError:
            self.verror.setText("Speech Recognition Not Available!")

class addSubject(QDialog):
    def __init__(self):
        super(addSubject,self).__init__()
        loadUi("subjectAdd.ui",self)
        self.subjectView.setColumnWidth(0,60)
        self.subjectView.setColumnWidth(1,200)
        self.subjectView.setColumnWidth(2,355)
        self.loadtable()
        now = datetime.now()
        day = now.strftime("%d-%m-%Y")
        self.datebar.setText(day)
        self.infobar.setText("You Can Add A Subject Below!")
        self.back.clicked.connect(self.goback)

    def loadtable(self):
        connection = sqlite3.connect("system.db")
        cursor = connection.cursor()
        query = "SELECT * FROM subject"
        index = 0
        for i in cursor.execute(query):
            self.subjectView.insertRow(index)
            self.subjectView.setItem(index,0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.subjectView.setItem(index,1, QtWidgets.QTableWidgetItem(str(i[1])))
            self.subjectView.setItem(index,2, QtWidgets.QTableWidgetItem(str(i[2])))
            index = index + 1
        connection.close()

    def goback(self):
        self.close()



#if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #start = addTeacher()
    #widget = QStackedWidget()
    #widget.addWidget(start)
    #widget.setFixedHeight(750)
    #widget.setFixedWidth(1500)
    #widget.show()
    #sys.exit(app.exec_())