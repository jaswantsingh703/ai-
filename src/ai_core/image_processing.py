import cv2
import pytesseract
import logging

class ImageProcessing:
    def __init__(self):
        """
        Initialize the Image Processing module.
        """
        self.tesseract_cmd = "tesseract"
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def extract_text(self, image_path):
        """
        Extract text from an image using OCR.
        """
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            return ""

    def detect_faces(self, image_path):
        """
        Detect faces in an image.
        """
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            return faces
        except Exception as e:
            logging.error(f"Error detecting faces: {e}")
            return []

# Example Usage
if __name__ == "__main__":
    img_processor = ImageProcessing()
    text = img_processor.extract_text("sample_image.png")
    print("Extracted Text:", text)
    faces = img_processor.detect_faces("sample_image.png")
    print("Detected Faces:", faces)
