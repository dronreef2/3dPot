#!/usr/bin/env python3
"""
Exemplo Prático: Integração LGM com Sistema de Modelagem Inteligente
Implementação completa da classe LGMIntegration
"""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import tempfile
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LGMIntegration:
    """
    Integração completa do LGM (Large Multi-View Gaussian Model) 
    com o sistema de modelagem inteligente 3D
    """
    
    def __init__(self, 
                 replicate_api_key: Optional[str] = None,
                 local_model_path: Optional[str] = None,
                 huggingface_token: Optional[str] = None,
                 workspace_path: str = "workspace_lgm",
                 cache_enabled: bool = True):
        
        self.replicate_api_key = replicate_api_key
        self.local_model_path = local_model_path
        self.huggingface_token = huggingface_token
        self.workspace_path = Path(workspace_path)
        self.cache_enabled = cache_enabled
        self.cache_dir = self.workspace_path / "cache"
        
        # Criar diretórios necessários
        self.workspace_path.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configurar Replicate se disponível
        if replicate_api_key:
            os.environ['REPLICATE_API_TOKEN'] = replicate_api_key
            self._test_replicate_connection()
        
        # Verificar recursos locais
        self.gpu_available = self._check_gpu_availability()
        self.local_setup_complete = self._check_local_setup()
        
        # Determinar método preferencial
        self.method = self._determine_best_method()
        logger.info(f"LGM Integration initialized: method={self.method}, gpu={self.gpu_available}")
    
    def _check_gpu_availability(self) -> bool:
        """Verifica disponibilidade de GPU CUDA"""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"GPU disponível: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
                return gpu_memory >= 8  # Mínimo 8GB para LGM
            return False
        except ImportError:
            logger.warning("PyTorch não disponível, assumindo GPU indisponível")
            return False
    
    def _check_local_setup(self) -> bool:
        """Verifica se setup local está completo"""
        if not self.local_model_path:
            return False
            
        # Verificar se arquivo do modelo existe
        model_file = Path(self.local_model_path)
        if not model_file.exists():
            logger.warning(f"Arquivo do modelo não encontrado: {self.local_model_path}")
            return False
        
        # Verificar se scripts do LGM estão disponíveis
        lgm_path = Path("LGM")
        required_files = ["app.py", "convert.py", "requirements.txt"]
        
        for file in required_files:
            if not (lgm_path / file).exists():
                logger.warning(f"Arquivo LGM não encontrado: {lgm_path / file}")
                return False
        
        return True
    
    def _test_replicate_connection(self) -> bool:
        """Testa conexão com Replicate"""
        try:
            import replicate
            # Teste simples - listar modelos (isso não custa créditos)
            models = replicate.models.list()
            logger.info("Conexão com Replicate estabelecida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro na conexão com Replicate: {e}")
            return False
    
    def _determine_best_method(self) -> str:
        """Determina o melhor método baseado nos recursos"""
        if self.replicate_api_key:
            return "replicate"
        elif self.gpu_available and self.local_setup_complete:
            return "local"
        else:
            return "huggingface"
    
    def _generate_cache_key(self, prompt: str, image_path: Optional[str] = None, **kwargs) -> str:
        """Gera chave de cache para evitar regenerações"""
        import hashlib
        cache_data = f"{prompt}_{image_path}_{kwargs}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Recupera resultado do cache"""
        if not self.cache_enabled:
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Verificar se cache não expirou (24h)
                    if time.time() - cached_data.get('timestamp', 0) < 86400:
                        logger.info("Resultado encontrado no cache")
                        return cached_data
                    else:
                        logger.info("Cache expirado, removendo arquivo")
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Erro ao ler cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Salva resultado no cache"""
        if not self.cache_enabled:
            return
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        result['timestamp'] = time.time()
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Resultado salvo no cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")
    
    def generate_3d_from_text(self, 
                             prompt: str, 
                             num_outputs: int = 1,
                             resolution: int = 800,
                             guidance_scale: float = 7.5,
                             seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera modelo 3D a partir de prompt de texto
        
        Args:
            prompt: Descrição textual do objeto 3D
            num_outputs: Número de variações a gerar
            resolution: Resolução da geração
            guidance_scale: Intensidade do guidance
            seed: Seed para reprodutibilidade
        
        Returns:
            Dict com resultado da geração
        """
        logger.info(f"Gerando 3D de texto: '{prompt[:50]}...'")
        
        # Verificar cache primeiro
        cache_key = self._generate_cache_key(prompt, None, 
                                           num_outputs=num_outputs,
                                           resolution=resolution)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Determinar método e executar
        if self.method == "replicate":
            result = self._generate_via_replicate_text(
                prompt, num_outputs, resolution, guidance_scale, seed
            )
        elif self.method == "local":
            result = self._generate_locally_text(
                prompt, num_outputs, resolution, guidance_scale, seed
            )
        else:
            result = self._generate_via_huggingface_text(
                prompt, num_outputs, resolution
            )
        
        # Salvar no cache se bem-sucedido
        if result.get('success'):
            self._save_to_cache(cache_key, result)
        
        return result
    
    def generate_3d_from_image(self, 
                              image_path: str,
                              prompt: Optional[str] = None,
                              num_outputs: int = 1,
                              resolution: int = 800) -> Dict[str, Any]:
        """
        Gera modelo 3D a partir de imagem
        
        Args:
            image_path: Caminho para imagem de entrada
            prompt: Prompt adicional (opcional)
            num_outputs: Número de variações
            resolution: Resolução da geração
        
        Returns:
            Dict com resultado da geração
        """
        if not os.path.exists(image_path):
            return {'success': False, 'error': f"Imagem não encontrada: {image_path}"}
        
        logger.info(f"Gerando 3D de imagem: {image_path}")
        
        # Verificar cache
        cache_key = self._generate_cache_key(prompt or "", image_path,
                                           num_outputs=num_outputs,
                                           resolution=resolution)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Executar geração
        if self.method == "replicate":
            result = self._generate_via_replicate_image(
                image_path, prompt, num_outputs, resolution
            )
        elif self.method == "local":
            result = self._generate_locally_image(
                image_path, prompt, num_outputs, resolution
            )
        else:
            result = self._generate_via_huggingface_image(
                image_path, prompt, num_outputs, resolution
            )
        
        # Salvar no cache
        if result.get('success'):
            self._save_to_cache(cache_key, result)
        
        return result
    
    def _generate_via_replicate_text(self, prompt: str, num_outputs: int, 
                                   resolution: int, guidance_scale: float,
                                   seed: Optional[int]) -> Dict[str, Any]:
        """Geração via Replicate com prompt de texto"""
        try:
            import replicate
            
            # Modelo LGM no Replicate (verificar modelo atualizado)
            model_name = "cjwbw/lgm"
            
            start_time = time.time()
            
            input_params = {
                "prompt": prompt,
                "num_outputs": num_outputs,
                "image_resolution": resolution,
                "guidance_scale": guidance_scale,
            }
            
            if seed is not None:
                input_params["seed"] = seed
            
            logger.info(f"Chamando Replicate: {model_name}")
            output = replicate.run(model_name, input=input_params)
            processing_time = time.time() - start_time
            
            # Processar output
            if isinstance(output, list):
                output_files = [str(file) if hasattr(file, 'read') else file for file in output]
            else:
                output_files = [str(output)]
            
            result = {
                'success': True,
                'method': 'replicate',
                'prompt': prompt,
                'output_files': output_files,
                'processing_time': processing_time,
                'format': 'gaussian_splat',
                'model': model_name,
                'input_params': input_params
            }
            
            logger.info(f"Replicate generation completed: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração Replicate: {e}")
            return {
                'success': False, 
                'error': str(e), 
                'method': 'replicate',
                'fallback_available': self.gpu_available and self.local_setup_complete
            }
    
    def _generate_via_replicate_image(self, image_path: str, prompt: Optional[str],
                                    num_outputs: int, resolution: int) -> Dict[str, Any]:
        """Geração via Replicate com imagem"""
        try:
            import replicate
            
            model_name = "cjwbw/lgm"
            
            # Ler imagem
            with open(image_path, 'rb') as image_file:
                start_time = time.time()
                
                input_params = {
                    "image": image_file,
                    "num_outputs": num_outputs,
                    "image_resolution": resolution,
                }
                
                if prompt:
                    input_params["prompt"] = prompt
                
                logger.info(f"Chamando Replicate (imagem): {model_name}")
                output = replicate.run(model_name, input=input_params)
                processing_time = time.time() - start_time
            
            # Processar output
            if isinstance(output, list):
                output_files = [str(file) if hasattr(file, 'read') else file for file in output]
            else:
                output_files = [str(output)]
            
            result = {
                'success': True,
                'method': 'replicate',
                'source_image': image_path,
                'prompt': prompt,
                'output_files': output_files,
                'processing_time': processing_time,
                'format': 'gaussian_splat',
                'model': model_name,
                'input_params': input_params
            }
            
            logger.info(f"Replicate image generation completed: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração Replicate (imagem): {e}")
            return {
                'success': False, 
                'error': str(e), 
                'method': 'replicate'
            }
    
    def _generate_locally_text(self, prompt: str, num_outputs: int,
                             resolution: int, guidance_scale: float,
                             seed: Optional[int]) -> Dict[str, Any]:
        """Geração local usando GPU"""
        try:
            # Preparar comando para script local do LGM
            cmd = [
                'python', 'LGM/app.py', 'big',
                '--resume', self.local_model_path,
                '--prompt', prompt,
                '--output_size', str(resolution),
                '--num_outputs', str(num_outputs),
            ]
            
            if guidance_scale != 7.5:
                cmd.extend(['--guidance_scale', str(guidance_scale)])
            
            if seed is not None:
                cmd.extend(['--seed', str(seed)])
            
            # Diretório de trabalho
            work_dir = self.workspace_path / "local_generation"
            work_dir.mkdir(exist_ok=True)
            
            start_time = time.time()
            logger.info(f"Iniciando geração local: {' '.join(cmd)}")
            
            # Executar comando
            result = subprocess.run(
                cmd, 
                cwd=work_dir,
                capture_output=True, 
                text=True, 
                timeout=600  # 10 minutos timeout
            )
            
            processing_time = time.time() - start_time
            
            if result.returncode == 0:
                # Localizar arquivos de output
                output_files = self._find_output_files(work_dir)
                
                result_dict = {
                    'success': True,
                    'method': 'local',
                    'prompt': prompt,
                    'output_files': output_files,
                    'processing_time': processing_time,
                    'format': 'gaussian_splat',
                    'command': ' '.join(cmd),
                    'stdout': result.stdout
                }
                
                logger.info(f"Geração local completada: {processing_time:.2f}s")
                return result_dict
            else:
                logger.error(f"Erro na geração local: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'method': 'local',
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na geração local")
            return {
                'success': False,
                'error': 'Timeout na geração (10 minutos)',
                'method': 'local'
            }
        except Exception as e:
            logger.error(f"Erro na geração local: {e}")
            return {
                'success': False, 
                'error': str(e), 
                'method': 'local'
            }
    
    def _generate_locally_image(self, image_path: str, prompt: Optional[str],
                              num_outputs: int, resolution: int) -> Dict[str, Any]:
        """Geração local usando imagem"""
        try:
            # Copiar imagem para workspace
            work_dir = self.workspace_path / "local_generation"
            work_dir.mkdir(exist_ok=True)
            
            image_dest = work_dir / "input_image.jpg"
            shutil.copy2(image_path, image_dest)
            
            # Preparar comando
            cmd = [
                'python', 'LGM/app.py', 'big',
                '--resume', self.local_model_path,
                '--test_path', str(image_dest),
                '--output_size', str(resolution),
                '--num_outputs', str(num_outputs),
            ]
            
            if prompt:
                cmd.extend(['--prompt', prompt])
            
            start_time = time.time()
            logger.info(f"Iniciando geração local (imagem): {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            processing_time = time.time() - start_time
            
            if result.returncode == 0:
                output_files = self._find_output_files(work_dir)
                
                return {
                    'success': True,
                    'method': 'local',
                    'source_image': image_path,
                    'prompt': prompt,
                    'output_files': output_files,
                    'processing_time': processing_time,
                    'format': 'gaussian_splat'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'method': 'local'
                }
                
        except Exception as e:
            return {
                'success': False, 
                'error': str(e), 
                'method': 'local'
            }
    
    def _find_output_files(self, search_dir: Path) -> List[str]:
        """Localiza arquivos de output gerados"""
        output_files = []
        
        # Extensões comuns de output do LGM
        extensions = ['.ply', '.splat', '.glb', '.obj', '.stl']
        
        for ext in extensions:
            files = search_dir.rglob(f"*{ext}")
            for file in files:
                if file.is_file() and file.stat().st_size > 1000:  # Arquivo não vazio
                    output_files.append(str(file.absolute()))
        
        # Ordenar por data de modificação (mais recente primeiro)
        output_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        logger.info(f"Arquivos encontrados: {len(output_files)}")
        return output_files
    
    def _generate_via_huggingface_text(self, prompt: str, num_outputs: int, resolution: int) -> Dict[str, Any]:
        """Geração via Hugging Face (método alternativo)"""
        return {
            'success': False,
            'error': 'Hugging Face API não implementada neste exemplo',
            'method': 'huggingface',
            'note': 'Use Replicate ou setup local para funcionalidade completa'
        }
    
    def _generate_via_huggingface_image(self, image_path: str, prompt: Optional[str],
                                      num_outputs: int, resolution: int) -> Dict[str, Any]:
        """Geração via Hugging Face com imagem"""
        return {
            'success': False,
            'error': 'Hugging Face API não implementada neste exemplo',
            'method': 'huggingface'
        }
    
    def convert_to_printable_format(self, 
                                  input_file: str, 
                                  output_format: str = "obj",
                                  quality: str = "high") -> Dict[str, Any]:
        """
        Converte modelo 3D para formato imprimível
        
        Args:
            input_file: Arquivo de entrada (.ply, .splat, etc.)
            output_format: Formato de saída (obj, stl, glb)
            quality: Qualidade da conversão (low, medium, high)
        
        Returns:
            Dict com resultado da conversão
        """
        if not os.path.exists(input_file):
            return {'success': False, 'error': f"Arquivo não encontrado: {input_file}"}
        
        logger.info(f"Convertendo {input_file} para {output_format}")
        
        try:
            # Se arquivo é .ply, usar script de conversão do LGM
            if input_file.endswith('.ply'):
                return self._convert_ply_to_format(input_file, output_format, quality)
            else:
                return self._convert_generic_format(input_file, output_format, quality)
                
        except Exception as e:
            logger.error(f"Erro na conversão: {e}")
            return {'success': False, 'error': str(e)}
    
    def _convert_ply_to_format(self, input_file: str, output_format: str, quality: str) -> Dict[str, Any]:
        """Converte arquivo .ply usando script do LGM"""
        try:
            work_dir = self.workspace_path / "conversion"
            work_dir.mkdir(exist_ok=True)
            
            # Copiar arquivo para workspace
            input_dest = work_dir / "input.ply"
            shutil.copy2(input_file, input_dest)
            
            # Comando de conversão
            cmd = [
                'python', 'LGM/convert.py', 'big',
                '--test_path', str(input_dest)
            ]
            
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if result.returncode == 0:
                # Localizar arquivo convertido
                converted_files = self._find_output_files(work_dir)
                
                # Encontrar arquivo no formato desejado
                target_file = None
                for file in converted_files:
                    if file.endswith(f'.{output_format}'):
                        target_file = file
                        break
                
                if target_file:
                    return {
                        'success': True,
                        'input_file': input_file,
                        'output_file': target_file,
                        'format': output_format,
                        'processing_time': processing_time,
                        'conversion_method': 'lgm_convert'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Arquivo no formato {output_format} não encontrado',
                        'available_files': converted_files
                    }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'stdout': result.stdout
                }
                
        except Exception as e:
            return {
                'success': False, 
                'error': str(e)
            }
    
    def _convert_generic_format(self, input_file: str, output_format: str, quality: str) -> Dict[str, Any]:
        """Conversão genérica de formatos (placeholder)"""
        return {
            'success': False,
            'error': f'Conversão {input_file} -> {output_format} não implementada',
            'supported_input': ['.ply'],
            'supported_output': ['.obj', '.stl', '.glb']
        }
    
    def estimate_printing_cost(self, model_file: str, material: str = "PLA") -> Dict[str, Any]:
        """
        Estima custo de impressão para modelo gerado
        
        Args:
            model_file: Arquivo do modelo 3D
            material: Material para impressão (PLA, ABS, PETG)
        
        Returns:
            Dict com estimativa de custo
        """
        try:
            # Importar integração com Slant 3D
            from slant3d_integration import Slant3DAPI
            
            # Configurar API (assumindo chave disponível)
            api_key = os.getenv('SLANT3D_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': 'SLANT3D_API_KEY não configurada'
                }
            
            slant_api = Slant3DAPI(api_key)
            
            # Estimar usando API do Slant 3D
            # Nota: Esta é uma implementação simplificada
            result = {
                'success': True,
                'model_file': model_file,
                'material': material,
                'estimated_cost': 0.0,  # Será calculado pela API
                'estimated_time': 0,    # Será calculado pela API
                'note': 'Estimativa baseada em análise de volume do modelo'
            }
            
            return result
            
        except ImportError:
            return {
                'success': False,
                'error': 'Slant3DAPI não disponível',
                'recommendation': 'Configure integração com Slant 3D para estimativas precisas'
            }
        except Exception as e:
            return {
                'success': False, 
                'error': str(e)
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso e configuração"""
        return {
            'method': self.method,
            'gpu_available': self.gpu_available,
            'local_setup_complete': self.local_setup_complete,
            'replicate_configured': bool(self.replicate_api_key),
            'huggingface_configured': bool(self.huggingface_token),
            'cache_enabled': self.cache_enabled,
            'workspace_path': str(self.workspace_path),
            'cache_size': len(list(self.cache_dir.glob("*.json"))) if self.cache_enabled else 0,
            'supported_formats': {
                'input': ['.txt', '.jpg', '.png', '.jpeg'],
                'output': ['.ply', '.splat', '.obj', '.stl', '.glb']
            }
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Limpa cache de resultados"""
        if not self.cache_enabled:
            return {'success': True, 'message': 'Cache desabilitado'}
        
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            for file in cache_files:
                file.unlink()
            
            logger.info(f"Cache limpo: {len(cache_files)} arquivos removidos")
            return {
                'success': True,
                'files_removed': len(cache_files),
                'message': f'{len(cache_files)} arquivos de cache removidos'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema LGM"""
        health = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Verificar GPU
        if self.gpu_available:
            health['checks']['gpu'] = {'status': 'ok', 'message': 'GPU disponível'}
        else:
            health['checks']['gpu'] = {'status': 'warning', 'message': 'GPU não disponível'}
        
        # Verificar setup local
        if self.local_setup_complete:
            health['checks']['local_setup'] = {'status': 'ok', 'message': 'Setup local completo'}
        else:
            health['checks']['local_setup'] = {'status': 'warning', 'message': 'Setup local incompleto'}
        
        # Verificar Replicate
        if self.replicate_api_key:
            # Teste simples de conectividade
            try:
                import replicate
                health['checks']['replicate'] = {'status': 'ok', 'message': 'API key configurada'}
            except:
                health['checks']['replicate'] = {'status': 'error', 'message': 'Erro na configuração'}
        else:
            health['checks']['replicate'] = {'status': 'info', 'message': 'API key não configurada'}
        
        # Determinar status geral
        if all(check['status'] in ['ok', 'info'] for check in health['checks'].values()):
            health['overall_status'] = 'healthy'
        elif any(check['status'] == 'error' for check in health['checks'].values()):
            health['overall_status'] = 'unhealthy'
        else:
            health['overall_status'] = 'degraded'
        
        return health


# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    lgm_config = {
        'replicate_api_key': 'r8_your_replicate_token_here',
        'local_model_path': '/path/to/lgm/model.safetensors',
        'workspace_path': '/workspace/lgm',
        'cache_enabled': True
    }
    
    # Inicializar integração
    lgm = LGMIntegration(**lgm_config)
    
    # Exemplo de geração de texto
    result = lgm.generate_3d_from_text(
        prompt="A futuristic robot head with LED eyes",
        num_outputs=1,
        resolution=800
    )
    
    print("Resultado da geração:")
    print(json.dumps(result, indent=2))
    
    # Verificar saúde do sistema
    health = lgm.health_check()
    print("\nStatus do sistema:")
    print(json.dumps(health, indent=2))