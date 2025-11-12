"""
Exemplo de uso do WebSocket para dispositivos IoT
Sistema de Prototipagem Sob Demanda
"""

import asyncio
import json
import websockets
from datetime import datetime


class IoTDeviceSimulator:
    """Simulador de dispositivo IoT para testar WebSocket"""
    
    def __init__(self, device_id: str, device_type: str = "ESP32"):
        self.device_id = device_id
        self.device_type = device_type
        self.websocket = None
        self.connected = False
    
    async def connect(self, ws_url: str = "ws://localhost:8000/ws/connect"):
        """Conecta ao servidor WebSocket"""
        try:
            # Parâmetros de query para identificação
            query_params = f"?device_id={self.device_id}"
            full_url = ws_url + query_params
            
            print(f"🔌 Conectando dispositivo {self.device_id} a {full_url}")
            
            self.websocket = await websockets.connect(full_url)
            self.connected = True
            
            # Envia mensagem de conexão
            await self.send_message({
                "type": "device_connect",
                "data": {
                    "device_id": self.device_id,
                    "device_type": self.device_type,
                    "serial_number": f"{self.device_type}-{self.device_id}",
                    "capabilities": ["temperature", "humidity", "pressure"],
                    "firmware_version": "1.0.0"
                }
            })
            
            print(f"✅ Dispositivo {self.device_id} conectado com sucesso!")
            
            # Inicia tarefas de background
            asyncio.create_task(self.send_sensor_data())
            asyncio.create_task(self.listen_messages())
            asyncio.create_task(self.keepalive())
            
        except Exception as e:
            print(f"❌ Erro ao conectar dispositivo {self.device_id}: {e}")
    
    async def send_message(self, message: dict):
        """Envia mensagem via WebSocket"""
        if self.connected and self.websocket:
            await self.websocket.send(json.dumps(message))
            print(f"📤 [{self.device_id}] Enviado: {message['type']}")
    
    async def send_sensor_data(self):
        """Envia dados de sensores periodicamente"""
        sensor_data = [
            {"sensor_type": "temperature", "value": 22.5, "unit": "celsius"},
            {"sensor_type": "humidity", "value": 45.0, "unit": "%"},
            {"sensor_type": "pressure", "value": 1013.25, "unit": "hPa"}
        ]
        
        while self.connected:
            try:
                for sensor in sensor_data:
                    data_message = {
                        "type": "sensor_data",
                        "data": {
                            "device_id": self.device_id,
                            **sensor,
                            "timestamp": datetime.utcnow().isoformat(),
                            "quality": "high"
                        }
                    }
                    await self.send_message(data_message)
                    await asyncio.sleep(5)  # Envia a cada 5 segundos
                    
            except Exception as e:
                print(f"❌ Erro ao enviar dados de sensor: {e}")
                await asyncio.sleep(5)
    
    async def listen_messages(self):
        """Escuta mensagens do servidor"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_server_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Mensagem inválida recebida: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Conexão fechada para dispositivo {self.device_id}")
            self.connected = False
        except Exception as e:
            print(f"❌ Erro ao escutar mensagens: {e}")
    
    async def handle_server_message(self, message: dict):
        """Processa mensagens recebidas do servidor"""
        message_type = message.get("type")
        data = message.get("data", {})
        
        if message_type == "connection_established":
            print(f"✅ [{self.device_id}] Conexão estabelecida: {data.get('connection_id')}")
            
        elif message_type == "success":
            print(f"✅ [{self.device_id}] Sucesso: {data.get('message')}")
            
        elif message_type == "error":
            print(f"❌ [{self.device_id}] Erro: {data.get('message')}")
            
        elif message_type == "device_command":
            command = data.get("command")
            parameters = data.get("parameters", {})
            print(f"📋 [{self.device_id}] Comando recebido: {command} com parâmetros {parameters}")
            
            # Simula execução de comando
            await asyncio.sleep(1)
            
            result_message = {
                "type": "command_result",
                "data": {
                    "command": command,
                    "result": {"status": "completed", "duration": 1.0}
                }
            }
            await self.send_message(result_message)
            
        elif message_type == "heartbeat":
            print(f"💓 [{self.device_id}] Heartbeat recebido")
            
        elif message_type == "firmware_update_available":
            print(f"🔄 [{self.device_id}] Atualização de firmware disponível: {data}")
            
        else:
            print(f"📨 [{self.device_id}] Mensagem recebida: {message_type} - {data}")
    
    async def keepalive(self):
        """Envia keepalive periodicamente"""
        while self.connected:
            try:
                await asyncio.sleep(30)  # A cada 30 segundos
                await self.send_message({
                    "type": "keepalive",
                    "data": {
                        "device_id": self.device_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            except Exception as e:
                print(f"❌ Erro ao enviar keepalive: {e}")
    
    async def disconnect(self):
        """Desconecta do servidor"""
        if self.connected:
            await self.send_message({
                "type": "device_disconnect",
                "data": {"device_id": self.device_id}
            })
            
            await self.websocket.close()
            self.connected = False
            print(f"🔌 Dispositivo {self.device_id} desconectado")


class DashboardClient:
    """Cliente do dashboard para receber atualizações"""
    
    def __init__(self, user_id: str = "dashboard"):
        self.user_id = user_id
        self.websocket = None
        self.connected = False
    
    async def connect(self, ws_url: str = "ws://localhost:8000/ws/connect"):
        """Conecta ao servidor WebSocket"""
        try:
            query_params = f"?user_id={self.user_id}"
            full_url = ws_url + query_params
            
            print(f"🖥️ Conectando dashboard como {self.user_id}")
            
            self.websocket = await websockets.connect(full_url)
            self.connected = True
            
            # Inscreve para atualizações de dispositivos
            await self.send_message({
                "type": "subscribe_device",
                "data": {"device_id": "ESP32-001"}
            })
            
            print(f"✅ Dashboard conectado como {self.user_id}")
            
            # Escuta mensagens
            await self.listen_messages()
            
        except Exception as e:
            print(f"❌ Erro ao conectar dashboard: {e}")
    
    async def send_message(self, message: dict):
        """Envia mensagem via WebSocket"""
        if self.connected and self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def listen_messages(self):
        """Escuta mensagens do servidor"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_server_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Mensagem inválida: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Dashboard desconectado")
            self.connected = False
        except Exception as e:
            print(f"❌ Erro ao escutar mensagens: {e}")
    
    async def handle_server_message(self, message: dict):
        """Processa mensagens do servidor"""
        message_type = message.get("type")
        data = message.get("data", {})
        
        if message_type == "sensor_data":
            device_id = data.get("device_id")
            sensor_type = data.get("sensor_type")
            value = data.get("value")
            unit = data.get("unit")
            
            print(f"📊 [{device_id}] {sensor_type}: {value}{unit}")
            
        elif message_type == "device_status_update":
            device_id = data.get("device_id")
            status = data.get("status")
            battery = data.get("battery_level")
            
            print(f"📡 [{device_id}] Status: {status}, Bateria: {battery}%")
            
        elif message_type == "device_alert":
            device_id = data.get("device_id")
            alert_type = data.get("alert_type")
            severity = data.get("severity")
            
            print(f"🚨 [{device_id}] Alerta {severity}: {alert_type}")
            
        elif message_type == "system_alert":
            title = data.get("title")
            severity = data.get("severity")
            
            print(f"⚠️ Sistema {severidade}: {title}")
            
        else:
            print(f"📨 Dashboard recebeu: {message_type}")


async def test_websocket_communication():
    """Teste completo de comunicação WebSocket"""
    
    print("🧪 Iniciando teste de comunicação WebSocket...")
    print("=" * 60)
    
    # Cria dispositivos
    devices = [
        IoTDeviceSimulator("ESP32-001"),
        IoTDeviceSimulator("ESP32-002"),
    ]
    
    # Cria dashboard
    dashboard = DashboardClient("operator-123")
    
    try:
        # Conecta dispositivos
        device_tasks = []
        for device in devices:
            task = asyncio.create_task(device.connect())
            device_tasks.append(task)
        
        # Conecta dashboard
        dashboard_task = asyncio.create_task(dashboard.connect())
        
        # Aguarda conexões
        await asyncio.sleep(2)
        
        print("\n📊 Testando comandos de dispositivo...")
        
        # Simula envio de comando para dispositivo
        if devices[0].connected:
            await devices[0].send_message({
                "type": "device_command",
                "data": {
                    "device_id": "ESP32-001",
                    "command": "calibrate",
                    "parameters": {"sensors": ["temperature", "humidity"]}
                }
            })
        
        print("\n⏳ Aguardando comunicação por 30 segundos...")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    finally:
        # Desconecta todos
        print("\n🔌 Desconectando dispositivos...")
        for device in devices:
            await device.disconnect()
        
        if dashboard.connected:
            await dashboard.websocket.close()
        
        print("✅ Teste concluído")


async def test_specific_features():
    """Teste de funcionalidades específicas"""
    
    print("🎯 Testando funcionalidades específicas...")
    print("=" * 60)
    
    device = IoTDeviceSimulator("ESP32-TEST")
    
    try:
        await device.connect()
        await asyncio.sleep(2)
        
        # Testa calibração
        print("\n🔧 Testando calibração...")
        await device.send_message({
            "type": "calibration",
            "data": {
                "device_id": "ESP32-TEST",
                "calibration_data": {
                    "temperature": {"offset": 0.5, "scale": 1.0},
                    "humidity": {"offset": -1.0, "scale": 0.95}
                }
            }
        })
        
        # Testa atualização de firmware
        print("\n🔄 Testando atualização de firmware...")
        await device.send_message({
            "type": "firmware_update",
            "data": {
                "device_id": "ESP32-TEST",
                "firmware_version": "1.0.0"
            }
        })
        
        # Testa status update
        print("\n📡 Testando atualização de status...")
        await device.send_message({
            "type": "device_status",
            "data": {
                "device_id": "ESP32-TEST",
                "status": "maintenance",
                "battery_level": 15,
                "signal_strength": -75
            }
        })
        
        await asyncio.sleep(10)
        
    finally:
        await device.disconnect()


if __name__ == "__main__":
    print("🚀 Sistema de Prototipagem - Teste WebSocket")
    print("=" * 60)
    print("Selecione o teste:")
    print("1. Teste completo de comunicação")
    print("2. Teste de funcionalidades específicas")
    print("3. Apenas simulação de dispositivo")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_websocket_communication())
    elif choice == "2":
        asyncio.run(test_specific_features())
    elif choice == "3":
        device = IoTDeviceSimulator("ESP32-DEMO")
        asyncio.run(device.connect())
    else:
        print("❌ Opção inválida")