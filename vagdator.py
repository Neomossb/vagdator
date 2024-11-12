import os
import torch
import torch.nn as nn
import pandas as pd
import time
import serial
import cv2

serial_on = True

servo_a_min = 20
servo_a_max = 160

servo_b_min = 20
servo_b_max = 160

servo_c_min = 20
servo_c_max = 160

servo_d_min = 20
servo_d_max = 160

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
        ser = serial.Serial(com_port, baud_rate, timeout=0.01)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    time.sleep(2)

    print(df.head)
    num_rows = df.shape[0]
    print("Number of rows:", num_rows)

    for x in range(num_rows):

        precipitation = df.loc[x, 'precipitation']
        temp_max = df.loc[x, 'temp_max']
        temp_min = df.loc[x, 'temp_min']
        wind = df.loc[x, 'wind']

        precipitation_processed = max(0, min(round(precipitation * 6), 180))
        temp_max_processed = max(0, min(round(temp_max * 5.29), 180))
        temp_min_processed = max(0, min(round((temp_min + 5) * 7.72), 180))
        wind_processed = max(0, min(round(wind * 20), 180))

        go_string = "A" + str(round(((servo_a_max-servo_a_min)/180) * precipitation_processed + servo_a_min)) + "B" + str(round(((servo_b_max-servo_b_min)/180) * temp_max_processed + servo_b_min)) + "C" + str(round(((servo_c_max-servo_c_min)/180) * temp_min_processed + servo_c_min)) + "D" + str(round(((servo_d_max-servo_d_min)/180) * wind_processed + servo_d_min))
        off_string = "A0B0C0D0"

        weather_next = df.loc[x+1, 'weather']

        print(precipitation)
        print(temp_max)
        print(temp_min)
        print(wind)

        print(precipitation_processed)
        print(temp_max_processed)
        print(temp_min_processed)
        print(wind_processed)

        print(weather_next)

        if serial_on:
            ser.write(go_string.encode())
            time.sleep(0.4)
            ser.write(off_string.encode())

        time.sleep(5)
        ret, frame = cap.read()

        new_width, new_height = 256, 192

        start_x, start_y = 64, 48  # Top-left corner of the crop
        end_x, end_y = 192, 144  # Bottom-right corner of the crop

        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to black and white
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0) # gaussian blur for better edge detection
        sobel_xy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5) # edge detection

        resized_image = cv2.resize(sobel_xy, (new_width, new_height), interpolation=cv2.INTER_AREA)

        cropped_image = resized_image[start_y:end_y, start_x:end_x]

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
            cv2.imwrite(save_path, cropped_image)
            print(f"Image saved to {save_path}")
        else:
            print("Error: Could not capture an image.")

    ser.close()
    cap.release()