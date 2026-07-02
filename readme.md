# 🐾 Animal Detection System

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![YOLOv11](https://img.shields.io/badge/YOLO-v11-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange) ![REST
API](https://img.shields.io/badge/API-REST-success)
![Swagger](https://img.shields.io/badge/Docs-Swagger-brightgreen)

An AI-powered Animal Detection System built with **Flask**, **YOLOv11**,
**OpenCV**, and **MySQL**. The application detects people and supported
animal classes from uploaded images or a live webcam feed, stores
results in a relational database, generates reports, provides REST APIs
with Swagger documentation, and visualizes detection statistics using
NumPy and Matplotlib.

------------------------------------------------------------------------

# Features

-   User Registration & Login
-   Secure Session Management
-   Image Upload
-   YOLOv11 Animal & Person Detection
-   Live Webcam Detection
-   Detection Results with Confidence Scores
-   MySQL Database Integration
-   CSV Report Generation
-   PDF Report Generation
-   Detection Analytics (Bar Graph)
-   REST APIs
-   Swagger API Documentation

------------------------------------------------------------------------

# Technology Stack

  Layer             Technologies
  ----------------- -----------------------
  Frontend          HTML, CSS, Jinja2
  Backend           Python, Flask
  AI Model          YOLOv11 (Ultralytics)
  Database          MySQL
  Computer Vision   OpenCV
  Analytics         NumPy, Matplotlib
  Documentation     Swagger (Flasgger)

------------------------------------------------------------------------

# System Architecture

``` text
             +----------------------+
             |      Web Browser     |
             +----------+-----------+
                        |
                        v
              Flask Web Application
                        |
      +-----------------+-----------------+
      |                 |                 |
      v                 v                 v
 Authentication   YOLOv11 Detector    REST APIs
      |                 |                 |
      +--------+--------+                 |
               |                          |
               v                          v
          MySQL Database          Swagger Documentation
               |
               v
      CSV / PDF Reports / Graph Analytics
```

------------------------------------------------------------------------

# Screenshots

> Create a folder named **screenshots** and place the following images
> inside it.

## Login

![Login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard.png)

## Detection Results

![Results](screenshots/results.png)

## Detection Analytics

![Graph](screenshots/graph.png)

## Live Webcam Detection

![Webcam](screenshots/webcam.png)

## PDF Report

![PDF](screenshots/pdf.png)

## CSV Export

![CSV](screenshots/csv.png)

------------------------------------------------------------------------

# REST API Endpoints

  Method   Endpoint                    Description
  -------- --------------------------- -------------------
  POST     `/api/register`             Register a user
  POST     `/api/login`                Login
  POST     `/api/logout`               Logout
  POST     `/api/upload`               Upload images
  GET      `/api/detect`               Run detection
  GET      `/api/history`              Upload history
  GET      `/api/results/<image_id>`   Detection results
  GET      `/api/profile`              User profile
  DELETE   `/api/image/<image_id>`     Delete image

Swagger UI:

``` text
http://127.0.0.1:5000/apidocs
```

------------------------------------------------------------------------

# Skills Demonstrated

-   Flask Development
-   REST API Design
-   Swagger Documentation
-   MySQL Database Design
-   SQL Relationships
-   Session Authentication
-   Computer Vision
-   YOLOv11 Integration
-   OpenCV
-   NumPy
-   Matplotlib
-   PDF & CSV Report Generation
-   Git & GitHub

------------------------------------------------------------------------

# Future Improvements

-   JWT Authentication
-   Docker Support
-   Cloud Deployment
-   Object Tracking in Video
-   React Frontend
-   Email Notifications
-   Admin Dashboard

------------------------------------------------------------------------

# Installation

``` bash
git clone <repository-url>
cd AnimalDetection

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

python app.py
```

Open:

``` text
http://127.0.0.1:5000
```

------------------------------------------------------------------------

# Author

**Divyam Choudhary**

AI-powered Animal Detection System built as a portfolio project
demonstrating Computer Vision, Flask backend development, REST APIs,
MySQL integration, analytics, and reporting.
