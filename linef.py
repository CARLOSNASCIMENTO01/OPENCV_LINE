import cv2
import numpy as np

# --- CONFIGURAÇÕES ---
Kp = 0.6               # ganho proporcional
MIN_GREEN_AREA = 200   # área mínima da mancha verde
ROI_SIZE = 200         # tamanho do quadrado de análise
SMOOTH = 0.2           # suavização do movimento do ROI
cap = cv2.VideoCapture(2)

# Posição inicial do ROI (centro da tela)
ret, frame = cap.read()
h, w = frame.shape[:2]
roi_cx, roi_cy = w // 2, h // 2  # posição central inicial

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- ROI dinâmico (segue a linha) ---
    x1 = int(roi_cx - ROI_SIZE // 2)
    y1 = int(roi_cy - ROI_SIZE // 2)
    x2 = int(roi_cx + ROI_SIZE // 2)
    y2 = int(roi_cy + ROI_SIZE // 2)

    # Garante que o ROI não saia da tela
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    roi = frame[y1:y2, x1:x2]

    # --- DETECÇÃO DA LINHA PRETA ---
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, black_line = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        black_line, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cx_black, cy_black = None, None
    if contours:
        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] != 0:
            cx_black = int(M["m10"] / M["m00"])
            cy_black = int(M["m01"] / M["m00"])
            cv2.circle(roi, (cx_black, cy_black), 5, (0, 0, 255), -1)

    # --- CONTROLE PROPORCIONAL ---
    if cx_black is not None:
        center_x = ROI_SIZE // 2
        error = cx_black - center_x
        correction = Kp * error
        print(f"Erro: {error}, Saída proporcional: {correction:.2f}")

        # Movimento do ROI segue o centro da linha (suavizado)
        roi_cx = int((1 - SMOOTH) * roi_cx + SMOOTH * (x1 + cx_black))
        roi_cy = int((1 - SMOOTH) * roi_cy + SMOOTH * (y1 + cy_black))

    # --- DETECÇÃO DE MARCAÇÕES VERDES ---
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 80, 80])
    upper_green = np.array([85, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Remoção de ruído
    mask_green = cv2.GaussianBlur(mask_green, (5, 5), 0)
    mask_green = cv2.morphologyEx(
        mask_green, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask_green = cv2.morphologyEx(
        mask_green, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours_green, _ = cv2.findContours(
        mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    greens_left, greens_right = [], []

    for c in contours_green:
        area = cv2.contourArea(c)
        if area < MIN_GREEN_AREA or cx_black is None:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cx_green = int(M["m10"] / M["m00"])
        cy_green = int(M["m01"] / M["m00"])
        cv2.circle(roi, (cx_green, cy_green), 7, (0, 255, 0), -1)

        # Só considera verdes atrás da linha preta
        if cy_green >= cy_black:
            if cx_green < cx_black:
                greens_left.append((cx_green, cy_green))
            else:
                greens_right.append((cx_green, cy_green))

    # --- DECISÃO DE AÇÃO ---
    action = "IGNORAR"
    if greens_left and greens_right:
        action = "GIRAR 180°"
    elif greens_left:
        action = "GIRAR 90° ESQUERDA"
    elif greens_right:
        action = "GIRAR 90° DIREITA"

    if action != "IGNORAR":
        print(f"Marcação verde detectada! Ação: {action}")
        cv2.putText(roi, action, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # --- VISUALIZAÇÃO ---
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.imshow("Camera", frame)
    cv2.imshow("ROI Dinamico", roi)
    cv2.imshow("Mask Verde", mask_green)
    cv2.imshow("Linha Preta", black_line)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
