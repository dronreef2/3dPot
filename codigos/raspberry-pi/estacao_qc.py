#!/usr/bin/env python3
"""
Estação de Controle de Qualidade com Visão Computacional
Raspberry Pi + OpenCV + Web Interface
"""

import cv2
import numpy as np
import time
import json
import os
from flask import Flask, render_template, request, jsonify
from picamera2 import Picamera2
import RPi.GPIO as GPIO
from threading import Thread, Event
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EstacaoQC:
    def __init__(self):
        # Configurações
        self.config = {
            'width': 640,
            'height': 480,
            'fps': 30,
            'led_brightness': 100,  # 0-100%
            'motor_steps': 200,
            'inspection_positions': 8,  # Posições para rotação
            'threshold_confidence': 0.7
        }
        
        # Inicializa GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)  # LED ring
        GPIO.setup(18, GPIO.OUT)  # Motor de passo
        GPIO.setup(19, GPIO.OUT)  # Direção do motor
        
        # PWM para controle de brilho dos LEDs
        self.led_pwm = GPIO.PWM(17, 1000)
        self.led_pwm.start(0)
        
        # Estado da aplicação
        self.app_running = True
        self.inspection_active = False
        self.current_result = None
        self.last_inspection_time = None
        
        # Inicializa câmera
        self.initialize_camera()
        
        # Inicializa Flask
        self.app = Flask(__name__)
        self.setup_routes()
        
    def initialize_camera(self):
        """Inicializa a câmera Pi"""
        try:
            self.picam2 = Picamera2()
            self.picam2.configure(self.picam2.create_still_configuration(
                main={"size": (self.config['width'], self.config['height'])}
            ))
            self.picam2.start()
            time.sleep(2)  # Aguarda estabilização
            logger.info("Câmera inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar câmera: {e}")
            self.picam2 = None
    
    def setup_routes(self):
        """Configura rotas do servidor web"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'status': 'ready' if not self.inspection_active else 'inspecting',
                'last_inspection': self.last_inspection_time,
                'current_result': self.current_result,
                'camera_ready': self.picam2 is not None
            })
        
        @self.app.route('/api/start_inspection', methods=['POST'])
        def start_inspection():
            if self.inspection_active:
                return jsonify({'error': 'Inspeção já em andamento'}), 400
            
            # Inicia inspeção em thread separada
            thread = Thread(target=self.run_inspection)
            thread.daemon = True
            thread.start()
            
            return jsonify({'message': 'Inspeção iniciada'})
        
        @self.app.route('/api/led_control', methods=['POST'])
        def control_led():
            data = request.get_json()
            brightness = data.get('brightness', 50)
            brightness = max(0, min(100, brightness))  # Limita entre 0-100
            
            self.led_pwm.ChangeDutyCycle(brightness)
            logger.info(f"LED configurado para {brightness}%")
            
            return jsonify({'success': True, 'brightness': brightness})
        
        @self.app.route('/api/capture_test')
        def capture_test():
            """Captura uma imagem de teste"""
            if not self.picam2:
                return jsonify({'error': 'Câmera não disponível'}), 500
            
            try:
                image_path = '/tmp/test_capture.jpg'
                self.picam2.capture_file(image_path)
                return jsonify({'success': True, 'image': 'test_capture.jpg'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def set_led_brightness(self, brightness):
        """Define brilho dos LEDs (0-100%)"""
        duty_cycle = max(0, min(100, brightness))
        self.led_pwm.ChangeDutyCycle(duty_cycle)
    
    def step_motor(self, steps, direction=1):
        """Move o motor de passo"""
        GPIO.output(19, direction)  # Define direção
        
        for _ in range(steps):
            GPIO.output(18, GPIO.HIGH)
            time.sleep(0.001)  # 1ms de pulso
            GPIO.output(18, GPIO.LOW)
            time.sleep(0.001)
    
    def capture_image(self, position):
        """Captura uma imagem na posição especificada"""
        image_path = f'/tmp/inspection_pos_{position}.jpg'
        
        try:
            self.picam2.capture_file(image_path)
            return image_path
        except Exception as e:
            logger.error(f"Erro ao capturar imagem na posição {position}: {e}")
            return None
    
    def load_reference_image(self, model_name):
        """Carrega imagem de referência do modelo 3D"""
        reference_path = f'/static/models/{model_name}_reference.jpg'
        
        if os.path.exists(reference_path):
            return cv2.imread(reference_path)
        else:
            logger.warning(f"Imagem de referência não encontrada: {reference_path}")
            return None
    
    def detect_defects(self, test_image, reference_image):
        """Detecta defeitos usando comparação de imagens"""
        if reference_image is None:
            return {
                'defects': [],
                'confidence': 0.0,
                'status': 'no_reference'
            }
        
        # Redimensiona imagens para o mesmo tamanho
        h, w = reference_image.shape[:2]
        test_resized = cv2.resize(test_image, (w, h))
        
        # Converte para grayscale
        ref_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
        test_gray = cv2.cvtColor(test_resized, cv2.COLOR_BGR2GRAY)
        
        # Calcula diferença absoluta
        diff = cv2.absdiff(ref_gray, test_gray)
        
        # Aplica threshold
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Encontra contornos de diferenças
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analisa cada contorno
        defects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filtra ruídos pequenos
                x, y, w, h = cv2.boundingRect(contour)
                defects.append({
                    'area': area,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'severity': 'high' if area > 1000 else 'medium' if area > 500 else 'low'
                })
        
        # Calcula confiança (inversamente proporcional aos defeitos encontrados)
        total_area = w * h
        defect_area = sum(d['area'] for d in defects)
        confidence = 1.0 - (defect_area / total_area)
        confidence = max(0.0, confidence)
        
        return {
            'defects': defects,
            'confidence': confidence,
            'status': 'approved' if confidence > self.config['threshold_confidence'] else 'rejected',
            'defect_count': len(defects)
        }
    
    def run_inspection(self):
        """Executa o processo completo de inspeção"""
        self.inspection_active = True
        logger.info("Iniciando inspeção...")
        
        try:
            # Acende LEDs
            self.set_led_brightness(self.config['led_brightness'])
            time.sleep(1)
            
            # Captura imagens em todas as posições
            images = []
            positions = self.config['inspection_positions']
            
            for i in range(positions):
                logger.info(f"Capturando posição {i+1}/{positions}")
                
                # Move para a posição
                step_angle = 360 // positions
                self.step_motor(step_angle * 2)  # 2 pulsos por grau (ajuste conforme motor)
                
                time.sleep(0.5)  # Aguarda estabilização
                
                # Captura imagem
                image_path = self.capture_image(i)
                if image_path:
                    images.append(image_path)
            
            # Carrega imagem de referência
            reference_image = self.load_reference_image('default_model')
            
            # Analisa todas as imagens
            all_results = []
            for i, image_path in enumerate(images):
                image = cv2.imread(image_path)
                if image is not None:
                    result = self.detect_defects(image, reference_image)
                    all_results.append({
                        'position': i,
                        'result': result
                    })
            
            # Consolida resultados
            total_confidence = sum(r['result']['confidence'] for r in all_results) / len(all_results)
            total_defects = sum(r['result']['defect_count'] for r in all_results)
            
            final_result = {
                'timestamp': time.time(),
                'positions_inspected': len(images),
                'average_confidence': total_confidence,
                'total_defects': total_defects,
                'status': 'approved' if total_confidence > self.config['threshold_confidence'] else 'rejected',
                'position_details': all_results
            }
            
            self.current_result = final_result
            self.last_inspection_time = time.time()
            
            logger.info(f"Inspeção concluída: {final_result['status']} (confiança: {total_confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Erro durante inspeção: {e}")
            self.current_result = {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
        
        finally:
            # Desliga LEDs
            self.set_led_brightness(0)
            self.inspection_active = False
    
    def run(self):
        """Inicia o servidor web"""
        logger.info("Iniciando Estação de Controle de Qualidade")
        logger.info("Dashboard disponível em: http://localhost:5000")
        self.app.run(host='0.0.0.0', port=5000, debug=False)
    
    def cleanup(self):
        """Limpa recursos"""
        self.app_running = False
        if hasattr(self, 'led_pwm'):
            self.led_pwm.stop()
        if hasattr(self, 'picam2'):
            self.picam2.stop()
        GPIO.cleanup()

def main():
    """Função principal"""
    try:
        estacao = EstacaoQC()
        estacao.run()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        if 'estacao' in locals():
            estacao.cleanup()

if __name__ == "__main__":
    main()
