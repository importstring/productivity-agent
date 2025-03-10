import cv2
import time

def test_camera():
    print("Testing camera access...")
    print("1. Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    print("2. Camera opened successfully")
    print("3. Testing camera properties...")
    
    # Try to set and verify camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"4. Camera properties: {width}x{height} @ {fps}fps")
    print("5. Attempting to read frames...")
    
    try:
        for i in range(10):
            ret, frame = cap.read()
            if ret:
                print(f"Frame {i+1}: Success - Shape: {frame.shape}")
                # Save the first frame as a test
                if i == 0:
                    cv2.imwrite('test_frame.jpg', frame)
                    print("Saved test frame as 'test_frame.jpg'")
            else:
                print(f"Frame {i+1}: Failed to capture")
            time.sleep(0.1)
    
    except Exception as e:
        print(f"Error during capture: {e}")
    finally:
        print("6. Cleaning up...")
        cap.release()
        print("Test completed")

if __name__ == "__main__":
    test_camera() 