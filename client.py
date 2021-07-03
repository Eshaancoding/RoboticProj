import io
import socket
import struct
import time
import picamera

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
            if client_socket_disconnect.recv(1024).decode() == "s":
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
    client_socket_disconnect.close()
    finish = time.time()
print('Sent %d images in %d seconds at %.2ffps' % (
    count, finish-start, count / (finish-start)))