import os
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

import pyqrcode

from url_validator import validate_url


QR_SCALE = 10


# ============================================================
# TERMINAL QR DISPLAY
# ============================================================

def display_qr_in_terminal(qr):
    """
    Display the QR code directly in the terminal.
    """

    matrix = qr.code

    print()
    print(" " * 6 + "QR CODE")
    print()

    border = 2

    width = len(matrix)
    height = len(matrix)

    for y in range(-border, height + border, 2):

        line = ""

        for x in range(-border, width + border):

            top = False
            bottom = False

            if 0 <= y < height and 0 <= x < width:
                top = matrix[y][x] == 1

            if 0 <= y + 1 < height and 0 <= x < width:
                bottom = matrix[y + 1][x] == 1

            if top and bottom:
                line += "█"

            elif top:
                line += "▀"

            elif bottom:
                line += "▄"

            else:
                line += " "

        print(line)

    print()


# ============================================================
# CREATE QR
# ============================================================

def create_qr(url):
    try:
        return pyqrcode.create(url)

    except Exception as error:
        print(f"\n❌ Unable to create QR code: {error}")
        return None


# ============================================================
# FILE NAME
# ============================================================

def generate_filename(url):

    parsed = urlparse(url)
    hostname = parsed.hostname

    if hostname:
        hostname = hostname.replace("www.", "")
        hostname = hostname.replace(".", "_")
    else:
        hostname = "website"

    return f"{hostname}_qr.png"


# ============================================================
# DOWNLOAD QR
# ============================================================

def download_qr(qr, url):

    filename = generate_filename(url)

    base, extension = os.path.splitext(filename)

    counter = 1

    while os.path.exists(filename):
        filename = f"{base}_{counter}{extension}"
        counter += 1

    try:

        qr.png(
            filename,
            scale=QR_SCALE
        )

        full_path = os.path.abspath(filename)

        print("\n✅ QR code downloaded successfully!")
        print(f"📁 File: {full_path}")

        return full_path

    except Exception as error:

        print(f"\n❌ Unable to save QR code: {error}")

        return None


# ============================================================
# COPY QR TO WINDOWS CLIPBOARD
# ============================================================

def copy_qr_to_clipboard(qr):

    if sys.platform != "win32":

        print(
            "\n⚠️ QR image clipboard copy is currently "
            "supported on Windows."
        )

        return False

    temporary_file = os.path.join(
        tempfile.gettempdir(),
        "qr_code_clipboard.png"
    )

    try:

        qr.png(
            temporary_file,
            scale=QR_SCALE
        )

        escaped_path = temporary_file.replace("'", "''")

        powershell_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$image = [System.Drawing.Image]::FromFile('{escaped_path}')

[System.Windows.Forms.Clipboard]::SetImage($image)
"""

        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("\n✅ QR code copied to clipboard!")
        print(
            "You can paste it into WhatsApp, Word, "
            "PowerPoint, Paint, etc."
        )

        return True

    except Exception as error:

        print(f"\n❌ Unable to copy QR code: {error}")

        return False


# ============================================================
# MENU
# ============================================================

def qr_menu(qr, url):

    while True:

        print("=" * 45)
        print("                 OPTIONS")
        print("=" * 45)

        print("1. Download QR")
        print("2. Copy QR")
        print("3. Generate Another QR")
        print("4. Exit")

        print("=" * 45)

        choice = input("Enter choice: ").strip()

        if choice == "1":

            download_qr(qr, url)

        elif choice == "2":

            copy_qr_to_clipboard(qr)

        elif choice == "3":

            return "another"

        elif choice == "4":

            return "exit"

        else:

            print("\n⚠️ Invalid choice.")
            print("Please select 1, 2, 3 or 4.")


# ============================================================
# GENERATE QR FLOW
# ============================================================

def generate_qr_flow(url):

    print("\n🔍 Checking website...")

    is_valid, normalized_url, error = validate_url(
        url,
        check_dns=True
    )

    if not is_valid:

        print(f"\n❌ {error}")
        print("Please check the URL and try again.")

        return "invalid"

    print("✅ Website verified!")
    print(f"🔗 URL: {normalized_url}")

    qr = create_qr(normalized_url)

    if qr is None:
        return "invalid"

    display_qr_in_terminal(qr)

    print("✅ QR code generated successfully!")

    return qr_menu(
        qr,
        normalized_url
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 45)
    print("          QR CODE GENERATOR CLI")
    print("=" * 45)

    print()
    print("Generate QR codes for valid website URLs.")
    print("The domain will be checked before generation.")
    print()
    print("Type 'exit' to close the application.")

    while True:

        print("\n" + "-" * 45)

        url = input("Enter website URL: ").strip()

        if url.lower() in ("exit", "quit", "q"):

            print(
                "\n👋 Thank you for using QR Code Generator!"
            )

            break

        if not url:

            print("\n⚠️ Please enter a website URL.")
            continue

        result = generate_qr_flow(url)

        if result == "another":

            print("\n🔄 Generate another QR code...")
            continue

        if result == "exit":

            print("\n👋 Goodbye!")
            break

        if result == "invalid":

            continue


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()
