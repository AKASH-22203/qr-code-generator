import base64
import os
import socket
from io import BytesIO
from urllib.parse import urlparse

import cv2
import numpy as np
import pyqrcode
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

QR_SCALE = 10

# Maximum uploaded image size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ============================================================
# URL FORMAT VALIDATION
# ============================================================

def normalize_url(value):
    """
    Normalize and validate the basic URL structure.

    Accepted examples:
        google.com
        www.google.com
        https://google.com
        http://github.com

    The function checks URL structure only.
    DNS validation is performed separately.
    """

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    # Automatically add HTTPS when protocol is missing.
    if not value.lower().startswith(("http://", "https://")):
        value = "https://" + value

    try:
        parsed = urlparse(value)

        # Only HTTP and HTTPS websites are allowed.
        if parsed.scheme.lower() not in ("http", "https"):
            return None

        # Hostname must exist.
        if not parsed.hostname:
            return None

        hostname = parsed.hostname.lower()

        # Reject whitespace anywhere in the URL.
        if any(character.isspace() for character in value):
            return None

        # localhost is allowed for local development.
        if hostname != "localhost" and "." not in hostname:
            return None

        # Reject malformed hostnames.
        if hostname.startswith(".") or hostname.endswith("."):
            return None

        if ".." in hostname:
            return None

        # DNS names cannot exceed 253 characters.
        if len(hostname) > 253:
            return None

        return value

    except (ValueError, TypeError):
        return None


# ============================================================
# DNS VALIDATION
# ============================================================

def domain_exists(hostname):
    """
    Check whether the hostname can be resolved using DNS.
    """

    try:
        socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        return True

    except (socket.gaierror, socket.timeout, OSError):
        return False


# ============================================================
# COMPLETE URL VALIDATION
# ============================================================

def validate_url(value):
    """
    Perform:

    1. URL structure validation
    2. DNS/domain existence validation

    Returns:

        (True, normalized_url, None)

    or:

        (False, None, error_message)
    """

    url = normalize_url(value)

    if not url:
        return (
            False,
            None,
            "Please enter a valid HTTP/HTTPS website URL."
        )

    parsed = urlparse(url)
    hostname = parsed.hostname.lower()

    # Allow localhost during development.
    if hostname == "localhost":
        return True, url, None

    # Verify that the domain actually exists.
    if not domain_exists(hostname):
        return (
            False,
            None,
            f"The website '{hostname}' could not be found. "
            "Please check the URL."
        )

    return True, url, None


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# GENERATE QR
# ============================================================

@app.route("/generate", methods=["POST"])
def generate_qr():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Please provide a website URL."
        }), 400

    raw_url = data.get("url", "")

    # Validate URL + DNS.
    is_valid, url, error_message = validate_url(raw_url)

    if not is_valid:
        return jsonify({
            "error": error_message
        }), 400

    # Generate QR code.
    try:

        qr = pyqrcode.create(url)

        buffer = BytesIO()

        qr.png(
            buffer,
            scale=QR_SCALE
        )

        buffer.seek(0)

        img_base64 = base64.b64encode(
            buffer.read()
        ).decode("utf-8")

        return jsonify({
            "qr": f"data:image/png;base64,{img_base64}",
            "url": url
        })

    except Exception:
        return jsonify({
            "error": (
                "Unable to generate the QR code. "
                "Please try again."
            )
        }), 500


# ============================================================
# SCAN QR
# ============================================================

@app.route("/scan", methods=["POST"])
def scan_qr():

    if "image" not in request.files:
        return jsonify({
            "error": "No image was provided."
        }), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({
            "error": "Please select an image."
        }), 400

    try:

        image_data = file.read()

        if not image_data:
            return jsonify({
                "error": "The uploaded image is empty."
            }), 400

        img_array = np.frombuffer(
            image_data,
            np.uint8
        )

        img = cv2.imdecode(
            img_array,
            cv2.IMREAD_COLOR
        )

        if img is None:
            return jsonify({
                "error": "Invalid image. Please upload a valid image."
            }), 400

        detector = cv2.QRCodeDetector()

        data, bbox, _ = detector.detectAndDecode(img)

        if not data:
            return jsonify({
                "error": "No QR code found in the image."
            }), 400

        # Validate the content found inside the QR.
        is_valid, scanned_url, error_message = validate_url(data)

        if not is_valid:
            return jsonify({
                "error": (
                    "QR code found, but it does not contain "
                    "a valid website URL."
                )
            }), 400

        return jsonify({
            "url": scanned_url
        })

    except Exception:
        return jsonify({
            "error": "Unable to scan the QR code."
        }), 500


# ============================================================
# INVALID FILE SIZE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image is too large. Maximum allowed size is 10 MB."
    }), 413


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )