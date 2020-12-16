from io import BytesIO
import argparse
import time
import json
import os

from gtts import gTTS
import pyttsx3
from flask import Flask, jsonify, request, make_response, render_template, Response
# from flask_socketio import SocketIO
# from werkzeug import FileWrapper

app = Flask(__name__)

# async_mode = None
# socket_ = SocketIO(app, async_mode=async_mode)
dir_path = os.path.dirname(os.path.realpath(__file__))
support_audio_type = ['mp3', 'wav']

@app.route('/tts/http/<model>', methods=['POST'])
def tts(model):
    toc = time.time()

    name, text, return_type = decode_request(request)

    try:
        if model == "gtts":
            audio_fp = BytesIO()
            tts = gTTS(text, lang='en')
            tts.write_to_fp(audio_fp)
            with open(dir_path + '/voice.mp3', 'wb') as f:
                tts.write_to_fp(f)

            with open(dir_path + '/voice.mp3', 'rb') as binfile:
                ba = bytearray(binfile.read())

            # ba = bytearray(audio_fp.read())
            # print(audio_fp.read())

        else:
            engine = pyttsx3.init()
            # engine.say(text)
            engine.save_to_file(text, dir_path + '/voice.mp3')
            engine.runAndWait()
            with open(dir_path + '/voice.mp3', 'rb') as binfile:
                ba = bytearray(binfile.read())

        response = make_response(ba)

        if return_type in support_audio_type:
            response.headers.set('Content-Type', 'audio/wav')
            response.headers.set(
                'Content-Disposition', 'attachment', filename='%s.%s' % (name, return_type))
        else:
            response.headers.set('Content-Type', 'application/octet-stream')
            # response.headers.set(
            #     'Content-Disposition', 'attachment', filename='%s.%s' % (name, return_type))

        return response, 200
            
    except Exception as ex:
        print(ex)
        return {'error': str(ex)}, 200

def decode_request(request):
    if request.content_type == 'application/json':
        req = request.get_json()

        if 'text' in req:
            if 'return_type' in req:
                return req['name'], req['text'], req['return_type']
            else:
                return req['name'], req['text'], 'mp3'
        else:
            return None, None, None
    else:
        req = request.form
        return req.get('name'), req.get('text'), req.get('type')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'-p', '--port',
		type=int,
		default=5432,
		help='Port of serving api')
	args = parser.parse_args()
	app.run(host='0.0.0.0', port=args.port, debug=True)
	# app.run(host='0.0.0.0', port=8000)