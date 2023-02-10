import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
import win32gui
from PIL import ImageGrab, Image
import cv2
import os
from keras.models import load_model

model = load_model('mnist1.h5')
print('Loaded the trained model')

def get_handle():
    toplist = []
    windows_list = []
    canvas = 0
    def enum_win(hwnd, result):
        win_text = win32gui.GetWindowText(hwnd)
        #print(hwnd, win_text)
        windows_list.append((hwnd, win_text))
    win32gui.EnumWindows(enum_win, toplist)
    for (hwnd, win_text) in windows_list:
        if 'tk' == win_text:
            canvas = hwnd
    return canvas

def predict_digit(img):
    img.save('test.jpg')
    preprocessed_image = preprocessing_image()
    # print(type(preprocessed_image))
    # print(preprocessed_image.shape)
    img = preprocessed_image.reshape(1, 28, 28, 1)
    img = img/255.0
    # print(img)
    #predicting the digit
    result = model.predict([img])[0]
    os.remove('test.jpg')
    return np.argmax(result), max(result)

def preprocessing_image():
    image = cv2.imread('test.jpg')
    #print(type(image))
    
    #converts the image from a 3-channel color image to a single channel grayscale image using the cv2.cvtColor function.
    grey = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY) 

    # convert a grayscale image into a binary image where the pixel values are either 0 (black) or 255 (white). This helps to simplify the image, making it easier to perform image analysis and feature extraction.
    # In this line of code, the cv2.threshold function is used to perform binary thresholding on the grayscale image grey.copy(). The grey.copy() is used to avoid modifying the original grayscale image. The first argument of the function is the grayscale image that is being thresholded. The second argument, 75, is the threshold value. Any pixel value in the grayscale image that is greater than or equal to 75 will be set to 255 (white) in the binary image, and any pixel value less than 75 will be set to 0 (black). The third argument, 255, is the maximum value that can be assigned to any pixel in the binary image. Finally, the fourth argument, cv2.THRESH_BINARY_INV, is a flag that specifies the type of thresholding to be performed. In this case, the flag cv2.THRESH_BINARY_INV specifies that the binary image should be inverted, so that pixels with values greater than or equal to the threshold value will be set to 0 (black), and pixels with values less than the threshold value will be set to 255 (white).
    # ret is the threshold value used in the thresholding operation, and thresh is the binary thresholded image.
    ret, thresh = cv2.threshold(grey.copy(), 75, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('binarized image', thresh)

    # Contours are the boundaries of an object in an image. They can be defined as a curve joining all the continuous points along the boundary of an object, having the same intensity or color.
    
    # The cv2.findContours function is used to detect the boundaries of objects in an image. In this line, it is applied to the binary thresholded image, thresh. 
    # The first argument to the function is the source image, which is the binary thresholded image in this case. The second argument, cv2.RETR_EXTERNAL, specifies that only external contours should be returned. This means that the function will only return the contours of the outermost boundaries of the objects in the image and will not consider the contours of any holes or internal boundaries within those objects.
    # The third argument, cv2.CHAIN_APPROX_SIMPLE, specifies that the function should return a simplified representation of the contours. This means that it will reduce the number of points in each contour by removing redundant points, resulting in a more compact representation of the contour.
    # The function returns two values, contours and _. The contours variable is a list of numpy arrays, where each numpy array represents a contour in the image. The second value, which is ignored in this case by assigning it to _, is a hierarchy representation of the contours. 
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(type(contours[0]))
    # print(len(contours[0]))
    
    cv2.drawContours(image, contours, -1, (0, 255, 0), 3)  #The -1 argument specifies that all contours should be drawn and the (0, 255, 0) argument specifies the color of the contours.
    #cv2.imshow('Contours', image) 
    for c in contours:
        x,y,w,h = cv2.boundingRect(c) # This line finds the bounding rectangle of the current contour        
        
        # Creating a rectangle around the digit in the original image (for displaying the digits fetched via contours)
        cv2.rectangle(image, (x,y), (x+w, y+h), color=(0, 255, 0), thickness=2)
        
        # Cropping out the digit from the image corresponding to the current contours in the for loop
        digit = thresh[y:y+h, x:x+w]        
        # Resizing that digit to (18, 18)
        
        resized_digit = cv2.resize(digit, (18,18))        
        # Padding the digit with 5 pixels of black color (zeros) in each side to finally produce the image of (28, 28)
        
        padded_digit = np.pad(resized_digit, ((5,5),(5,5)), "constant", constant_values=0)        
        # Adding the preprocessed digit to the list of preprocessed digits
        
        preprocessed_digit = (padded_digit)
    return preprocessed_digit

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.x = self.y = 0
        self.title("Digit Recognition using Deep Learning")
        self.canvas = tk.Canvas(self, width=400, height=400, bg = "white", cursor="cross")
        self.label = tk.Label(self, text="           ", font=("Helvetica", 48))
        self.classify_btn = ttk.Button(self, text = "Recognise", command =self.classify_handwriting,style='Fun.TButton')
        self.button_clear = ttk.Button(self, text = "Clear", command = self.clear_all,style='Fun.TButton')
        # Grid structure
        self.canvas.grid(row=0, column=0, pady=2, sticky=W, )
        self.label.grid(row=0, column=1,pady=2, padx=2)
        self.classify_btn.grid(row=1, column=1, pady=2, padx=2)
        self.button_clear.grid(row=1, column=0, pady=2)
        #self.canvas.bind("<Motion>", self.start_pos)
        self.canvas.bind("<B1-Motion>", self.draw_lines)
        
    def clear_all(self):
        self.canvas.delete("all")
        self.label.configure(text="           ")
        
    def classify_handwriting(self):
        HWND = self.canvas.winfo_id() # get the handle of the canvas
        hwnd = get_handle()
        rect = win32gui.GetWindowRect(HWND) # get the coordinate of the canvas
        x1, y1, x2, y2 = rect
        im = ImageGrab.grab((x1+40, y1+40, x2+100, y2+100))
        digit, acc = predict_digit(im)
        print(digit)
        self.label.configure(text= str(digit)+', '+ str(int(acc*100))+'%')
    def draw_lines(self, event):
        self.x = event.x
        self.y = event.y
        r=8
        self.canvas.create_oval(self.x-r, self.y-r, self.x + r, self.y + r, fill='black')
        
app = App()
mainloop()
