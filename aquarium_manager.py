import paho.mqtt.client as mqtt
import sqlite3, json, time

# DB Setup
conn = sqlite3.connect("iot.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS logs (
    timestamp TEXT,
    sensor TEXT,
    value TEXT
)""")
conn.commit()

def log_data(topic, value):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO logs VALUES (?, ?, ?)", (ts, topic, value))
    conn.commit()
    print(f"{ts} | {topic}: {value}")

# Thresholds
MAX_TEMP = 30
MIN_TEMP = 15
MIN_WATER_LEVEL = 30
PUMP_OFF_THRESHOLD = 80

# State tracking
pump_state = "OFF"

def on_message(client, userdata, msg):
    global pump_state
    data = msg.payload.decode()

    # --- Pump and Lamp Status (JSON) ---
    if msg.topic in ["aquarium/pump/status", "aquarium/lamp/status"]:
        try:
            status = json.loads(data)
            log_data(msg.topic, json.dumps(status))  # store JSON string
            print(f"Status update: {msg.topic} {status}")
        except Exception as e:
            print(f"Error parsing relay status on {msg.topic}: {e}")
        return

    # --- Temperature Sensor ---
    if msg.topic == "aquarium/temp":
        try:
            log_data(msg.topic, data)
            t = json.loads(data)["temp"]

            if t > MAX_TEMP:
                client.publish("aquarium/alarm", f"⚠️ High Temperature! ({t}°C)")
            elif t < MIN_TEMP:
                client.publish("aquarium/alarm", f"⚠️ Low Temperature! ({t}°C)")
        except Exception as e:
            print("Error parsing temp:", e)

    # --- Water Level Sensor ---
    elif msg.topic == "aquarium/water_level":
        try:
            log_data(msg.topic, data)
            lvl = json.loads(data)["level"]

            if lvl < MIN_WATER_LEVEL and pump_state == "OFF":
                client.publish("aquarium/pump", "ON")
                pump_state = "ON"
                client.publish("aquarium/alarm", f"⚠️ Pump ON (Low water {lvl}%)")

            elif lvl > PUMP_OFF_THRESHOLD and pump_state == "ON":
                client.publish("aquarium/pump", "OFF")
                pump_state = "OFF"
                client.publish("aquarium/alarm", f"✅ Pump OFF (Water restored {lvl}%)")

        except Exception as e:
            print("Error parsing water level:", e)

    
    # --- Feeder Button ---
    elif msg.topic == "aquarium/feed":
        log_data("aquarium/feed", data)
        client.publish("aquarium/alarm", "✅ Fish fed!")

    elif msg.topic == "aquarium/alarm":
        log_data("aquarium/alarm", data)

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("aquarium/#")

print("🐟 Manager running... logging sensors + relay status")
client.loop_forever()
