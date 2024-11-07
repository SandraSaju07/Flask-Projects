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