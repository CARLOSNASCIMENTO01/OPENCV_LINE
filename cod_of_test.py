import cv2
import numpy as np
import threading

# -------- CONFIG --------
Kp = 0.5
URL_CAMERA = "http://10.0.0.141:8080/video"

# -------- CAMERA THREAD --------
class Camera:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.frame = None
        self.running = True

        # remove buffer
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            # descarta frames antigos
            for _ in range(2):
                self.cap.read()

            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()


# -------- INICIO --------
cam = Camera(URL_CAMERA)

print("Rodando...")

while True:
    frame = cam.read()

    if frame is None:
        continue

    # 🔥 RESOLUÇÃO BAIXA (GANHO GRANDE)
    frame = cv2.resize(frame, (320, 240))
    h, w = frame.shape[:2]

    # 🔥 USA SÓ METADE INFERIOR
    """frame = frame[int(h*0.5):h, :]
    h, w = frame.shape[:2]"""

    # -------- LINHA --------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 🔥 threshold leve (mais rápido)
    mask = gray < 100
    mask = mask.astype(np.uint8) * 255

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) > 150:
            M = cv2.moments(largest)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])

                # -------- CONTROLE P --------
                center = w // 2
                error = cx - center
                output = Kp * error

                if error > 15:
                    comando = "DIREITA"
                elif error < -15:
                    comando = "ESQUERDA"
                else:
                    comando = "RETO"

                print(f"{comando} | erro: {error} | P: {output:.2f}")

                # visual leve
                cv2.circle(frame, (cx, h//2), 5, (0, 0, 255), -1)
                cv2.line(frame, (center, 0), (center, h), (255, 0, 0), 2)

    # -------- VISUAL (OPCIONAL) --------
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.stop()
cv2.destroyAllWindows()