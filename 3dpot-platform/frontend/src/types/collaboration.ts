// Sprint 6+: Collaborative Features Types
// Funcionalidades colaborativas em tempo real

export interface CollaborativeSession {
  id: string;
  modelId: string;
  modelName: string;
  participants: SessionParticipant[];
  status: 'active' | 'paused' | 'ended';
  createdBy: string;
  createdAt: Date;
  lastActivity: Date;
  permissions: SessionPermissions;
  chatEnabled: boolean;
  voiceEnabled: boolean;
  videoEnabled: boolean;
  screenShareEnabled: boolean;
}

export interface SessionParticipant {
  id: string;
  userId: string;
  username: string;
  email: string;
  avatar?: string;
  role: 'owner' | 'editor' | 'viewer' | 'commentator';
  permissions: ParticipantPermissions;
  connectionStatus: 'connected' | 'disconnected' | 'away' | 'busy';
  joinedAt: Date;
  lastSeen: Date;
  cursor?: CursorPosition;
  selection?: ModelSelection[];
  isTyping: boolean;
  isSpeaking: boolean;
  isVideoEnabled: boolean;
  isAudioEnabled: boolean;
  peerId: string; // For WebRTC connections
}

export interface ParticipantPermissions {
  canEdit: boolean;
  canComment: boolean;
  canInvite: boolean;
  canShare: boolean;
  canExport: boolean;
  canScreenshot: boolean;
  canControl: boolean;
  maxSessionTime: number; // in minutes, 0 = unlimited
}

export interface SessionPermissions {
  requireApproval: boolean;
  maxParticipants: number;
  allowAnonymous: boolean;
  recordingEnabled: boolean;
  timeLimit: number; // in minutes, 0 = unlimited
  passwordProtected: boolean;
  password?: string;
  domainRestriction?: string[];
}

export interface CursorPosition {
  x: number;
  y: number;
  z: number;
  mode: 'view' | 'edit' | 'selection';
  color: string;
}

export interface ModelSelection {
  objectId: string;
  type: 'vertex' | 'edge' | 'face' | 'object';
  indices: number[];
  mode: 'add' | 'subtract' | 'replace';
}

export interface CollaborationEvent {
  id: string;
  type: CollaborationEventType;
  userId: string;
  sessionId: string;
  timestamp: Date;
  data: CollaborationEventData;
  metadata: EventMetadata;
}

export type CollaborationEventType = 
  | 'cursor_move'
  | 'model_selection'
  | 'model_edit'
  | 'comment_add'
  | 'comment_edit'
  | 'comment_delete'
  | 'user_joined'
  | 'user_left'
  | 'user_role_changed'
  | 'screen_share_start'
  | 'screen_share_stop'
  | 'voice_start'
  | 'voice_stop'
  | 'video_start'
  | 'video_stop'
  | 'session_pause'
  | 'session_resume'
  | 'model_lock'
  | 'model_unlock'
  | 'change_suggestion';

export interface CollaborationEventData {
  cursorPosition?: CursorPosition;
  selection?: ModelSelection[];
  editOperation?: EditOperation;
  comment?: Comment;
  screenShareUrl?: string;
  voiceStatus?: boolean;
  videoStatus?: boolean;
  roleChange?: RoleChange;
  lockInfo?: LockInfo;
  suggestion?: ChangeSuggestion;
}

export interface EventMetadata {
  duration?: number;
  success: boolean;
  error?: string;
  version: string;
  sessionVersion: number;
}

export interface EditOperation {
  type: 'transform' | 'modify' | 'add' | 'delete' | 'duplicate';
  target: string; // object ID
  originalData?: any;
  newData: any;
  parameters: EditParameters;
}

export interface EditParameters {
  transform?: {
    position?: Vector3;
    rotation?: Vector3;
    scale?: Vector3;
  };
  geometry?: {
    vertices?: number[];
    edges?: number[];
    faces?: number[];
    operations?: string[];
  };
  material?: {
    color?: string;
    texture?: string;
    properties?: any;
  };
}

export interface Comment {
  id: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  content: string;
  timestamp: Date;
  position?: Vector3;
  attachments?: CommentAttachment[];
  replies: Comment[];
  status: 'active' | 'resolved' | 'deleted';
  mentions: Mention[];
  reactions: CommentReaction[];
}

export interface CommentAttachment {
  type: 'image' | 'video' | 'file' | 'link';
  url: string;
  name: string;
  size: number;
  mimeType: string;
}

export interface Mention {
  userId: string;
  username: string;
  start: number;
  end: number;
}

export interface CommentReaction {
  type: 'like' | 'dislike' | 'helpful' | 'confused' | 'excited';
  userId: string;
  timestamp: Date;
}

export interface RoleChange {
  fromRole: ParticipantRole;
  toRole: ParticipantRole;
  reason?: string;
  changedBy: string;
}

export type ParticipantRole = 'owner' | 'editor' | 'viewer' | 'commentator';

export interface LockInfo {
  objectId: string;
  lockedBy: string;
  lockType: 'soft' | 'hard';
  timestamp: Date;
  timeout?: number; // Auto-unlock after timeout
}

export interface ChangeSuggestion {
  id: string;
  authorId: string;
  title: string;
  description: string;
  changes: EditOperation[];
  impact: ImpactAnalysis;
  status: 'pending' | 'approved' | 'rejected' | 'implemented';
  votes: SuggestionVote[];
  deadline?: Date;
}

export interface ImpactAnalysis {
  affectedObjects: string[];
  complexity: 'low' | 'medium' | 'high';
  estimatedTime: number; // in minutes
  risks: string[];
  benefits: string[];
}

export interface SuggestionVote {
  userId: string;
  vote: 'up' | 'down' | 'neutral';
  reason?: string;
  timestamp: Date;
}

export interface VersionControl {
  id: string;
  sessionId: string;
  version: number;
  modelId: string;
  changes: EditOperation[];
  authorId: string;
  message: string;
  timestamp: Date;
  parentVersion?: number;
  tags: VersionTag[];
  isPublic: boolean;
  downloadUrl?: string;
  thumbnailUrl?: string;
}

export interface VersionTag {
  name: string;
  color: string;
  type: 'milestone' | 'release' | 'branch' | 'experimental';
}

export interface ActivityFeed {
  id: string;
  sessionId: string;
  events: CollaborationEvent[];
  filter: ActivityFilter;
  pagination: ActivityPagination;
}

export interface ActivityFilter {
  eventTypes: CollaborationEventType[];
  users: string[];
  dateRange: {
    start: Date;
    end: Date;
  };
  keywords?: string;
}

export interface ActivityPagination {
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface WebRTCConnection {
  id: string;
  sessionId: string;
  participantId: string;
  peerId: string;
  connectionType: 'voice' | 'video' | 'screen_share';
  status: 'connecting' | 'connected' | 'disconnected' | 'failed';
  mediaStream?: MediaStream;
  configuration: RTCConfiguration;
  bandwidth: BandwidthMetrics;
  quality: ConnectionQuality;
}

export interface RTCConfiguration {
  iceServers: RTCIceServer[];
  audioConstraints: MediaTrackConstraints;
  videoConstraints: MediaTrackConstraints;
  bandwidth: BandwidthLimits;
}

export interface RTCIceServer {
  urls: string | string[];
  username?: string;
  credential?: string;
}

export interface BandwidthMetrics {
  upload: number; // kbps
  download: number; // kbps
  latency: number; // ms
  packetLoss: number; // percentage
}

export interface BandwidthLimits {
  maxVideo: number;
  maxAudio: number;
  minVideo: number;
  minAudio: number;
}

export interface ConnectionQuality {
  rating: 'excellent' | 'good' | 'fair' | 'poor';
  score: number; // 0-100
  issues: QualityIssue[];
  recommendations: string[];
}

export interface QualityIssue {
  type: 'bandwidth' | 'latency' | 'packet_loss' | 'connection';
  severity: 'low' | 'medium' | 'high';
  description: string;
  solution: string;
}

export interface CollaborativeState {
  session: CollaborativeSession | null;
  participants: SessionParticipant[];
  myCursor: CursorPosition | null;
  selections: ModelSelection[];
  comments: Comment[];
  versionHistory: VersionControl[];
  activeUsers: string[];
  isConnected: boolean;
  connectionQuality: ConnectionQuality | null;
  errors: CollaborationError[];
}

export interface CollaborationError {
  id: string;
  type: 'network' | 'permission' | 'conflict' | 'sync' | 'media';
  message: string;
  details: any;
  timestamp: Date;
  resolved: boolean;
  resolution?: string;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

// Real-time synchronization
export interface SyncMessage {
  type: 'delta' | 'full' | 'confirmation' | 'request' | 'response';
  sessionId: string;
  version: number;
  timestamp: Date;
  data: any;
  sequence: number;
}

export interface ConflictResolution {
  type: 'merge' | 'accept' | 'reject' | 'manual';
  strategy: string;
  priority: number;
  timeout: number;
  manual: boolean;
}

// Collaboration analytics
export interface CollaborationAnalytics {
  sessionId: string;
  duration: number;
  participantCount: number;
  editOperations: number;
  comments: number;
  suggestions: number;
  votes: number;
  conflicts: number;
  resolutions: number;
  averageLatency: number;
  peakParticipants: number;
  featureUsage: FeatureUsage[];
}

export interface FeatureUsage {
  feature: string;
  usage: number;
  percentage: number;
  peak: number;
}

// Export collaborative session data
export interface SessionExport {
  sessionId: string;
  model: Model3D;
  versionHistory: VersionControl[];
  comments: Comment[];
  activityLog: CollaborationEvent[];
  participantList: SessionParticipant[];
  analytics: CollaborationAnalytics;
  exportedAt: Date;
  exportedBy: string;
  format: 'json' | 'pdf' | 'html';
}