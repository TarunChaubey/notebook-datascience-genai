import cv2
import time
from ultralytics import YOLO

# Load YOLO model (you can change to 'yolov8n.pt', 'yolov8s.pt', etc.)
model = YOLO("yolo11n.onnx", )

def run_inference(source=0):
    """
    Run YOLO inference on a video file or webcam stream.
    :param source: path to video file (e.g. 'video.mp4') or webcam index (e.g. 0)
    """
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error: Could not open source {source}")
        return

    prev_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Measure FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time

        # Run YOLOv8 inference
        results = model(frame, verbose=False)

        # Plot results on the frame
        annotated_frame = results[0].plot()

        # Display FPS
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show video output
        cv2.imshow("YOLO Inference", annotated_frame)

        # Quit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Uncomment one of these lines to choose source

    # For video file
    run_inference("Cyberabad Traffic Police.mp4")

    # For real-time webcam feed
    # run_inference(0)
