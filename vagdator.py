import os
import torch
import torch.nn as nn
import pandas as pd
import time
import serial
import cv2

serial_on = False

com_port = 'COM3'
baud_rate = 9600

script_dir = os.path.dirname(os.path.abspath(__file__))
print(script_dir)

csv_file = "seattle-weather.csv"
csv_path = os.path.join(script_dir, csv_file)

drizzle_path = os.path.join(script_dir, "photo", "drizzle")
fog_path = os.path.join(script_dir, "photo", "fog")
rain_path = os.path.join(script_dir, "photo", "rain")
snow_path = os.path.join(script_dir, "photo", "snow")
sun_path = os.path.join(script_dir, "photo", "sun")


df = pd.read_csv(csv_path)

if __name__ == "__main__":
    if serial_on:
        ser = serial.Serial(com_port, baud_rate, timeout=1)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    time.sleep(2)

    print(df.head)
    num_rows = df.shape[0]
    print("Number of rows:", num_rows)

    for x in range(num_rows):
        print(df.loc[x, 'date'])
        print(df.loc[x, 'temp_max'])


        weather = df.loc[x, 'weather']
        temp_max = df.loc[x, 'temp_max']
        if serial_on:
            ser.write(temp_max.encode())

        time.sleep(5)
        ret, frame = cap.read()

        if ret:
            # Set up the save path
            if weather == 'drizzle':
                save_dir = drizzle_path  # Folder where you want to save the image
            if weather == 'fog':
                save_dir = fog_path
            if weather == 'rain':
                save_dir = rain_path
            if weather == 'snow':
                save_dir = snow_path
            if weather == 'sun':
                save_dir = sun_path
            print(save_dir)


            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, str(x) + ".jpg")
            print(save_path)

            # Save the image
            cv2.imwrite(save_path, frame)
            print(f"Image saved to {save_path}")
        else:
            print("Error: Could not capture an image.")

    ser.close()
    cap.release()