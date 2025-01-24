#!/usr/bin/env python3

import sys
import serial
import time
from datetime import datetime, timedelta, timezone

from utils.rtcm3 import RTCMReader
from utils.socketwrapper import SocketWrapper
from utils  import ntripclient

# only for logging
LOG_TO_FILE = True
LOG_FILENAME = "f9p_nmea.log"

###############################################################################
# User Configuration Section
###############################################################################

# NTRIP Caster Information
NTRIP_HOST = "caster.centipede.fr"       # e.g., "rtk2go.com"
NTRIP_PORT = 2101                          # Default NTRIP port is often 2101
MOUNTPOINT = ""             # e.g., "MOUNTPOINT"
NTRIP_USERNAME = "centipede"
NTRIP_PASSWORD = "centipede"

# Serial/USB Connection to ZED-F9P
SERIAL_PORT = "/dev/ttyACM0"   # /dev/ttyACM0 or /dev/ttyUSB0 depending on your setup
SERIAL_BAUD = 115200           # Typical for ZED-F9P over USB
TIMEOUT = 1                    # Serial timeout in seconds

###############################################################################
# Main Script
###############################################################################

def main():

    # Open a file for logging if needed
    log_file = None
    if LOG_TO_FILE:
        log_file = open(LOG_FILENAME, "w")
        print(f"Logging NMEA to: {LOG_FILENAME}")
    # Open serial connection to ZED-F9P
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=TIMEOUT)
        print(f"Opened serial port: {SERIAL_PORT} at {SERIAL_BAUD} baud.")
    except serial.SerialException as e:
        print(f"Failed to open serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

    # Optional: get closest mount point
    MOUNTPOINT=""
    if MOUNTPOINT=="":
        print(" **** Getting closest mountpoint ****")
        roverlat = 44.83
        roverlon = -0.56
        mindist = 100000
        index=0
        lst = ntripclient.ntrip_getmountpoints(NTRIP_HOST,NTRIP_PORT,NTRIP_USERNAME,NTRIP_PASSWORD)
        for (i,l) in enumerate(lst):
            dist=ntripclient.sphericaldist(roverlat,roverlon,l['latitude'],l['longitude'])
            if dist<mindist:
                mindist=dist
                index=i
        print(f"Closest mountpoint {lst[index]['name']} at {int(mindist)}km in {lst[index]['locality']}")
        if log_file:
            log_file.write(f"Detected mount point {lst[index]['name']} at {int(mindist)}km in {lst[index]['locality']}\n")
        MOUNTPOINT=lst[index]['name']
    else:
        if LOG_TO_FILE:
            log_file.write(f"Using mount point {MOUNTPOINT}\n")
    if LOG_TO_FILE:
        log_file.write("Latitude\tLongitude\tAltitude\tFix\n")
        log_file.flush()
    # Attempt to connect to the NTRIP caster
    try:
        print(" **** Connecting to caster ****")
        ntrip_socket = ntripclient.create_ntrip_request(
            NTRIP_HOST,
            NTRIP_PORT,
            MOUNTPOINT,
            NTRIP_USERNAME,
            NTRIP_PASSWORD,
        )
    except Exception as e:
        print(f"Failed to connect to NTRIP caster: {e}")
        ser.close()
        sys.exit(1)

    print(" **** Starting RTCM forwarding loop ****")
    last_activity = datetime.now()
    last_report = datetime.now()
    packets_sent=0
    try:
        parser = RTCMReader(SocketWrapper(ntrip_socket,1))
        while True:
            raw_data = parser.read()
            if raw_data is None:
                if datetime.now() - last_activity > timedelta(seconds=5):
                    print("Server timeout...reconnecting")
                    if not ntripclient.renew_request(ntrip_socket,NTRIP_HOST,NTRIP_PORT,MOUNTPOINT,NTRIP_USERNAME,NTRIP_PASSWORD):
                        print("reconnection error. Aborting.")
                        break
            else:
                ser.write(raw_data)
                last_activity = datetime.now()
                packets_sent += 1
            
            if datetime.now()-last_report > timedelta(seconds=60):
                print(f"[{datetime.now().strftime("%H:%M:%S")}] {packets_sent} packets sent to u-blox")
                last_report=datetime.now()
                ser.close()
                time.sleep(0.1)
                ser.open()
            '''
            try:
                nmea_data = ser.readall()
                if nmea_data:
                    sl = nmea_data.decode().splitlines()
                    for s in sl:
                        if "GGA" in s:
                            if LOG_TO_FILE:
                                log_file.write(s)
                                log_file.flush()
                            print("****** Got position "+s)
                        # msg = UBXReader.parse(s.encode())
                        # if msg is not None and msg.identity=="NAV_PVT" :
                        #     print(msg)
                        #     if LOG_TO_FILE:
                        #         log_file.write(f"{msg.lat}\t{msg.lon}\t{msg.hMSL/1000}\t{msg.fixtype}")
                else:
                    print("No NMEA received")
            except Exception as e:
                print(f"Error reading from ZED-F9P: {e}")
            '''
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        print("Closing connections...")
        ser.close()
        ntrip_socket.close()

if __name__ == "__main__":
    main()
