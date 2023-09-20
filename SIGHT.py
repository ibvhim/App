import os
import cv2
import subprocess
import tkinter as tk
from ultralytics import YOLO
from PIL import Image as PIM, ImageTk
from tkinter import ttk, filedialog, PhotoImage

# Class that contains the main menu page
class App:
    def __init__(self, master):
        # Initialize the variables (Main Window)
        self.master = master
        self.master.title("Surveillance Software")  # Window title
        self.window_width, self.window_height = 1280, 720  # set the width and height of the window
        self.screen_width, self.screen_height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()  # get the screen width and height
        self.x, self.y = int((self.screen_width / 2) - (self.window_width / 2)), int((self.screen_height / 2) - (self.window_height / 2))  # calculate the x and y coordinates for the window
        self.master.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")  # set the dimensions and position of the window

        # Model Variables 
        self.model = None # Model
        self.source = None # Selected source
        self.temp_source = None
        self.video_frame = None # Video frame   
        self.image_frame = None # Image frame
        self.app_dir = os.getcwd() # get the current working directory
        self.yolov7_dir = 'yolov7/' # set the child directory path
        self.tracker_ = 'botsort.yaml' # Track method

        # Background and Icons
        self.back_arrow_icon = PhotoImage(file='assets/back_arrow.png')  # Back button icon
        self.default = "assets/background_gifs/man_sitting_chair.gif" # default background path
        self.gif = PIM.open(self.default) # open the gif/png
        self.temp_bg = None

        # Main menu background(gif)
        self.bg_label = ttk.Label(self.master)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch the label to cover the whole window
        self.background_gif()

        # Source selection dropdown
        self.source_types = ["Select Source", "Webcam", "Image/Video"]  # Add "Blank" as the first option
        self.source_var = tk.StringVar(value=self.source_types[0])
        self.source_var.set(self.source_types[0])
        self.source_menu = ttk.Combobox(self.bg_label, values=self.source_types, textvariable=self.source_var, state="readonly")
        self.source_menu.place(relx=0.9, rely=0.6, anchor="se")
        self.source_menu.bind("<<ComboboxSelected>>", self.select_source)

        # Object Detection button
        self.objectdetection = ttk.Button(self.bg_label, text="Object Detection", state=tk.DISABLED, command=self.ObjectDetection_menu, style='Accent.TButton')
        self.objectdetection.place(relx=0.9,rely=0.65, anchor="se")

        # Object Tracking button
        self.objecttracking = ttk.Button(self.bg_label, text="Object Tracking", state=tk.DISABLED, command=self.ObjectTracking_menu, style='Accent.TButton')
        self.objecttracking.place(relx=0.9,rely=0.7, anchor="se")

        # Settings button
        self.settings_button = ttk.Button(self.bg_label, text="Settings", style='Accent.TButton', command=self.Settings)
        self.settings_button.place(relx=0.9,rely=0.75, anchor="se")

        # Quit button
        self.quit_button = ttk.Button(self.bg_label, text="Quit", style='Quit.TButton', command=self.quit_app)
        self.quit_button.place(relx=0.9,rely=0.8, anchor="se")

        self.update_frame(0, self.bg_label)

    # Function to check if "self.gif" path is GIF or PNG and set it as the background
    def background_gif(self):
        self.frames = []
        is_gif = False

        # Check the file type
        if self.gif.format == 'GIF':
            is_gif = True

        try:
            while True:
                if is_gif:
                    resized_frame = self.gif.resize((self.window_width, self.window_height), PIM.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(resized_frame))
                    self.gif.seek(len(self.frames))  # to go to the next frame
                else:
                    resized_image = self.gif.resize((self.window_width, self.window_height), PIM.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(resized_image))
                    break  # to exit the loop (for PNG)

        except EOFError:
            pass

    # Function to update the frame (GIF background)
    def update_frame(self, index, label):
        frame = self.frames[index]
        label.configure(image=frame)
        index = (index + 1) % len(self.frames)
        self.master.after(100, self.update_frame, index, label)

    # Function to select a source
    def select_source(self, event):
        # Disable detect button
        self.objectdetection.config(state=tk.DISABLED)
        self.objecttracking.config(state=tk.DISABLED)
        
        # Destroy previous video or image frame if it exists
        if self.video_frame is not None:
            self.video_frame.destroy()
            self.video_frame = None
        if self.image_frame is not None:
            self.image_frame.destroy()
            self.image_frame = None
        
        # Update selected source
        source_type = self.source_var.get()
        if source_type == "Select Source":
            self.source = None
            self.temp_source = None
            self.objecttracking.config(state=tk.DISABLED)
            self.objectdetection.config(state=tk.DISABLED)  # Disable buttons for blank source

        elif source_type == "Webcam":
            if self.source != None:
                self.source = None
                self.temp_source = None
            self.source = 0
            self.temp_source = 0
            self.objectdetection.config(state=tk.NORMAL)
            self.objecttracking.config(state=tk.NORMAL)  # Enable buttons for webcam source

        elif source_type == "Image/Video":
            if self.source != None:
                self.source = None  # Release the previous source [image/video]
                self.temp_source = None
            filetypes = (("Image files", "*.jpg *.jpeg *.png"), ("Video files", "*.mp4 *.avi"))
            source_path = filedialog.askopenfilename(filetypes=filetypes)
            if source_path:
                self.source = source_path
                self.temp_source = source_path
                self.objectdetection.config(state=tk.NORMAL)
                if any(source_path.endswith(extension) for extension in ('.mp4', '.avi')):
                    self.objecttracking.config(state=tk.NORMAL)  # Disable tracking button for image/video source
                else:
                    self.objecttracking.config(state=tk.DISABLED)
            else:
                self.source_var.set("Select Source")
                self.source = None


                    #########################################

                    # OBJECT DETECTION WINDOW CONFIGURATION #

                    #########################################

    def ObjectDetection_menu(self):
        self.OD = tk.Toplevel()
        self.OD.title("Object Detection")
        self.OD.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

        # Object Detection background(gif)
        self.objectdetection_bg_label = ttk.Label(self.OD)
        self.objectdetection_bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch the label to cover the whole window
        self.background_gif()

        # Back arrow button
        self.back_button = ttk.Button(self.objectdetection_bg_label, text="<", command= self.quit_OD, style='Quit.TButton')
        self.back_button.place(x= 10, y=10)

        # Model selection dropdown
        self.detect_model_names = ["Select Model", "YOLOv8", "YOLOv8-Segment", "YOLOv8-Pose"] 
        self.detect_model_var = tk.StringVar(value=self.detect_model_names[0])
        self.detect_model_var.set(self.detect_model_names[0])
        self.detect_model_menu = ttk.Combobox(self.objectdetection_bg_label, values=self.detect_model_names, textvariable=self.detect_model_var, state="readonly")
        self.detect_model_menu.place(relx=0.9, rely=0.65, anchor="se")
        self.detect_model_menu.bind("<<ComboboxSelected>>", self.enable_detect)

        # "Detect Object" button
        self.detectobject = ttk.Button(self.objectdetection_bg_label, text="Detect Object", command=self.run_detector, state=tk.DISABLED, style='Accent.TButton')
        self.detectobject.place(relx=0.9,rely=0.7, anchor="se")

        # Quit button
        self.quit_button = ttk.Button(self.objectdetection_bg_label, text="Quit", style='Quit.TButton', command=self.quit_app)
        self.quit_button.place(relx=0.9,rely=0.75, anchor="se")

        # Update the frames (for the background) 
        self.update_frame(0, self.objectdetection_bg_label)

    # Enable the Detect Button on choosing a model
    def enable_detect(self, event):
            if self.detect_model_var.get() in ['YOLOv8']:
                self.detectobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x.pt')
            
            elif self.detect_model_var.get() in ['YOLOv8-Segment']:
                self.detectobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x-seg.pt')

            elif self.detect_model_var.get() in ['YOLOv8-Pose']:
                self.detectobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x-pose-p6.pt')

            else:
                self.detectobject.config(state=tk.DISABLED)
                self.model = None
    
    def detector(self, source_):

        results = self.model.predict(source=source_, line_thickness=1, classes=[0], save=True) # 0 - Person
                
        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame 
        cv2.namedWindow('YOLOv8 Inference',cv2.WINDOW_NORMAL)
        cv2.imshow('YOLOv8 Inference', annotated_frame)
        cv2.resizeWindow('YOLOv8 Inference', 600,600)

    # Checks if a given file is an image or a video
    def isImg(self, file):
        # Check if the file is an image
        if file.endswith(".jpg") or file.endswith(".png"):
            return True
        # Check if the file is a video
        elif file.endswith(".mp4") or file.endswith(".avi"):
            return False

    # Runs the detector() function 
    def run_detector(self):
        # If source is an Image or a Video
        if self.source_var.get() == "Image/Video":
            
            if not self.isImg(self.temp_source):
                cap = cv2.VideoCapture(self.temp_source)
            
                while cap.isOpened():
                    success, frame = cap.read()
                    if success:
                        # Detect the object
                        self.detector(frame)
                        
                        # Break the loop if 'q' is pressed
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        # Break the loop if the end of the video is reached 
                        break
                
                # Releaase the video capture object and close the display window
                cap.release()
                cv2.destroyAllWindows()

            elif self.isImg(self.temp_source):
                # Read the image
                cap = cv2.imread(self.temp_source)
                
                # Detect the object 
                self.detector(cap)
                # Break the loop if 'q' is pressed
                cv2.waitKey(0) & 0xFF == ord("q")
                cv2.destroyAllWindows()

        # Check if source is a webcam
        elif self.source_var.get() == "Webcam":
            cap = cv2.VideoCapture(0)
            
            while cap.isOpened():
                success, frame = cap.read()
                if success:
                    # Detect the object
                    self.detector(frame)
                    # Break the loop if 'q' is pressed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # Break the loop if the end of the video is reached 
                    break
                
            # Releaase the video capture object and close the display window
            cap.release()
            cv2.destroyAllWindows()

    

                    #########################################

                    # OBJECT TRACKING WINDOW CONFIGURATION #

                    #########################################

    def ObjectTracking_menu(self):
        self.OT = tk.Toplevel()
        self.OT.title("Object Tracking")
        self.OT.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

        # Object Tracking background(gif)
        self.objecttracking_bg_label = ttk.Label(self.OT)
        self.objecttracking_bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Stretch the label to cover the whole window
        self.background_gif()
        
        # Back arrow button
        self.back_button = ttk.Button(self.objecttracking_bg_label, text="<", command= self.quit_OT, style='Quit.TButton')
        self.back_button.place(x= 10, y=10)
        
        # Tracking Model selection dropdown
        self.track_model_names = ["Select Model ", "YOLOv8", "YOLOv8-Segment", "YOLOv8-Pose", "YOLOv7",] # "YOLOv7-Precise"] 
        self.track_model_var = tk.StringVar(value=self.track_model_names[0])
        self.track_model_var.set(self.track_model_names[0])
        self.track_model_menu = ttk.Combobox(self.objecttracking_bg_label, values=self.track_model_names, textvariable=self.track_model_var, state="readonly")
        self.track_model_menu.place(relx=0.9, rely=0.6, anchor="se")
        self.track_model_menu.bind("<<ComboboxSelected>>", self.enable_track)

        # Tracking Method selection dropdown
        self.track_method_names = ["Select Tracker", "BoT-SORT", "ByteTrack"] 
        self.track_method_var = tk.StringVar(value=self.track_method_names[0])
        self.track_method_var.set(self.track_method_names[0])
        self.track_method_menu = ttk.Combobox(self.objecttracking_bg_label, values=self.track_method_names, textvariable=self.track_method_var, state="readonly")
        self.track_method_menu.place(relx=0.9,rely=0.65, anchor="se")
        self.track_method_menu.bind("<<ComboboxSelected>>", self.update_track_method)

        # "Track Object" button
        self.trackobject = ttk.Button(self.objecttracking_bg_label, text="Track Object", state=tk.DISABLED, command=self.run_tracker, style='Accent.TButton')
        self.trackobject.place(relx=0.9,rely=0.7, anchor="se")

        # Quit button
        self.quit_button = ttk.Button(self.objecttracking_bg_label, text="Quit", style='Quit.TButton', command=self.quit_app)
        self.quit_button.place(relx=0.9,rely=0.75, anchor="se")
        
        # Update the frames (for the background) 
        self.update_frame(0, self.objecttracking_bg_label)

    # Enable the Track Button on choosing a model
    def enable_track(self, event):
            if self.track_model_var.get() in ['YOLOv8']:
                self.trackobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x.pt')
                self.track_method_menu['state'] = 'readonly'

            elif self.track_model_var.get() in ['YOLOv8-Segment']:
                self.trackobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x-seg.pt')
                self.track_method_menu['state'] = 'readonly'

            elif self.track_model_var.get() in ['YOLOv8-Pose']:
                self.trackobject.config(state=tk.NORMAL)
                self.model = YOLO('models/yolov8x-pose-p6.pt')
                self.track_method_menu['state'] = 'readonly'

            elif self.track_model_var.get() in ['YOLOv7']:
                self.trackobject.config(state=tk.NORMAL)
                self.model = 'models/yolov7x.pt'
                self.track_method_var.set(self.track_method_names[0])
                self.track_method_menu['state'] = 'disabled'

            # elif self.track_model_var.get() in ['YOLOv7-Precise']:
            #     self.trackobject.config(state=tk.NORMAL)
            #     self.model = 'models/yolov7x.pt'
            #     self.track_method_var.set(self.track_method_names[0])
            #     self.track_method_menu['state'] = 'disabled'
            
            else:
                self.model = None
                self.trackobject.config(state=tk.DISABLED)
                self.track_method_var.set(self.track_method_names[0])
                self.track_method_menu['state'] = 'readonly'

    # Update the tacking method when user chooses it in the combobox
    def update_track_method(self, event):
        if self.track_method_var.get() in ['BoT-SORT']:
            self.tracker_ = 'botsort.yaml'
            print(f'You have chosen the {str(self.tracker_.split(".")[0]).upper()} tracker!')

        elif self.track_method_var.get() in ['ByteTrack']:
            self.tracker_ = 'bytetrack.yaml'
            print(f'You have chosen the {str(self.tracker_.split(".")[0]).upper()} tracker!')
        
        else:
            self.tracker_ = 'botsort.yaml'
            print(f'{str(self.tracker_.split(".")[0]).upper()} has been chosen as the default tracker!')

    # Track 
    def tracker(self, source_, tracker_):

        results = self.model.track(source = source_, tracker = tracker_, classes = [0], persist=True, save=True)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame 
        cv2.namedWindow('YOLOv8 Inference',cv2.WINDOW_NORMAL)
        cv2.imshow('YOLOv8 Inference', annotated_frame)
        cv2.resizeWindow('YOLOv8 Inference', 600,600)


    def run_tracker(self):
        
        # Run YOLOv8 tracker if YOLOv8 is selected 
        if self.track_model_var.get() in ["YOLOv8", "YOLOv8-Segment", "YOLOv8-Pose"]:
            # If source is an Image or a Video
            if self.source_var.get() == "Image/Video":
                # Confirm source is a video
                if not self.isImg(self.temp_source):
                    cap = cv2.VideoCapture(self.temp_source)
                
                    while cap.isOpened():
                        success, frame = cap.read()
                        if success:
                            # track the object
                            self.tracker(frame, self.tracker_)
                            
                            # Break the loop if 'q' is pressed
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                        else:
                            # Break the loop if the end of the video is reached 
                            break
                    
                    # Releaase the video capture object and close the display window
                    cap.release()
                    cv2.destroyAllWindows()

            # Check if source is a webcam
            elif self.source_var.get() == "Webcam":
                cap = cv2.VideoCapture(0)
                
                while cap.isOpened():
                    success, frame = cap.read()
                    if success:
                        # Detect the object
                        self.tracker(frame, self.tracker_)
                        # Break the loop if 'q' is pressed
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        # Break the loop if the end of the video is reached 
                        break
                    
                # Releaase the video capture object and close the display window
                cap.release()
                cv2.destroyAllWindows()
        
        # Run YOLOv7 tracker if YOLOv7 is selected
        elif self.track_model_var.get() in ['YOLOv7']:
            # navigate to the child directory
            os.chdir(self.yolov7_dir)

            # Track object 
            command = ["python", "detect_or_track.py", "--weights", str(f'{os.pardir}/{self.model}'), 
                                                       "--source", str(self.temp_source), 
                                                       "--classes", "0",
                                                       "--track", 
                                                       "--show-track", 
                                                       "--view-img",  
                                                       "--unique-track-color", 
                                                       "--nosave", 
                                                       "--nobbox"]

            subprocess.run(command)
    
            # navigate back to the parent directory
            os.chdir(self.app_dir)

        # Yet to add the below functionality
        # elif self.track_model_var.get() in ['YOLOv7-Precise']:
        #     # navigate to the child directory
        #     os.chdir(self.yolov7_dir)

        #     # Track object 
        #     command = ["python", "detect_or_track.py", "--weights", str(f'{os.pardir}/{self.model}'), 
        #                                                "--source", str(self.temp_source), 
        #                                                "--classes", "0",
        #                                                "--track", 
        #                                                "--show-track", 
        #                                                "--view-img",  
        #                                                "--unique-track-color", 
        #                                                "--nosave", 
        #                                                "--nobbox",
        #                                                "--precise-track"]

        #     subprocess.run(command)
    
        #     # navigate back to the parent directory
        #     os.chdir(self.app_dir)
        
        else: 
            print('Error 212: User did not select a model!')


                    #########################################

                    #    SETTINGS WINDOW CONFIGURATION      #

                    #########################################

    def Settings(self):
        self.settings = tk.Toplevel()
        self.settings.title("Settings")
        self.settings_window_width, self.settings_window_height = 304, 304  # set the width and height of the window
        self.settings_x, self.settings_y = int((self.screen_width / 2) - (self.settings_window_width / 2)), int((self.screen_height / 2) - (self.settings_window_height / 2))  # calculate the x and y coordinates for the window
        self.settings.geometry(f"{self.settings_window_width}x{self.settings_window_height}+{self.settings_x}+{self.settings_y}")  # set the dimensions and position of the window

        # Settings frame
        self.settings_frame = ttk.Frame(self.settings, style='Card.TFrame', padding=(5,5,5,5))
        self.settings_frame.pack(expand=True)

        # Background selection dropdown
        self.background_types = ["Select Background", "Image (*.png)", 'GIF'] # Add "Blank" as the first option
        self.background_var = tk.StringVar(value=self.background_types[0])
        self.background_var.set(self.background_types[0])
        self.background_menu = ttk.Combobox(self.settings_frame, values=self.background_types, textvariable=self.background_var, state="readonly")
        self.background_menu.pack(padx=10, pady=10)
        self.background_menu.bind("<<ComboboxSelected>>", self.select_bg)

        # Save button
        self.settings_save_btn = ttk.Button(self.settings_frame, text="Save",state=tk.DISABLED, command=self.save_bg, style='Accent.TButton')
        self.settings_save_btn.pack(padx=10, pady=10)
       
        # Back button
        self.settings_back_btn = ttk.Button(self.settings_frame, text="Back", command=self.quit_Settings, style='Quit.TButton')
        self.settings_back_btn.pack(padx=10, pady=10)

        # Back arrow button
        # self.back_button = ttk.Button(self.settings, text="<", command= self.quit_Settings, style='Quit.TButton')
        # self.back_button.place(x= 10, y=10)

    # Function to select a background
    def select_bg(self, event):
        # Disable save button
        self.settings_save_btn.config(state=tk.DISABLED)

        background = self.background_var.get()

        if background == "Select Background":
            self.temp_gif = None

        elif background == "Image (*.png)":
            filetypes = (("Image files", "*.png"),)
            bg_path = filedialog.askopenfilename(filetypes=filetypes)

            if bg_path:
                self.temp_gif = PIM.open(bg_path)
                self.settings_save_btn.config(state=tk.NORMAL)
            else:
                self.background_var.set("Select Background")

        elif background == "GIF":
            filetypes = (("GIF files", "*.gif"),)
            bg_path = filedialog.askopenfilename(filetypes=filetypes)

            if bg_path:
                self.temp_gif = PIM.open(bg_path)
                self.settings_save_btn.config(state=tk.NORMAL)
            else:
                self.background_var.set("Select Background")

    # Function to save the selected background
    def save_bg(self):
        if self.temp_gif is not None:
            self.gif = self.temp_gif
            self.update_main_page_background() 
            self.quit_Settings()

    def update_main_page_background(self):
            self.background_gif()
            self.update_frame(0, self.bg_label)

    # Quits the Object Detection window
    def quit_OD(self):
        self.OD.destroy()

    # Quits the Object Detection window
    def quit_Settings(self):
        self.settings.destroy()

    # Quits the Object Detection window
    def quit_OT(self):
        self.OT.destroy()

    # Quits the application
    def quit_app(self):
        self.master.destroy()

    def start(self):
        self.master.mainloop() # Start the app
        

# Set up the main window
root = tk.Tk()

# Set the theme -> azure.tcl 
root.tk.call("source", "assets/Forest-ttk/forest-light.tcl")

# Choose the mode
# root.tk.call("set_theme", "dark")
ttk.Style().theme_use('forest-light')

# Create an instance of the GUI class
app = App(root)

# Start the GUI running
app.start()
