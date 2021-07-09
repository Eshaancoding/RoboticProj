import io
import socket
import struct
import time
import picamera
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

def reset ():
    GPIO.output(8, GPIO.LOW)
    GPIO.output(10, GPIO.LOW)
    GPIO.output(16, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)

def move_foward ():  # 8 HIGH, 10 LOW, will move right motor forward
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(16, GPIO.LOW)
    GPIO.output(8, GPIO.HIGH)
    GPIO.output(10, GPIO.LOW)

def move_backward ():
    GPIO.output(18, GPIO.LOW)
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(8, GPIO.LOW)
    GPIO.output(10, GPIO.HIGH)

def right_turn ():
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(16, GPIO.LOW)
    GPIO.output(8, GPIO.LOW)
    GPIO.output(10, GPIO.HIGH)

def left_turn ():
    GPIO.output (18, GPIO.LOW)
    GPIO.output (16, GPIO.HIGH)
    GPIO.output (8, GPIO.HIGH)
    GPIO.output (10, GPIO.LOW)

client_socket = socket.socket()
client_socket.connect(('192.168.0.21', 8000))
client_socket_disconnect = socket.socket()
client_socket_disconnect.connect(('192.168.0.21', 8080))
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        time.sleep(2)
        count = 0
        stream = io.BytesIO()
        start = time.time()
        # Use the video-port for captures...
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            count += 1
            recieve = client_socket_disconnect.recv(1024).decode() 
            if recieve == "s":
                break
            elif recieve == "c":
                reset()
            elif recieve == "f":
                move_foward()
            elif recieve == "b":
                move_backward()
            elif recieve == "r":
                right_turn()
            elif recieve == "l":
                left_turn()
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    GPIO.cleanup()
    connection.close()
    client_socket.close()
    client_socket_disconnect.close()
    finish = time.time()
print('Sent %d images in %d seconds at %.2ffps' % (
    count, finish-start, count / (finish-start)))