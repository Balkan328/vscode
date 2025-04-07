# Flask and GPIO imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO

# OpenCV and NumPy imports
import cv2
import numpy as np

# GPIO setup
GPIO_PIN_DIR_MOTEUR1 = 17
GPIO_PIN_VIT_MOTEUR1 = 27
GPIO_PIN_DIR_MOTEUR2 = 22
GPIO_PIN_VIT_MOTEUR2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN_DIR_MOTEUR1, GPIO.OUT)
GPIO.setup(GPIO_PIN_VIT_MOTEUR1, GPIO.OUT)
GPIO.setup(GPIO_PIN_DIR_MOTEUR2, GPIO.OUT)
GPIO.setup(GPIO_PIN_VIT_MOTEUR2, GPIO.OUT)

GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.LOW)
GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.LOW)
GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.LOW)
GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.LOW)

# Flask setup
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/moteur', methods=['POST'])
def controleMoteur():
    data = request.json
    GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.HIGH if data['dirGauche'] else GPIO.LOW)
    GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.HIGH if data['vitGauche'] else GPIO.LOW)
    GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.HIGH if data['dirDroite'] else GPIO.LOW)
    GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.HIGH if data['vitDroite'] else GPIO.LOW)
    return jsonify({'message': 'motor state updated successfully'})

# OpenCV functions
def detect_red_ball_on_frame(frame, min_radius=10, max_radius=400, param1=50, param2=30, min_dist=20):
    if frame is None or frame.size == 0:
        return None, None, None, None, None

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    gray = cv2.bitwise_and(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), mask=mask)
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        1,
        min_dist,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=max_radius,
    )

    if circles is not None:
        circles = np.uint16(np.around(circles[0, :]))
        return circles.tolist(), hsv, mask, gray, gray_blurred
    else:
        return None, hsv, mask, gray, gray_blurred

def draw_circles_on_frame(frame, circles):
    if frame is None or frame.size == 0:
        return

    if circles is not None:
        for x, y, r in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
    cv2.imshow("Detected Red Ball", frame)

# Camera and robot control logic
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        circles, hsv, mask, gray, gray_blurred = detect_red_ball_on_frame(frame)

        if circles:
            # Assuming the first detected circle is the target
            x, y, r = circles[0]
            frame_center_x = frame.shape[1] // 2

            if x < frame_center_x - 50:  # Ball is to the left
                GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.HIGH)
                GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.HIGH)
                GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.LOW)
                GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.HIGH)
            elif x > frame_center_x + 50:  # Ball is to the right
                GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.LOW)
                GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.HIGH)
                GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.HIGH)
                GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.HIGH)
            else:  # Ball is centered
                GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.HIGH)
                GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.HIGH)
                GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.HIGH)
                GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.HIGH)
        else:
            # Stop the robot if no ball is detected
            GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.LOW)
            GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.LOW)
            GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.LOW)
            GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.LOW)

        draw_circles_on_frame(frame.copy(), circles)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()