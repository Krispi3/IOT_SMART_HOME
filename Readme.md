# 🐠 Smart Aquarium – MQTT Demo (IOT_SMART_HOME)

A small **IoT smart-home aquarium simulator** built with **MQTT**, a **PyQt5 GUI**, a central **logic manager**, and **SQLite** logging.  
It runs emulator scripts for sensors and relays that talk via a public broker and lets you control equipment (pump/lamp) in **ON / OFF / AUTO** modes, raise alerts, and trigger feeding events.

> Last updated: 2025-09-18

---

## ✨ What it does

- **Temperature sensor** publishes readings and raises alarms when out of the safe range.

- **Water level sensor** simulates changes and toggles the **pump** automatically for safety.

- **Pump** and **Lamp relays** accept `ON`/`OFF`/`AUTO` commands and publish their status.

- **Feeder button** (a tiny GUI) publishes a feeding event.

- **Aquarium Manager** listens to all topics, writes **logs to SQLite**, and enforces safety automations.

- **Main GUI (PyQt5)** shows temperature, level, status, and alarms, and provides quick control buttons.

---

## 🧩 Architecture (overview)

```

[Temp Sensor] ─┐

[Water Level] ─┼──>  MQTT (broker.hivemq.com)  <── [Pump Relay]

[Feeder Button]┘                                  [Lamp Relay]

                      │

                [Aquarium Manager] ──> SQLite (iot.db)

                      │

                     GUI (PyQt5)

```

- MQTT traffic goes through the public broker `broker.hivemq.com:1883` (demo/learning only).

- All components publish/subscribe under `aquarium/#`.

---

## 🧰 Tech stack

- Python 3.10+

- [paho-mqtt](https://pypi.org/project/paho-mqtt/) for MQTT

- [PyQt5](https://pypi.org/project/PyQt5/) for the GUI

- SQLite (`iot.db`) for logs

> `requirements.txt` contains `paho-mqtt`. Install `PyQt5` as well (used by the GUI and some emulators).

---

## 📁 Project structure (expected)

```

smart_aquarium/

├─ data_manager/

│  └─ aquarium_manager.py      # central consumer/manager logic + SQLite logging

├─ emulators/

│  ├─ temp_sensor.py           # temperature sensor emulator

│  ├─ water_level_sensor.py    # water level sensor emulator

│  ├─ pump_relay.py            # pump relay (ON/OFF/AUTO + status)

│  ├─ lamp_relay.py            # lamp relay (ON/OFF/AUTO + status)

│  └─ feeder_button.py         # feeding button (small GUI)

├─ gui_app/

│  └─ aquarium_gui.py          # main PyQt5 GUI

├─ iot.db                      # SQLite log database

└─ requirements.txt

```

---

## 🔌 MQTT topics

**Commands & status**

- `aquarium/pump` ← commands: `ON` / `OFF` / `AUTO`

- `aquarium/pump/status` → human-friendly status (e.g., `ON (AUTO)`)

- `aquarium/lamp` ← commands: `ON` / `OFF` / `AUTO`

- `aquarium/lamp/status` → human-friendly status



**Sensors**

- `aquarium/temp` → `{ "temp": 23.5 }`

- `aquarium/water_level` → `{ "level": 72 }  # percent`



**Events**

- `aquarium/feed` → `pressed`/`released`

- `aquarium/alarm` → text message (e.g., `⚠️ TEMP_HIGH 30.8°C`)

---

## 🛠️ Setup

### Windows (recommended for GUI)

```bash

cd smart_aquarium

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

pip install PyQt5

```

### WSL (heads‑up: PyQt5 needs an X server)

```bash

cd smart_aquarium

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

pip install PyQt5

# For GUI under WSL: install an X server on Windows (e.g., VcXsrv) and set DISPLAY

```

> If the public broker is slow/unavailable, you may switch to `test.mosquitto.org:1883` in the code.

---

## 🚀 Run (multi‑terminal)

> Open several terminals in `smart_aquarium` with the virtualenv **activated**.



1) **Relays**

```bash

python emulators/pump_relay.py

python emulators/lamp_relay.py

```

2) **Sensors**

```bash

python emulators/temp_sensor.py

python emulators/water_level_sensor.py

```

3) **Manager (logic + logging)**

```bash

python data_manager/aquarium_manager.py

```

4) **User interfaces**

```bash

# Main GUI

python gui_app/aquarium_gui.py



# Feeding button (optional mini GUI)

python emulators/feeder_button.py

```

> Suggested order: Relays → Sensors → Manager → GUI. You can start/stop components independently.

---

## 🔎 Quick manual checks (no code changes)

If you have `mosquitto-clients`:

```bash

# Turn the pump ON

mosquitto_pub -h broker.hivemq.com -t aquarium/pump -m "ON"



# Watch all traffic

mosquitto_sub -h broker.hivemq.com -t "aquarium/#"

```

---

## 🗃️ Logs (SQLite)

- SQLite file: `iot.db`

- Example quick peek (Python):

```python

import sqlite3

conn = sqlite3.connect("iot.db")

for row in conn.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20"):

    print(row)

```

---

## 🔒 Notes & safety

- Public MQTT brokers are **not secure**. For demos only—avoid sensitive data.

- Relays include **basic safety fallbacks** (e.g., return to `AUTO` on dangerous conditions).

- Thresholds (temperature, level) are defined in code and can be adjusted.

---

## 🧩 Troubleshooting

- **No GUI on WSL** → run on Windows or install an X server and export `DISPLAY`.

- **No MQTT messages** → check internet/broker/firewall; port 1883 must be open.

- **DB permission error** → run from the project folder; delete `iot.db` to recreate.

- **Version conflicts** → create a fresh virtualenv and reinstall dependencies.

---

## 🗺️ Roadmap

- Web dashboard (Streamlit/Flask) that tails SQLite in near‑real‑time.

- Persist configurable thresholds (YAML/JSON).

- Private MQTT with TLS/auth.

- Docker Compose for the full stack.

---

## 👩🏻‍💻 Credits

Built as part of an IoT course.

**Owners**: Or Dorbin & Karina Haimov
Thank You!

