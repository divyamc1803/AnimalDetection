# 🐾 Animal Detection System

An AI-powered Animal Detection Web Application built using **Flask**, **YOLOv11**, **OpenCV**, and **SQL Server**. The application allows users to securely log in, upload images or use a live webcam to detect animals, and generate downloadable reports.

---

## 🚀 Features

- 🔐 User Registration & Login (SQL Server)
- 🔒 Secure Password Hashing
- 📁 Upload Multiple Images
- 🎥 Live Webcam Animal Detection
- 🤖 Animal Detection using YOLOv11
- 📊 Detection Summary
- 📄 Download PDF Report
- 📑 Download CSV Report
- 🗑️ Clear Detection Session
- 👤 User Authentication with Flask Sessions

---

## 🛠️ Technologies Used

- Python
- Flask
- YOLOv11 (Ultralytics)
- OpenCV
- SQL Server
- HTML
- CSS
- ReportLab
- PyODBC

---

## 📂 Project Structure

```text
AnimalDetection/
│
├── app.py
├── database.py
├── detector.py
├── report.py
├── webcam.py
├── Train.py
├── yolo11n.pt
├── templates/
├── static/
├── images/
├── README.md
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/divyamc1803/AnimalDetection.git
```

Move into the project folder:

```bash
cd AnimalDetection
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 💾 Database Setup

Create a SQL Server database named:

```
AnimalDetectionDB
```

Create the **Users** table:

```sql
CREATE TABLE Users
(
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);
```

Update the SQL Server credentials inside `database.py` if required.

---

## ▶️ Running the Project

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the Flask application:

```bash
python3 app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 🧠 Model Training

The repository includes **Train.py** for training a custom YOLO model.

The model was trained using a custom animal dataset.

To retrain the model:

```bash
python3 Train.py
```

---

## 📸 Screenshots

You can add screenshots here later.

Example:

```
Login Page

Dashboard

Animal Detection Results

Webcam Detection
```

---

## 🔮 Future Improvements

- Detection History using SQL Server
- Analytics Dashboard
- Animal Detection Charts
- Save Detected Images
- Admin Dashboard
- Improved UI Design
- Cloud Deployment

---

## 👨‍💻 Author

**Divyam Choudhary**

GitHub:
https://github.com/divyamc1803

---

## ⭐ If you like this project

Give this repository a ⭐ on GitHub.