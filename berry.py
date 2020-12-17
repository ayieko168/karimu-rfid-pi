import serial
import time
import concurrent.futures
import requests
import datetime


url = "http://localhost:105/car"

def send_tag_data(tag_id):  

    r = requests.post(url, data={'lineNumber': 1, 'tagid': tag_id, 'dateTime': str(datetime.datetime.now())})
    print((tag_id, r.status_code, r.reason))

try:
    with serial.Serial('COM25', 9600, timeout=2) as ser:
        while True:

            ser.write(b'\x7C\xFF\xFF\x11\x32\x00\x43')

            ## Read the data from usb serial
            read_ids = []
            bytesToRead = ser.inWaiting()
            if bytesToRead > 0:
                
                data_raw = ser.read(bytesToRead)
                data = hex(int.from_bytes(data_raw, byteorder='big'))
                actual_data =data.upper().split('X')[-1]

                if len(actual_data) > 14:

                    actual_data = ' '.join([actual_data[i:i+2] for i in range(0, len(actual_data), 2)])
                    #print('\n')
                    #print(actual_data)

                    ## Get indiviadual bit data
                    bit_data = actual_data.split(' ')

                    rtn_bit =  int(bit_data[4], 16)
                    tag_count = int(bit_data[5], 16)
                    tag_len = int(bit_data[6], 16)
                    antn_number = int(bit_data[7], 16)

                    #print(f"rtn_bit :{rtn_bit}, tag_count: {tag_count}, tag_len: {tag_len}, antn_number: {antn_number}")

                    try:
                        start_bit = 7
                        _ids = bit_data[start_bit:]
                        start = 0
                        end = tag_len
                        for j in range(tag_count):
                            _id = _ids[start: end]
                            _id_str = ' '.join(_id)
                            #print(f"CARD {j+1} ID:: {_id_str}")

                            read_ids.append(_id_str)
                            start = end
                            end+=tag_len

                        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
                            executor.map(send_tag_data, read_ids)
                            
                    except Exception as e:
                        print(f"ERROR:: {e}")

                            
                    

            time.sleep(0.25)
except Exception as e:
    print(f"ERROR :: {e}")
