import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import requests

class Ui_Dialog(QDialog):

    def __init__(self):
        super(Ui_Dialog, self).__init__()
        loadUi("tester.ui", self)
        self.getInput()

    def getInput(self):
        lat, lon = 51.641331,-0.738161
        API = "a4d93bcbeefcfb2df57940dcfe7f61ee"
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API}&units=metric"
        res = requests.get(url)

        data = res.json()
        city = data["name"]
        description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        self.cityDisplay.setText(city)
        self.descriptionDisplay.setText(description)
        self.tempDisplay.setText(str(temperature)+"°C")


if __name__ == "__main__":
   app = QApplication(sys.argv)
   ui = Ui_Dialog()
   ui.show()
   sys.exit(app.exec_())