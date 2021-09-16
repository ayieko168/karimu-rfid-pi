import serial
import serial.tools.list_ports
import os
import concurrent.futures
import requests
import datetime
import time

## Variables
COMPORT = 'COM4'
url = "http://192.168.0.105:105/car" 
read_tags = {}
time_delta = int(6e+10) * 0.5  ## Check time in minutes

print(time_delta)

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
            
            ## Check the twice thing
            ret = chech_2x(clean_data)
            
            ## Send the ID data to the server
            if ret:
                print(read_tags, clean_data)
                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                    executor.map(send_tag_data, [clean_data])


except Exception as e:
    
    print(f"Error!! :: {e}")
    if 'FileNotFoundError' in str(e):
        print('The port you decleraed is not connected, bellow is a list of active ports...')
        list_available_ports()
    
    else:
        list_available_ports()
        
    