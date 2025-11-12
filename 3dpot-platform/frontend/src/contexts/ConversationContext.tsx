import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { Message, ConversationSession, ConversationResponse, ExtractedSpecs } from '@/types';
import { generateId } from '@/utils/helpers';

interface ConversationState {
  sessions: ConversationSession[];
  currentSessionId: string | null;
  messages: Record<string, Message[]>;
  isConnected: boolean;
  isTyping: boolean;
  currentMessage: string;
  extractedSpecs: ExtractedSpecs | null;
  confidence: number;
  error: string | null;
  loading: boolean;
}

type ConversationAction =
  | { type: 'SET_SESSIONS'; payload: ConversationSession[] }
  | { type: 'SET_CURRENT_SESSION'; payload: string }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'ADD_AGENT_RESPONSE'; payload: { sessionId: string; response: ConversationResponse } }
  | { type: 'SET_CONNECTION_STATUS'; payload: boolean }
  | { type: 'SET_TYPING'; payload: boolean }
  | { type: 'SET_CURRENT_MESSAGE'; payload: string }
  | { type: 'SET_EXTRACTED_SPECS'; payload: { specs: ExtractedSpecs; confidence: number } }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'CLEAR_SESSION'; payload: string }
  | { type: 'RESET_CONVERSATION' };

const initialState: ConversationState = {
  sessions: [],
  currentSessionId: null,
  messages: {},
  isConnected: false,
  isTyping: false,
  currentMessage: '',
  extractedSpecs: null,
  confidence: 0,
  error: null,
  loading: false,
};

function conversationReducer(state: ConversationState, action: ConversationAction): ConversationState {
  switch (action.type) {
    case 'SET_SESSIONS':
      return { ...state, sessions: action.payload };

    case 'SET_CURRENT_SESSION':
      return { ...state, currentSessionId: action.payload };

    case 'ADD_MESSAGE':
      const { sessionId, ...messageData } = action.payload;
      return {
        ...state,
        messages: {
          ...state.messages,
          [sessionId]: [...(state.messages[sessionId] || []), action.payload],
        },
      };

    case 'ADD_AGENT_RESPONSE':
      const { sessionId: responseSessionId, response } = action.payload;
      const agentMessage: Message = {
        id: generateId(),
        content: response.response,
        timestamp: response.timestamp,
        isUser: false,
        sessionId: responseSessionId,
        extractedSpecs: response.extractedSpecs,
        confidence: response.confidence,
      };

      return {
        ...state,
        messages: {
          ...state.messages,
          [responseSessionId]: [...(state.messages[responseSessionId] || []), agentMessage],
        },
        isTyping: false,
        extractedSpecs: response.extractedSpecs,
        confidence: response.confidence,
      };

    case 'SET_CONNECTION_STATUS':
      return { ...state, isConnected: action.payload };

    case 'SET_TYPING':
      return { ...state, isTyping: action.payload };

    case 'SET_CURRENT_MESSAGE':
      return { ...state, currentMessage: action.payload };

    case 'SET_EXTRACTED_SPECS':
      return {
        ...state,
        extractedSpecs: action.payload.specs,
        confidence: action.payload.confidence,
      };

    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };

    case 'SET_LOADING':
      return { ...state, loading: action.payload };

    case 'CLEAR_SESSION':
      const { [action.payload]: removedSession, ...remainingMessages } = state.messages;
      return {
        ...state,
        messages: remainingMessages,
        currentSessionId: state.currentSessionId === action.payload ? null : state.currentSessionId,
      };

    case 'RESET_CONVERSATION':
      return {
        ...initialState,
        sessions: state.sessions,
        isConnected: state.isConnected,
      };

    default:
      return state;
  }
}

interface ConversationContextType {
  state: ConversationState;
  dispatch: React.Dispatch<ConversationAction>;
  
  // Actions
  setSessions: (sessions: ConversationSession[]) => void;
  setCurrentSession: (sessionId: string) => void;
  addUserMessage: (content: string) => void;
  addAgentResponse: (sessionId: string, response: ConversationResponse) => void;
  setConnectionStatus: (connected: boolean) => void;
  setTyping: (typing: boolean) => void;
  setCurrentMessage: (message: string) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  clearSession: (sessionId: string) => void;
  resetConversation: () => void;
  
  // Getters
  getCurrentMessages: () => Message[];
  getCurrentSession: () => ConversationSession | null;
  hasActiveSession: () => boolean;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export function ConversationProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, initialState);

  // Actions
  const setSessions = useCallback((sessions: ConversationSession[]) => {
    dispatch({ type: 'SET_SESSIONS', payload: sessions });
  }, []);

  const setCurrentSession = useCallback((sessionId: string) => {
    dispatch({ type: 'SET_CURRENT_SESSION', payload: sessionId });
  }, []);

  const addUserMessage = useCallback((content: string) => {
    if (!state.currentSessionId) return;

    const userMessage: Message = {
      id: generateId(),
      content,
      timestamp: new Date().toISOString(),
      isUser: true,
      sessionId: state.currentSessionId,
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_CURRENT_MESSAGE', payload: '' });
    dispatch({ type: 'SET_TYPING', payload: true });
  }, [state.currentSessionId]);

  const addAgentResponse = useCallback((sessionId: string, response: ConversationResponse) => {
    dispatch({ type: 'ADD_AGENT_RESPONSE', payload: { sessionId, response } });
  }, []);

  const setConnectionStatus = useCallback((connected: boolean) => {
    dispatch({ type: 'SET_CONNECTION_STATUS', payload: connected });
  }, []);

  const setTyping = useCallback((typing: boolean) => {
    dispatch({ type: 'SET_TYPING', payload: typing });
  }, []);

  const setCurrentMessage = useCallback((message: string) => {
    dispatch({ type: 'SET_CURRENT_MESSAGE', payload: message });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const clearSession = useCallback((sessionId: string) => {
    dispatch({ type: 'CLEAR_SESSION', payload: sessionId });
  }, []);

  const resetConversation = useCallback(() => {
    dispatch({ type: 'RESET_CONVERSATION' });
  }, []);

  // Getters
  const getCurrentMessages = useCallback((): Message[] => {
    if (!state.currentSessionId) return [];
    return state.messages[state.currentSessionId] || [];
  }, [state.currentSessionId, state.messages]);

  const getCurrentSession = useCallback((): ConversationSession | null => {
    return state.sessions.find(s => s.sessionId === state.currentSessionId) || null;
  }, [state.sessions, state.currentSessionId]);

  const hasActiveSession = useCallback((): boolean => {
    return state.currentSessionId !== null;
  }, [state.currentSessionId]);

  const value: ConversationContextType = {
    state,
    dispatch,
    setSessions,
    setCurrentSession,
    addUserMessage,
    addAgentResponse,
    setConnectionStatus,
    setTyping,
    setCurrentMessage,
    setError,
    setLoading,
    clearSession,
    resetConversation,
    getCurrentMessages,
    getCurrentSession,
    hasActiveSession,
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation(): ConversationContextType {
  const context = useContext(ConversationContext);
  if (context === undefined) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
}