# 👋 Wellcome To the World of **"Hello World"**!

> Hi. This is our first "README" file for this project and we have no purpose of doing that except for fun...!

---

## 🗓️ About This README
Today is **"sunday-june 21,2026 (1405/03/31)"**,<br>two amir (Amir Mohammad and Amir mmd) decided to write this text for keepsake... :)

---

## 🚀 Our Advice
> "I say to everyone who is reading this text that **Live Long Programmers**....!"

---
![Programers](.md%20Files/01_For_Keepsake.jpg)
*Happy Coding! 💻*

---

# Laser Surface Scanner

A laser triangulation-based surface inspection system developed for measuring object profiles and evaluating surface flatness using computer vision techniques.

## 📖 Overview

The Laser Surface Scanner is a research project designed to capture the cross-sectional profile of an object using laser triangulation. A laser line is projected onto the object's surface, and a calibrated camera captures the reflected laser line. Image processing algorithms are then used to extract the laser profile and calculate surface geometry.

This repository contains the image processing and measurement algorithms used in the project.

## ✨ Features

- Laser line detection
- Camera calibration
- Image preprocessing
- Laser profile extraction
- Surface profile visualization
- Distance measurement using laser triangulation
- Surface flatness analysis

## 🛠 Technologies

- Python
- OpenCV
- NumPy
- Raspberry Pi Camera
- Laser Triangulation
- Computer Vision

## 📂 Project Structure

```text
Laser-Surface-Scanner/
│
├── calibration/         # Camera calibration scripts
├── processing/          # Image processing algorithms
├── detection/           # Laser line detection
├── measurement/         # Distance calculation
├── utils/               # Utility functions
├── images/              # Sample images
├── results/             # Output results
├── requirements.txt
└── README.md
```

## ⚙️ How It Works

1. Capture an image using the calibrated camera.
2. Detect the laser line from the captured image.
3. Extract the center of the laser stripe.
4. Convert pixel positions into real-world coordinates using camera calibration.
5. Generate the surface profile.
6. Analyze surface flatness and geometry.

## 📷 Example Workflow

```text
Laser Projector
        │
        ▼
Object Surface
        │
        ▼
Camera Capture
        │
        ▼
Image Processing
        │
        ▼
Laser Line Detection
        │
        ▼
Triangulation
        │
        ▼
Surface Profile
```

## 🎯 Applications

- Surface inspection
- Quality control
- Reverse engineering
- Manufacturing
- Research laboratories
- Industrial measurement

## 🚀 Future Improvements

- Real-time scanning
- 3D point cloud generation
- Automatic calibration
- Noise reduction
- GPU acceleration
- Higher measurement accuracy 

## 👨‍💻 Author

**Amir Mohammadi**

Electrical Engineer | Embedded Systems | Computer Vision | DevOps | Cybersecurity

---

*This project was developed as part of a research project on laser-based surface inspection and computer vision.*