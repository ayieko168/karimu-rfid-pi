import serial
import time
import concurrent.futures
import requests
import datetime
import logging
import smtplib
from email.message import EmailMessage
import os, sys

print()

EMAIL_UPDATE_FREQUENCY = 240  # How frequent to send email updates - intager in seconds - 43200(12Hrs)
start_time = time.time()
COMPORT = "COM4"
url = "http://192.168.0.107:5000/api/events/rfid/read"
#url = "http://localhost:105/car"

#log_file = r"C:\Users\PERCY\Desktop\RFID_PI_LOGS.log"
log_file = f"C:/Users/{os.getlogin()}/Desktop/RFID_PI_LOGS.log"
print(f"Saving logs to :: {log_file}")

logging.basicConfig(filename=log_file, 
                    filemode='a', 
                    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.DEBUG)

print("RFID Reader started...")


def send_tag_data(tag_id):  

    r = requests.post(url, json={'laneNumber': 1, 'tagNumber': str(tag_id), 'dateTime': str(datetime.datetime.now())})
    print((tag_id, r.status_code, r.reason))

def test_endpoint_connection(url=url, timeout=3):
    try:
        #r = requests.get(url, timeout=timeout)
        r = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError as ex:
        return ex

def send_report():
    
    msg = EmailMessage()
    msg['Subject'] = "RFID PI EMAIL UPDATE"
    msg['From'] = "rfidpike@gmail.com"
    msg['To'] = 'antonyalen1960@gmail.com'
    
    with open(log_file, 'rb') as f:
        file_data = f.read()
        file_name = f.name
    
    msg.set_content(f"[SENDER DETAILS]\nUser Name: {os.getlogin()}\nPython Executable: {sys.executable}\n\n\n[See Attached Log File.]")
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(user='rfidpike@gmail.com', password='inmycozsfigvhzzu')
        smtp.send_message(msg)
        
    print("Done sending email.")
    logging.info("Done sending email.")


internet = test_endpoint_connection()
if internet is not True:
    logging.critical("Could not connect to the endpoint, Error details: {internet}\n\nNo data to send..")
    print(f"Could not connect to the endpoint, Error details: {internet}\n\nNo data to send..")



# Send conp

try:
    with serial.Serial(COMPORT, 9600, timeout=2) as ser:
        logging.info('Opening concurrency threadpool...')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            logging.info('Opened threadpool with max_workers of 25')
            
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
                        print('\n')
                        print(f"actual_data: {actual_data}")
                        logging.debug(f'Recived the following (raw) data: {actual_data}')

                        ## Get indiviadual bit data
                        bit_data = actual_data.split(' ')

                        rtn_bit =  int(bit_data[4], 16)
                        tag_count = int(bit_data[5], 16)
                        tag_len = int(bit_data[6], 16)
                        antn_number = int(bit_data[7], 16)

                        print(f"\nrtn_bit :{rtn_bit}, tag_count: {tag_count}, tag_len: {tag_len}, antn_number: {antn_number}\n")
                        logging.debug(f'Post processing info: \n\tReturn Bit: {rtn_bit}\n\tTag Count: {tag_count}\n\tTag length: {tag_len}\n\tAntenna Number: {antn_number}')
                        try:
                            start_bit = 7
                            _ids = bit_data[start_bit:]
                            start = 0
                            end = tag_len
                            for j in range(tag_count):
                                _id = _ids[start: end]
                                _id_str = ' '.join(_id)
                                print(f"CARD {j+1} ID:: {_id_str}")
                                logging.debug(f'Individual ID data: CARD {j+1} ID:: {_id_str}')
                                read_ids.append(_id_str)
                                start = end
                                end+=tag_len

                            
                            executor.map(send_tag_data, read_ids)
                            
                            print("#"*25)
                            logging.debug(f'End of data stream.')
                        except Exception as e:
                            print(f"ERROR:: {e}")
                            logging.error("Exception occurred", exc_info=True)
                            
                            print(f"Sending crush report email...")
                            logging.info(f'Sending crush report email...')
                            executor.submit(send_report)
                            start_time = time.time()
                            

                                
                if int(time.time() - start_time) == EMAIL_UPDATE_FREQUENCY:
                    print(f"Sending update email...")
                    logging.info(f'Sending update email...')
                    executor.submit(send_report)
                    start_time = time.time()
                    
                time.sleep(0.25)

except Exception as e:
    print(f"ERROR :: {e}")
    logging.error("Exception occurred", exc_info=True)
    
    print(f"Sending crush report email...")
    logging.info(f'Sending crush report email...')
    executor.submit(send_report)
    start_time = time.time()
