#-*-coding:utf-8-*-
# 필요한 라이브러리를 불러옴

import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request
from flask import render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# trigger 핀과 echo 핀의 GPIO 핀 번호 설정
TRIG = 27
ECHO = 22
#motor pin GPIO
moter_A = 5
moter_B = 6
# green LED, yellow LED, red LED
led_Y = 25
led_G = 26
led_R = 16

# 불필요한 warning 제거, GPIO핀의 번호 모드 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# trigger 핀과 echo 핀을 각각 출력과 입력으로 설정
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.setup(led_G, GPIO.OUT)
GPIO.setup(led_Y, GPIO.OUT)
GPIO.setup(led_R, GPIO.OUT)

GPIO.setup(moter_A, GPIO.OUT)
GPIO.setup(moter_B, GPIO.OUT)
# trigger 핀으로부터 0V(0, False) 출력 (즉, 출력하지 않음)
GPIO.output(TRIG, False)
time.sleep(2)




# OLED 128X64 (i2c_address = 연결된 OLED 주소) 인스턴스 disp 생성
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
# 주워진 mode('1';흑백화면)과 크기(width,height)를 가지고 이미지 생성
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# OLED 화면 초기화
disp.begin()
# OLED 화면 클리어
disp.clear()
disp.display()
# OLED 화면에 출력할 직사각형와 문자열의 left top corner 위치(x,y) 설정
x = 15
padding = 0
y = 5
# OLED 화면에 출력할 문자열의 폰트 설정
font = ImageFont.load_default()

#pwm instance p, GPIO pwm 50Hz
#pwm instance r, y, g
p=GPIO.PWM(moter_A, 50)
lr=GPIO.PWM(led_R, 50)
ly=GPIO.PWM(led_Y, 50)
lg=GPIO.PWM(led_G, 50)
dc_1=100
dc_2=50
dc_s=70

p.start(0)
lr.start(0)
ly.start(0)
lg.start(0)

lr.ChangeDutyCycle(dc_s)
ly.ChangeDutyCycle(dc_s)
lg.ChangeDutyCycle(dc_s)

# 이미지 상에 그리기를 수행할 object 생성
draw = ImageDraw.Draw(image)
# 이미상에 직사각형 그리기[위치와 크기, 윤곽선색(outline), 채우기색(fill) 설정]
draw.rectangle((1,1,width-2,height-2), outline=255, fill=0) # 0: 검정색, 255: 흰색
draw.text((x,y), 'hello - User!', font=font, fill=255)
# 화면 표시
disp.image(image)
disp.display()
time.sleep(3)




@app.route("/")
def home():
    return render_template("index1.html") # index.html 문서는 templates 디렉토리 내에 있어야 함
@app.route("/fan/on")
def fan_on():
    while True:
        #중복그리기를 방지하기 위해 그리기를 수행할 새로운 object 생성 초기화
        # 이미지 상에 그리기를 수행할 object 생성
        draw = ImageDraw.Draw(image)
        # 이미상에 직사각형 그리기[위치와 크기, 윤곽선색(outline), 채우기색(fill) 설정]
        draw.rectangle((1,1,width-2,height-2), outline=255, fill=0) # 0: 검정색, 255: 흰색
        
        
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        while GPIO.input(ECHO) == False:
            start= time.time()
        while GPIO.input(ECHO) == True:
            stop= time.time()

        check_time = stop - start # 초음파가 발사되어 수신될 때까지 걸린 시간
        distance = check_time * 34300 / 2 # 초음파센서와 물체와의 거리 계산    
        
        time.sleep(1.5) # 1.5초 간격으로 센서 측정
            
        if distance <= 30:
            p.ChangeDutyCycle(dc_1)
            GPIO.output(moter_B,GPIO.LOW)
            lr.ChangeDutyCycle(0)
            ly.ChangeDutyCycle(0)
            lg.ChangeDutyCycle(dc_1)
            draw.text((x,y), 'Set the fan\nto strong winds!', font=font, fill=255)
            # 화면 표시
            disp.image(image)
            disp.display()
            
        elif distance >=30 and distance <= 50:
            p.ChangeDutyCycle(dc_2)
            GPIO.output(moter_B,GPIO.LOW)
            lr.ChangeDutyCycle(0)
            ly.ChangeDutyCycle(dc_1)
            lg.ChangeDutyCycle(0)
            draw.text((x,y), 'Set the fan\nto weak winds!', font=font, fill=255)
            # 화면 표시
            disp.image(image)
            disp.display()
            
            
        else:
            p.ChangeDutyCycle(0)
            GPIO.output(moter_B,GPIO.LOW)
            lr.ChangeDutyCycle(dc_1)
            ly.ChangeDutyCycle(0)
            lg.ChangeDutyCycle(0)
            draw.text((x,y), 'Stop the fan!', font=font, fill=255)
            # 화면 표시
            disp.image(image)
            disp.display()

        
@app.route("/fan/off")
def fan_off():
    while True:
        p.ChangeDutyCycle(0)
        GPIO.output(moter_B,GPIO.LOW)
        lr.ChangeDutyCycle(0)
        ly.ChangeDutyCycle(0)
        lg.ChangeDutyCycle(0)
        draw.rectangle((1,1,width-2,height-2), outline=255, fill=255) # 0: 검정색, 255: 흰색
    
if __name__ == "__main__":
    app.run(host="0.0.0.0")
