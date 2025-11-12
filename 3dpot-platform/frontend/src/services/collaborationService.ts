// Sprint 6+: Collaboration Service
// Serviço completo para colaboração em tempo real

import { io, Socket } from 'socket.io-client';
import SimplePeer from 'simple-peer';
import toast from 'react-hot-toast';
import { EventEmitter } from 'events';

// Types
import type {
  CollaborativeSession,
  SessionParticipant,
  CollaborationEvent,
  Comment,
  VersionControl,
  WebRTCConnection,
  ChangeSuggestion,
  UserProfile
} from '@/types/collaboration';

interface CollaborationServiceConfig {
  apiUrl: string;
  wsUrl: string;
  maxParticipants: number;
  sessionTimeout: number;
  enableVoiceChat: boolean;
  enableVideoChat: boolean;
  enableScreenShare: boolean;
  enableFileSharing: boolean;
}

interface PeerConnectionData {
  peer: SimplePeer.Instance;
  userId: string;
  connectionId: string;
  mediaStream?: MediaStream;
  dataChannel?: RTCDataChannel;
  status: 'connecting' | 'connected' | 'disconnected' | 'failed';
}

export class CollaborationService extends EventEmitter {
  private config: CollaborationServiceConfig;
  private socket: Socket | null = null;
  private currentSession: CollaborativeSession | null = null;
  private currentUser: SessionParticipant | null = null;
  private participants: Map<string, SessionParticipant> = new Map();
  private comments: Map<string, Comment> = new Map();
  private versionHistory: VersionControl[] = [];
  private peerConnections: Map<string, PeerConnectionData> = new Map();
  private mediaStream: MediaStream | null = null;
  private screenShareStream: MediaStream | null = null;
  private isConnected = false;
  private sessionTimeout: NodeJS.Timeout | null = null;

  constructor(config: CollaborationServiceConfig) {
    super();
    this.config = {
      maxParticipants: 20,
      sessionTimeout: 2 * 60 * 60 * 1000, // 2 hours
      enableVoiceChat: true,
      enableVideoChat: true,
      enableScreenShare: true,
      enableFileSharing: true,
      ...config
    };
    this.initializeConnection();
  }

  private async initializeConnection() {
    try {
      await this.connectSocket();
      console.log('🔌 Collaboration service connected');
    } catch (error) {
      console.error('❌ Failed to connect collaboration service:', error);
      this.reconnectSocket();
    }
  }

  private async connectSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(`${this.config.wsUrl}/collaboration`, {
          transports: ['websocket'],
          timeout: 10000
        });

        this.socket.on('connect', () => {
          this.isConnected = true;
          this.emit('connected');
          resolve();
        });

        this.socket.on('disconnect', () => {
          this.isConnected = false;
          this.emit('disconnected');
          this.handleDisconnection();
        });

        this.socket.on('session_joined', (session: CollaborativeSession) => {
          this.handleSessionJoined(session);
        });

        this.socket.on('user_joined', (user: SessionParticipant) => {
          this.handleUserJoined(user);
        });

        this.socket.on('user_left', (userId: string) => {
          this.handleUserLeft(userId);
        });

        this.socket.on('participant_updated', (participant: SessionParticipant) => {
          this.handleParticipantUpdated(participant);
        });

        this.socket.on('collaboration_event', (event: CollaborationEvent) => {
          this.handleCollaborationEvent(event);
        });

        this.socket.on('comment_added', (comment: Comment) => {
          this.handleCommentAdded(comment);
        });

        this.socket.on('comment_updated', (comment: Comment) => {
          this.handleCommentUpdated(comment);
        });

        this.socket.on('comment_deleted', (commentId: string) => {
          this.handleCommentDeleted(commentId);
        });

        this.socket.on('version_created', (version: VersionControl) => {
          this.handleVersionCreated(version);
        });

        this.socket.on('suggestion_added', (suggestion: ChangeSuggestion) => {
          this.handleSuggestionAdded(suggestion);
        });

        this.socket.on('suggestion_updated', (suggestion: ChangeSuggestion) => {
          this.handleSuggestionUpdated(suggestion);
        });

        this.socket.on('webrtc_offer', (data: any) => {
          this.handleWebRTCOffer(data);
        });

        this.socket.on('webrtc_answer', (data: any) => {
          this.handleWebRTCAnswer(data);
        });

        this.socket.on('webrtc_ice_candidate', (data: any) => {
          this.handleWebRTCIceCandidate(data);
        });

        this.socket.on('error', (error: any) => {
          console.error('Socket error:', error);
          this.emit('error', error);
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  private reconnectSocket() {
    setTimeout(() => {
      console.log('🔄 Reconnecting collaboration service...');
      if (this.socket) {
        this.socket.connect();
      } else {
        this.initializeConnection().catch(console.error);
      }
    }, 3000);
  }

  private handleDisconnection() {
    this.cleanupSession();
    this.emit('disconnected');
  }

  private cleanupSession() {
    if (this.sessionTimeout) {
      clearTimeout(this.sessionTimeout);
      this.sessionTimeout = null;
    }

    // Close all peer connections
    this.peerConnections.forEach(connection => {
      connection.peer.destroy();
    });
    this.peerConnections.clear();

    // Stop media streams
    this.stopMediaStream();
    this.stopScreenShare();

    // Reset state
    this.currentSession = null;
    this.currentUser = null;
    this.participants.clear();
    this.comments.clear();
    this.versionHistory = [];
  }

  private handleSessionJoined(session: CollaborativeSession) {
    this.currentSession = session;
    this.setupSessionTimeout();
    this.emit('session_joined', session);
    
    // Load session data
    this.loadSessionData(session.id);
  }

  private setupSessionTimeout() {
    if (this.sessionTimeout) {
      clearTimeout(this.sessionTimeout);
    }

    this.sessionTimeout = setTimeout(() => {
      this.endSession();
      toast.warning('Session expired due to inactivity');
    }, this.config.sessionTimeout);
  }

  private handleUserJoined(user: SessionParticipant) {
    this.participants.set(user.id, user);
    this.emit('user_joined', user);
    
    // Establish WebRTC connection if needed
    if (this.currentSession?.voiceEnabled || this.currentSession?.videoEnabled) {
      this.initiatePeerConnection(user.id);
    }
    
    toast.success(`${user.username} joined the session`);
  }

  private handleUserLeft(userId: string) {
    const user = this.participants.get(userId);
    this.participants.delete(userId);
    
    // Close peer connection
    this.closePeerConnection(userId);
    
    this.emit('user_left', userId);
    toast.info(`${user?.username || 'User'} left the session`);
  }

  private handleParticipantUpdated(participant: SessionParticipant) {
    this.participants.set(participant.id, participant);
    this.emit('participant_updated', participant);
  }

  private handleCollaborationEvent(event: CollaborationEvent) {
    this.emit('collaboration_event', event);
    
    // Handle specific event types
    switch (event.type) {
      case 'cursor_move':
        this.handleCursorMove(event);
        break;
      case 'model_selection':
        this.handleModelSelection(event);
        break;
      case 'model_edit':
        this.handleModelEdit(event);
        break;
      case 'comment_add':
        this.handleCommentAdded(event.data.comment);
        break;
    }
  }

  private handleCursorMove(event: CollaborationEvent) {
    this.emit('cursor_move', {
      userId: event.userId,
      position: event.data.cursorPosition
    });
  }

  private handleModelSelection(event: CollaborationEvent) {
    this.emit('model_selection', {
      userId: event.userId,
      selection: event.data.selection
    });
  }

  private handleModelEdit(event: CollaborationEvent) {
    this.emit('model_edit', {
      userId: event.userId,
      operation: event.data.editOperation
    });
  }

  private handleCommentAdded(comment: Comment) {
    this.comments.set(comment.id, comment);
    this.emit('comment_added', comment);
    toast.success('New comment added');
  }

  private handleCommentUpdated(comment: Comment) {
    this.comments.set(comment.id, comment);
    this.emit('comment_updated', comment);
  }

  private handleCommentDeleted(commentId: string) {
    this.comments.delete(commentId);
    this.emit('comment_deleted', commentId);
  }

  private handleVersionCreated(version: VersionControl) {
    this.versionHistory.push(version);
    this.emit('version_created', version);
  }

  private handleSuggestionAdded(suggestion: ChangeSuggestion) {
    this.emit('suggestion_added', suggestion);
  }

  private handleSuggestionUpdated(suggestion: ChangeSuggestion) {
    this.emit('suggestion_updated', suggestion);
  }

  // WebRTC Management
  private async initiatePeerConnection(userId: string, initiator = false): Promise<void> {
    try {
      const connectionId = this.generateConnectionId();
      
      // Create peer connection
      const peer = new SimplePeer({
        initiator,
        trickle: false,
        config: {
          iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
          ]
        }
      });

      const connectionData: PeerConnectionData = {
        peer,
        userId,
        connectionId,
        status: 'connecting'
      };

      this.peerConnections.set(userId, connectionData);

      // Setup peer event handlers
      peer.on('signal', (signal) => {
        this.sendWebRTCSignal(userId, signal);
      });

      peer.on('connect', () => {
        connectionData.status = 'connected';
        this.emit('peer_connected', { userId, connectionId });
      });

      peer.on('data', (data) => {
        this.handlePeerData(userId, data);
      });

      peer.on('stream', (stream) => {
        this.handlePeerStream(userId, stream);
      });

      peer.on('close', () => {
        this.handlePeerDisconnected(userId);
      });

      peer.on('error', (error) => {
        console.error('Peer connection error:', error);
        this.handlePeerError(userId, error);
      });

      // Get user media if needed
      if (this.config.enableVoiceChat || this.config.enableVideoChat) {
        await this.getUserMedia();
        if (this.mediaStream) {
          this.mediaStream.getTracks().forEach(track => {
            peer.addTrack(track, this.mediaStream!);
          });
        }
      }

    } catch (error) {
      console.error('Failed to initiate peer connection:', error);
      this.handlePeerError(userId, error as Error);
    }
  }

  private sendWebRTCSignal(userId: string, signal: any) {
    if (this.socket) {
      this.socket.emit('webrtc_signal', {
        to: userId,
        signal,
        from: this.currentUser?.id
      });
    }
  }

  private handleWebRTCOffer(data: any) {
    this.initiatePeerConnection(data.from, false);
    
    const connection = this.peerConnections.get(data.from);
    if (connection) {
      connection.peer.signal(data.signal);
    }
  }

  private handleWebRTCAnswer(data: any) {
    const connection = this.peerConnections.get(data.from);
    if (connection) {
      connection.peer.signal(data.signal);
    }
  }

  private handleWebRTCIceCandidate(data: any) {
    const connection = this.peerConnections.get(data.from);
    if (connection) {
      connection.peer.signal(data.signal);
    }
  }

  private handlePeerData(userId: string, data: any) {
    try {
      const parsedData = JSON.parse(data.toString());
      this.emit('peer_data', { userId, data: parsedData });
    } catch (error) {
      console.error('Failed to parse peer data:', error);
    }
  }

  private handlePeerStream(userId: string, stream: MediaStream) {
    const connection = this.peerConnections.get(userId);
    if (connection) {
      connection.mediaStream = stream;
      this.emit('peer_stream', { userId, stream });
    }
  }

  private handlePeerDisconnected(userId: string) {
    this.closePeerConnection(userId);
    this.emit('peer_disconnected', userId);
  }

  private handlePeerError(userId: string, error: Error) {
    this.emit('peer_error', { userId, error });
    console.error(`Peer connection error with ${userId}:`, error);
  }

  private closePeerConnection(userId: string) {
    const connection = this.peerConnections.get(userId);
    if (connection) {
      connection.peer.destroy();
      this.peerConnections.delete(userId);
    }
  }

  private generateConnectionId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  // Session Management
  async createSession(modelId: string, userProfile: UserProfile): Promise<string> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          modelId,
          user: userProfile,
          settings: {
            maxParticipants: this.config.maxParticipants,
            voiceEnabled: this.config.enableVoiceChat,
            videoEnabled: this.config.enableVideoChat,
            screenShareEnabled: this.config.enableScreenShare,
            fileSharingEnabled: this.config.enableFileSharing
          }
        })
      });

      const session = await response.json();
      return session.id;
    } catch (error) {
      console.error('Failed to create session:', error);
      throw error;
    }
  }

  async joinSession(sessionId: string, userProfile: UserProfile): Promise<void> {
    try {
      if (this.socket) {
        this.socket.emit('join_session', {
          sessionId,
          user: userProfile
        });
      }
    } catch (error) {
      console.error('Failed to join session:', error);
      throw error;
    }
  }

  async endSession(): Promise<void> {
    if (this.currentSession && this.socket) {
      this.socket.emit('end_session', {
        sessionId: this.currentSession.id
      });
    }
    
    this.cleanupSession();
  }

  async leaveSession(): Promise<void> {
    if (this.currentSession && this.socket) {
      this.socket.emit('leave_session', {
        sessionId: this.currentSession.id
      });
    }
    
    this.cleanupSession();
  }

  private async loadSessionData(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/sessions/${sessionId}/data`);
      const data = await response.json();

      // Load comments
      data.comments?.forEach((comment: Comment) => {
        this.comments.set(comment.id, comment);
      });

      // Load version history
      if (data.versionHistory) {
        this.versionHistory = data.versionHistory;
      }

    } catch (error) {
      console.error('Failed to load session data:', error);
    }
  }

  // User Management
  async updateUserStatus(status: 'away' | 'busy' | 'connected'): Promise<void> {
    if (this.currentUser && this.socket) {
      this.currentUser.connectionStatus = status;
      
      this.socket.emit('update_status', {
        sessionId: this.currentSession?.id,
        status
      });
    }
  }

  async updateUserRole(userId: string, role: string): Promise<void> {
    if (this.socket) {
      this.socket.emit('update_role', {
        sessionId: this.currentSession?.id,
        userId,
        role
      });
    }
  }

  async inviteUser(email: string): Promise<void> {
    if (this.socket && this.currentSession) {
      this.socket.emit('invite_user', {
        sessionId: this.currentSession.id,
        email,
        sessionUrl: `${window.location.origin}/session/${this.currentSession.id}`
      });
      
      toast.success('Invitation sent successfully');
    }
  }

  // Media and Stream Management
  async getUserMedia(audio = true, video = false): Promise<MediaStream> {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio,
        video: video ? {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 }
        } : false
      });

      return this.mediaStream;
    } catch (error) {
      console.error('Failed to get user media:', error);
      throw new Error('Failed to access microphone/camera');
    }
  }

  async startScreenShare(): Promise<MediaStream> {
    try {
      this.screenShareStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          mediaSource: 'screen'
        },
        audio: true
      });

      // Share screen with peers
      this.peerConnections.forEach(connection => {
        if (this.screenShareStream) {
          this.screenShareStream.getTracks().forEach(track => {
            connection.peer.addTrack(track, this.screenShareStream!);
          });
        }
      });

      this.emit('screen_share_started', this.screenShareStream);
      return this.screenShareStream;
    } catch (error) {
      console.error('Failed to start screen share:', error);
      throw new Error('Failed to start screen sharing');
    }
  }

  async stopScreenShare(): Promise<void> {
    if (this.screenShareStream) {
      this.screenShareStream.getTracks().forEach(track => track.stop());
      this.screenShareStream = null;
      
      this.emit('screen_share_stopped');
    }
  }

  private stopMediaStream(): void {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
  }

  async toggleAudio(): Promise<boolean> {
    if (this.mediaStream) {
      const audioTrack = this.mediaStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        this.emit('audio_toggled', audioTrack.enabled);
        return audioTrack.enabled;
      }
    }
    return false;
  }

  async toggleVideo(): Promise<boolean> {
    if (this.mediaStream) {
      const videoTrack = this.mediaStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        this.emit('video_toggled', videoTrack.enabled);
        return videoTrack.enabled;
      }
    }
    return false;
  }

  // Collaboration Events
  emitCursorMove(position: { x: number; y: number; z: number; mode: string }): void {
    if (this.socket && this.currentSession) {
      this.socket.emit('cursor_move', {
        sessionId: this.currentSession.id,
        position,
        mode: position.mode
      });
    }
  }

  emitModelSelection(selection: any[]): void {
    if (this.socket && this.currentSession) {
      this.socket.emit('model_selection', {
        sessionId: this.currentSession.id,
        selection
      });
    }
  }

  emitModelEdit(operation: any): void {
    if (this.socket && this.currentSession) {
      this.socket.emit('model_edit', {
        sessionId: this.currentSession.id,
        operation
      });
    }
  }

  // Comment Management
  async addComment(comment: Omit<Comment, 'id' | 'timestamp' | 'reactions'>): Promise<Comment> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...comment,
          sessionId: this.currentSession?.id
        })
      });

      const newComment = await response.json();
      return newComment;
    } catch (error) {
      console.error('Failed to add comment:', error);
      throw error;
    }
  }

  async updateComment(commentId: string, content: string): Promise<void> {
    try {
      await fetch(`${this.config.apiUrl}/collaboration/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
      });
    } catch (error) {
      console.error('Failed to update comment:', error);
      throw error;
    }
  }

  async deleteComment(commentId: string): Promise<void> {
    try {
      await fetch(`${this.config.apiUrl}/collaboration/comments/${commentId}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Failed to delete comment:', error);
      throw error;
    }
  }

  // Version Control
  async createVersion(message: string, changes: any[]): Promise<VersionControl> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/versions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sessionId: this.currentSession?.id,
          message,
          changes
        })
      });

      const version = await response.json();
      return version;
    } catch (error) {
      console.error('Failed to create version:', error);
      throw error;
    }
  }

  async loadVersion(versionId: string): Promise<void> {
    try {
      await fetch(`${this.config.apiUrl}/collaboration/versions/${versionId}/load`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      console.error('Failed to load version:', error);
      throw error;
    }
  }

  // Change Suggestions
  async addSuggestion(suggestion: Omit<ChangeSuggestion, 'id' | 'votes' | 'timestamp'>): Promise<ChangeSuggestion> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...suggestion,
          sessionId: this.currentSession?.id
        })
      });

      const newSuggestion = await response.json();
      return newSuggestion;
    } catch (error) {
      console.error('Failed to add suggestion:', error);
      throw error;
    }
  }

  async voteOnSuggestion(suggestionId: string, vote: 'up' | 'down' | 'neutral', reason?: string): Promise<void> {
    try {
      await fetch(`${this.config.apiUrl}/collaboration/suggestions/${suggestionId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vote, reason })
      });
    } catch (error) {
      console.error('Failed to vote on suggestion:', error);
      throw error;
    }
  }

  // File Sharing
  async shareFile(file: File, description?: string): Promise<string> {
    if (!this.config.enableFileSharing) {
      throw new Error('File sharing is not enabled');
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', description || '');
      formData.append('sessionId', this.currentSession?.id || '');

      const response = await fetch(`${this.config.apiUrl}/collaboration/files`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      // Emit file shared event
      if (this.socket && this.currentSession) {
        this.socket.emit('file_shared', {
          sessionId: this.currentSession.id,
          fileId: result.id,
          fileName: file.name,
          description
        });
      }

      return result.id;
    } catch (error) {
      console.error('Failed to share file:', error);
      throw error;
    }
  }

  async downloadSharedFile(fileId: string): Promise<Blob> {
    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/files/${fileId}`);
      return await response.blob();
    } catch (error) {
      console.error('Failed to download shared file:', error);
      throw error;
    }
  }

  // Session Analytics
  async getSessionAnalytics(): Promise<any> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/sessions/${this.currentSession.id}/analytics`);
      return await response.json();
    } catch (error) {
      console.error('Failed to get session analytics:', error);
      throw error;
    }
  }

  async exportSessionData(format: 'json' | 'pdf' | 'html' = 'json'): Promise<Blob> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    try {
      const response = await fetch(`${this.config.apiUrl}/collaboration/sessions/${this.currentSession.id}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ format })
      });

      return await response.blob();
    } catch (error) {
      console.error('Failed to export session data:', error);
      throw error;
    }
  }

  // Getters
  getCurrentSession(): CollaborativeSession | null {
    return this.currentSession;
  }

  getCurrentUser(): SessionParticipant | null {
    return this.currentUser;
  }

  getParticipants(): SessionParticipant[] {
    return Array.from(this.participants.values());
  }

  getComments(): Comment[] {
    return Array.from(this.comments.values());
  }

  getVersionHistory(): VersionControl[] {
    return [...this.versionHistory];
  }

  getPeerConnections(): Map<string, PeerConnectionData> {
    return this.peerConnections;
  }

  isConnected(): boolean {
    return this.isConnected;
  }

  isInSession(): boolean {
    return this.currentSession !== null;
  }

  // Cleanup
  destroy(): void {
    this.cleanupSession();
    
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    
    this.removeAllListeners();
  }
}

// Service instance
export const collaborationService = new CollaborationService({
  apiUrl: process.env.VITE_API_URL || 'http://localhost:8000',
  wsUrl: process.env.VITE_WS_URL || 'ws://localhost:8000'
});