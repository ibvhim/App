# <p align='center'>SIGHT Software Documentation<p>

**SIGHT** (Surveillance & Image Gathering for High-accuracy Tracking) is a fully customizable software built on Python's Tkinter library, enabling users to perform a wide range of image and video processing tasks, including Object Detection, Object Tracking, Key-point Detection, Gait Tracking, and Instance Segmentation.

## Preview
![](assets/sight.gif)


## Features 
- Highly adaptable source code for easy customization
- Custmizable backgrounds *(because why not!!)*
- Compatible with both CPU and GPU processing
- Supports both pre-recorded and real-time videos *(and images ofcourse)*


## Installation Guide

Follow these essential installation steps to set up SIGHT on your system:

### Step 1: Clone the Repository

```shell
git clone https://github.com/ibvhim/SIGHT.git
```

### Step 2: Change Directory

```shell
cd path/to/cloned_repository
```

### Step 3: Create a Python Environment

```shell
conda create -n SIGHT python==3.9 requests
```

### Step 4: Activate the Environment

```shell
conda activate SIGHT
```

### Step 5: Run Setup

```shell
python setup.py
```

### Step 6: Install Required Libraries

```shell
pip install -r requirements.txt
```

#### 6.1 (Optional): For GPU Users

If you wish to utilize your GPU for detections, use the following command:

```shell
pip install -r requirements_gpu.txt
```

### Step 7: Launch SIGHT Software

```shell
python SIGHT.py
```

---

### References & Credits
- **YOLOv7:** https://github.com/WongKinYiu/yolov7
- **YOLOv8:** https://github.com/ultralytics/ultralytics
- **Tkinter Theme:** https://github.com/rdbende/Forest-ttk-theme (I modified this theme)

---
#### <p align='center'>Hope you enjoy my side project, feel free to submit PRs. I would love to see your ideas and you can always contact me on <a href='https://www.linkedin.com/in/ibvhim/'>LinkedIn</a></p> 



<center><p align = "center"> :star::star::star: </p> </center>
