import cv2
import logging
import os
import tempfile
import numpy as np

class VideoProcessing:
    """
    Video processing module with face detection and analysis capabilities.
    """
    
    def __init__(self):
        """
        Initialize the Video Processing module.
        """
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            logging.info("Video Processing module initialized")
        except Exception as e:
            logging.error(f"Error initializing Video Processing module: {e}")
            self.face_cascade = None

    def detect_faces_in_video(self, video_path, display=False, save_output=False, output_path=None):
        """
        Detect faces in a video and optionally display or save the processed video.
        
        Args:
            video_path (str): Path to the video file
            display (bool): Whether to display the processed video
            save_output (bool): Whether to save the processed video
            output_path (str, optional): Path to save the processed video
            
        Returns:
            dict: Results of face detection
        """
        if not os.path.exists(video_path):
            return {"error": "Video file not found."}
            
        if self.face_cascade is None:
            return {"error": "Face detection is not initialized."}
            
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"error": "Could not open video file."}
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create output video writer if needed
            out = None
            if save_output:
                if output_path is None:
                    # Create temporary output file
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                        output_path = temp_file.name
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Process video
            face_counts = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect faces in frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                face_counts.append(len(faces))
                
                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                # Display if requested
                if display:
                    cv2.imshow("Video Processing - Face Detection", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Save if requested
                if save_output and out is not None:
                    out.write(frame)
                
                frame_count += 1
                
                # Log progress
                if frame_count % 100 == 0:
                    logging.info(f"Processed {frame_count}/{total_frames} frames")
            
            # Clean up
            cap.release()
            if out is not None:
                out.release()
            if display:
                cv2.destroyAllWindows()
            
            # Prepare results
            results = {
                "total_frames": frame_count,
                "frames_with_faces": sum(1 for count in face_counts if count > 0),
                "max_faces": max(face_counts) if face_counts else 0,
                "avg_faces": np.mean(face_counts) if face_counts else 0,
                "output_path": output_path if save_output else None
            }
            
            return results
            
        except Exception as e:
            logging.error(f"Error processing video: {e}")
            return {"error": f"Error processing video: {str(e)}"}