import os
from datetime import datetime
import cv2
import serial
import time
import requests
import json
from azure.iot.device import IoTHubDeviceClient, Message

AZURE_ENDPOINT = "endpoint name"
AZURE_KEY = "API key here"
VISION_URL = AZURE_ENDPOINT + "vision/v3.2/analyze?visualFeatures=Objects,Description"

connection_str = "HostName=IoT-PIR-demo.azure-devices.net;DeviceId=motion-device-1;SharedAccessKey=N5X10CsFoVbo4yNKyd5JF0YNjI7gbW070KhyK4HzFj4="
device_client = IoTHubDeviceClient.create_from_connection_string(connection_str)
device_client.connect()

ser = serial.Serial('COM3', 9600)
os.makedirs("snapshots", exist_ok=True)
cam = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
print("System ready. Waiting for motion...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line == "MOTION":
            print("Motion detected! Starting face detection...")
            msg = Message('{"event": "motion_detected", "timestamp": "' + datetime.now().isoformat() + '"}')
            device_client.send_message(msg)
            print("Message sent to IoT Hub!")
            start_time = time.time()
            snapshot_taken = False
            while time.time() - start_time < 10:
                ret, frame = cam.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    if not snapshot_taken:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"snapshots/snapshot_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"Snapshot saved as {filename}")

                        # Azure Vision API call 
                        with open(filename, "rb") as image_data:
                            headers = {
                                "Ocp-Apim-Subscription-Key": AZURE_KEY,
                                "Content-Type": "application/octet-stream"
                            }
                            response = requests.post(VISION_URL, headers=headers, data=image_data)
                            result = response.json()
                            print("Azure Vision API result:")
                            print(json.dumps(result, indent=2))

                        snapshot_taken = True
                cv2.imshow("Face Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            print("Face detection session ended.")
            cam.release()

            cv2.destroyAllWindows()
