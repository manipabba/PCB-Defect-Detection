from flask import Flask, request, Response, jsonify, make_response
import jsonpickle
import numpy as np
import cv2
import base64
import json
from pcb_analyze import process_pcb_img


""" Requirements
flask - pip3 install flask
numpy - pip3 install numpy
opencv - pip3 install opencv
jsonpickle - pip3 install jsonpickle
tensorflow - pip3 install tensorflow
skimage - pip3 install scikit-image
pandas - pip3 install pandas
"""
app = Flask(__name__)
app.config["DEBUG"] = True

def build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/', methods=['GET'])
def home():
    return "<h1>This is a basic API to find defects in PCB Images</h1>"

@app.route('/api/find_defects', methods=['POST', 'OPTIONS'])
# @cross_origin()
def find_defects():
    r = request

    if r.method == 'OPTIONS':
        return build_cors_preflight_response()
    elif r.method == 'POST':
        # convert to cv2 image
        img_str = json.loads(r.data.decode('utf8'))["data"].split(",")[1]
        nparr = np.frombuffer(base64.b64decode(img_str), dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        pred, diff, pre = process_pcb_img(img, preprocessBool=json.loads(r.data.decode('utf8'))["preprocess"])

        _, pred = cv2.imencode('.jpg', pred)
        pred = base64.b64encode(pred).decode("utf-8")
        _, diff = cv2.imencode('.jpg', diff)
        diff = base64.b64encode(diff).decode("utf-8")
        _, pre = cv2.imencode('.jpg', pre)
        pre = base64.b64encode(pre).decode("utf-8")

        # response for client
        response = {
            'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0]),
            'pred': pred,
            'diff': diff,
            'pre': pre,
            'tag_header': "data:image/jpeg;base64,"
        }

        # jsonify and add cors enabled headers
        response = jsonify(response)
        return corsify_actual_response(response)

app.run()