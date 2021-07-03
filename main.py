import io
import socket
import struct
from PIL import Image
import tkinter as tk
import time
import numpy

class main (tk.Tk):
    def __init__ (self, *args, **kwags):
        tk.Tk.__init__(self, *args, **kwags)
        self.estabilsh_connection()
        self.init_image()

    def init_image (self):
        blank_array = numpy.zeros((640, 480))
        self.panel = tk.Label(self, image=Image.fromarray(blank_array))
        self.panel.pack(side="bottom", fill="both", expand="yes")

    def estabilsh_connection (self):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        print("Listening...")
        self.server_socket.listen(0)
        self.connection = self.server_socket.accept()[0].makefile('rb')
        print("Connection established!")

    def close_connection (self):
        self.connection.close()
        self.server_socket.close()

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
        image = Image.open(image_stream)
        
        # display image
        self.panel.configure(image=image)
        self.panel.image = image
        

root = main(className = "Image")
while True:
    root.update()
    root.update_idletasks()
    root.re_update()
    time.sleep(0.09)
    