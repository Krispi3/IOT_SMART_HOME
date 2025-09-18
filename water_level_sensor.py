import paho.mqtt.client as mqtt
import time, json

BROKER = "broker.hivemq.com"
PORT = 1883
LEVEL_TOPIC = "aquarium/water_level"
PUMP_STATUS_TOPIC = "aquarium/pump/status"
PUMP_CMD_TOPIC = "aquarium/pump"

current_level = 50
pump_on = False
pump_mode = "AUTO"

def on_message(client, userdata, msg):
    global pump_on, pump_mode
    if msg.topic == PUMP_STATUS_TOPIC:
        try:
            status = json.loads(msg.payload.decode())  # ✅ decode JSON
            pump_on = status.get("state", "OFF") == "ON"
            pump_mode = status.get("mode", "AUTO")
            print(f"Pump status received: state={status.get('state')} mode={status.get('mode')}")
        except Exception as e:
            print("Error parsing pump status:", e)


def main():
    global current_level

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(PUMP_STATUS_TOPIC)

    while True:
        client.loop(timeout=0.1)

        # Simulate water level
        if pump_on:
            current_level += 2
        else:
            current_level -= 1

        # Clamp range
        if current_level >= 100:
            current_level = 100
            if pump_on:
                # Auto stop pump at full
                client.publish(PUMP_CMD_TOPIC, "OFF")
                print("💧 Water full → Auto stopping pump")
        elif current_level < 0:
            current_level = 0

        payload = json.dumps({"level": current_level})
        client.publish(LEVEL_TOPIC, payload)
        print("Sent water level:", payload)
        time.sleep(5)

if __name__ == "__main__":
    main()
