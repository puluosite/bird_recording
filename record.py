import numpy as np
import os
import cv2
import threading
import time
import datetime
import shutil
import sys

# Set resolution for the video capture
# Function adapted from https://kirr.co/0l6qmh
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    '.avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    '.mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return  VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

time_out = False

def time_n_secs_and_change_flag(n_secs):
    global time_out
    time.sleep(n_secs)
    #print("Timed out!!!!!")
    time_out = True

def extract_date_from_file(filename):
    tkns = filename.split('_')
    return tkns[0]+'_'+tkns[1]+'_'+tkns[2]

def test_move_file(filename):
    #filename = "2019_08_11_20_29_39.avi"
    date = extract_date_from_file(filename)
    src_dir = os.path.join(os.getcwd(), filename)
    dest_dir = os.path.join(os.path.normpath("//192.168.1.30/prost_backup/recording/bird"), date)
    dest_dir_with_file = os.path.join(dest_dir, filename)
    print(src_dir)
    print(dest_dir) 
    if not os.path.exists(dest_dir):
        print("folder not there! create!")
        os.makedirs(dest_dir)
    shutil.move(src_dir, dest_dir_with_file)

def move_file_to_cloud(filename):
    #src_dir = os.path.join(os.getcwd(), filename)
    #dest_dir = os.path.join(os.path.normpath("//192.168.1.30/prost_backup/recording/bird"), filename) 
    #shutil.move(src_dir, dest_dir)
    test_move_file(filename)

def record_video_for_n_secs(filename, cap, n_secs):
    frames_per_second = 24.0
    resolution = '480p'
    out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(cap, resolution))

    # start a thread that
    global time_out
    time_out = False

    t = threading.Thread(target=time_n_secs_and_change_flag, args=(n_secs,))
    t.setDaemon(True)
    t.start()
    while (not time_out):
        ret, frame = cap.read()
        out.write(frame)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            out.release()
            return -1

    t.join()
    # seperate thread to move file to cloud
    t2 = threading.Thread(target=move_file_to_cloud, args=(filename,))
    t2.start()

    out.release()
            
    #sleep for 10 min record 5min per 15min
    time.sleep(600)
    return 0

def check_time_in_day_time(st):
    st_ct = st.time()
    if (st_ct >= datetime.time(6,0) and st_ct <= datetime.time(20,30)):
        return True
    return False


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("grabs the logitech webcam!!!!")
    
    while(True):
        st = datetime.datetime.now()
        if (not check_time_in_day_time(st)):
            print("not recording at night")
            time.sleep(600)
            continue

        #filename = 'video.mp4'
        filename = st.strftime("%Y_%m_%d_%H_%M_%S") + ".avi"
        res = record_video_for_n_secs(filename, cap, 300)
        if (res != 0):
            print("return value is: %d"%(res))
            break


    #print("return value is: %d"%(res))
    cap.release()
    cv2.destroyAllWindows()


