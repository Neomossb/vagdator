import os
import torch
import torch.nn as nn
import pandas as pd
import time
import serial

serial_on = False

com_port = 'COM3'
baud_rate = 9600

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = "seattle-weather.csv"
csv_path = os.path.join(script_dir, csv_file)

df = pd.read_csv(csv_path)

if __name__ == "__main__":
    if serial_on:
        ser = serial.Serial(com_port, baud_rate, timeout=1)

    time.sleep(2)

    print(df.head)
    num_rows = df.shape[0]
    print("Number of rows:", num_rows)

    for x in range(num_rows):
        print(df.loc[x, 'date'])
        print(df.loc[x, 'temp_max'])

        data = df.loc[x, 'temp_max']
        if serial_on:
            ser.write(data.encode())

        time.sleep(1)

    ser.close()