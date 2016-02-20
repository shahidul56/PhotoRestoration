import Tkinter as tk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import os
import numpy as np
import cv2

import Image, ImageTk
from tkFileDialog import askopenfilename
from inpainting import *

def filePicker():
    tk.Tk().withdraw()
    filename = askopenfilename()
    return filename

class App():
    def __init__(self, master):
        self.master = master
        self.file = filePicker()
        self.crop_face()
        self.orig_img = Image.open(self.file)
        self.tk_img = ImageTk.PhotoImage(self.orig_img)
        w, h = self.orig_img.size
        self.mask = Image.new('L', self.orig_img.size, "black")
        self.mask_path = None
        self.canvas = tk.Canvas(master, width=w, height=h)
        self.canvas.pack()
        self.x = 0
        self.y =0
        self.select_windows=[]
        self.current_window=[]

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self._draw_image()

        self.points_pool=[]
        # import_button = tk.Button(self.master, text="select photo", command=(lambda : SelectAndShowImage(root))).pack(fill=tk.X, side = tk.TOP, )
        # pick_button = tk.Button(self.master,text="select masks").pack(fill=tk.X, side = tk.TOP)
        save_button = tk.Button(self.master,text="save masks",command=(self.save_mask)).pack(fill=tk.X, side = tk.TOP)#this is intermediate , will delete later
        restore_button = tk.Button(self.master,text="restore",command=(lambda : inpaint(self.file,self.mask_path))).pack(fill=tk.X, side = tk.TOP)
        self.master.mainloop()

    def crop_face(self):
        # Get user supplied values
        curr_path = os.getcwd()
        imagePath = self.file
        cascPath = curr_path.replace("/python", "/data/cascade/haarcascade_frontalface_default.xml")
        face_path= curr_path.replace("/python", "/data/images/face_cropped/")
        oldfileName = (self.file)[(self.file).rfind("/")+1:-4]
        face_filename = face_path+oldfileName+"_face.png"
        print face_filename
        # Create the haar cascade
        faceCascade = cv2.CascadeClassifier(cascPath)
# /home/wenchen/frameworks/projects/PhotoRestoration/data/images/face_cropped
# /home/wenchen/frameworks/projects/PhotoRestoration/data/face_cropped/original_female_potrait_face.png
        # Read the image
        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        print "Found {0} faces!".format(len(faces))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.imwrite(face_filename,image[y:y+h,x:x+w])
        # cv2.imshow("Faces found", image)
        cv2.waitKey(0)
    def save_mask(self):

        curr_path = os.getcwd()
        new_path = curr_path.replace("/python", "/data/images/mask/")
        oldfileName = (self.file)[(self.file).rfind("/")+1:-4]
        output = ImageOps.fit(self.mask, self.orig_img.size, centering=(0.5, 0.5))
        draw = ImageDraw.Draw(self.mask)

        # for window in self.select_windows:
        #     draw.rectangle(window,fill="white")
        # print self.select_windows
        # for point in self.points_pool:
        draw.polygon(self.points_pool,fill="white")
        # print self.select_windows

        output.paste(self.mask)
        self.mask_path = new_path+oldfileName+"_mask.png"
        output.save(self.mask_path)
        print "saved mask"

    def _draw_image(self):
         self.canvas.create_image(0,0,anchor="nw",image=self.tk_img)

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        # self.current_window.append((self.start_x,self.start_y))
        self.points_pool.append((event.x,event.y))
        print "appending start",(event.x,event.y)
        # create rectangle if not yet exist
        #if not self.rect:
        self.rect = self.canvas.create_line(self.x, self.y, 1, 1, fill="white")

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)
    def on_button_release(self, event):
        # self.current_window.append((event.x,event.y))
        # self.select_windows.append(self.current_window)
        # self.current_window=[]
        self.points_pool.append((event.x,event.y))
        print "appending end",(event.x,event.y)

root = tk.Tk()
App(root)
