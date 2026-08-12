# 🔳 QR Code Generator & Scanner

A Python-based **QR Code Generator & Scanner** with both a **CLI application** and a **Flask web application**.

## 🌐 Live Demo

🚀 **[Open QR Code Generator & Scanner](https://qrcodegenerator-iyzh.onrender.com/)**

## ✨ Features

### 🌐 Web Application

- Generate QR codes for valid website URLs
- URL and DNS validation
- Download QR code as PNG
- Copy QR code image to clipboard
- Webcam QR scanner
- Validate scanned QR URLs
- Open scanned websites in a new tab
- Responsive UI

### 💻 CLI

- Generate QR codes from terminal
- Terminal QR preview
- URL and DNS validation
- Download QR codes
- Copy QR images to clipboard
- Generate multiple QR codes without restarting
- Webcam QR scanner

## 🛠️ Tech Stack

**Backend**
- Python
- Flask
- PyQRCode
- OpenCV
- NumPy
- Pillow

**Frontend**
- HTML
- CSS
- JavaScript

**Deployment**
- GitHub
- Render
- Gunicorn

## 📁 Project Structure

```text
qr-code-generator/
│
├── qr-code-generator-cli/
│   ├── qr.py
│   ├── qr_scanner.py
│   ├── url_validator.py
│   └── requirements.txt
│
├── qr-code-generator-web/
│   ├── app.py
│   ├── render.yaml
│   ├── requirements.txt
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── scanner.js
│
├── README.md
└── .gitignore
```

## 🚀 Run Locally

### Web Application

```bash
cd qr-code-generator-web

python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

### CLI

```bash
cd qr-code-generator-cli
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate QR:

```bash
python qr.py
```

Scan QR:

```bash
python qr_scanner.py
```

## 🔗 URL Validation

The application accepts valid website URLs such as:

```text
https://google.com
http://google.com
www.google.com
google.com
```

Invalid or nonexistent domains are rejected before QR generation.

## 📷 QR Scanner

The scanner validates the decoded QR content before treating it as a website.

```text
Valid Website QR → ✅ Accepted
Plain Text QR    → ❌ Rejected
Invalid URL QR   → ❌ Rejected
```

## 🌍 Deployment

The Flask web application is deployed using **Render**.

**Live Application:**

https://qrcodegenerator-iyzh.onrender.com/

## 👨‍💻 Author

**Akash Hugar**

GitHub:  
https://github.com/AKASH-22203

---

⭐ If you find this project useful, consider giving it a star!
