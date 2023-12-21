import hashlib
import time
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import sys
from PyQt5 import QtWidgets
import sqlite3
import requests
from ARFeed import ARFeature

class TeacherPortal(QDialog):
    def __init__(self,teacherid):
        super(TeacherPortal,self).__init__()
        loadUi("TeacherPortal.ui",self)
        self.teacherid = teacherid
        self.getWeather()
        self.displayName()
        self.back.clicked.connect(self.logout)
        self.diagram.clicked.connect(self.gotodiagram)

    def getWeather(self):
        lat, lon = 51.641331,-0.738161
        API = "a4d93bcbeefcfb2df57940dcfe7f61ee"
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API}&units=metric"
        res = requests.get(url)
        data = res.json()
        city = data["name"]
        description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        self.city.setText(city)
        self.description.setText(description)
        self.temp.setText(str(temperature)+"°C")

    def displayName(self):
        connection = sqlite3.connect("system.db")
        cursor = connection.cursor()
        query = "SELECT Username FROM teacher WHERE TeacherID = ?"
        cursor.execute(query, (self.teacherid,))
        result = cursor.fetchone()
        connection.close()
        if result is None:
            self.welcome.setText("WELCOME!")
        else:
            self.welcome.setText("WELCOME "+result[0])

    def gotodiagram(self):
        self._new_window = ARFeature()
        self._new_window.show()

    def logout(self):
        self.close()