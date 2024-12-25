import cv2
import uuid
from datetime import datetime
from threading import Thread
from sql import SQLHelper
import numpy as np

dbname, table_name = 'RTPSDB', 'FrameTable'

sql_obj = SQLHelper(dbname, table_name)

class StreamVideoPreprocessing:
    
    @staticmethod
    def ExtractFreame(source_link, cam_id):
        
        cap = cv2.VideoCapture(source_link)

        while cap.isOpened():

            ret, frame = cap.read()

            if ret is None:
                print("File Not Read")

            frame_id = datetime.now().strftime("%m%d%Y%H%M%S%f")[:-4]

            date_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
            
            frame = cv2.putText(frame, f"{date_time}", (40, 40), cv2.FONT_ITALIC, 0.7, (0, 0, 255), 1)
            
            data = {"frame_id": frame_id, "cam_id": cam_id, "date_time": date_time,
                   "Site_id": np.random.randint(0,100,1)[0],"username": "tarunchaubey","email_id": "tarunchaubey09@gmail.com"}

            query = f"""INSERT INTO ExtractedFrameFromVideo (frame_id, cam_id, date_time, Site_id, username, email_id) VALUES {tuple(data.values())};"""
            
            sql_obj.RunQuery(query, verbose=False)

            print(data,"\n")

            # cv2.imshow("VideoApps", frame)

            # Use a small delay (e.g., 1 millisecond)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# Test source_link_a
t1 = Thread(target=StreamVideoPreprocessing.ExtractFreame, args=("http://192.168.1.5:4747/video", 1))
t1.start()

# Test source_link_b
t2 = Thread(target=StreamVideoPreprocessing.ExtractFreame, args=("http://192.168.1.2:4747/video", 2))
t2.start()