import cv2
import time

def test_camera():
    print("Attempting to open camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    print("Camera opened successfully")
    print("Capturing 5 frames...")
    
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1}: {frame.shape}")
        else:
            print(f"Frame {i+1}: Failed to capture")
        time.sleep(1)
    
    cap.release()
    print("Camera test completed")

if __name__ == "__main__":
    test_camera() 