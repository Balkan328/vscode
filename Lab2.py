from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

#GPIO
import RPi.GPIO as GPIO
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

#Flask
app = Flask(__name__)
CORS(app)

#Flask page d'accueil
@app.route('/')
def index():
    return render_template('index.html')
 
 #Flask allumer eteindre DEL
@app.route('/moteur', methods=['POST'])
def controleMoteur():

        print(request.json)

        dirGaucheOn = request.json['dirGauche']
        if dirGaucheOn:
            GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.HIGH)
        else:
            GPIO.output(GPIO_PIN_DIR_MOTEUR1, GPIO.LOW)


        vitGaucheOn = request.json['vitGauche']
        if vitGaucheOn:
            GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.HIGH)
        else:
            GPIO.output(GPIO_PIN_VIT_MOTEUR1, GPIO.LOW)

        dirDroiteOn = request.json['dirDroite']
        if dirDroiteOn:
            GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.HIGH)
        else:
            GPIO.output(GPIO_PIN_DIR_MOTEUR2, GPIO.LOW)

        vitDroiteOn = request.json['vitDroite']
        if vitDroiteOn:
            GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.HIGH)
        else:
            GPIO.output(GPIO_PIN_VIT_MOTEUR2, GPIO.LOW)

        return jsonify({'message': 'motor state updated successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
