import paho.mqtt.client as mqtt
import time, random, json

BROKER = "broker.hivemq.com"
PORT = 1883
TEMP_TOPIC = "aquarium/temp"
ALARM_TOPIC = "aquarium/alarm"
LAMP_STATUS_TOPIC = "aquarium/lamp/status"

# Sampling interval
SAMPLE_INTERVAL = 5

# Thresholds
MAX_TEMP = 30
MIN_TEMP = 15

# Initial temperature
temperature = 22.0

lamp_on = False
lamp_mode = "AUTO"

def on_message(client, userdata, msg):
    global lamp_on, lamp_mode
    if msg.topic == LAMP_STATUS_TOPIC:
        try:
            status = json.loads(msg.payload.decode())
            lamp_on = status.get("state", "OFF") == "ON"
            lamp_mode = status.get("mode", "AUTO")
            print(f"Lamp status received: state={status.get('state')} mode={status.get('mode')}")
        except Exception as e:
            print("Error parsing lamp status:", e)

def main():
    global temperature

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(LAMP_STATUS_TOPIC)
    client.loop_start()

    while True:
        # Cooling when lamp OFF
        if not lamp_on:
            temperature -= random.uniform(0.05, 0.15)
        # Heating when lamp ON
        else:
            temperature += random.uniform(0.2, 0.4)

        # Small noise
        temperature += random.uniform(-0.05, 0.05)

        # Clamp realistic range
        temperature = max(5, min(40, temperature))

        # Publish temperature
        payload = json.dumps({"temp": round(temperature, 2)})
        client.publish(TEMP_TOPIC, payload)
        print("Sent temp:", payload)

        # Alarm if outside safe range
        if temperature > MAX_TEMP:
            client.publish(ALARM_TOPIC, f"⚠️ High Temperature! ({round(temperature,2)}°C)")
        elif temperature < MIN_TEMP:
            client.publish(ALARM_TOPIC, f"⚠️ Low Temperature! ({round(temperature,2)}°C)")

        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    main()
