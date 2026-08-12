import cv2
import webbrowser

from url_validator import validate_url


def scan_qr_code():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("❌ Unable to access the camera.")
        print("Please check your camera connection.")

        return

    detector = cv2.QRCodeDetector()

    print("=" * 45)
    print("          QR CODE SCANNER CLI")
    print("=" * 45)

    print()
    print("📷 Camera started.")
    print("Point the camera at a QR code.")
    print("Press Q to exit.")
    print()

    try:

        while True:

            success, image = cap.read()

            if not success:

                print("❌ Unable to read camera frame.")
                break

            data, bbox, _ = detector.detectAndDecode(image)

            if data:

                print()
                print("🔍 QR code detected!")
                print(f"📦 Content: {data}")

                is_valid, normalized_url, error = validate_url(
                    data,
                    check_dns=True
                )

                if is_valid:

                    print("✅ Valid website URL detected!")
                    print(f"🔗 URL: {normalized_url}")

                    print("\n🌐 Opening website...")

                    webbrowser.open(normalized_url)

                else:

                    print(
                        "\n❌ This QR code does not contain "
                        "a valid website URL."
                    )

                    print(f"Reason: {error}")

                break

            cv2.imshow(
                "QR Code Scanner - Press Q to Exit",
                image
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                print("\n👋 Scanner closed.")
                break

    finally:

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    scan_qr_code()