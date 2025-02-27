import cv2
import logging

class VideoProcessing:
    def __init__(self):
        """
        Initialize the Video Processing module.
        """
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detect_faces_in_video(self, video_path):
        """
        Detect faces in a video and display processed frames.
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logging.error("Error: Could not open video file.")
                return
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.imshow("Video Processing - Face Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            logging.error(f"Error processing video: {e}")

# Example Usage
if __name__ == "__main__":
    vid_processor = VideoProcessing()
    vid_processor.detect_faces_in_video("sample_video.mp4")
