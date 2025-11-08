import RPi.GPIO as GPIO
import time

# ==========================
# Configuração dos pinos
# ==========================
IN1 = 17  # Direção motor A
IN2 = 27
ENA = 18  # PWM motor A

IN4 = 23
ENB = 13  # PWM motor B

# ==========================
# Configuração inicial
# ==========================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB], GPIO.OUT)

# PWM estável com frequência alta (5 kHz)
pwmA = GPIO.PWM(ENA, 5000)
pwmB = GPIO.PWM(ENB, 5000)
pwmA.start(0)
pwmB.start(0)

# ==========================
# Funções de movimento
# ==========================
def frente(vel=50):
    pwmA.ChangeDutyCycle(vel)
    pwmB.ChangeDutyCycle(vel)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print(f"➡️ Indo pra frente com velocidade {vel}%")

def tras(vel=50):
    pwmA.ChangeDutyCycle(vel)
    pwmB.ChangeDutyCycle(vel)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print(f"⬅️ Indo pra trás com velocidade {vel}%")

def direita(vel=50):
    pwmA.ChangeDutyCycle(vel)
    pwmB.ChangeDutyCycle(vel)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print(f"↪️ Virando à direita com velocidade {vel}%")

def esquerda(vel=50):
    pwmA.ChangeDutyCycle(vel)
    pwmB.ChangeDutyCycle(vel)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print(f"↩️ Virando à esquerda com velocidAade {vel}%")

def parar():
    GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
    print("🛑 Parado")

# ==========================
# Teste básico
# ==========================
try:
    while True:
        frente(30)
        time.sleep(2)
        parar()
        time.sleep(0.2)
        direita(40)
        time.sleep(1)
        parar()
        time.sleep(0.2)
        

except KeyboardInterrupt:
    parar()
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()
    print("🚪 Programa finalizado com segurança.")
