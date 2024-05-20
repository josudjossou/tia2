from __future__ import division
import paho.mqtt.client as mqtt
import pigpio
import time
import Adafruit_PCA9685

# Configuration des broches du moteur
motor_input1 = 15
motor_input2 = 14
motor_enable = 4
motor_input3 = 27
motor_input4 = 18
motor_enable2 = 17

# Configuration MQTT
mqtt_broker_address = "192.168.100.176"  # Ton adresse IP MQTT
mqtt_port = 1883
mqtt_user = "user1"

mqtt_password = "2024"

# Initialisation de pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Impossible de se connecter à pigpio")
    exit()

# Configuration des broches du moteur
pi.set_mode(motor_input1, pigpio.OUTPUT)
pi.set_mode(motor_input2, pigpio.OUTPUT)
pi.set_PWM_frequency(motor_enable, 1000)  # Ajustez selon vos besoins
pi.set_mode(motor_input3, pigpio.OUTPUT)
pi.set_mode(motor_input4, pigpio.OUTPUT)
pi.set_PWM_frequency(motor_enable2, 1000)  # Ajustez selon vos besoins

# Fonctions de contrôle du moteur
def motor_forward():
    pi.write(motor_input1, 1)
    pi.write(motor_input2, 0)
    pi.write(motor_input3, 1)
    pi.write(motor_input4, 0)
    pi.set_PWM_dutycycle(motor_enable, 255)  # PWM pour contrôler la vitesse
    pi.set_PWM_dutycycle(motor_enable2, 255)

def motor_backward():
    pi.write(motor_input1, 0)
    pi.write(motor_input2, 1)
    pi.write(motor_input3, 0)
    pi.write(motor_input4, 1)
    pi.set_PWM_dutycycle(motor_enable, 255)  # PWM pour contrôler la vitesse
    pi.set_PWM_dutycycle(motor_enable2, 255)

def motor_stop():
    pi.write(motor_input1, 0)
    pi.write(motor_input2, 0)
    pi.write(motor_input3, 0)
    pi.write(motor_input4, 0)
    pi.set_PWM_dutycycle(motor_enable, 0)  # Arrêt des moteurs
    pi.set_PWM_dutycycle(motor_enable2, 0)

def motor_left():
    pi.write(motor_input1, 1)
    pi.write(motor_input2, 0)
    pi.write(motor_input3, 0)
    pi.write(motor_input4, 1)
    pi.set_PWM_dutycycle(motor_enable, 255)  # PWM pour contrôler la vitesse
    pi.set_PWM_dutycycle(motor_enable2, 255)

def motor_right():
    pi.write(motor_input1, 0)
    pi.write(motor_input2, 1)
    pi.write(motor_input3, 1)
    pi.write(motor_input4, 0)
    pi.set_PWM_dutycycle(motor_enable, 255)  # PWM pour contrôler la vitesse
    pi.set_PWM_dutycycle(motor_enable2, 255)

# Initialisation du PCA9685
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)  # Fréquence pour les servomoteurs (50 Hz)

# Définir les canaux des servomoteurs
servo_channels = [11, 12, 13, 14, 15]

# Fonction pour convertir un angle en largeur d'impulsion (pulse)
def angle_to_pwm(angle):
    pulse_min = 150  # Largeur d'impulsion minimale
    pulse_max = 600  # Largeur d'impulsion maximale
    pulse_range = pulse_max - pulse_min
    pwm_value = int(pulse_min + (pulse_range * angle / 180))  # Conversion de l'angle en PWM
    return pwm_value

# Fonction de contrôle des servomoteurs
def set_servo_angle(channel, angle):
    pwm_value = angle_to_pwm(angle)
    pwm.set_pwm(channel, 0, pwm_value)

def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code " + str(rc))
    if rc == 0:
        client.subscribe("esp8266")
    else:
        print("Échec de la connexion, code de retour %d\n", rc)

def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print(f"Message reçu sur le topic '{msg.topic}': {message}")
    
    command = message.strip().lower()  # Convertir en minuscules et supprimer les espaces indésirables
    
    if command == "haut":
        motor_forward()
    elif command == "stop":
        motor_stop()
    elif command == "bas":
        motor_backward()
    elif command == "gauche":
        motor_left()
    elif command == "droite":
        motor_right()
    elif command.startswith("servo"):
        parts = command.split("servo")
        if len(parts) == 2:
            servo_id = int(parts[1][0])
            angle = int(parts[1][1:])
            if 1 <= servo_id <= 5 and 0 <= angle <= 180:
                set_servo_angle(servo_channels[servo_id - 1], angle)
            else:
                print("Identifiant de servo ou angle invalide.")
        else:
            print("Commande servo invalide.")
    else:
        print("Commande non reconnue.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_broker_address, mqtt_port, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Déconnexion de MQTT et arrêt de pigpio")
finally:
    client.disconnect()
    pi.stop()

