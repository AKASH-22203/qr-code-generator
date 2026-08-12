# 🔳 QR Code Generator & Scanner

A Python-based **QR Code Generator & Scanner** with both a **CLI application** and a **Flask web application**.

The application generates QR codes only for **valid and resolvable website URLs** and provides QR scanning, downloading, and clipboard copy functionality.

## ✨ Features

### 🌐 Web Application

- Generate QR codes for valid website URLs
- Automatic `https://` addition
- URL and domain validation
- DNS verification
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
qrcodegenerator/
│
├── app.py
├── qr.py
├── qrscanner.py
├── requirements.txt
├── render.yaml
├── .python-version
├── .gitignore
├── README.md
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── scanner.js
```

> `venv/` is not included in the repository.

## 🚀 Run Locally

### 1. Clone Repository

```bash
git clone https://github.com/AKASH-22203/qrcodegenerator.git
cd qrcodegenerator
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Web Application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

## 💻 Run CLI

### QR Generator

```bash
python qr.py
```

### QR Scanner

```bash
python qrscanner.py
```

## 🔗 URL Validation

The application accepts URLs such as:

```text
https://google.com
http://google.com
www.google.com
google.com
```

Invalid or nonexistent domains are rejected before QR generation.

Example:

```text
Enter website URL: whatsaoo.co

❌ The website 'whatsaoo.co' could not be found.
```

## 📷 QR Scanner

The scanner validates the decoded QR content before treating it as a website.

```text
Valid URL QR       → ✅ Accepted
Plain text QR      → ❌ Rejected
Invalid URL QR     → ❌ Rejected
```

## 🌍 Deployment

The Flask application is configured for deployment using **Render**.

Deployment configuration:

```text
render.yaml
.python-version
```

## 👨‍💻 Author

**Akash Hugar**

GitHub:  
https://github.com/AKASH-22203/qrcodegenerator

---

⭐ If you find this project useful, consider giving it a star!
