import serial
import os
import concurrent.futures
import requests
import datetime


COMPORT = 'COM9'
url = "http://192.168.0.105:105/car"

def send_tag_data(tag_id):  

    r = requests.post(url, json={'laneNumber': 1, 'tagNumber': str(tag_id), 'dateTime': str(datetime.datetime.now())})
    print((tag_id, r.status_code, r.reason))

try:
    ser =  serial.Serial(COMPORT)

    while True:
        
        
        ## Get the Data from the reader
        read_raw = ser.readline()
        
        # print(read_raw)
        data = read_raw.decode('UTF-8')
        clean_data = data[2:].strip()
        
        # print(clean_data, len(clean_data))
        
        ## Check if length of read ID is valid
        if len(clean_data) == 10:
            print("OK!!")
            
            ## Send the ID data to the server
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                executor.map(send_tag_data, [clean_data])
   
except Exception as e:
    
    print(f"Error!! :: {e}")
    