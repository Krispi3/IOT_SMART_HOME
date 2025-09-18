import sys
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer

# MQTT Setup
client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)

class FeederApp(QWidget):
    def __init__(self):
        super().__init__()

        self.is_pressed = False
        self.time_left = 0

        # GUI window
        self.setWindowTitle("Aquarium Feeder Button")
        self.resize(300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Feeder state: released", self)
        layout.addWidget(self.label)

        self.button = QPushButton("Feed Fish", self)
        self.button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.button.clicked.connect(self.feed_fish)
        layout.addWidget(self.button)

        # Progress bar (visual timer)
        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(2000)  # 2000 ms = 2 sec
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        # Timer for countdown updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def feed_fish(self):
        if not self.is_pressed:  # only allow press if currently released
            self.is_pressed = True
            self.time_left = 2000  # 2 seconds in ms
            client.publish("aquarium/feed", "pressed")
            print("Feeder button: pressed")
            self.label.setText("Feeder state: pressed")

            # Start visual timer
            self.progress.setValue(2000)
            self.timer.start(100)  # update every 100ms

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 100
            self.progress.setValue(self.time_left)
        else:
            self.timer.stop()
            self.release_button()

    def release_button(self):
        self.is_pressed = False
        client.publish("aquarium/feed", "released")
        print("Feeder button: released")
        self.label.setText("Feeder state: released")
        self.progress.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    feeder = FeederApp()
    feeder.show()
    sys.exit(app.exec_())
