import sys, json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
)

BROKER = "broker.hivemq.com"
PORT = 1883

# Topics
PUMP_CMD = "aquarium/pump"
PUMP_STATUS = "aquarium/pump/status"
LAMP_CMD = "aquarium/lamp"
LAMP_STATUS = "aquarium/lamp/status"

class AquariumGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🐟 Smart Aquarium Dashboard")
        self.resize(500, 450)

        layout = QVBoxLayout()

        # Sensor displays
        self.temp_lbl = QLabel("Temp: -- °C")
        self.water_lbl = QLabel("Water Level: -- %")
        self.feed_lbl = QLabel("Feeder: --")

        # Pump
        self.pump_lbl = QLabel("Pump: waiting for status…")
        pump_btns = QHBoxLayout()
        btn_pump_on = QPushButton("Pump ON")
        btn_pump_off = QPushButton("Pump OFF")
        btn_pump_auto = QPushButton("Pump AUTO")
        btn_pump_on.clicked.connect(lambda: client.publish(PUMP_CMD, "ON"))
        btn_pump_off.clicked.connect(lambda: client.publish(PUMP_CMD, "OFF"))
        btn_pump_auto.clicked.connect(lambda: client.publish(PUMP_CMD, "AUTO"))
        pump_btns.addWidget(btn_pump_on)
        pump_btns.addWidget(btn_pump_off)
        pump_btns.addWidget(btn_pump_auto)

        # Lamp
        self.lamp_lbl = QLabel("Lamp: waiting for status…")
        lamp_btns = QHBoxLayout()
        btn_lamp_on = QPushButton("Lamp ON")
        btn_lamp_off = QPushButton("Lamp OFF")
        btn_lamp_auto = QPushButton("Lamp AUTO")
        btn_lamp_on.clicked.connect(lambda: client.publish(LAMP_CMD, "ON"))
        btn_lamp_off.clicked.connect(lambda: client.publish(LAMP_CMD, "OFF"))
        btn_lamp_auto.clicked.connect(lambda: client.publish(LAMP_CMD, "AUTO"))
        lamp_btns.addWidget(btn_lamp_on)
        lamp_btns.addWidget(btn_lamp_off)
        lamp_btns.addWidget(btn_lamp_auto)

        
        # Alarm display
        self.alarm_lbl = QLabel("Alarms: None")
        self.alarm_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: darkred;")

        # Add widgets to layout
        layout.addWidget(self.temp_lbl)
        layout.addWidget(self.water_lbl)
        layout.addWidget(self.feed_lbl)
        layout.addWidget(self.pump_lbl)
        layout.addLayout(pump_btns)
        layout.addWidget(self.lamp_lbl)
        layout.addLayout(lamp_btns)
        layout.addWidget(self.alarm_lbl)

        self.setLayout(layout)

    # Update methods
    def update_temp(self, temp): 
        self.temp_lbl.setText(f"Temp: {temp} °C")

    def update_water(self, lvl): 
        self.water_lbl.setText(f"Water Level: {lvl} %")

    def update_feed(self, state): 
        if state.lower() == "pressed":
            self.feed_lbl.setText("Feeder: PRESSED")
            self.feed_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
        elif state.lower() == "released":
            self.feed_lbl.setText("Feeder: RELEASED")
            self.feed_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
        else:
            self.feed_lbl.setText(f"Feeder: {state}")
            self.feed_lbl.setStyleSheet("font-size: 14px; color: black;")

    def update_alarm(self, text): 
        self.alarm_lbl.setText(f"ALARM: {text}")

    def update_pump(self, status_json):
        try:
            status = json.loads(status_json)
            mode = status.get("mode", "AUTO")
            state = status.get("state", "OFF")
        except:
            mode, state = "AUTO", "OFF"

        self.pump_lbl.setText(f"Pump: {state} ({mode})")

        # 4-state color coding
        if mode == "AUTO" and state == "ON":
            self.pump_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        elif mode == "AUTO" and state == "OFF":
            self.pump_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        elif mode == "MANUAL" and state == "ON":
            self.pump_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        elif mode == "MANUAL" and state == "OFF":
            self.pump_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: darkred;")

    def update_lamp(self, status_json):
        try:
            status = json.loads(status_json)
            mode = status.get("mode", "AUTO")
            state = status.get("state", "OFF")
        except:
            mode, state = "AUTO", "OFF"

        self.lamp_lbl.setText(f"Lamp: {state} ({mode})")

        # 4-state color coding
        if mode == "AUTO" and state == "ON":
            self.lamp_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: yellow;")
        elif mode == "AUTO" and state == "OFF":
            self.lamp_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        elif mode == "MANUAL" and state == "ON":
            self.lamp_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        elif mode == "MANUAL" and state == "OFF":
            self.lamp_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: darkred;")

# MQTT callbacks
def on_message(client, userdata, msg):
    data = msg.payload.decode().strip()
    if msg.topic == "aquarium/temp":
        try: gui.update_temp(json.loads(data)["temp"])
        except: pass
    elif msg.topic == "aquarium/water_level":
        try: gui.update_water(json.loads(data)["level"])
        except: pass
    elif msg.topic == "aquarium/feed":
        gui.update_feed(data)
    elif msg.topic == PUMP_STATUS:
        gui.update_pump(data)
    elif msg.topic == LAMP_STATUS:
        gui.update_lamp(data)
    elif msg.topic == "aquarium/alarm":
        gui.update_alarm(data)

client = mqtt.Client()
client.on_message = on_message

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AquariumGUI()
    gui.show()

    client.connect(BROKER, PORT, 60)
    client.subscribe("aquarium/#")
    client.loop_start()

    sys.exit(app.exec_())
