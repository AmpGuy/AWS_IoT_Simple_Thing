import time
import json
import random
from awscrt import io
from awscrt.mqtt import QoS
from awsiot import mqtt_connection_builder
import os
import RPi.GPIO as GPIO  # Add GPIO library
import logging

# Enable debug logging for MQTT client
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mqtt_debug.log'),
        logging.StreamHandler()
    ]
)

logging.getLogger("awsiot").setLevel(logging.DEBUG)

# GPIO Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
INPUT_PIN = 0  # GPIO 0 (Pin 27 on Raspberry Pi)
GPIO.setup(INPUT_PIN, GPIO.IN)  # Set pin as input

# Get credentials from environment variables and strip any extra characters
ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "").strip("{}' ")
CERT_PATH = os.getenv("AWS_IOT_CERT_PATH", "").strip("{}' ")
PRI_KEY_PATH = os.getenv("AWS_IOT_PRIVATE_KEY_PATH", "").strip("{}' ")
CA_PATH = os.getenv("AWS_IOT_ROOT_CA_PATH", "").strip("{}' ")
CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "").strip("{}' ")
TOPIC = "sensors/data"

# Verify all required variables are set
if not all([ENDPOINT, CERT_PATH, PRI_KEY_PATH, CA_PATH, CLIENT_ID]):
    raise ValueError("Missing required environment variables")

# Print configuration
print("Configuration:")
print(f'ENDPOINT: ', {ENDPOINT})
print(f'CERT_PATH: ', {CERT_PATH})
print(f'PRI_KEY_PATH: ', {PRI_KEY_PATH})
print(f'CA_PATH: ', {CA_PATH})
print(f'CLIENT_ID: ', {CLIENT_ID})
print(f'TOPIC: ', {TOPIC})

# Callback functions
def on_connection_interrupted(mqtt_connection, error, **kwargs):
    logging.error(f"Connection interrupted. error: {error}")

def on_connection_resumed(mqtt_connection, return_code, session_present, **kwargs):
    logging.info(f"Connection resumed. return_code: {return_code}, session_present: {session_present}")

def on_message_received(topic, payload, **kwargs):
    try:
        print(f"\nReceived message from topic '{topic}': {payload}")
        message = json.loads(payload)
        print(f"Decoded message: {json.dumps(message, indent=2)}")
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Raw message: {payload.decode()}")

try:
    # Verify certificate files exist before attempting connection
    for file_path in [CERT_PATH, PRI_KEY_PATH, CA_PATH]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Certificate file not found: {file_path}")

    # Initialize AWS IoT client
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=PRI_KEY_PATH,
        client_bootstrap=client_bootstrap,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed
    )

    print(f"Connecting to {ENDPOINT} with client ID '{CLIENT_ID}'...")
    connect_future = mqtt_connection.connect()
    connect_result = connect_future.result()
    print(f"Connection Result: {connect_result}")

    # Subscribe to topic
    print(f"Subscribing to topic: {TOPIC}")
    subscribe_future, _ = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscription result: {subscribe_result}")
    print("Connected and subscribed!")

    # Start sensing
    while True:
        try:
            # Generate random float between 20.0 and 30.0 (simulating temperature)
            temperature = round(random.uniform(20.0, 30.0), 2)
            
            # Read GPIO state
            gpio_state = GPIO.input(INPUT_PIN)
            
            # Create message payload
            message = {
                "timestamp": int(time.time()),
                "device_id": CLIENT_ID,
                "temperature": temperature,
                "gpio_state": gpio_state  # Add GPIO state to the payload
            }
            
            # Convert message to JSON
            message_json = json.dumps(message)
            
            # Publish message
            print(f"Publishing: {message_json}")
            future, _= mqtt_connection.publish(
                topic=TOPIC,
                payload=message_json,
                qos=QoS.AT_LEAST_ONCE  # Use integer value: 0 for AT_MOST_ONCE, 1 for AT_LEAST_ONCE, 2 for EXACTLY_ONCE
            )

            future.result()   
            print(f"Published message successfully")

            # Wait for 5 seconds before next reading
            time.sleep(5)

        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}", exc_info=True)
            continue
    
except KeyboardInterrupt:
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    GPIO.cleanup()  # Clean up GPIO on exit
    print("Disconnected!")

except Exception as e:
    logging.error(f"Connection failed: {str(e)}", exc_info=True)
    GPIO.cleanup()
    
    # Print detailed error information
    print("\nDetailed error information:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nCertificate verification:")
    print(f"Certificate exists: {os.path.exists(CERT_PATH)}")
    print(f"Private key exists: {os.path.exists(PRI_KEY_PATH)}")
    print(f"CA file exists: {os.path.exists(CA_PATH)}")
    
    # Check file permissions
    print("\nFile permissions:")
    for file_path in [CERT_PATH, PRI_KEY_PATH, CA_PATH]:
        if os.path.exists(file_path):
            print(f"{file_path}: {oct(os.stat(file_path).st_mode)[-3:]}")


