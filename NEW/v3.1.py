import serial
import serial.tools.list_ports
import os
import concurrent.futures
import requests
import datetime
import time
import threading
import logging
import logging.handlers
import os


## setup logger
logger = logging.getLogger(__name__)
fl_handler = logging.FileHandler('kenha_rfid.log')
fl_handler.setLevel(logging.DEBUG)
fl_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fl_handler.setFormatter(fl_format)
logger.addHandler(fl_handler)


## Variables
devices = [
    {"COMPORT": 'COM25', "machine_id": "gB6EMj3aTw01"},
    {"COMPORT": 'COM4', "machine_id": "8GNeUCBU4b02"},
]
# url = "http://127.0.0.1:105/car" 
url = "http://192.168.1.2/api/Events/rfid/read"
read_tags = {}
time_delta = int(6e+10) * 0.5  ## Check time in minutes
connection_timeout = 30  ## Time in seconds to timeout

print(time_delta)
logger.debug("Starting RFID listener..")

def list_available_ports():
    
    ## Get the ports instance
    ports = serial.tools.list_ports.comports()
    
    ## Iterate thru the ports inatances and print out the port info
    count = 1
    print("#"*60)
    for port, desc, hwid in sorted(ports):
        print(f"PORT {count}")
        print(f"\t->PORT: {port}\n\t->DESCRIPTION: {desc}\n\t->HWID: {hwid}\n\n")
        count +=1

def chech_2x(tag_id):
    
    ## Check if the ID is in the dictionary
    if tag_id in read_tags.keys():
        
        ## Check if the time is passed
        # if time is passed, send it
        if int(time.time_ns() - read_tags[tag_id]) >= time_delta:
            print("time is passed, send it")
            ## Reset the timer for the ID
            read_tags[tag_id] = time.time_ns()
            
            ## Return a true to allow sending of ID to server
            return True
        
        ## If not passed, dont send
        else:
            print("not passed, dont send")
            return False
        
    else:
        print("Not in keys, adding...")
        ## add the ID to the dictionary
        read_tags[tag_id] = time.time_ns()
        
        ## Return False to prevent sending 
        return True
        
    # print(read_tags, tag_id)
    
    
    
def send_tag_data(tag_id):  
    
    print(f"Sending tag :: {tag_id}")
    
    try:
        
        conext = {
          "readerNumber": "string",
          "tagNumber": "string"
        }
        
        r = requests.post(url, json=conext, timeout=connection_timeout)
        print((tag_id, r.status_code, r.reason))
    
    except Exception as e:
        
        print(f"Error sending ID to server :: {e}")

## Run the serial listenner
def listener(device):
    
    try:
        print(f"Starting listener [{device}]...")
        ser =  serial.Serial(device["COMPORT"])
        
        print(f"Listenner started, {ser}\n")
        print("#"*50)

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
                
                ## Check the twice thing
                ret = chech_2x(clean_data)
                print(f"Checked the twice thing :: {ret}")
                
                ## Send the ID data to the server
                if ret:
                    print(read_tags, clean_data)
                    threading.Thread(target=send_tag_data, args=(clean_data,)).start()
                    # with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                        # executor.map(send_tag_data, [clean_data])


    except Exception as e:
        
        print(f"Error!! :: {e}")
        if 'FileNotFoundError' in str(e):
            print('The port you decleraed is not connected, bellow is a list of active ports...')
            list_available_ports()
        
        else:
            list_available_ports()
                

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor2:
    executor2.map(listener, devices)