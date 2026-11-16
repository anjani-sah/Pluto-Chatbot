# Pluto 🤖
### Your Smart AI-Powered Voice Companion

Pluto is an AI-enabled voice companion designed to make everyday interactions more natural and connected. It combines conversational AI, speech recognition, natural-sounding speech, persistent user preferences, and IoT device control in a Raspberry Pi-based system.

Pluto listens for its wake word, understands spoken requests, responds using an AI language model, and can interact with connected devices through MQTT. It also supports expressive eye controls through an ESP32-C3 and room-condition monitoring using a DHT22 sensor.

## Features

### AI Conversation
- Conversational responses powered by the OpenAI Chat Completions API.
- Maintains short-term conversation context.
- Stores user preferences in a local JSON memory file.
- Supports multiple interaction personalities:
  - Normal
  - Professional
  - Therapist
  - Roast

### Voice Interaction
- Wake-word activation using the phrase **"hello Pluto"**.
- Speech recognition using the SpeechRecognition library and Google Speech Recognition.
- Text-to-speech using OpenAI's `gpt-4o-mini-tts` model.
- Switchable voice options, including Echo, Nova, Alloy, Shimmer, Fable, and Onyx.
- Voice activity detection with WebRTC VAD.
- Audio response caching to reduce repeated generation and playback latency.
- Interruptible speech playback.

### Smart Home Control
- MQTT-based communication with connected IoT devices.
- Supports light and fan control.
- Uses the following MQTT topics:
  - `home/livingroom/light`
  - `home/livingroom/fan`
- Connects to a local Mosquitto broker by default.

### Interactive Eyes
- Serial communication with a Seeed Studio XIAO ESP32-C3.
- Supports eye wake, sleep, blink, listening, and speaking states.
- Provides personality and attention-level controls.
- Includes commands to enable or disable face tracking.

### Environmental Monitoring
- DHT22 sensor integration for room temperature and humidity.
- Supports the Adafruit CircuitPython DHT library and the legacy Adafruit_DHT library.
- Uses mock readings when compatible hardware libraries are unavailable, which is useful for basic software testing.

### Additional Capabilities
- Weather-related voice queries.
- Google Programmable Search integration for spoken web searches.
- Raspberry Pi platform detection and audio backend selection.
- Audio and performance optimizations for Raspberry Pi 5.

## System Architecture

1. The microphone captures the user's speech.
2. Pluto waits for the wake phrase and then listens for commands.
3. Voice activity detection helps identify speech segments.
4. Speech Recognition converts the audio into text.
5. Pluto handles supported commands locally or sends general questions to the OpenAI API.
6. The response is converted into speech using OpenAI text-to-speech.
7. MQTT and serial communication control connected hardware when required.
8. User preferences are stored locally in `pluto_memory.json`.

## Hardware Requirements

The following components are used by the full hardware setup:

| Component | Purpose |
|---|---|
| Raspberry Pi 5 | Main processing unit |
| Microphone | Voice input |
| Speaker | Voice output |
| XIAO ESP32-C3 | Serial interface for animated eyes |
| Compatible eye display or mechanism | Visual expressions |
| DHT22 sensor | Temperature and humidity monitoring |
| ESP32-based IoT device | Light and fan control through MQTT |
| Wi-Fi connection | API access and network communication |

Some software features can be tested on a Linux or macOS computer without the complete hardware setup. GPIO sensor readings and physical device controls require the corresponding hardware.

## Software Stack

| Technology | Use |
|---|---|
| Python | Main application |
| OpenAI API | AI conversation and text-to-speech |
| SpeechRecognition | Speech-to-text |
| Google Speech Recognition | Voice transcription |
| WebRTC VAD | Voice activity detection |
| PyAudio | Microphone audio capture |
| pygame | Audio playback |
| NumPy | Audio and numerical processing |
| Paho MQTT | IoT messaging |
| pyserial | ESP32-C3 serial communication |
| Adafruit DHT | DHT22 sensor support |
| Google Custom Search JSON API | Web search |

## Repository Structure

```text
Pluto-Chatbot/
└── plutobot4/
    ├── Pluto-demonstration .mp4
    └── plutobot4/
        ├── bot2
        ├── dht22_sensor.py
        ├── raspberry_pi_audio.py
        ├── requirements_pi5.txt
        ├── pluto_memory.json
        ├── listen_chime.mp3
        ├── RASPBERRY_PI_SETUP.md
        └── tts_cache/
```

The main application is currently stored in the file named `bot2` without a `.py` extension.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/anjani-sah/Pluto-Chatbot.git
cd Pluto-Chatbot/plutobot4/plutobot4
```

### 2. Install System Dependencies

On Raspberry Pi OS or another Debian-based Linux distribution:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential portaudio19-dev
sudo apt install -y alsa-utils ffmpeg
```

Install and start Mosquitto if you plan to use MQTT device control:

```bash
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

The repository includes a Raspberry Pi dependency list:

```bash
pip install --upgrade pip
pip install -r requirements_pi5.txt
```

If PyAudio or another hardware-specific package fails to install, check that its system development dependencies are installed first.

### 5. Configure API Credentials

The application uses OpenAI and Google Custom Search credentials. Configure your own credentials before running the application.

Recommended approach:

1. Create an OpenAI API key from the OpenAI developer platform.
2. Create a Google Custom Search JSON API key and Programmable Search Engine ID if you want web search.
3. Store the credentials as environment variables.
4. Update the application to read these values from the environment instead of placing credentials directly in source code.

Example:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export GOOGLE_SEARCH_API_KEY="your_google_api_key"
export GOOGLE_CSE_ID="your_search_engine_id"
```

The current source file contains credential values directly in the code. Replace those values with your own credentials and avoid committing API keys to GitHub. Revoke and regenerate any credentials that have previously been exposed in a public repository.

### 6. Configure Hardware Connections

Before launching the complete system:

- Connect the microphone and speaker to the Raspberry Pi.
- Configure the MQTT broker address in the application. The default is `localhost` on port `1883`.
- Connect the ESP32-C3 to USB serial. The default port is `/dev/ttyUSB0`, with alternative ports checked by the application.
- Connect the DHT22 sensor to the configured GPIO pin. The default pin is GPIO 4.
- Ensure your ESP32 MQTT firmware uses the same topics and message format expected by the application.

### 7. Run Pluto

The main Python file has no extension, so run it explicitly with Python:

```bash
python bot2
```

Wait for the microphone initialization message. Say **"hello Pluto"** to activate the assistant and begin a conversation.

Press `Ctrl + C` to stop the application.

## Example Voice Commands

| What you can say | Action |
|---|---|
| "Hello Pluto" | Wake up the assistant |
| "What's the weather in Pune?" | Ask for weather information |
| "Search for machine learning news" | Search the web |
| "Turn on the light" | Publish a light-control MQTT message |
| "Turn off the fan" | Publish a fan-control MQTT message |
| "What's the room temperature?" | Read the DHT22 sensor |
| "Switch to female voice" | Change the text-to-speech voice |
| "Switch to professional mode" | Change the assistant's personality |
| "Enable face tracking" | Enable the eye tracking command |
| "Blink" | Trigger an eye blink |
| "Go to sleep" | Put Pluto into sleep mode |

The availability of hardware commands depends on the connected devices and their firmware.

## Configuration Reference

| Setting | Default | Description |
|---|---|---|
| MQTT broker | `localhost` | MQTT broker host |
| MQTT port | `1883` | MQTT broker port |
| Light topic | `home/livingroom/light` | Light control topic |
| Fan topic | `home/livingroom/fan` | Fan control topic |
| ESP32-C3 serial port | `/dev/ttyUSB0` | Initial serial port |
| ESP32-C3 baud rate | `115200` | Serial communication speed |
| DHT22 GPIO pin | `4` | Sensor data pin |
| Default TTS voice | `echo` | OpenAI TTS voice |

These values are defined in the application source and can be adjusted to match your hardware setup.

## Troubleshooting

### Microphone or PyAudio errors

Install PortAudio development files and ALSA utilities:

```bash
sudo apt install -y portaudio19-dev python3-dev alsa-utils
pip install --upgrade pyaudio
```

Check that Linux detects your audio devices:

```bash
arecord -l
aplay -l
```

### MQTT connection errors

Check that Mosquitto is running:

```bash
sudo systemctl status mosquitto
```

Test publishing a message:

```bash
mosquitto_pub -h localhost -t home/livingroom/light -m ON
```

### ESP32-C3 not detected

Check available serial devices:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Verify the USB cable supports data transfer and that the current user has permission to access the serial device.

### DHT22 sensor unavailable

Check the GPIO wiring, sensor library installation, and configured GPIO pin. On non-Raspberry Pi systems, the application uses mock sensor readings.

### Virtual environment problems

Refer to [RASPBERRY_PI_SETUP.md](plutobot4/RASPBERRY_PI_SETUP.md) for Raspberry Pi setup and troubleshooting guidance.

## Demonstration

A demonstration video is available in the repository:

[`Pluto-demonstration .mp4`](plutobot4/Pluto-demonstration%20.mp4)

## Security

- Never publish API keys, passwords, or private broker credentials.
- Use environment variables or a local `.env` file for secrets.
- Add local credential files to `.gitignore`.
- Restrict MQTT broker access when deploying outside a trusted local network.
- Review hardware permissions before running the application with elevated privileges.

## Project Status

Pluto is an evolving AI and IoT companion project. Its capabilities depend on the available hardware, API credentials, network connectivity, and compatible ESP32 firmware.

## Author

**Anjani Sah**

- GitHub: [@anjani-sah](https://github.com/anjani-sah)
- Project: [Pluto Chatbot](https://github.com/anjani-sah/Pluto-Chatbot)

---

Made with Python, AI, and embedded systems.
