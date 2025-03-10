import cv2

def test_camera_devices():
    print("Checking available camera devices...")
    
    # Try different camera indices
    for i in range(10):
        print(f"\nTesting camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if not cap.isOpened():
            print(f"Camera index {i} not available")
            continue
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"Camera {i} found:")
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
        
        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print("Successfully captured a frame")
            # Save the frame as a test
            cv2.imwrite(f'test_frame_{i}.jpg', frame)
            print(f"Saved test frame as 'test_frame_{i}.jpg'")
        else:
            print("Failed to capture frame")
        
        # Release the camera
        cap.release()
    
    print("\nCamera device test completed")

if __name__ == "__main__":
    test_camera_devices() 