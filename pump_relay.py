import time, json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
CMD_TOPIC = "aquarium/pump"          # Commands: ON / OFF / AUTO
STATUS_TOPIC = "aquarium/pump/status"
LEVEL_TOPIC = "aquarium/water_level"

pump_on = False
auto_mode = True
current_level = 50

# Safety threshold
DANGEROUSLY_LOW = 10   # %

def publish_status(client):
    status_msg = json.dumps({
        "mode": "AUTO" if auto_mode else "MANUAL",
        "state": "ON" if pump_on else "OFF"
    })
    client.publish(STATUS_TOPIC, status_msg, retain=True)
    print("Pump status published:", status_msg)

def on_message(client, userdata, msg):
    global pump_on, auto_mode, current_level
    if msg.topic == CMD_TOPIC:
        cmd = msg.payload.decode().strip().upper()
        if cmd == "ON":
            pump_on = True
            auto_mode = False
            print("Pump forced ON (manual)")
        elif cmd == "OFF":
            pump_on = False
            auto_mode = False
            print("Pump forced OFF (manual)")
        elif cmd == "AUTO":
            auto_mode = True
            print("Pump back to AUTO mode")
        publish_status(client)

    elif msg.topic == LEVEL_TOPIC:
        try:
            current_level = json.loads(msg.payload.decode())["level"]
        except:
            pass

def main():
    global pump_on, auto_mode, current_level
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(CMD_TOPIC)
    client.subscribe(LEVEL_TOPIC)

    print("Pump relay running")
    publish_status(client)  # ✅ Send initial state on startup

    while True:
        client.loop(timeout=0.1)

        # Safety override
        if not auto_mode and current_level < DANGEROUSLY_LOW:
            auto_mode = True
            pump_on = True
            print("⚠️ Safety override → Pump back to AUTO (low water)")
            publish_status(client)

        if auto_mode:
            if pump_on and current_level >= 100:
                pump_on = False
                print("💧 Water full → Pump auto OFF")
                publish_status(client)

        time.sleep(3)

if __name__ == "__main__":
    main()
