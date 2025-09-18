import time, json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
CMD_TOPIC = "aquarium/lamp"          # Commands: ON / OFF / AUTO
STATUS_TOPIC = "aquarium/lamp/status"
TEMP_TOPIC = "aquarium/temp"

lamp_on = False
auto_mode = True
current_temp = 22

# Safety thresholds
DANGEROUSLY_LOW_TEMP = 10
DANGEROUSLY_HIGH_TEMP = 35

def publish_status(client):
    status_msg = json.dumps({
        "mode": "AUTO" if auto_mode else "MANUAL",
        "state": "ON" if lamp_on else "OFF"
    })
    client.publish(STATUS_TOPIC, status_msg, retain=True)
    print("Lamp status published:", status_msg)

def on_message(client, userdata, msg):
    global lamp_on, auto_mode, current_temp
    if msg.topic == CMD_TOPIC:
        cmd = msg.payload.decode().strip().upper()
        if cmd == "ON":
            lamp_on = True
            auto_mode = False
            print("Lamp forced ON (manual)")
        elif cmd == "OFF":
            lamp_on = False
            auto_mode = False
            print("Lamp forced OFF (manual)")
        elif cmd == "AUTO":
            auto_mode = True
            print("Lamp back to AUTO mode")
        publish_status(client)

    elif msg.topic == TEMP_TOPIC:
        try:
            current_temp = json.loads(msg.payload.decode())["temp"]
        except:
            pass

def main():
    global lamp_on, auto_mode, current_temp
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(CMD_TOPIC)
    client.subscribe(TEMP_TOPIC)

    print("Lamp relay running")
    publish_status(client)  # ✅ Send initial state on startup

    while True:
        client.loop(timeout=0.1)

        # Safety override
        if not auto_mode and (current_temp < DANGEROUSLY_LOW_TEMP or current_temp > DANGEROUSLY_HIGH_TEMP):
            auto_mode = True
            print("⚠️ Safety override → Lamp back to AUTO (dangerous temp)")
            publish_status(client)

        if not auto_mode and (current_temp < 15 or current_temp > 30):
         auto_mode = True
         print("⚠️ Safety override → Lamp back to AUTO (out of safe range)")
         publish_status(client)

        time.sleep(3)

if __name__ == "__main__":
    main()
