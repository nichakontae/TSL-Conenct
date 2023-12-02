import onnxruntime as ort
from flask import request, Flask, jsonify
from PIL import Image
import numpy as np
from flask_socketio import SocketIO, emit
import base64
from io import BytesIO
from utils import create_predict_folder, delete_predict_folder
from extend_model import hand_pose_detection
import shutil
from dotenv import load_dotenv
import os

load_dotenv()
cors = os.getenv('CORS')
secret_key = os.getenv('SECRET_KEY')
port = os.getenv('PORT')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=cors)
app.config['SECRET_KEY'] = secret_key

class_conf_main = {
    "Mo": 0.5,
    "No": 0.5,
    "O": 0.7,
    "SaRaE": 0.7,
    "SaRaA": 0.5,
    "SaRaAr": 0.6,
    "SaRaAe": 0.65,
    "MaiHanAkat": 0.75,
    "Ko": 0.7,
    "Bo": 0.75,
    "Wo": 0.55,
    "Ya": 0.55,
    "Lo": 0.8,
    "Ro": 0.7,
    "MaiMaLai": 0.75
}


class_conf_close = {
    "Mo": 0.6,
    "No": 0.5,
    "O": 0.75,
    "SaRaE": 0.8,
}


def base64_to_image(base64_string):
    # Extract the base64 encoded binary data from the input string
    base64_data = base64_string.split(",")[1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)

    image_stream = BytesIO(image_bytes)
    image = Image.open(image_stream)
    return image


@socketio.on("connect")
def test_connect():
    print("Connected")
    socketio.emit("connected", {"data": "Connected"})


@socketio.on("image")
def receive_image(image):
    print("receive image!")
    # Decode the base64-encoded image data
    image = base64_to_image(image)
    boxes = detect_objects_on_image(image)
    socketio.emit("processed_image", {'boxes': boxes})


@socketio.on("create_folders")
def create_folders():
    try:
        create_predict_folder("predict")
        create_predict_folder("pre_processing")
        print("Folders created")
        socketio.emit("folders_created", {"data": "Folders created"})
    except Exception as e:
        print(f"Error creating folders: {e}")
        socketio.emit("folders_creation_failed", {"data": f"Error creating folders: {e}"})


@socketio.on("delete_folders")
def delete_folders():
    shutil.rmtree("predict", ignore_errors=True)
    shutil.rmtree("pre_processing", ignore_errors=True)
    print("Folders deleted")
    socketio.emit("folders_deleted", {"data": "Folders deleted"})


def detect_objects_on_image(buf):
    """
    Function receives an image,
    passes it through YOLOv8 neural network
    and returns an array of detected objects
    and their bounding boxes
    :param buf: Input image file stream
    :return: Array of bounding boxes in format [[x1,y1,x2,y2,object_type,probability],..]
    """
    null_result = []

    input_data, img_width, img_height = prepare_input(buf)
    output = run_model(input_data)
    output2 = run_extend_model(input_data)

    boxes = process_output(output, img_width, img_height)
    if len(boxes) > 0:
        label = boxes[0][4]
        print("main model predict: ", label)
        if label in ["Mo", "No", "SaRaE", "O"]:
            boxes = process_output_close_hand(output2, img_width, img_height)
            print("running close hand model...")
            if len(boxes) > 0:
                print("close hand predict: ", boxes[0][4])
        elif label in ["SaRaA", "SaRaAr", "SaRaAe"]:
            buf.save(f"./pre_processing/main_model/{label}.jpg")
            result = hand_pose_detection(label)
            print("running hand pose model...")
            print("hand pose predict: ", result)
            if result != "" and result != "null":
                boxes[0][4] = result
            else:
                boxes = null_result
    return boxes


def prepare_input(img):
    """
    Function used to convert input image to tensor,
    required as an input to YOLOv8 object detection
    network.
    :param img: Uploaded file input stream
    :return: Numpy array in a shape (3,width,height) where 3 is number of color channels
    """
    # img = Image.open(buf)
    img_width, img_height = img.size
    img = img.resize((800, 800))
    img = img.convert("RGB")
    input_data = np.array(img) / 255.0
    input_data = input_data.transpose(2, 0, 1)
    input_data = input_data.reshape(1, 3, 800, 800)
    return input_data.astype(np.float32), img_width, img_height


def run_model(input_data):
    """
    Function used to pass provided input tensor to
    YOLOv8 neural network and return result
    :param input_data: Numpy array in a shape (3,width,height)
    :return: Raw output of YOLOv8 network as an array of shape (1,84,8400)
    """
    model = ort.InferenceSession("s7m.onnx", providers=['CPUExecutionProvider'])
    outputs = model.run(["output0"], {"images": input_data})
    return outputs[0]


def run_extend_model(input_data):
    """
    Function used to pass provided input tensor to
    YOLOv8 neural network and return result
    :param input_data: Numpy array in a shape (3,width,height)
    :return: Raw output of YOLOv8 network as an array of shape (1,84,8400)
    """
    model = ort.InferenceSession("extend_modelv22.onnx", providers=['CPUExecutionProvider'])
    outputs = model.run(["output0"], {"images": input_data})
    return outputs[0]


def process_output(output, img_width, img_height):
    """
    Function used to convert RAW output from YOLOv8 to an array
    of detected objects. Each object contain the bounding box of
    this object, the type of object and the probability
    :param output: Raw output of YOLOv8 network which is an array of shape (1,84,8400)
    :param img_width: The width of original image
    :param img_height: The height of original image
    :return: Array of detected objects in a format [[x1,y1,x2,y2,object_type,probability],..]
    """
    output = output[0].astype(float)
    output = output.transpose()

    boxes = []
    for row in output:
        prob = row[4:].max()
        class_id = row[4:].argmax()
        label = main_classes[class_id]
        if prob < class_conf_main.get(label):
            continue
        xc, yc, w, h = row[:4]
        x1 = (xc - w / 2) / 800 * img_width
        y1 = (yc - h / 2) / 800 * img_height
        x2 = (xc + w / 2) / 800 * img_width
        y2 = (yc + h / 2) / 800 * img_height
        boxes.append([x1, y1, x2, y2, label, prob])

    boxes.sort(key=lambda x: x[5], reverse=True)
    result = []
    while len(boxes) > 0:
        result.append(boxes[0])
        boxes = [box for box in boxes if iou(box, boxes[0]) < 0.5]

    return result


def process_output_close_hand(output, img_width, img_height):
    """
    Function used to convert RAW output from YOLOv8 to an array
    of detected objects. Each object contain the bounding box of
    this object, the type of object and the probability
    :param output: Raw output of YOLOv8 network which is an array of shape (1,84,8400)
    :param img_width: The width of original image
    :param img_height: The height of original image
    :return: Array of detected objects in a format [[x1,y1,x2,y2,object_type,probability],..]
    """
    output = output[0].astype(float)
    output = output.transpose()

    boxes = []
    for row in output:
        prob = row[4:].max()
        class_id = row[4:].argmax()
        label = close_hand_classes[class_id]
        if prob < class_conf_close.get(label):
            continue
        xc, yc, w, h = row[:4]
        x1 = (xc - w / 2) / 800 * img_width
        y1 = (yc - h / 2) / 800 * img_height
        x2 = (xc + w / 2) / 800 * img_width
        y2 = (yc + h / 2) / 800 * img_height
        boxes.append([x1, y1, x2, y2, label, prob])

    boxes.sort(key=lambda x: x[5], reverse=True)
    result = []
    while len(boxes) > 0:
        result.append(boxes[0])
        boxes = [box for box in boxes if iou(box, boxes[0]) < 0.5]

    return result


def iou(box1, box2):
    """
    Function calculates "Intersection-over-union" coefficient for specified two boxes
    https://pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/.
    :param box1: First box in format: [x1,y1,x2,y2,object_class,probability]
    :param box2: Second box in format: [x1,y1,x2,y2,object_class,probability]
    :return: Intersection over union ratio as a float number
    """
    return intersection(box1, box2) / union(box1, box2)


def union(box1, box2):
    """
    Function calculates union area of two boxes
    :param box1: First box in format [x1,y1,x2,y2,object_class,probability]
    :param box2: Second box in format [x1,y1,x2,y2,object_class,probability]
    :return: Area of the boxes union as a float number
    """
    box1_x1, box1_y1, box1_x2, box1_y2 = box1[:4]
    box2_x1, box2_y1, box2_x2, box2_y2 = box2[:4]
    box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
    box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
    return box1_area + box2_area - intersection(box1, box2)


def intersection(box1, box2):
    """
    Function calculates intersection area of two boxes
    :param box1: First box in format [x1,y1,x2,y2,object_class,probability]
    :param box2: Second box in format [x1,y1,x2,y2,object_class,probability]
    :return: Area of intersection of the boxes as a float number
    """
    box1_x1, box1_y1, box1_x2, box1_y2 = box1[:4]
    box2_x1, box2_y1, box2_x2, box2_y2 = box2[:4]
    x1 = max(box1_x1, box2_x1)
    y1 = max(box1_y1, box2_y1)
    x2 = min(box1_x2, box2_x2)
    y2 = min(box1_y2, box2_y2)
    return (x2 - x1) * (y2 - y1)


# Array of YOLOv8 class labels
main_classes = [
    'Bo', 'Ko', 'Lo', 'MaiHanAkat', 'MaiMaLai', 'Mo', 'No', 'O', 'Ro', 'SaRaA', 'SaRaAe', 'SaRaAr', 'SaRaE', 'Wo', 'Ya'
]

close_hand_classes = ['Mo', 'No', 'O', 'SaRaE']

if __name__ == "__main__":
    socketio.run(app, debug=True, port=port, host='0.0.0.0')
