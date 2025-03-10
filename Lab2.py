import RPi.GPIO as GPIO
import time
import os
from flask import Flask, request, jsonify

# GPIO Configuration
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # LED Pin
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button with pull-up resistor

# Flask App Initialization
app = Flask(__name__, static_folder='static')

# Variable to store LED state
led_state = False

@app.route('/get', methods=['GET'])
def get_led_status():
    """Returns the current state of the LED and the button"""
    global led_state
    status = "on" if led_state else "off"
    
    # Read button state (LOW = Pressed, HIGH = Not Pressed)
    button_state = "on" if GPIO.input(27) == GPIO.LOW else "off"

    return jsonify({"led": status, "button": button_state})

@app.route('/post', methods=['POST'])
def post_led_control():
    """Controls the LED based on POST request data"""
    global led_state
    data = request.get_json()

    if not data or "led" not in data:
        return jsonify({"error": "Invalid JSON data"}), 400

    if data["led"] == "true":
        GPIO.output(17, GPIO.HIGH)  # Turn LED ON
        led_state = True
        return jsonify({"message": "LED turned ON"})

    elif data["led"] == "false":
        GPIO.output(17, GPIO.LOW)  # Turn LED OFF
        led_state = False
        return jsonify({"message": "LED turned OFF"})

    else:
        return jsonify({"error": "Invalid value for 'led', use 'true' or 'false'"}), 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)  # Accessible on network
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        GPIO.cleanup()  # Release GPIO resources
