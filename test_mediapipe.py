import cv2
import mediapipe as mp
import time

def test_mediapipe():
    print("Initializing MediaPipe...")
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    print("Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    print("Camera opened successfully")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = pose.process(frame_rgb)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                print("Pose detected!")
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
            
            # Display frame
            cv2.imshow('MediaPipe Test', frame)
            
            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.1)  # Small delay to reduce CPU usage
            
    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        pose.close()

if __name__ == "__main__":
    test_mediapipe() 