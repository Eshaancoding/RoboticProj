import io
import socket
import struct
from PIL import Image, ImageTk
import tkinter as tk
import time
import numpy
import cv2

class main (tk.Tk):
    def __init__ (self, *args, **kwags):
        tk.Tk.__init__(self, *args, **kwags)
        self.estabilsh_connection()
        self.init_image()
        self.want_disconnect = False
        self.bind("<KeyPress>", lambda i : self.key_press(i))
        self.bind("<KeyRelease>", lambda i : self.key_release(i))
        self.key_forward = False
        self.key_backward = False
        self.key_left = False
        self.key_right = False

    def key_release (self, event=None):
        key = event.keysym
        if key == "w" or key == "W":
            self.key_forward = False 
        elif key == "s" or key == "S":
            self.key_backward = False
        elif key == "a" or key == "A":
            self.key_left = False
        elif key == "d" or key == "D":
            self.key_right = False

    def key_press (self, event=None):
        key = event.keysym        
        if key == "b" or key == "B":
            self.want_disconnect = True
        elif key == "w" or key == "W":
            self.key_forward = True 
        elif key == "s" or key == "S":
            self.key_backward = True
        elif key == "a" or key == "A":
            self.key_left = True
        elif key == "d" or key == "D":
            self.key_right = True

    def init_image (self):
        image = Image.fromarray(numpy.zeros((640,480)))
        image = ImageTk.PhotoImage(image)
        self.label = tk.Label(self, image=image)
        self.label.pack(side="bottom", fill="both", expand="yes")

    def estabilsh_connection (self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        
        self.server_disconnect_socket = socket.socket()
        self.server_disconnect_socket.bind(('0.0.0.0', 8080))
        
        print("Listening...")
        
        self.server_socket.listen(0)
        self.connection = self.server_socket.accept()[0].makefile('rb')
       
        self.server_disconnect_socket.listen(0)
        self.server_disconnect_connection, _ = self.server_disconnect_socket.accept()
        
        print("Connection established!")
        time.sleep(2)

    def close_connection (self):
        self.connection.close()
        self.server_socket.close()
        self.server_disconnect_socket.close()
        self.server_disconnect_connection.close()

    def re_update (self):
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            print("Connection closed.")
            self.close_connection()
            exit(0)
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(self.connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream).rotate(180)
        
        if self.want_disconnect:
            self.server_disconnect_connection.send("s".encode())
            self.close_connection()
            exit(0)
        elif self.key_forward: 
            self.server_disconnect_connection.send("f".encode())
        elif self.key_backward:
            self.server_disconnect_connection.send("b".encode())
        elif self.key_left: 
            self.server_disconnect_connection.send("l".encode())
        elif self.key_right: 
            self.server_disconnect_connection.send("r".encode())
        else:
            self.server_disconnect_connection.send("c".encode())

        # image display
        image = ImageTk.PhotoImage(image)
        self.label.configure(image=image)
        self.label.image = image

root = main(className = "Image")
while True:
    root.update()
    root.update_idletasks()
    root.re_update()
    