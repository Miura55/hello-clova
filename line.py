import os
import random

from flask import (
    Flask, request, jsonify
)
from cek import (
    Clova, SpeechBuilder, ResponseBuilder
)



# Flask
app = Flask(__name__)

# Clova
application_id = 'kmiura.herokuapp.com'
clova = Clova(
    application_id=application_id,
    default_language='ja',
    debug_mode=True)

speech_builder = SpeechBuilder(default_language='ja')
response_builder = ResponseBuilder(default_language='ja')

# 起動時に実行
@clova.handle.launch
def launch_request_handler(clova_request):
    return clova.response("こんにちは，サイコロに設定したい数字を指定してください")

# 終了時に実行
@clova.handle.end
def end_handler(clova_request):
    return

@app.route('/', methods=['GET', 'POST'])
def lambda_handler(event=None, context=None):
    app.logger.info('Lambda function invoked index()')
    return 'hello from Flask!'

@app.route('/clova', methods=['POST'])
def clova_service():
    resp = clova.route(body=request.data, header=request.headers)
    resp = jsonify(resp)
    # make sure we have correct Content-Type that CEK expects
    resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
    return resp

@clova.handle.intent('CallNumberIntent')
def find_gourmet_by_prefecture_intent_handler(clova_request):
    app.logger.info('find_gourmet_by_prefecture_intent_handler method called!!')
    end_num = clova_request.slot_value('endNum')
    app.logger.info('endNum: %s', end_num)
    response = None
    if end_num is not None:
        try:
            response = decide_num(end_num)
        except Exception as e:
            # 処理中に例外が発生した場合は、最初からやり直してもらう
            app.logger.error('Exception at make_gourmet_info_message_for: %s', e)
            text = '処理中にエラーが発生しました。もう一度はじめからお願いします。'
            response = response_builder.simple_speech_text(text)
    else:
        text = 'もう一度数を指定してください'
        response = response_builder.simple_speech_text(text)
        response_builder.add_reprompt(response,
            'いくつからいくつまでの範囲で振って欲しいですか？')
    # retrun
    return response



if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.debug = True
    app.run(host="0.0.0.0", port=port)
