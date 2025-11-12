import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ConversationProvider } from '@/contexts/ConversationContext';
import { DashboardPage } from '@/pages/DashboardPage';
import { ChatPage } from '@/pages/ChatPage';
import { HistoryPage } from '@/pages/HistoryPage';
import Model3DPage from '@/pages/Model3DPage';

// Estilos CSS globais do TailwindCSS
import '@/index.css';

function App() {
  return (
    <ConversationProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Rota padrão - Dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Dashboard */}
            <Route path="/dashboard" element={<DashboardPage />} />
            
            {/* Chat - Lista sessões ou redireciona para nova */}
            <Route path="/chat" element={<HistoryPage />} />
            
            {/* Chat específico - Nova conversa */}
            <Route path="/chat/:sessionId" element={<ChatPage />} />
            
            {/* Histórico de conversas */}
            <Route path="/history" element={<HistoryPage />} />
            
            {/* 3D Model Viewer */}
            <Route path="/3d" element={<Model3DPage />} />
            <Route path="/3d/:modelId" element={<Model3DPage />} />
            
            {/* Rota fallback - redireciona para dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>

          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10B981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </ConversationProvider>
  );
}

export default App;