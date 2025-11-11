# 3dPot v2.0 - Sistema de Autenticação JWT OAuth2

## 🔐 Implementação Completa do Sprint 1

Este documento descreve o sistema de autenticação robusto implementado no Sprint 1, incluindo JWT OAuth2 completo, refresh tokens, rate limiting e segurança avançada.

## 📋 Funcionalidades Implementadas

### ✅ Sistema Completo de Autenticação
- **Registro de usuários** com validação de senha forte
- **Login/Logout** com tokens JWT
- **Refresh tokens** para renovação automática
- **Gerenciamento de sessões** múltiplas
- **Reset de senha** com tokens temporários
- **Verificação de email** (estrutura preparada)
- **Rate limiting** para prevenção de ataques
- **Bloqueio automático** por tentativas falhadas
- **Audit logging** completo

### ✅ Segurança Avançada
- **Hash de senhas** com bcrypt
- **Tokens JWT** assinados com chave secreta
- **Validação de força** de senha configurável
- **Proteção CSRF** e CORS configurado
- **Rate limiting** por IP e usuário
- **Logs de auditoria** para rastreabilidade
- **Soft delete** de usuários
- **Bloqueio temporário** de contas

### ✅ Middleware e Proteção
- **Middleware de autenticação** automático
- **Dependências protegidas** para rotas
- **Verificação de permissões** por role
- **Rate limiting middleware** configurável
- **CORS configurado** para desenvolvimento

## 🏗️ Arquitetura do Sistema

### 📁 Estrutura de Arquivos

```
backend/
├── core/
│   └── config.py              # Configurações robustas
├── models/
│   └── __init__.py           # Modelos User + RefreshToken
├── schemas/
│   └── __init__.py           # Schemas de autenticação
├── services/
│   └── auth_service.py       # Serviço principal de auth
├── middleware/
│   └── auth.py               # Middleware e dependências
├── routes/
│   └── auth.py               # Rotas de autenticação
├── database.py               # Configuração do banco
├── main.py                   # Aplicação principal
├── requirements.txt          # Dependências
└── .env.example             # Variáveis de ambiente
```

### 🔄 Fluxo de Autenticação

```mermaid
graph TD
    A[Usuário] -->|POST /register| B[Registro]
    A -->|POST /login| C[Login]
    C -->|Credenciais válidas| D[Geração JWT]
    C -->|Credenciais inválidas| E[Rate Limiting]
    D -->|Access + Refresh Token| F[Usuário Logado]
    F -->|Refresh Token| G[Renovação Automática]
    F -->|Logout| H[Revogação de Tokens]
    I[Serviços Protegidos] -->|Bearer Token| J[Middleware Auth]
    J -->|Token Válido| K[Usuário Autenticado]
    J -->|Token Inválido| L[Erro 401]
```

## 🚀 Como Usar

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone <repository-url>
cd 3dPot

# Configure as variáveis de ambiente
cp backend/.env.example .env
# Edite .env com suas configurações

# Inicie o ambiente
./start-sprint1.sh
```

### 2. Registro de Usuário

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "username": "meuusuario",
    "full_name": "Meu Nome Completo",
    "password": "MinhaSenh@123",
    "company": "Minha Empresa",
    "website": "https://meusite.com"
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "meuusuario",
    "password": "MinhaSenh@123",
    "remember_me": false,
    "device_info": {
      "device_type": "web",
      "browser": "Chrome",
      "os": "Windows"
    }
  }'
```

**Resposta:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "a1b2c3d4e5f6...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid-do-usuario",
      "email": "usuario@exemplo.com",
      "username": "meuusuario",
      "role": "user",
      "is_active": true,
      "is_verified": false
    }
  }
}
```

### 4. Acesso a Rotas Protegidas

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5. Renovação de Tokens

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "a1b2c3d4e5f6..."
  }'
```

### 6. Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "a1b2c3d4e5f6..."
  }'
```

## 🔒 Endpoints Disponíveis

### Autenticação
| Método | Endpoint | Descrição | Protegido |
|--------|----------|-----------|-----------|
| POST | `/api/v1/auth/register` | Registro de usuário | ❌ |
| POST | `/api/v1/auth/login` | Login | ❌ |
| POST | `/api/v1/auth/refresh` | Renovar tokens | ❌ |
| POST | `/api/v1/auth/logout` | Logout | ✅ |
| POST | `/api/v1/auth/logout-all` | Logout todas sessões | ✅ |
| GET | `/api/v1/auth/profile` | Perfil do usuário | ✅ |
| PUT | `/api/v1/auth/profile` | Atualizar perfil | ✅ |

### Gerenciamento de Senha
| Método | Endpoint | Descrição | Protegido |
|--------|----------|-----------|-----------|
| POST | `/api/v1/auth/reset-password` | Solicitar reset | ❌ |
| POST | `/api/v1/auth/reset-password/confirm` | Confirmar reset | ❌ |
| POST | `/api/v1/auth/change-password` | Trocar senha | ✅ |

### Sessões
| Método | Endpoint | Descrição | Protegido |
|--------|----------|-----------|-----------|
| GET | `/api/v1/auth/sessions` | Listar sessões | ✅ |
| DELETE | `/api/v1/auth/sessions/{id}` | Revogar sessão | ✅ |

### Utilitários
| Método | Endpoint | Descrição | Protegido |
|--------|----------|-----------|-----------|
| GET | `/api/v1/auth/token/verify` | Verificar token | ❌ |
| GET | `/api/v1/auth/health` | Health check | ❌ |

## 🛡️ Configurações de Segurança

### Políticas de Senha
```python
# Configurações em .env
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
```

### Rate Limiting
```python
# Configurações em .env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### JWT
```python
# Configurações em .env
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SECRET_KEY=your-super-secret-key-change-in-production-must-be-32-chars-minimum
```

## 🔍 Uso no Frontend (React)

### Service de Autenticação

```typescript
// services/authService.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

class AuthService {
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await axios.post(`${API_BASE}/auth/register`, userData);
    return response.data;
  }

  async login(credentials: LoginData): Promise<AuthResponse> {
    const response = await axios.post(`${API_BASE}/auth/login`, credentials);
    if (response.data.success) {
      this.setTokens(response.data.data);
    }
    return response.data;
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    const response = await axios.post(`${API_BASE}/auth/refresh`, {
      refresh_token: refreshToken
    });
    if (response.data.success) {
      this.setTokens(response.data.data);
    }
    return response.data;
  }

  setTokens(data: any) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }
}

export default new AuthService();
```

### Protected Route Component

```typescript
// components/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = authService.getAccessToken();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

export default ProtectedRoute;
```

## 🧪 Testes do Sistema

### Teste Básico de Autenticação

```bash
# 1. Registrar usuário
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"TestPass123!"}'

# 2. Fazer login
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123!"}')

# Extrair token da resposta
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.data.access_token')

# 3. Acessar rota protegida
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Health Check

```bash
# Verificar se todos os serviços estão rodando
curl http://localhost:8000/api/v1/auth/health
curl http://localhost:3000
curl http://localhost:9000/minio/health/live
```

## 📊 Monitoramento

### Logs de Autenticação
```bash
# Ver logs do backend
docker-compose -f docker-compose.dev.yml logs -f backend

# Ver logs específicos de autenticação
docker-compose -f docker-compose.dev.yml logs -f backend | grep "AUTH_"
```

### Métricas
- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   ```bash
   docker-compose -f docker-compose.dev.yml restart postgres
   ```

2. **Tokens não válidos**
   - Verificar se SECRET_KEY está configurada no .env
   - Verificar se tokens não expiraram

3. **Rate limiting ativado**
   - Aguardar tempo limite (60 minutos)
   - Verificar logs para mais detalhes

4. **CORS errors**
   - Verificar FRONTEND_URL no .env
   - Configurar CORS corretamente

### Comandos de Debug

```bash
# Verificar status dos containers
docker-compose -f docker-compose.dev.yml ps

# Verificar logs de erro
docker-compose -f docker-compose.dev.yml logs --tail=50

# Conectar ao banco
docker-compose -f docker-compose.dev.yml exec postgres psql -U 3dpot -d 3dpot_dev

# Verificar redes Docker
docker network ls
docker network inspect 3dpot-3dpot-network
```

## 🎯 Próximos Passos

1. **Integração com Minimax M2 API** (Sprint 2)
2. **Interface conversacional** no frontend (Sprint 2)
3. **Sistema de projetos** completo (Sprint 3)
4. **Modelagem 3D** automatizada (Sprint 4)
5. **Simulação PyBullet** (Sprint 5)
6. **Orçamentação automática** (Sprint 6)

## 📚 Documentação Técnica

### Estrutura do JWT
```json
{
  "sub": "uuid-do-usuario",
  "username": "meuusuario",
  "email": "usuario@exemplo.com",
  "role": "user",
  "type": "access",
  "iat": 1634567890,
  "exp": 1634568690,
  "jti": "uuid-unico-do-token"
}
```

### Modelo User (Banco)
```python
class User(Base):
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum('user', 'premium', 'admin'))
    
    # Auth fields
    refresh_tokens = Column(JSON, default=list)
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

---

## ✅ Status da Implementação

- ✅ **Docker Compose** configurado para desenvolvimento
- ✅ **Sistema JWT OAuth2** completo implementado
- ✅ **Rate limiting** e segurança implementados
- ✅ **Refresh tokens** com rotação automática
- ✅ **Gerenciamento de sessões** múltiplas
- ✅ **Reset de senha** funcional
- ✅ **Middleware de proteção** configurado
- ✅ **Documentação completa** e exemplos
- ✅ **Testes básicos** implementados

**Sprint 1 Status: ✅ CONCLUÍDO**

A base sólida de autenticação está pronta para suportar as funcionalidades avançadas dos próximos sprints!