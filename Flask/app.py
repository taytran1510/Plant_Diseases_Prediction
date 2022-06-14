from flask import Flask, render_template, jsonify, request, Markup, Response
import cv2
from model import predict_image
import utils
import base64
import pdfkit
from flask import make_response

app = Flask(__name__)
video=cv2.VideoCapture(0)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/webcam')
def index():
    """Video streaming home page."""
    return render_template('camera.html')

@app.route('/takeimage', methods = ['POST'])
def takeimage():
    name = request.form['name']
    print(name)
    _, frame = video.read()
    cv2.imwrite(f'{name}.jpg', frame)
    return Response(status = 200)


def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = video.read()
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            file = request.files['file']
            print('_____________________')
            print(file)
            print('____________________')
            img = file.read()
            print(type(img))
            prediction = predict_image(img)
            print(prediction)
            res = Markup(utils.disease_dic[prediction])
            return render_template('display.html', status=200, result=res)
        except:
            pass
    return render_template('index.html', status=500, res="Internal Server Error")

@app.route('/predictcam', methods=['GET', 'POST'])
def predictcam():
    try:
        #file = cv2.imread("C:/Users/T480/Desktop/Plant_AI-master/Plant_AI-master/Flask/t.jpg")
        with open('C:/Users/T480/Desktop/Plant_AI-master/Plant_AI-master/Flask/t.jpg', "rb") as image_file:
            img = image_file.read()
        #print('***********************')
        #print(type(file))
        #print('*********************')
        #img = file.read()
        print('***********************')
        print(img)
        print('*********************')
        prediction = predict_image(img)
        print(prediction)
        res = Markup(utils.disease_dic[prediction])    
        return render_template('display.html', status=200, result=res)
    except:
        pass
    return render_template('index.html', status=500, res="Internal Server Error")

@app.route('/printpdf', methods=['GET', 'POST'])
def printpdf():
    # try:
    #     # need install 'wkhtmltopdf' from: https://wkhtmltopdf.org/downloads.html
    #     config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    #     pdf = pdfkit.from_file('templates/display.html','output.pdf', configuration=config)
    #     # pdf = pdfkit.from_string(html, False)
    #     response = make_response(pdf)
    #     response.headers["Content-Type"] = "application/pdf"
    #     response.headers["Content-Disposition"] = "inline; filename=output.pdf"
    #     return response
    # except:
    #     pass
    # return render_template('index.html', status=500, res="Internal Server Error")
    if request.method == 'POST':
        try:
            file = request.files['file']
            img = file.read()
            prediction = predict_image(img)
            res = Markup(utils.disease_dic[prediction])
            html = render_template('printpdf.html', result=res)
            # need install 'wkhtmltopdf' from: https://wkhtmltopdf.org/downloads.html
            config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
            pdf = pdfkit.from_string(html, configuration=config)
            # pdf = pdfkit.from_string(html, False)
            response = make_response(pdf)
            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = "inline; filename=output.pdf"
            return response
        except:
            pass
    return render_template('index.html', status=500, res="Internal Server Error")

if __name__ == "__main__":
    app.run(debug=True)
