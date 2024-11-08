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


        temp_max = df.loc[x, 'temp_max']

        serial_string = str(temp_max)

        weather_next = df.loc[x+1, 'weather']

        if serial_on:
            ser.write(serial_string.encode())

        time.sleep(5)
        ret, frame = cap.read()

        new_width, new_height = 128, 96

        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to black and white
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0) # gaussian blur for better edge detection
        sobel_xy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) # edge detection

        resized_image = cv2.resize(sobel_xy, (new_width, new_height), interpolation=cv2.INTER_AREA)

        if ret:
            # Set up the save path
            if weather_next == 'drizzle':
                save_dir = drizzle_path  # Folder where you want to save the image
            if weather_next == 'fog':
                save_dir = fog_path
            if weather_next == 'rain':
                save_dir = rain_path
            if weather_next == 'snow':
                save_dir = snow_path
            if weather_next == 'sun':
                save_dir = sun_path
            print(save_dir)


            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, str(x) + ".jpg")
            print(save_path)

            # Save the image
            cv2.imwrite(save_path, resized_image)
            print(f"Image saved to {save_path}")
        else:
            print("Error: Could not capture an image.")

    ser.close()
    cap.release()