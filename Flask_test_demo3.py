#coding=utf-8
from flask import Flask, render_template, Response,request, flash,redirect,url_for,session,jsonify
#导入wtf扩展的表单类
from flask_wtf import FlaskForm
#导入自定义表单需要的字段
from wtforms import SubmitField,StringField,PasswordField
#导入wtf扩展提供的表单验证器
from wtforms.validators import DataRequired,EqualTo
import mqtt_client1
import sys
import base64
import numpy as np
import cv2
from face_app.face import Face_app
#import json
#import threading

'''#-------------------------------------------------------------mqtt--------------------------------------------------------------------------
try:
    my_client1
except:
    my_client1 = mqtt_client1.Mqtt_client1()

try:
    my_client2
except:
    #print(2222)
    my_client2 = mqtt_client1.Mqtt_client2()
#-------------------------------------------------------------------------------------------------------------------------------------------
'''

app = Flask(__name__)
app.config['SECRET_KEY']='heima'
start_flag = False
quit_flag  = False
face_rec = Face_app()


#自定义表单类，文本字段、密码字段、提交按钮
# 需要自定义一个表单类
class RegisterForm(FlaskForm):
    username = StringField(u'用户名称:', validators=[DataRequired()])
    password = PasswordField(u'输入密码:', validators=[DataRequired()])
    password2 = PasswordField(u'确认密码:', validators=[DataRequired(), EqualTo(u'password', u'密码输入不一致')])
    input = SubmitField(u'提交')

#定义根路由视图函数，生成表单对象，获取表单数据，进行表单数据验证
@app.route('/', methods=['GET', 'POST'])
def form():
    register_form = RegisterForm()

    if request.method == 'POST':
        # 调用validate_on_submit方法, 可以一次性执行完所有的验证函数的逻辑
        if register_form.validate_on_submit():
            # 进入这里就表示所有的逻辑都验证成功
            username = request.form.get('username')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            if username=='0000' and password=='0000' and password2=='0000':
                session['success'] = 'xxx'
                return redirect('/stream')
            else:
                flash('参数有误')
            #print (username)
            #return redirect('/stream')

        else:
            #message = register_form.errors.get('password2')[0]
            #flash(message)
            flash('参数有误')

    return render_template('sign_in.html', form=register_form)

@app.route("/start_display")
def action1():    # button
    info = session.get('success')
    if not info:
        return redirect('/')
    global start_flag

    start_flag = True
    print('start display!!!')
    return "Success"#, {'Content-Type': 'text/plain'}

@app.route("/stop_display")
def action2():    # button
    info = session.get('success')
    if not info:
        return redirect('/')
    global start_flag
    start_flag = False
    print('stop display!!!')
    return "Success"#, {'Content-Type': 'text/plain'}

@app.route('/stream')  # 主页
def index():
    info = session.get('success')
    if not info:
        return redirect('/')
    global quit_flag
    quit_flag = False
    # jinja2模板，具体格式保存在index.html文件中
    #print('here')
    return render_template('stream.html')

def gen():
    global start_flag,quit_flag
    my_client1 = mqtt_client1.Mqtt_client1()
    my_client2 = mqtt_client1.Mqtt_client2()
    while True:
        my_client1.client.loop()
        if quit_flag == True:
            break
        if start_flag == False:
            continue
        if my_client1.img_str == None:
            continue
        frame = my_client1.drawSth_OnJpgFrame(my_client1.get_cvFrame(),my_client2.rect_list)#.tobytes()
        #print('frame:',frame)
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    del my_client1
    del my_client2
    print('quit')
    #print('myclient1 ref num:',sys.getrefcount(Mqtt_client1()))
    

@app.route('/video_feed')  # 这个地址返回视频流响应
def video_feed():
    info = session.get('success')
    if not info:
        return redirect('/')
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')   

@app.route('/quit') 
def quit():
    global quit_flag
    quit_flag = True
    session.clear()
    return redirect('/')

@app.route('/TurnToFaceHtml') 
def TurnToFaceHtml():
    return render_template('faceLogin.html')

@app.route('/upload',methods=['GET', 'POST']) 
def upload_img():
    if request.method == 'POST':
        base64_img = request.form.get('img')
        # base64解码
        imgdata = base64.b64decode(base64_img)
        # 转换为np数组
        img_array = np.fromstring(imgdata, np.uint8)
        # 转换成opencv可用格式
        img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
        #cv2.imwrite('123.jpg',img)
        name_list = face_rec.recognize_fromImg(img)
        if "zhujunhui" in name_list:
            session['success'] = 'xxx'
            return '1'
            #return redirect('/stream')
        else:
            return '0'#Response("not")

    return "Success"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,ssl_context=('./ssl/server.crt', './ssl/server.key'))












