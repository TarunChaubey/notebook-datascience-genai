
from datetime import datetime
import numpy as np
import os
import csv

frame_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
defect_type = np.random.choice(['EL','VL'])
height, width, = np.random.randint(1080,4096,1)[0], np.random.randint(1080,4096,1)[0]
bbox = np.random.randint(0,4096,4)


def WriteFrameMetadataLogs(data, csv_filename=f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"):
    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_filename)

    # Write header if the file is created for the first time
    with open(csv_filename, 'a', newline='') as csvfile:
        fieldnames = ['frame_id', 'date_time', 'defect_type', 'height', 'width', 'x_min', 'y_min', 'x_max', 'y_max']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        # Write the data to the CSV file
        writer.writerow(data)

# store data
WriteFrameMetadataLogs({'frame_id':frame_id,'date_time':date_time, 'defect_type':defect_type,'height':height,
                        'width':width,'x_min': bbox[0], 'y_min':  bbox[1], 'x_max': bbox[2], 'y_max': bbox[3]})
