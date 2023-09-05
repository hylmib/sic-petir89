import RPi.GPIO as GPIO
import time
import atexit
import threading

from ubidots_get_post import *

onButton = False
statusMotor1 = False
statusMotor2 = False

TRIG1 = 21
ECHO1= 20
TRIG2 = 6
ECHO2 = 5

ENA = 25
IN1 = 24
IN2 = 23

ENB = 17
IN3 = 22
IN4 = 27

SERVO = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Init ultrasonic 1
GPIO.setup(TRIG1,GPIO.OUT)
GPIO.setup(ECHO1,GPIO.IN)
GPIO.output(TRIG1,False)

# INNT ULTRASONIC 2
GPIO.setup(TRIG2,GPIO.OUT)
GPIO.setup(ECHO2,GPIO.IN)
GPIO.output(TRIG2,False)

# Init DC Motor 1
GPIO.setup(ENA,GPIO.OUT)
GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)
GPIO.output(IN1,GPIO.LOW)
GPIO.output(IN2,GPIO.LOW)
motor_1 = GPIO.PWM(ENA,1000)
motor_1.start(25)

#INT DC MOTOR 2
GPIO.setup(ENB,GPIO.OUT)
GPIO.setup(IN3,GPIO.OUT)
GPIO.setup(IN4,GPIO.OUT)
GPIO.output(IN3,GPIO.LOW)
GPIO.output(IN4,GPIO.LOW)
motor_2 = GPIO.PWM(ENB,1000)
motor_2.start(25)

#INT SERVO YANG KEHUBUNG DENGAN ULTRA 1
GPIO.setup(SERVO, GPIO.OUT)
pwm_servo=GPIO.PWM(SERVO, 50)
pwm_servo.start(0)

# Adjust servo speed and direction
turn_left = 2.5 #CCW
stop_servo = 0
turn_right = 8 #CW

# DEF 1 
def forward_motor_1():
    high1()
    GPIO.output(ENA,GPIO.HIGH)
    GPIO.output(IN1,GPIO.HIGH)
    GPIO.output(IN2,GPIO.LOW)

def backward1():
    GPIO.output(ENA,GPIO.HIGH)
    GPIO.output(IN1,GPIO.LOW)
    GPIO.output(IN2,GPIO.HIGH)

def high1 () :
    motor_1.ChangeDutyCycle(15)

def stop1() : 
    GPIO.output(ENA,GPIO.LOW)
    GPIO.output(IN1,GPIO.LOW)
    GPIO.output(IN2,GPIO.LOW)

#int def motor2
def forward_motor_2():
    high2()
    GPIO.output(ENB,GPIO.HIGH)
    GPIO.output(IN3,GPIO.HIGH)
    GPIO.output(IN4,GPIO.LOW)

def backward2():
    GPIO.output(ENB,GPIO.HIGH)
    GPIO.output(IN3,GPIO.LOW)
    GPIO.output(IN4,GPIO.HIGH)

def high2() :
    motor_2.ChangeDutyCycle(15)

def stop2() : 
    GPIO.output(ENB,GPIO.LOW)
    GPIO.output(IN3,GPIO.LOW)
    GPIO.output(IN4,GPIO.LOW)
    
def distance1():
    # set Trigger to HIGH
    GPIO.output(TRIG1, True)
    time.sleep(0.00001)
    GPIO.output(TRIG1, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(ECHO1) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(ECHO1) == 1:
        StopTime = time.time()
    
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

def distance2():
    # set Trigger to HIGH
    GPIO.output(TRIG2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(TRIG2, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(ECHO2) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(ECHO2) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def stop_all():
    # Stop motor
    stop1()
    stop2()
    pwm_servo.ChangeDutyCycle(stop_servo)
    time.sleep(2)

# Firstly motor1 stop
stop1()
stop2()
#print("Ketik r untuk run dan s untuk stop.....")
#print("r-run s-stop")

def main_prog():
    global statusMotor1, statusMotor2
    while True:
        # If Button is On or True
        if(onButton):
            print("Button On")
            
            distance_1 = distance1()
            distance_2 = distance2()
            
            print("Jarak 1:", distance_1)
            print("Jarak 2", distance_2)

            if distance_1 < 10 :
                forward_motor_1()
                statusMotor1 = True
                #print("Start Motor 1")
                time.sleep(5)
                pwm_servo.ChangeDutyCycle(turn_right) # Putar servo
                #print("Start Servo")
            else:
                stop1()
                statusMotor1 = False
                pwm_servo.ChangeDutyCycle(stop_servo) # Putar servo
                #print("Stop Motor 1 & Servo")
                
            if distance_2 > 10 :
                forward_motor_2()
                statusMotor2 = True
                #print("Start Motor 2")
            else :
                stop2()
                statusMotor2 = False
                #print("Stop Motor 2")
        
        # Else: button is False or Off
        else:
            print("Button Off")
            statusMotor1 = False
            statusMotor2 = False
            stop_all()
        
def ubidots():
    global onButton
    print("Start Ubidots")
    
    while True:
        onButton = get_var("button_on")
        print(onButton)
        
        if(statusMotor1):
            send_text("motor_1", "Motor 1 - ON")
        else:
            send_text("motor_1", "Motor 1 - OFF")
        
        if(statusMotor2):
            send_text("motor_2", "Motor 2 - ON")
        else:
            send_text("motor_2", "Motor 2 - OFF")
        
if __name__ == '__main__':
    try:
        t1 = threading.Thread(target=ubidots)
        t2 = threading.Thread(target=main_prog)
        
        # starting thread 1 & 2
        t1.start()
        t2.start()
        
        # wait until thread 1 & 2 is completely executed
        t1.join()
        t2.join()
     
        # both threads completely executed
        print("Done!")
            
    finally:
        GPIO.cleanup()