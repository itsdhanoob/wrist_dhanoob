import cv2

# Open the webcam
cap = cv2.VideoCapture(-1)

# Check if the webcam is successfully opened
if not cap.isOpened():
    print("Failed to open webcam.")
    exit(1)

# Capture a frame from the webcam
ret, frame = cap.read()

# Check if the frame is captured successfully
if not ret:
    print("Failed to capture frame.")
    exit(1)

# Display the captured frame
cv2.imshow("Webcam", frame)
cv2.waitKey(0)

# Release the webcam
cap.release()
cv2.destroyAllWindows()
