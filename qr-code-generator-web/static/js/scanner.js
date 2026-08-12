// ============================================================
// QR CODE GENERATOR & SCANNER
// ============================================================

// ============================================================
// GLOBAL VARIABLES
// ============================================================

const video = document.getElementById('video')
const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')

let stream = null
let isScanning = false

// ============================================================
// URL FORMAT VALIDATION
// ============================================================

function normalizeAndValidateURL(value) {
  if (!value || typeof value !== 'string') {
    return null
  }

  value = value.trim()

  if (!value) {
    return null
  }

  // Automatically add HTTPS when protocol is missing.
  if (
    !value.toLowerCase().startsWith('http://') &&
    !value.toLowerCase().startsWith('https://')
  ) {
    value = 'https://' + value
  }

  try {
    const url = new URL(value)

    // Only HTTP and HTTPS are allowed.
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return null
    }

    // Hostname must exist.
    if (!url.hostname) {
      return null
    }

    // Reject whitespace.
    if (/\s/.test(value)) {
      return null
    }

    const hostname = url.hostname.toLowerCase()

    // Reject malformed hostnames.
    if (
      hostname.startsWith('.') ||
      hostname.endsWith('.') ||
      hostname.includes('..')
    ) {
      return null
    }

    // Normal websites should contain a dot.
    if (!hostname.includes('.') && hostname !== 'localhost') {
      return null
    }

    return url.href
  } catch (error) {
    return null
  }
}

// ============================================================
// GENERATOR MESSAGE
// ============================================================

function showMessage(message, type) {
  const messageElement = document.getElementById('message')

  messageElement.textContent = message

  messageElement.className = 'message ' + type
}

function clearMessage() {
  const messageElement = document.getElementById('message')

  messageElement.textContent = ''

  messageElement.className = 'message'
}

// ============================================================
// GENERATE QR
// ============================================================

async function generateQR() {
  const input = document.getElementById('urlInput')

  const generateButton = document.getElementById('generateBtn')

  const rawURL = input.value.trim()

  // --------------------------------------------------------
  // Basic frontend validation
  // --------------------------------------------------------

  const validURL = normalizeAndValidateURL(rawURL)

  if (!validURL) {
    showMessage(
      '❌ Please enter a valid website URL. Example: https://www.google.com',
      'error',
    )

    hideQRCode()

    input.focus()

    return
  }

  // --------------------------------------------------------
  // Loading state
  // --------------------------------------------------------

  generateButton.disabled = true

  generateButton.textContent = 'Checking website...'

  showMessage('🔍 Checking whether the website exists...', 'info')

  hideQRCode()

  // --------------------------------------------------------
  // Send URL to Flask
  // --------------------------------------------------------

  try {
    const response = await fetch('/generate', {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        url: validURL,
      }),
    })

    let data

    try {
      data = await response.json()
    } catch (error) {
      throw new Error('Invalid server response.')
    }

    // ----------------------------------------------------
    // Backend rejected URL
    // ----------------------------------------------------

    if (!response.ok) {
      showMessage(
        '❌ ' + (data.error || 'This website URL is not valid.'),
        'error',
      )

      hideQRCode()

      return
    }

    // ----------------------------------------------------
    // QR generated
    // ----------------------------------------------------

    if (data.qr && data.url) {
      const qrImage = document.getElementById('qrImg')

      const generatedURL = document.getElementById('generatedUrl')

      const qrContainer = document.getElementById('qrContainer')

      qrImage.src = data.qr

      qrImage.alt = 'QR Code for ' + data.url

      generatedURL.textContent = data.url

      qrContainer.classList.add('show')

      showMessage(
        '✓ Website verified and QR code generated successfully!',
        'success',
      )
    } else {
      showMessage('❌ QR code could not be generated.', 'error')

      hideQRCode()
    }
  } catch (error) {
    console.error('Generate QR error:', error)

    showMessage(
      '❌ Unable to connect to the server. Please try again.',
      'error',
    )

    hideQRCode()
  } finally {
    generateButton.disabled = false

    generateButton.textContent = 'Generate QR Code'
  }
}

// ============================================================
// HIDE QR
// ============================================================

function hideQRCode() {
  const qrContainer = document.getElementById('qrContainer')

  const qrImage = document.getElementById('qrImg')

  const generatedURL = document.getElementById('generatedUrl')

  qrContainer.classList.remove('show')

  qrImage.removeAttribute('src')

  generatedURL.textContent = ''
}

// ============================================================
// DOWNLOAD QR
// ============================================================

function downloadQR() {
  const qrImage = document.getElementById('qrImg')

  if (!qrImage.src) {
    showMessage('Please generate a QR code first.', 'error')

    return
  }

  const link = document.createElement('a')

  link.download = 'qr-code.png'

  link.href = qrImage.src

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)

  showMessage('✓ QR code downloaded successfully!', 'success')
}

// ============================================================
// COPY QR IMAGE
// ============================================================

async function copyQR() {
  const qrImage = document.getElementById('qrImg')

  if (!qrImage.src) {
    showMessage('Please generate a QR code first.', 'error')

    return
  }

  // Check browser support.
  if (!navigator.clipboard || typeof ClipboardItem === 'undefined') {
    showMessage(
      '❌ Your browser does not support image copying. Please use Download QR.',
      'error',
    )

    return
  }

  try {
    const response = await fetch(qrImage.src)

    const blob = await response.blob()

    await navigator.clipboard.write([
      new ClipboardItem({
        'image/png': blob,
      }),
    ])

    showMessage('✓ QR code copied to clipboard!', 'success')
  } catch (error) {
    console.error('Copy QR error:', error)

    showMessage('❌ Copy failed. Please use Download QR instead.', 'error')
  }
}

// ============================================================
// TAB SWITCH
// ============================================================

function switchTab(tabName, clickedButton) {
  document.querySelectorAll('.tab-content').forEach(function (tab) {
    tab.classList.remove('active')
  })

  document.querySelectorAll('.tab-btn').forEach(function (button) {
    button.classList.remove('active')
  })

  const selectedTab = document.getElementById(tabName)

  if (selectedTab) {
    selectedTab.classList.add('active')
  }

  if (clickedButton) {
    clickedButton.classList.add('active')
  }

  // Stop camera when leaving scanner.
  if (tabName !== 'scanner') {
    stopScanner()
  }
}

// ============================================================
// START SCANNER
// ============================================================

async function startScanner() {
  // Stop an existing stream first.
  if (stream) {
    stopScanner()
  }

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showScanResult(
      '❌ Camera access is not supported by this browser.',
      'error',
    )

    return
  }

  try {
    showScanResult('📷 Requesting camera access...', 'info')

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: {
          ideal: 'environment',
        },
      },

      audio: false,
    })

    video.srcObject = stream

    video.style.display = 'block'

    await video.play()

    document.getElementById('scanBtn').disabled = false

    isScanning = true

    showScanResult(
      '📷 Camera started. Point it at a QR code and click Scan QR.',
      'info',
    )
  } catch (error) {
    console.error('Camera error:', error)

    stream = null

    isScanning = false

    showScanResult(
      '❌ Unable to access the camera. Please allow camera permission and try again.',
      'error',
    )
  }
}

// ============================================================
// STOP SCANNER
// ============================================================

function stopScanner() {
  isScanning = false

  if (stream) {
    stream.getTracks().forEach(function (track) {
      track.stop()
    })

    stream = null
  }

  video.srcObject = null

  video.style.display = 'none'

  const scanButton = document.getElementById('scanBtn')

  if (scanButton) {
    scanButton.disabled = true
  }
}

// ============================================================
// SCAN QR
// ============================================================

async function scanImage() {
  if (!stream || !isScanning) {
    showScanResult('Please start the scanner first.', 'error')

    return
  }

  if (video.readyState < HTMLMediaElement.HAVE_ENOUGH_DATA) {
    showScanResult('Camera is not ready yet. Please wait a moment.', 'error')

    return
  }

  if (video.videoWidth === 0 || video.videoHeight === 0) {
    showScanResult('Camera image is not available yet. Please wait.', 'error')

    return
  }

  // --------------------------------------------------------
  // Capture current camera frame
  // --------------------------------------------------------

  canvas.width = video.videoWidth

  canvas.height = video.videoHeight

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

  // --------------------------------------------------------
  // Convert frame to image
  // --------------------------------------------------------

  canvas.toBlob(
    async function (blob) {
      if (!blob) {
        showScanResult('❌ Unable to capture the camera image.', 'error')

        return
      }

      const formData = new FormData()

      formData.append('image', blob, 'qr-scan.png')

      showScanResult('🔍 Scanning QR code...', 'info')

      try {
        const response = await fetch('/scan', {
          method: 'POST',
          body: formData,
        })

        let data

        try {
          data = await response.json()
        } catch (error) {
          throw new Error('Invalid server response.')
        }

        // ------------------------------------------------
        // Backend rejected QR
        // ------------------------------------------------

        if (!response.ok) {
          showScanResult(
            '❌ ' + (data.error || 'No valid website QR code found.'),
            'error',
          )

          return
        }

        // ------------------------------------------------
        // Valid website found
        // ------------------------------------------------

        if (data.url) {
          const safeURL = normalizeAndValidateURL(data.url)

          if (!safeURL) {
            showScanResult(
              '❌ The scanned QR code does not contain a valid website URL.',
              'error',
            )

            return
          }

          showScanResult(
            `
                        <strong>✓ Valid Website Found</strong>

                        <br><br>

                        <a
                            href="${escapeHTML(safeURL)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            ${escapeHTML(safeURL)}
                        </a>

                        <br>

                        <button
                            type="button"
                            class="open-link-btn"
                            onclick="openScannedURL('${encodeURIComponent(safeURL)}')"
                        >
                            Open Link
                        </button>
                        `,

            'success',
          )

          // Stop camera after successful scan.
          stopScanner()
        } else {
          showScanResult(
            '❌ No website URL was returned by the server.',
            'error',
          )
        }
      } catch (error) {
        console.error('Scan error:', error)

        showScanResult(
          '❌ Unable to communicate with the server. Please try again.',
          'error',
        )
      }
    },

    'image/png',
  )
}

// ============================================================
// OPEN SCANNED URL
// ============================================================

function openScannedURL(encodedURL) {
  try {
    const url = decodeURIComponent(encodedURL)

    const validURL = normalizeAndValidateURL(url)

    if (!validURL) {
      showScanResult(
        '❌ This QR code does not contain a valid website URL.',
        'error',
      )

      return
    }

    window.open(validURL, '_blank', 'noopener,noreferrer')
  } catch (error) {
    showScanResult('❌ Unable to open the scanned website.', 'error')
  }
}

// ============================================================
// SCAN RESULT
// ============================================================

function showScanResult(content, type) {
  const result = document.getElementById('result')

  result.innerHTML = content

  result.className = 'scan-result ' + type
}

// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(value) {
  const div = document.createElement('div')

  div.textContent = value

  return div.innerHTML
}

// ============================================================
// ENTER KEY
// ============================================================

const urlInput = document.getElementById('urlInput')

if (urlInput) {
  urlInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault()

      generateQR()
    }
  })
}

// ============================================================
// CLEANUP
// ============================================================

window.addEventListener('beforeunload', function () {
  stopScanner()
})
