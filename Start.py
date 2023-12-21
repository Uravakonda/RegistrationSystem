import hashlib
import time
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import sys
from PyQt5 import QtWidgets
from StudentAdd import StudentAdd
from AddWindows import addTeacher,addSubject
from VideoFeed import videoFeed
from TeacherPortal import TeacherPortal
import sqlite3
import nltk
from nltk.chat.util import Chat,reflections
import speech_recognition as sr

class Start(QDialog):
    def __init__(self):
        super(Start,self).__init__()
        loadUi("startPage.ui",self)
        self.label.setPixmap(QPixmap("LogoSmall.png"))
        self.micbox.addItems(self.getmics())
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginuser)

    def loginuser(self):
        username = self.username.text()
        password = self.password.text()
        hashval = hashlib.sha256()
        hashval.update(password.encode())
        hashpassword = hashval.hexdigest()

        if len(username)==0 and len(password)==0:
            self.usererror.setText("Please Fill In All Fields")
            self.passerror.setText("Please Fill In All Fields")
        elif len(username)==0:
            self.usererror.setText("Please Add The Username")
        elif len(password)==0:
            self.passerror.setText("Please Add The Password")
        elif username == "admin" and password == "admin":
            adminPage = Admin()
            widget.addWidget(adminPage)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            connection = sqlite3.connect("system.db")
            cursor = connection.cursor()
            query = "SELECT Password,VoicePrint FROM teacher WHERE Username = ?"
            cursor.execute(query,(username,))
            result = cursor.fetchone()
            connection.close()
            if result is None:
                self.usererror.setText("The Username Is Incorrect")
                self.passerror.setText("")
            else:
                result_pass =result[0]
                result_voiceprint = result[1]
                if result_pass == hashpassword:
                    self.infobar.setText("Say Something, I Am Listening...")
                    voiceprint = self.recordvoice(self.micbox.currentIndex())
                    if voiceprint == result_voiceprint:
                        menuPage = Menu()
                        widget.addWidget(menuPage)
                        widget.setCurrentIndex(widget.currentIndex()+1)
                    else:
                        self.infobar.setText("The Voice ID Is Incorrect")
                        self.usererror.setText("")
                else:
                    self.passerror.setText("The Password Is Incorrect")
                    self.usererror.setText("")

    def recordvoice(self,index):
        r = sr.Recognizer()
        with sr.Microphone(device_index=index) as source:
            audio = r.record(source,duration=4)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            self.infobar.setText("Sorry, Try Say That Again Please")
        except sr.RequestError:
            self.infobar.setText("Speech Recognition Not Available!")

    def getmics(self):
        list = sr.Microphone.list_microphone_names()
        return list

class Admin(QDialog):
    def __init__(self):
        super(Admin,self).__init__()
        loadUi("adminPage.ui",self)
        self.addstudent.clicked.connect(self.gotoaddstudent)
        self.addteacher.clicked.connect(self.gotoaddteacher)
        self.addsubject.clicked.connect(self.gotoaddsubject)
        self.back.clicked.connect(self.gotostart)

    def gotoaddstudent(self):
        self._new_window = StudentAdd()
        self._new_window.show()
    def gotoaddteacher(self):
        self._new_window = addTeacher()
        self._new_window.show()
    def gotoaddsubject(self):
        self._new_window = addSubject()
        self._new_window.show()
    def gotostart(self):
        startPage = Start()
        widget.addWidget(startPage)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class Menu(QDialog):
    def __init__(self):
        super(Menu,self).__init__()
        loadUi("menuPage.ui",self)
        self.regportal.clicked.connect(self.gotoreg)
        self.teachportal.clicked.connect(self.gototeach)
        #self.hwkportal.clicked.connect(self.gotohwk)
        #self.rgportal.clicked.connect(self.gotorg)
        self.infobar.setText("Welcome, you can ask me for help whenever!")
        self.search.clicked.connect(self.assistant)
        self.pairs = [
            ("what is this program",["This is a Registration System"]),
            ("(.*)registration(.*)",["That button will open the video feed for students to register"]),
            ("(.*)teacher(.*)",["That button will open a page, where you can view your lessons, or see some statistics"]),
            ("(.*)logout(.*)",["That button will make you go back to the start page!"]),
            ("(.*)log out(.*)", ["That button will make you go back to the start page!"]),
            ("(.*)what does this program do(.*)",["This is a Registration System"]),
            ("my name is (.*)",["welcome, %1"]),
            ("(hi|hello|hey)",["hello there","hi there","hey there"]),
            ("(.*)homework(.*)",["That button will open a page to let you set or edit homeworks"]),
            ("(.*)reports and grades(.*)",["That button will open a page to let you send reports, or view grades"]),
            ("(.*)help(.*)",["Ask me what buttons do, or what this program is, I can help you with anything!"]),
            ("(.*)your name(.*)",["My name is Assistant!"])
        ]
        self.chatbot = Chat(self.pairs,reflections)
        self.back.clicked.connect(self.gotostart)
    def gotoreg(self):
        self._new_window = videoFeed()
        self._new_window.show()

    def assistant(self):
        input =self.input.text()
        response = self.chatbot.respond(input)
        if response is None:
            response = "Sorry, I cannot help with that!"
        self.infobar.setText(response)
        self.input.clear()

    def gotostart(self):
        startPage = Start()
        widget.addWidget(startPage)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gototeach(self):
        tplogin = TPLogin()
        widget.addWidget(tplogin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class TPLogin(QDialog):
    def __init__(self):
        super(TPLogin,self).__init__()
        loadUi("TPLogin.ui",self)
        self.label.setPixmap(QPixmap("LogoMedium.png"))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginuser)
        self.back.clicked.connect(self.gotomenu)

    def loginuser(self):
        username = self.username.text()
        password = self.password.text()
        hashval = hashlib.sha256()
        hashval.update(password.encode())
        hashpassword = hashval.hexdigest()

        if len(username) == 0 and len(password) == 0:
            self.usererror.setText("Please Fill In All Fields")
            self.passerror.setText("Please Fill In All Fields")
        elif len(username) == 0:
            self.usererror.setText("Please Add The Username")
        elif len(password) == 0:
            self.passerror.setText("Please Add The Password")
        else:
            connection = sqlite3.connect("system.db")
            cursor = connection.cursor()
            query = "SELECT Password,TeacherID FROM teacher WHERE Username = ?"
            cursor.execute(query,(username,))
            result = cursor.fetchone()
            connection.close()
            if result is None:
                self.usererror.setText("The Username Is Incorrect")
                self.passerror.setText("")
            else:
                result_pass = result[0]
                resultID = result[1]
                if result_pass == hashpassword:
                    self._new_window = TeacherPortal(resultID)
                    self._new_window.show()
                else:
                    self.passerror.setText("The Password Is Incorrect")
                    self.usererror.setText("")

    def gotomenu(self):
        menuPage = Menu()
        widget.addWidget(menuPage)
        widget.setCurrentIndex(widget.currentIndex() + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    start = Start()
    widget = QStackedWidget()
    widget.addWidget(start)
    widget.setFixedHeight(750)
    widget.setFixedWidth(1500)
    widget.show()
    sys.exit(app.exec_())