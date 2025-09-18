# 🐟 Smart Aquarium - IoT_Smart_Home Project

This project simulates a smart aquarium control and monitoring system using **Python**, **MQTT**, and **PyQt5**.  
It includes sensors, relays, alarm logic, and a user-friendly GUI. Each component runs in its own terminal and communicates via MQTT.

---

## 📦 Components (run in separate terminals)

| File                      | Description                                  |
|---------------------------|----------------------------------------------|
| `aquarium_manager.py`     | Logs data, handles alarms, controls pump     |
| `water_level_sensor.py`   | Simulates water level changes                |
| `temp_sensor.py`          | Simulates aquarium temperature               |
| `lamp_relay.py`           | Controls the lamp relay                      |
| `pump_relay.py`           | Controls the pump relay                      |
| `feeder_button.py`        | Sends feeder events                          |
| `aquarium_gui.py`         | PyQt5 GUI dashboard                          |

---

## ▶️ How to Run (in this order)

Open a separate terminal for each component:

1. ✅ `aquarium_manager.py`  
   Starts the system and logs sensor data & alarms.

2. 🌊 `water_level_sensor.py`  
   Simulates water level. Increases when pump is ON, decreases when OFF.

3. 🌡️ `temp_sensor.py`  
   Simulates temperature depending on lamp state.

4. 💡 `lamp_relay.py`  
   Handles lamp auto/manual logic based on temperature.

5. 💧 `pump_relay.py`  
   Manages pump state based on water level and commands.

6. 🐟 `feeder_button.py`
   Click to send “feed” event to the system.

7. 🖥️ `aquarium_gui.py`  
   Displays real-time dashboard and allows control of pump/lamp.

---

## 💡 Dependencies

Install all requirements:

```bash
pip install -r requirements.txt

---

## 👩🏻‍💻 Credits

Built as part of an IoT course.

**Owners**: Or Dorbin & Karina Haimov
Thank You!

