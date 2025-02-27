import cv2
import logging
import os

# Check if pytesseract is available
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logging.warning("pytesseract module not available. OCR functionality will be limited.")

class ImageProcessing:
    """
    Image processing module with OCR and face detection capabilities.
    """
    
    def __init__(self):
        """
        Initialize the Image Processing module.
        """
        if PYTESSERACT_AVAILABLE:
            # Try to set tesseract command
            try:
                self.tesseract_cmd = "tesseract"
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
                logging.info("Tesseract initialized")
            except Exception as e:
                logging.error(f"Error initializing Tesseract: {e}")
        
        # Initialize face detection
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            logging.info("Face detection initialized")
        except Exception as e:
            logging.error(f"Error initializing face detection: {e}")
            self.face_cascade = None

    def extract_text(self, image_path):
        """
        Extract text from an image using OCR.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text or error message
        """
        if not os.path.exists(image_path):
            return "Image file not found."
            
        if not PYTESSERACT_AVAILABLE:
            return "OCR functionality is not available. Please install pytesseract."
            
        try:
            image = cv2.imread(image_path)
            if image is None:
                return "Failed to load image."
                
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply some preprocessing to improve OCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Perform OCR
            text = pytesseract.image_to_string(gray)
            
            return text.strip() if text else "No text detected in the image."
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            return f"Error processing image: {str(e)}"

    def detect_faces(self, image_path):
        """
        Detect faces in an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            list: List of detected faces (x, y, w, h) or empty list
        """
        if not os.path.exists(image_path):
            return []
            
        if self.face_cascade is None:
            logging.error("Face detection is not initialized.")
            return []
            
        try:
            image = cv2.imread(image_path)
            if image is None:
                logging.error("Failed to load image.")
                return []
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            return faces.tolist() if len(faces) > 0 else []
        except Exception as e:
            logging.error(f"Error detecting faces: {e}")
            return []
    
    def analyze_image(self, image_path):
        """
        Analyze an image for both text and faces.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Analysis results
        """
        if not os.path.exists(image_path):
            return {"error": "Image file not found."}
            
        results = {}
        
        # Extract text
        if PYTESSERACT_AVAILABLE:
            results["text"] = self.extract_text(image_path)
        else:
            results["text"] = "OCR not available"
        
        # Detect faces
        faces = self.detect_faces(image_path)
        results["faces_detected"] = len(faces)
        results["faces"] = faces
        
        return results