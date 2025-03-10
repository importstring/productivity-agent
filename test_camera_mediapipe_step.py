import cv2
import mediapipe as mp
import time
import numpy as np

def test_camera_mediapipe():
    # Step 1: Initialize MediaPipe
    print("Step 1: Initializing MediaPipe...")
    try:
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("MediaPipe initialized successfully")
    except Exception as e:
        print(f"Failed to initialize MediaPipe: {e}")
        return
    
    # Step 2: Initialize camera
    print("\nStep 2: Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return
    
    # Set and verify camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"Camera initialized: {width}x{height} @ {fps}fps")
    
    # Step 3: Process frames
    print("\nStep 3: Processing frames...")
    print("Press 'q' to quit")
    
    frame_count = 0
    pose_count = 0
    start_time = time.time()
    last_fps_print = time.time()
    
    try:
        while True:
            # Step 3a: Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame_count += 1
            
            # Step 3b: Convert to RGB and process with MediaPipe
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    pose_count += 1
                    
                    # Draw landmarks
                    annotated_frame = frame.copy()
                    mp_drawing.draw_landmarks(
                        annotated_frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )
                    
                    # Calculate shoulder alignment as a test metric
                    landmarks = results.pose_landmarks.landmark
                    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    
                    shoulder_angle = abs(np.arctan2(
                        right_shoulder.y - left_shoulder.y,
                        right_shoulder.x - left_shoulder.x
                    ))
                    shoulder_score = 1 - (shoulder_angle / np.pi)
                    
                    # Display metrics
                    cv2.putText(
                        annotated_frame,
                        f"Shoulder Score: {shoulder_score:.2f}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                    
                    # Show the annotated frame
                    cv2.imshow('Pose Detection', annotated_frame)
                else:
                    # Show the original frame if no pose detected
                    cv2.imshow('Pose Detection', frame)
                    
            except Exception as e:
                print(f"Error processing frame: {e}")
                cv2.imshow('Pose Detection', frame)
            
            # Print stats every second
            current_time = time.time()
            if current_time - last_fps_print >= 1:
                elapsed = current_time - start_time
                fps_actual = frame_count / elapsed
                pose_rate = pose_count / elapsed
                print(f"FPS: {fps_actual:.1f}, Pose Detection Rate: {pose_rate:.1f}/s")
                last_fps_print = current_time
            
            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        print("\nStep 4: Cleaning up...")
        elapsed_total = time.time() - start_time
        print(f"Total frames processed: {frame_count}")
        print(f"Total poses detected: {pose_count}")
        print(f"Average FPS: {frame_count / elapsed_total:.1f}")
        print(f"Average pose detection rate: {pose_count / elapsed_total:.1f}/s")
        
        cap.release()
        cv2.destroyAllWindows()
        pose.close()
        print("Test completed")

if __name__ == "__main__":
    test_camera_mediapipe() 