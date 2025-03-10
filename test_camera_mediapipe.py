import cv2
import mediapipe as mp
import time
import numpy as np

def test_camera_mediapipe():
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
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    
    # Get actual camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"Camera initialized with resolution: {width}x{height} @ {fps}fps")
    print("Press 'q' to quit")
    
    try:
        start_time = time.time()
        frame_count = 0
        pose_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame_count += 1
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = pose.process(frame_rgb)
            
            # Draw pose landmarks and calculate metrics
            if results.pose_landmarks:
                pose_count += 1
                
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )
                
                # Calculate some basic metrics
                landmarks = results.pose_landmarks.landmark
                
                # Shoulder alignment
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                shoulder_angle = abs(np.arctan2(
                    right_shoulder.y - left_shoulder.y,
                    right_shoulder.x - left_shoulder.x
                ))
                shoulder_score = 1 - (shoulder_angle / np.pi)
                
                # Display metrics
                cv2.putText(frame, f"Shoulder Score: {shoulder_score:.2f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Camera Test', frame)
            
            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Print stats every second
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                fps_actual = frame_count / elapsed_time
                pose_rate = pose_count / elapsed_time
                print(f"FPS: {fps_actual:.1f}, Pose Detection Rate: {pose_rate:.1f}/s")
                start_time = time.time()
                frame_count = 0
                pose_count = 0
            
    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        pose.close()

if __name__ == "__main__":
    test_camera_mediapipe() 