# Import required libraries
from flask import Flask,render_template,Response
import cv2 # type: ignore

# Create flask object
app = Flask(__name__)

# Initialize computer's default camera for video capture
camera = cv2.VideoCapture(0)

# Function to generate frames from video
def generate_frames():
    while True:
        # Read from camera
        success,frame = camera.read()

        if not success:
            break
        else:
            # Loads pretrained haarcascade classifiers for face and eye detection from XML files
            face_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface.xml')  
            eye_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_eye.xml')

            # Detect faces in a given frame and returns rectangle coorindates where faces are detected. 
            # The image size is scaled down by 10% each time by the scale factor 1.1
            # The minNeighbors parameter (7) specifies how many faces will be detected. A high value detects few faces
            #  and reduces face positives. 
            faces = face_cascade.detectMultiScale(frame, 1.1, 7)

            # Converts frame from colored (BGR) to gray scale image. Haarcascade classifiers work more effectively with 
            # gray scale images due to reduced data complexity.
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)  

            # Fech each rectangle coordinates
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y), (x+w,y+h), (255,0,0), 2)  # Draw the rectangle
                roi_gray = gray[y:y+h, x:x+w]  # Grayscle version of the exact face area
                roi_color = frame[y:y+h, x:x+w]  # Colored version of the exact face area

                # Detect eyes whithin the face region
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 7)
                # Fetch each eye coorindates and draws rectangle
                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color, (ex,ey), (ex+ew, ey+eh), (0,255,0), 2)

            # Encodes the captured frame as jpeg image
            _,buffer = cv2.imencode('.jpg',frame)
            # Convert the encoded image into a byte sequence which is necessary to send the frame over HTTP 
            # as a binary stream.
            frame = buffer.tobytes()

        # Sends each frame in a format suitable for streaming over HTTP. --frame indicates start of a new frame.
        # b'Content-Type: image/jpeg\r\n\r\n' indicates frame content is a jpeg image. frame jpeg encoded data as bytes.
        # b'\r\n' dontes end of current frame.
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Define root URL ('/')
@app.route('/')
def index():
    return render_template('index.html')

# Define route for the URL /video
@app.route('/video')
def video():
    # MIME type is used to tell the client that this response contains a continous stream of images where each part 
    # replaces the previos ones and each frame in the stream is separated by the text "--frame". This boundary helps
    # client to recognize each new image.
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

# Calling the function
if __name__ == '__main__':
    app.run()