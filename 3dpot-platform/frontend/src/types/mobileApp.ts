// Sprint 6+: Mobile Applications Types
// Aplicações nativas iOS/Android com React Native

export interface MobileApp {
  id: string;
  name: string;
  version: string;
  platform: 'ios' | 'android' | 'cross_platform';
  buildId: string;
  storeUrls: StoreUrls;
  status: AppStatus;
  distribution: DistributionConfig;
  features: MobileFeatures;
  permissions: AppPermission[];
  configurations: AppConfiguration;
  analytics: AppAnalytics;
  performance: PerformanceMetrics;
  crashReporting: CrashReporting;
  createdAt: Date;
  lastUpdated: Date;
}

export interface StoreUrls {
  ios?: string;
  android?: string;
  testFlight?: string;
  googlePlayInternal?: string;
  googlePlayBeta?: string;
  amazonAppstore?: string;
}

export type AppStatus = 'development' | 'testing' | 'pending_review' | 'approved' | 'rejected' | 'suspended' | 'live' | 'archived';

export interface DistributionConfig {
  channel: 'app_store' | 'google_play' | 'internal' | 'enterprise' | 'beta' | 'development';
  releaseType: 'production' | 'staging' | 'development' | 'beta' | 'alpha';
  autoUpdate: boolean;
  phasedRelease: boolean;
  regions: string[];
  deviceTypes: DeviceType[];
  minOSVersion: string;
  maxOSVersion?: string;
  requirements: DistributionRequirement[];
}

export interface DistributionRequirement {
  type: 'device' | 'feature' | 'capability';
  requirement: string;
  value: any;
  description: string;
}

export interface DeviceType {
  type: 'phone' | 'tablet' | 'watch' | 'tv' | 'vr';
  supported: boolean;
  orientation: OrientationType[];
  screenSize: ScreenSize[];
  aspectRatio: string[];
  platform: string[];
}

export type OrientationType = 'portrait' | 'landscape' | 'portrait_upsidedown';

export interface ScreenSize {
  name: string;
  minWidth: number;
  minHeight: number;
  maxWidth: number;
  maxHeight: number;
  dpi: string;
  safeAreas: SafeArea[];
}

export interface SafeArea {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface MobileFeatures {
  core: CoreFeatures;
  advanced: AdvancedFeatures;
  experimental: ExperimentalFeatures;
  integrations: IntegrationFeatures;
}

export interface CoreFeatures {
  model3dViewer: boolean;
  arPreview: boolean;
  vrSupport: boolean;
  modelGeneration: boolean;
  realTimeCollaboration: boolean;
  marketplaceAccess: boolean;
  offlineMode: boolean;
  sync: boolean;
  notifications: boolean;
  darkMode: boolean;
  accessibility: boolean;
  localization: boolean;
}

export interface AdvancedFeatures {
  advanced3DControls: boolean;
  realTimeRendering: boolean;
  voiceControl: boolean;
  gestureControl: boolean;
  hapticFeedback: boolean;
  cameraIntegration: boolean;
  photoCapture: boolean;
  videoRecording: boolean;
  screenRecording: boolean;
  applePay: boolean;
  googlePay: boolean;
  biometricAuth: boolean;
  faceId: boolean;
  touchId: boolean;
}

export interface ExperimentalFeatures {
  mixedReality: boolean;
  spatialComputing: boolean;
  sceneUnderstanding: boolean;
  environmentScanning: boolean;
  aiInsights: boolean;
  predictiveUI: boolean;
  adaptiveUI: boolean;
  contextAwareness: boolean;
  ambientComputing: boolean;
  neuralInterfaces: boolean;
}

export interface IntegrationFeatures {
  cloudRendering: boolean;
  aiAssistants: boolean;
  socialSharing: boolean;
  fileSystem: boolean;
  systemGallery: boolean;
  calendarIntegration: boolean;
  contactIntegration: boolean;
  locationServices: boolean;
  motionSensors: boolean;
  healthKit: boolean;
  googleFit: boolean;
  iCloud: boolean;
  googleDrive: boolean;
  dropbox: boolean;
  oneDrive: boolean;
}

export interface AppPermission {
  name: string;
  type: 'camera' | 'microphone' | 'location' | 'photos' | 'contacts' | 'calendar' | 'health' | 'motion' | 'notifications' | 'biometric';
  status: 'granted' | 'denied' | 'limited' | 'pending';
  rationale: string;
  required: boolean;
  optional: boolean;
  minOSVersion: string;
  platform: 'ios' | 'android' | 'both';
}

export interface AppConfiguration {
  ui: UIConfiguration;
  navigation: NavigationConfiguration;
  security: SecurityConfiguration;
  performance: PerformanceConfiguration;
  analytics: AnalyticsConfiguration;
  debugging: DebugConfiguration;
  network: NetworkConfiguration;
  storage: StorageConfiguration;
  update: UpdateConfiguration;
}

export interface UIConfiguration {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large' | 'xl';
  colorScheme: ColorScheme[];
  layout: LayoutConfiguration;
  animations: AnimationConfiguration;
  gestures: GestureConfiguration;
  accessibility: AccessibilityConfiguration;
}

export interface ColorScheme {
  name: string;
  primary: ColorDefinition;
  secondary: ColorDefinition;
  background: ColorDefinition;
  surface: ColorDefinition;
  error: ColorDefinition;
  warning: ColorDefinition;
  success: ColorDefinition;
  text: ColorDefinition;
  textSecondary: ColorDefinition;
}

export interface ColorDefinition {
  hex: string;
  rgba: string;
  hsla: string;
  theme: 'light' | 'dark' | 'auto';
  contrast: number;
  accessibility: 'AAA' | 'AA' | 'A' | 'fail';
}

export interface LayoutConfiguration {
  grid: GridConfiguration;
  spacing: SpacingConfiguration;
  borderRadius: BorderRadiusConfiguration;
  shadows: ShadowConfiguration;
  padding: PaddingConfiguration;
  margin: MarginConfiguration;
}

export interface GridConfiguration {
  columns: number;
  gutterWidth: number;
  gutterHeight: number;
  maxWidth: number;
  containerPadding: number;
}

export interface SpacingConfiguration {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
  baseUnit: number;
}

export interface BorderRadiusConfiguration {
  none: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  full: number;
}

export interface ShadowConfiguration {
  elevation: ShadowLevel[];
  opacity: number;
  blur: number;
  spread: number;
  color: string;
  offset: Vector2;
}

export interface ShadowLevel {
  level: number;
  elevation: number;
  opacity: number;
  blur: number;
}

export interface Vector2 {
  x: number;
  y: number;
}

export interface PaddingConfiguration {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
}

export interface MarginConfiguration {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
}

export interface AnimationConfiguration {
  duration: AnimationDuration;
  easing: AnimationEasing;
  spring: SpringConfiguration;
  interactions: InteractionConfiguration;
}

export interface AnimationDuration {
  fast: number;
  normal: number;
  slow: number;
  custom: AnimationDurationCustom;
}

export interface AnimationDurationCustom {
  entrance: number;
  exit: number;
  emphasis: number;
  nuance: number;
}

export interface AnimationEasing {
  linear: string;
  easeIn: string;
  easeOut: string;
  easeInOut: string;
  spring: string;
  elastic: string;
  bounce: string;
  back: string;
}

export interface SpringConfiguration {
  tension: number;
  friction: number;
  mass: number;
  stiffness: number;
  damping: number;
  velocity: number;
}

export interface InteractionConfiguration {
  tap: boolean;
  longPress: boolean;
  pan: boolean;
  pinch: boolean;
  swipe: boolean;
  shake: boolean;
  rotation: boolean;
}

export interface GestureConfiguration {
  pinchToZoom: boolean;
  panToRotate: boolean;
  doubleTap: boolean;
  longPress: boolean;
  swipeGestures: SwipeGestureConfig;
  hapticFeedback: HapticConfig;
  forceTouch: boolean;
  dragAndDrop: boolean;
}

export interface SwipeGestureConfig {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  threshold: number;
  velocity: number;
}

export interface HapticConfig {
  enabled: boolean;
  intensity: 'light' | 'medium' | 'heavy';
  pattern: 'selection' | 'impact' | 'notification' | 'success' | 'warning' | 'error';
}

export interface AccessibilityConfiguration {
  screenReader: boolean;
  highContrast: boolean;
  reduceMotion: boolean;
  fontScaling: boolean;
  voiceOver: boolean;
  switchControl: boolean;
  colorBlindness: ColorBlindnessType[];
  captions: boolean;
  audioDescription: boolean;
}

export type ColorBlindnessType = 'protanopia' | 'deuteranopia' | 'tritanopia' | 'achromatopsia';

export interface NavigationConfiguration {
  type: 'stack' | 'tab' | 'drawer' | 'modal';
  gesturesEnabled: boolean;
  backGestureEnabled: boolean;
  transitionStyle: 'default' | 'fade' | 'slide' | 'scale';
  headerStyle: HeaderStyle;
  tabBarStyle: TabBarStyle;
  statusBar: StatusBarStyle;
}

export interface HeaderStyle {
  visible: boolean;
  height: number;
  backgroundColor: string;
  textColor: string;
  fontSize: number;
  fontWeight: string;
  shadowEnabled: boolean;
  showBackButton: boolean;
  showTitle: boolean;
  showLogo: boolean;
}

export interface TabBarStyle {
  visible: boolean;
  height: number;
  backgroundColor: string;
  activeColor: string;
  inactiveColor: string;
  iconSize: number;
  fontSize: number;
  fontWeight: string;
  showLabels: boolean;
  showBadges: boolean;
}

export interface StatusBarStyle {
  visible: boolean;
  backgroundColor: string;
  barStyle: 'default' | 'light' | 'dark';
  hideOnScroll: boolean;
  hideStatusBarOnKeyboard: boolean;
}

export interface SecurityConfiguration {
  biometricAuth: BiometricConfig;
  encryption: EncryptionConfig;
  certificates: CertificateConfig;
  keychain: KeychainConfig;
  sslPinning: SSLPinningConfig;
  obfuscation: ObfuscationConfig;
}

export interface BiometricConfig {
  enabled: boolean;
  types: BiometricType[];
  allowDevicePasscode: boolean;
  lockoutPolicy: 'none' | 'device' | 'application';
  fallbackEnabled: boolean;
}

export type BiometricType = 'face_id' | 'touch_id' | 'fingerprint' | 'iris' | 'voice_recognition';

export interface EncryptionConfig {
  algorithm: 'aes256' | 'aes192' | 'aes128' | 'rsa' | 'ecc';
  keySize: number;
  ivSize: number;
  mode: 'ecb' | 'cbc' | 'cfb' | 'ofb' | 'gcm';
  padding: 'none' | 'pkcs7' | 'ansix923' | 'iso7816' | 'pkcs5';
}

export interface CertificateConfig {
  sslValidation: boolean;
  selfSignedAllowed: boolean;
  certificatePinning: boolean;
  allowExpired: boolean;
  allowNotYetValid: boolean;
}

export interface KeychainConfig {
  accessibility: 'when_unlocked' | 'after_first_unlock' | 'when_passcode_set_this_device_only' | 'when_unlocked_this_device_only';
  accessGroup?: string;
  cloudSync: boolean;
  biometricProtection: boolean;
}

export interface SSLPinningConfig {
  enabled: boolean;
  pins: SSlPin[];
  failClosed: boolean;
  timeout: number;
}

export interface SSlPin {
  hash: string;
  algorithm: 'sha256' | 'sha1';
  domain: string;
}

export interface ObfuscationConfig {
  enabled: boolean;
  level: 'low' | 'medium' | 'high' | 'maximum';
  removeLogging: boolean;
  stringObfuscation: boolean;
  controlFlowObfuscation: boolean;
  resourceObfuscation: boolean;
}

export interface PerformanceConfiguration {
  optimization: OptimizationConfig;
  memory: MemoryConfig;
  battery: BatteryConfig;
  network: NetworkPerformanceConfig;
  caching: CachingConfig;
  lazyLoading: LazyLoadingConfig;
  prefetching: PrefetchingConfig;
}

export interface OptimizationConfig {
  minify: boolean;
  bundleSize: number;
  deadCodeElimination: boolean;
  treeShaking: boolean;
  codeSplitting: boolean;
  chunkSplitting: boolean;
  assetOptimization: boolean;
}

export interface MemoryConfig {
  maxHeapSize: number;
  gcThreshold: number;
  leakDetection: boolean;
  memoryProfiling: boolean;
  memoryWarnings: boolean;
}

export interface BatteryConfig {
  lowPowerMode: LowPowerConfig;
  backgroundRefresh: BackgroundRefreshConfig;
  batteryAwareScheduling: boolean;
  powerEfficientAnimations: boolean;
}

export interface LowPowerConfig {
  enabled: boolean;
  threshold: number;
  features: LowPowerFeature[];
  autoEnable: boolean;
}

export interface LowPowerFeature {
  name: string;
  disabled: boolean;
  description: string;
}

export interface BackgroundRefreshConfig {
  enabled: boolean;
  interval: number;
  networkRequirement: 'any' | 'wifi' | 'unmetered';
  priority: 'low' | 'normal' | 'high';
}

export interface NetworkPerformanceConfig {
  timeout: number;
  retryCount: number;
  retryDelay: number;
  compressionEnabled: boolean;
  cacheControl: string;
  userAgent: string;
}

export interface CachingConfig {
  enabled: boolean;
  type: 'memory' | 'disk' | 'both';
  maxSize: number;
  ttl: number;
  strategy: 'cache_first' | 'network_first' | 'stale_while_revalidate';
  storage: CachingStorage;
}

export interface CachingStorage {
  memory: MemoryCacheConfig;
  disk: DiskCacheConfig;
}

export interface MemoryCacheConfig {
  maxSize: number;
  gcInterval: number;
  weakReferences: boolean;
}

export interface DiskCacheConfig {
  maxSize: number;
  directory: string;
  encryption: boolean;
  compression: boolean;
}

export interface LazyLoadingConfig {
  enabled: boolean;
  threshold: number;
  prefetchDistance: number;
  priority: 'low' | 'normal' | 'high';
}

export interface PrefetchingConfig {
  enabled: boolean;
  strategy: 'aggressive' | 'conservative' | 'adaptive';
  maxConcurrent: number;
  priorityQueue: boolean;
}

export interface AnalyticsConfiguration {
  events: AnalyticsEvent[];
  screens: AnalyticsScreen[];
  properties: AnalyticsProperty[];
  funnels: AnalyticsFunnel[];
  cohorts: AnalyticsCohort;
  attribution: AttributionConfig;
}

export interface AnalyticsEvent {
  name: string;
  category: string;
  label?: string;
  value?: number;
  parameters: EventParameter[];
  triggers: EventTrigger[];
  enabled: boolean;
}

export interface EventParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  default?: any;
}

export interface EventTrigger {
  type: 'auto' | 'manual' | 'scheduled' | 'conditional';
  condition?: string;
  delay?: number;
  frequency?: number;
}

export interface AnalyticsScreen {
  name: string;
  path: string;
  parameters: ScreenParameter[];
  tracking: ScreenTracking;
}

export interface ScreenParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object';
  required: boolean;
  default?: any;
}

export interface ScreenTracking {
  autoTrack: boolean;
  timing: boolean;
  exitTracking: boolean;
  duration: boolean;
}

export interface AnalyticsProperty {
  name: string;
  type: 'user' | 'device' | 'session' | 'app' | 'custom';
  value: any;
  scope: 'global' | 'user' | 'session';
  persistent: boolean;
}

export interface AnalyticsFunnel {
  name: string;
  steps: FunnelStep[];
  analysis: FunnelAnalysis;
}

export interface FunnelStep {
  name: string;
  event: string;
  criteria: string[];
  timeWindow: number;
  order: number;
}

export interface FunnelAnalysis {
  conversionRate: number;
  dropOffRate: number;
  averageTime: number;
  segment: boolean;
}

export interface AnalyticsCohort {
  retention: boolean;
  segments: CohortSegment[];
  timeframe: CohortTimeframe;
}

export interface CohortSegment {
  name: string;
  criteria: string[];
  color: string;
}

export interface CohortTimeframe {
  period: 'day' | 'week' | 'month';
  duration: number;
}

export interface AttributionConfig {
  provider: 'firebase' | 'adjust' | 'appsflyer' | 'branch' | 'custom';
  trackingEnabled: boolean;
  deepLinking: boolean;
  campaignTracking: boolean;
  sourceTracking: boolean;
}

export interface DebugConfiguration {
  enabled: boolean;
  level: 'development' | 'staging' | 'production';
  consoleLogging: boolean;
  fileLogging: boolean;
  remoteLogging: boolean;
  performanceMonitoring: boolean;
  memoryDebugging: boolean;
  networkDebugging: boolean;
  uiDebugging: boolean;
  unitTesting: boolean;
  integrationTesting: boolean;
  e2eTesting: boolean;
}

export interface NetworkConfiguration {
  api: ApiConfiguration;
  websocket: WebSocketConfiguration;
  offline: OfflineConfiguration;
  backgroundSync: BackgroundSyncConfig;
}

export interface ApiConfiguration {
  baseUrl: string;
  timeout: number;
  retryCount: number;
  retryDelay: number;
  cachePolicy: 'cache' | 'network' | 'refresh' | 'stale';
  compression: boolean;
  encryption: boolean;
  authentication: ApiAuth;
}

export interface ApiAuth {
  type: 'bearer' | 'basic' | 'oauth2' | 'api_key' | 'custom';
  token?: string;
  refreshToken?: string;
  expiresAt?: Date;
  autoRefresh: boolean;
}

export interface WebSocketConfiguration {
  enabled: boolean;
  url: string;
  protocols: string[];
  reconnect: boolean;
  maxReconnectAttempts: number;
  heartbeat: number;
  compression: boolean;
}

export interface OfflineConfiguration {
  enabled: boolean;
  storage: OfflineStorage;
  sync: OfflineSync;
  conflictResolution: ConflictResolution;
}

export interface OfflineStorage {
  type: 'sqlite' | 'realm' | 'mongodb' | 'watermelon';
  encryption: boolean;
  backup: boolean;
  maxSize: number;
}

export interface OfflineSync {
  strategy: 'last_write_wins' | 'server_wins' | 'custom';
  frequency: 'manual' | 'periodic' | 'realtime';
  batchSize: number;
  maxRetries: number;
}

export interface ConflictResolution {
  strategy: 'manual' | 'auto' | 'merge';
  rules: ConflictRule[];
  timeout: number;
}

export interface ConflictRule {
  field: string;
  priority: 'local' | 'remote' | 'custom';
  customLogic: string;
}

export interface BackgroundSyncConfig {
  enabled: boolean;
  interval: number;
  networkRequirement: 'any' | 'wifi' | 'unmetered';
  batteryLevel: number;
  priority: 'low' | 'normal' | 'high';
}

export interface StorageConfiguration {
  local: LocalStorage;
  secure: SecureStorage;
  cloud: CloudStorage;
  backup: BackupConfig;
}

export interface LocalStorage {
  enabled: boolean;
  type: 'async' | 'sync' | 'raw';
  compression: boolean;
  encryption: boolean;
  maxSize: number;
  ttl: number;
}

export interface SecureStorage {
  enabled: boolean;
  type: 'keychain' | 'keystore' | 'hardware';
  accessibility: string;
  touchIdRequired: boolean;
  faceIdRequired: boolean;
}

export interface CloudStorage {
  enabled: boolean;
  provider: 'iCloud' | 'GoogleDrive' | 'Dropbox' | 'OneDrive';
  autoSync: boolean;
  conflictResolution: 'manual' | 'auto' | 'ask';
  maxRetries: number;
}

export interface BackupConfig {
  enabled: boolean;
  frequency: 'daily' | 'weekly' | 'monthly' | 'manual';
  include: BackupInclude[];
  exclude: BackupExclude[];
  encryption: boolean;
  compression: boolean;
}

export interface BackupInclude {
  type: 'data' | 'files' | 'settings' | 'cache';
  path?: string;
  pattern?: string;
}

export interface BackupExclude {
  type: 'data' | 'files' | 'settings' | 'cache';
  path?: string;
  pattern?: string;
  reason: string;
}

export interface UpdateConfiguration {
  automatic: AutoUpdateConfig;
  manual: ManualUpdateConfig;
  rollout: RolloutConfig;
  rollback: RollbackConfig;
}

export interface AutoUpdateConfig {
  enabled: boolean;
  type: 'immediate' | 'delayed' | 'background';
  checkFrequency: number;
  downloadOnCellular: boolean;
  allowMetered: boolean;
  installationPrompt: boolean;
}

export interface ManualUpdateConfig {
  enabled: boolean;
  checkOnLaunch: boolean;
  checkOnResume: boolean;
  showUpdateDialog: boolean;
  allowSkip: boolean;
  remindLater: boolean;
  reminderInterval: number;
}

export interface RolloutConfig {
  enabled: boolean;
  percentage: number;
  userFilter: UserFilter[];
  deviceFilter: DeviceFilter[];
  geographicFilter: GeographicFilter;
  phasedRollout: boolean;
}

export interface UserFilter {
  type: 'version' | 'platform' | 'region' | 'user_type';
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains';
  value: any;
}

export interface DeviceFilter {
  type: 'model' | 'os_version' | 'screen_size' | 'memory';
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains';
  value: any;
}

export interface GeographicFilter {
  enabled: boolean;
  regions: string[];
  countries: string[];
  cities: string[];
  exclude: boolean;
}

export interface RollbackConfig {
  enabled: boolean;
  trigger: RollbackTrigger[];
  autoRollback: boolean;
  delay: number;
  notifications: boolean;
}

export interface RollbackTrigger {
  type: 'crash_rate' | 'user_rating' | 'error_rate' | 'performance' | 'manual';
  threshold: number;
  timeWindow: number;
}

// Mobile App States and Navigation
export interface AppState {
  navigation: NavigationState;
  models: Model3DState;
  user: UserState;
  settings: SettingsState;
  performance: PerformanceState;
  network: NetworkState;
  notifications: NotificationState;
}

export interface NavigationState {
  currentRoute: string;
  params: any;
  history: NavigationHistory[];
  canGoBack: boolean;
  isTransitioning: boolean;
}

export interface NavigationHistory {
  route: string;
  params: any;
  timestamp: Date;
}

export interface Model3DState {
  currentModel: Model3D | null;
  models: Model3D[];
  favorites: string[];
  history: string[];
  downloadProgress: DownloadProgress[];
  renderProgress: RenderProgress[];
  viewerSettings: ViewerSettings;
}

export interface DownloadProgress {
  modelId: string;
  progress: number;
  speed: number;
  eta: number;
  size: number;
  downloaded: number;
}

export interface RenderProgress {
  modelId: string;
  progress: number;
  status: string;
  estimatedTime: number;
}

export interface ViewerSettings {
  quality: 'low' | 'medium' | 'high' | 'ultra';
  antialiasing: boolean;
  shadows: boolean;
  lighting: string;
  background: 'solid' | 'gradient' | 'hdri' | 'custom';
  controls: ViewerControls;
}

export interface ViewerControls {
  rotation: boolean;
  zoom: boolean;
  pan: boolean;
  autoRotate: boolean;
  frameSelection: boolean;
  resetCamera: boolean;
}

export interface UserState {
  profile: UserProfile | null;
  preferences: UserPreferences;
  session: UserSession | null;
  authStatus: 'authenticated' | 'anonymous' | 'expired';
  subscription: UserSubscription | null;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  preferences: UserPreferences;
  createdAt: Date;
  lastLogin: Date;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: boolean;
  analytics: boolean;
  location: boolean;
  camera: boolean;
  microphone: boolean;
  backgroundAppRefresh: boolean;
}

export interface UserSession {
  token: string;
  refreshToken: string;
  expiresAt: Date;
  userAgent: string;
  ip: string;
  location: UserLocation;
}

export interface UserLocation {
  country: string;
  region: string;
  city: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

export interface UserSubscription {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'expired' | 'cancelled' | 'pending';
  expiresAt: Date;
  autoRenew: boolean;
  features: string[];
  usage: SubscriptionUsage;
}

export interface SubscriptionUsage {
  modelsCreated: number;
  storageUsed: number;
  renderTime: number;
  collaborationTime: number;
  marketplacePurchases: number;
}

export interface SettingsState {
  app: AppSettings;
  privacy: PrivacySettings;
  notifications: NotificationSettings;
  display: DisplaySettings;
  performance: PerformanceSettings;
  network: NetworkSettings;
}

export interface AppSettings {
  version: string;
  build: string;
  language: string;
  region: string;
  timezone: string;
  autoUpdate: boolean;
  crashReporting: boolean;
  analytics: boolean;
  telemetry: boolean;
}

export interface PrivacySettings {
  dataCollection: boolean;
  locationTracking: boolean;
  advertising: boolean;
  personalizedAds: boolean;
  shareAnalytics: boolean;
  shareCrashReports: boolean;
}

export interface NotificationSettings {
  enabled: boolean;
  push: PushNotificationSettings;
  email: EmailNotificationSettings;
  inApp: InAppNotificationSettings;
}

export interface PushNotificationSettings {
  enabled: boolean;
  sound: boolean;
  vibration: boolean;
  badge: boolean;
  categories: PushCategory[];
}

export interface PushCategory {
  id: string;
  name: string;
  enabled: boolean;
  sound?: string;
  badge?: number;
}

export interface EmailNotificationSettings {
  enabled: boolean;
  marketing: boolean;
  updates: boolean;
  security: boolean;
  newsletters: boolean;
}

export interface InAppNotificationSettings {
  enabled: boolean;
  duration: number;
  position: 'top' | 'bottom' | 'center';
  sound: boolean;
  animation: boolean;
}

export interface DisplaySettings {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  contrast: 'normal' | 'high';
  reducedMotion: boolean;
  screenOn: boolean;
  orientation: 'auto' | 'portrait' | 'landscape';
}

export interface PerformanceSettings {
  quality: 'low' | 'medium' | 'high' | 'auto';
  batteryOptimization: boolean;
  dataSaving: boolean;
  prefetching: boolean;
  caching: boolean;
  lazyLoading: boolean;
}

export interface NetworkSettings {
  useMobileData: boolean;
  compression: boolean;
  prefetchOnWifi: boolean;
  backgroundSync: boolean;
  offlineMode: boolean;
}

export interface PerformanceState {
  metrics: PerformanceMetrics;
  alerts: PerformanceAlert[];
  optimization: PerformanceOptimization;
  profiling: ProfilingData;
}

export interface PerformanceMetrics {
  cpu: number;
  memory: MemoryMetrics;
  battery: BatteryMetrics;
  network: NetworkMetrics;
  rendering: RenderingMetrics;
  storage: StorageMetrics;
}

export interface MemoryMetrics {
  used: number;
  available: number;
  total: number;
  heapSize: number;
  heapUsed: number;
  heapFragmentation: number;
}

export interface BatteryMetrics {
  level: number;
  state: 'charging' | 'discharging' | 'full' | 'unknown';
  voltage: number;
  current: number;
  temperature: number;
  health: number;
  isLowPowerMode: boolean;
}

export interface NetworkMetrics {
  type: 'wifi' | 'cellular' | 'ethernet' | 'unknown';
  quality: 'poor' | 'good' | 'excellent';
  downloadSpeed: number;
  uploadSpeed: number;
  latency: number;
  signalStrength: number;
}

export interface RenderingMetrics {
  fps: number;
  frameTime: number;
  drawCalls: number;
  triangles: number;
  vertices: number;
  textureMemory: number;
  shaderTime: number;
}

export interface StorageMetrics {
  used: number;
  available: number;
  total: number;
  cacheSize: number;
  tempSize: number;
}

export interface PerformanceAlert {
  type: 'memory' | 'battery' | 'network' | 'rendering' | 'storage';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  threshold: number;
  value: number;
  timestamp: Date;
}

export interface PerformanceOptimization {
  enabled: boolean;
  features: OptimizationFeature[];
  autoAdjust: boolean;
  userControl: boolean;
}

export interface OptimizationFeature {
  name: string;
  enabled: boolean;
  impact: 'low' | 'medium' | 'high';
  description: string;
  settings: any;
}

export interface ProfilingData {
  enabled: boolean;
  intervals: ProfilingInterval[];
  sessions: ProfilingSession[];
  reports: ProfilingReport[];
}

export interface ProfilingInterval {
  start: Date;
  end: Date;
  metrics: PerformanceMetrics;
}

export interface ProfilingSession {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  features: string[];
  metrics: PerformanceMetrics[];
  events: ProfilingEvent[];
}

export interface ProfilingEvent {
  timestamp: Date;
  type: 'action' | 'performance' | 'error' | 'memory' | 'rendering';
  data: any;
}

export interface ProfilingReport {
  id: string;
  sessionId: string;
  generated: Date;
  summary: ReportSummary;
  details: ReportDetails;
  recommendations: ReportRecommendation[];
}

export interface ReportSummary {
  performance: number;
  battery: number;
  memory: number;
  network: number;
  overall: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
}

export interface ReportDetails {
  charts: ReportChart[];
  tables: ReportTable[];
  snapshots: ReportSnapshot[];
}

export interface ReportChart {
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter';
  data: any;
  description: string;
}

export interface ReportTable {
  title: string;
  columns: string[];
  rows: any[][];
  summary: string;
}

export interface ReportSnapshot {
  timestamp: Date;
  metrics: PerformanceMetrics;
  screenshot?: string;
}

export interface ReportRecommendation {
  priority: 'low' | 'medium' | 'high';
  category: string;
  title: string;
  description: string;
  action: string;
  impact: string;
}

export interface NetworkState {
  connectivity: 'connected' | 'disconnected' | 'connecting';
  type: NetworkType;
  quality: NetworkQuality;
  offline: OfflineState;
  requests: RequestState[];
}

export type NetworkType = 'wifi' | 'cellular' | 'ethernet' | 'bluetooth' | 'unknown';

export type NetworkQuality = 'poor' | 'fair' | 'good' | 'excellent';

export interface OfflineState {
  enabled: boolean;
  mode: 'read_only' | 'full' | 'sync';
  lastSync: Date;
  pendingChanges: number;
  conflicts: SyncConflict[];
}

export interface SyncConflict {
  id: string;
  type: 'model' | 'setting' | 'user_data';
  local: any;
  remote: any;
  resolution?: 'keep_local' | 'keep_remote' | 'merge' | 'manual';
}

export interface RequestState {
  id: string;
  url: string;
  method: string;
  status: 'pending' | 'success' | 'error' | 'cancelled';
  progress: number;
  speed: number;
  eta: number;
  error?: string;
}

export interface NotificationState {
  permissions: NotificationPermission[];
  settings: NotificationSettings;
  pending: PendingNotification[];
  history: NotificationHistory[];
}

export interface NotificationPermission {
  platform: 'ios' | 'android';
  status: 'granted' | 'denied' | 'limited' | 'not_determined' | 'provisional';
  type: 'alert' | 'badge' | 'sound' | 'provisional';
  requestable: boolean;
}

export interface PendingNotification {
  id: string;
  title: string;
  message: string;
  data: any;
  scheduledAt?: Date;
  category: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
}

export interface NotificationHistory {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  category: string;
  action: string;
  result: 'opened' | 'dismissed' | 'timed_out' | 'deleted';
}

// AR/VR Mobile Features
export interface ARFeatures {
  enabled: boolean;
  capabilities: ARCapability[];
  detection: ARDetection;
  anchors: ARAnchor[];
  lighting: ARLighting;
  occlusion: AROcclusion;
}

export interface ARCapability {
  type: 'plane_detection' | 'image_tracking' | 'object_detection' | 'face_tracking' | 'body_tracking' | 'environment_scanning';
  supported: boolean;
  enabled: boolean;
  accuracy: number;
  confidence: number;
}

export interface ARDetection {
  planes: ARPlane[];
  images: ARImage[];
  objects: ARObject[];
  faces: ARFace[];
  environments: AREnvironment[];
}

export interface ARPlane {
  id: string;
  center: Vector3;
  extent: Vector2;
  normal: Vector3;
  alignment: string;
  type: 'horizontal' | 'vertical' | 'arbitrary';
  anchor: ARAnchor;
}

export interface ARImage {
  id: string;
  referenceImage: string;
  transform: ARTransform;
  boundingBox: ARBoundingBox;
  physicalSize: Vector2;
  trackingState: 'tracking' | 'not_tracking' | 'stopped';
}

export interface ARObject {
  id: string;
  class: string;
  transform: ARTransform;
  confidence: number;
  boundingBox: ARBoundingBox;
  attributes: ARAttribute[];
}

export interface ARFace {
  id: string;
  anchors: ARAnchor[];
  blendShapes: ARBlendShape[];
  eyePositions: Vector3[];
  isTracked: boolean;
  lookAtPoint: Vector3;
}

export interface ARAttribute {
  name: string;
  value: any;
  confidence: number;
}

export interface AREnvironment {
  id: string;
  name: string;
  type: 'indoor' | 'outdoor' | 'mixed';
  lighting: ARLightingEstimate;
  geometry: ARGeometry;
  materials: ARMaterial[];
}

export interface ARTransform {
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  timestamp: Date;
}

export interface ARBoundingBox {
  center: Vector3;
  size: Vector3;
  corners: Vector3[];
}

export interface ARAnchor {
  id: string;
  transform: ARTransform;
  sessionIdentifier: string;
  trackingState: 'tracking' | 'not_tracking' | 'stopped';
  supportFaceTracking: boolean;
  supportEnvironmentTexture: boolean;
}

export interface ARLightingEstimate {
  lightEstimation: 'notAvailable' | 'estimated' | 'ambientIntensity' | 'directionalLight' | 'omnidirectionalLight';
  primaryLightDirection: Vector3;
  primaryLightIntensity: number;
  sphericalHarmonicsCoefficients: number[];
  ambientIntensity: number;
  ambientColorTemperature: number;
}

export interface ARGeometry {
  type: 'triangle' | 'point' | 'line';
  vertices: Vector3[];
  faces: number[][];
  edges: number[][];
  normals: Vector3[];
}

export interface ARMaterial {
  name: string;
  diffuse: Vector3;
  specular: Vector3;
  roughness: number;
  metallic: number;
  transparency: number;
}

export interface ARBlendShape {
  name: string;
  value: number;
}

export interface ARBoundingBox {
  center: Vector3;
  size: Vector3;
  corners: Vector3[];
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Vector2 {
  x: number;
  y: number;
}

export interface ARPlane {
  id: string;
  center: Vector3;
  extent: Vector2;
  normal: Vector3;
  alignment: string;
  type: 'horizontal' | 'vertical' | 'arbitrary';
  anchor: ARAnchor;
}

export interface ARImage {
  id: string;
  referenceImage: string;
  transform: ARTransform;
  boundingBox: ARBoundingBox;
  physicalSize: Vector2;
  trackingState: 'tracking' | 'not_tracking' | 'stopped';
}

export interface ARObject {
  id: string;
  class: string;
  transform: ARTransform;
  confidence: number;
  boundingBox: ARBoundingBox;
  attributes: ARAttribute[];
}

export interface ARFace {
  id: string;
  anchors: ARAnchor[];
  blendShapes: ARBlendShape[];
  eyePositions: Vector3[];
  isTracked: boolean;
  lookAtPoint: Vector3;
}

export interface ARAttribute {
  name: string;
  value: any;
  confidence: number;
}

export interface AREnvironment {
  id: string;
  name: string;
  type: 'indoor' | 'outdoor' | 'mixed';
  lighting: ARLightingEstimate;
  geometry: ARGeometry;
  materials: ARMaterial[];
}

export interface ARTransform {
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  timestamp: Date;
}

export interface ARBoundingBox {
  center: Vector3;
  size: Vector3;
  corners: Vector3[];
}

export interface ARAnchor {
  id: string;
  transform: ARTransform;
  sessionIdentifier: string;
  trackingState: 'tracking' | 'not_tracking' | 'stopped';
  supportFaceTracking: boolean;
  supportEnvironmentTexture: boolean;
}

export interface ARLightingEstimate {
  lightEstimation: 'notAvailable' | 'estimated' | 'ambientIntensity' | 'directionalLight' | 'omnidirectionalLight';
  primaryLightDirection: Vector3;
  primaryLightIntensity: number;
  sphericalHarmonicsCoefficients: number[];
  ambientIntensity: number;
  ambientColorTemperature: number;
}

export interface ARGeometry {
  type: 'triangle' | 'point' | 'line';
  vertices: Vector3[];
  faces: number[][];
  edges: number[][];
  normals: Vector3[];
}

export interface ARMaterial {
  name: string;
  diffuse: Vector3;
  specular: Vector3;
  roughness: number;
  metallic: number;
  transparency: number;
}

export interface ARBlendShape {
  name: string;
  value: number;
}

export interface VRFeatures {
  enabled: boolean;
  vrHeadsets: VRHeadset[];
  inputControllers: VRInputController[];
  tracking: VRTracking;
  performance: VRPerformance;
}

export interface VRHeadset {
  id: string;
  name: string;
  type: 'standalone' | 'pc' | 'console' | 'mobile';
  display: VRDisplay;
  tracking: VRHeadsetTracking;
  ergonomics: VRErgonomics;
  features: string[];
}

export interface VRDisplay {
  resolution: Vector2;
  refreshRate: number;
  fov: number;
  pixelsPerDegree: number;
  distortion: VRDistortion;
}

export interface VRDistortion {
  radialDistortion: number;
  chromaticAberration: boolean;
  timeWarp: boolean;
  advancedDistortion: boolean;
}

export interface VRHeadsetTracking {
  positionTracking: boolean;
  rotationTracking: boolean;
  eyeTracking: boolean;
  faceTracking: boolean;
  roomScale: boolean;
  insideOutTracking: boolean;
  outsideInTracking: boolean;
  lighthouses: boolean;
  baseStations: boolean;
}

export interface VRErgonomics {
  weight: number;
  weightDistribution: string;
  strapSystem: string;
  ipdRange: Vector2;
  lensType: 'fresnel' | 'pancake' | 'catadioptric';
  ventilation: 'none' | 'passive' | 'active';
}

export interface VRInputController {
  id: string;
  type: 'wand' | 'touchpad' | 'gamepad' | 'leap' | 'data_glove' | 'eyetracking';
  hands: 'left' | 'right' | 'both';
  tracking: VRControllerTracking;
  features: VRControllerFeature[];
  haptic: VRHapticFeedback;
}

export interface VRControllerTracking {
  position: boolean;
  rotation: boolean;
  fingerTracking: boolean;
  forceFeedback: boolean;
  tactileFeedback: boolean;
  velocity: boolean;
  acceleration: boolean;
}

export interface VRControllerFeature {
  type: 'button' | 'trigger' | 'thumbstick' | 'touchpad' | 'gesture' | 'force';
  count: number;
  description: string;
}

export interface VRHapticFeedback {
  enabled: boolean;
  intensity: number;
  frequency: number;
  patterns: HapticPattern[];
}

export interface HapticPattern {
  name: string;
  duration: number;
  intensity: number;
  waveform: 'sine' | 'square' | 'sawtooth' | 'triangle';
  envelope: HapticEnvelope;
}

export interface HapticEnvelope {
  attack: number;
  sustain: number;
  release: number;
  peak: number;
}

export interface VRTracking {
  roomScale: VRRoomScale;
  worldScale: VRWorldScale;
  calibration: VRCalibration;
  accuracy: VRTrackingAccuracy;
}

export interface VRRoomScale {
  enabled: boolean;
  playAreaSize: Vector2;
  playAreaBounds: Vector2[];
  safetyZones: VRSafetyZone[];
  guardianSystem: boolean;
}

export interface VRSafetyZone {
  name: string;
  bounds: Vector2[];
  type: 'safe' | 'caution' | 'danger';
  visual: VRZoneVisual;
}

export interface VRZoneVisual {
  color: string;
  opacity: number;
  pattern: 'solid' | 'stripes' | 'checkered' | 'dots';
  height: number;
}

export interface VRWorldScale {
  enabled: boolean;
  realWorldScale: number;
  virtualScale: number;
  scaleFactor: number;
  unitSystem: 'metric' | 'imperial';
}

export interface VRCalibration {
  required: boolean;
  type: 'manual' | 'automatic' | 'guided';
  steps: CalibrationStep[];
  lastCalibration: Date;
}

export interface CalibrationStep {
  name: string;
  description: string;
  duration: number;
  completed: boolean;
  error?: string;
}

export interface VRTrackingAccuracy {
  position: number;
  rotation: number;
  latency: number;
  drift: number;
  jitter: number;
  confidence: number;
}

export interface VRPerformance {
  targetFPS: number;
  performanceLevel: 'low' | 'medium' | 'high' | 'ultra';
  supersampling: number;
  foveatedRendering: boolean;
  adaptiveQuality: boolean;
  motionSmoothing: boolean;
  fixedFoveatedRendering: boolean;
  dynamicFoveatedRendering: boolean;
}

// App Store and Publishing
export interface AppStoreSubmission {
  id: string;
  platform: 'ios' | 'android';
  build: string;
  status: 'draft' | 'submitted' | 'in_review' | 'approved' | 'rejected' | 'live' | 'suspended';
  submittedAt?: Date;
  approvedAt?: Date;
  rejectionReason?: string;
  metadata: SubmissionMetadata;
  review: SubmissionReview;
  screenshots: ScreenshotSubmission[];
  releaseNotes: ReleaseNotes[];
}

export interface SubmissionMetadata {
  version: string;
  buildNumber: string;
  category: string;
  contentRating: string;
  keywords: string[];
  description: string;
  shortDescription: string;
  features: string[];
  whatsNew: string;
  ageRating: AgeRating;
  localizations: LocalizationMetadata[];
}

export interface AgeRating {
  ios: AgeRatingIOS;
  android: AgeRatingAndroid;
  contentDescriptors: string[];
}

export interface AgeRatingIOS {
  code: string;
  level: number;
  descriptors: string[];
  descriptions: string[];
}

export interface AgeRatingAndroid {
  rating: string;
  age: number;
  categories: string[];
}

export interface LocalizationMetadata {
  language: string;
  country: string;
  description: string;
  shortDescription: string;
  keywords: string[];
  whatsNew: string;
  supportUrl?: string;
  marketingUrl?: string;
  privacyUrl: string;
}

export interface SubmissionReview {
  assignedTo?: string;
  priority: 'low' | 'normal' | 'high';
  contactEmail: string;
  demoAccount?: DemoAccount;
  specialInstructions?: string;
  reviewNotes: ReviewNote[];
}

export interface DemoAccount {
  username: string;
  password: string;
  instructions: string;
  testData: any;
}

export interface ReviewNote {
  timestamp: Date;
  reviewer: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'question';
  resolved: boolean;
}

export interface ScreenshotSubmission {
  platform: 'iphone' | 'ipad' | 'android_phone' | 'android_tablet';
  orientation: 'portrait' | 'landscape';
  device: string;
  size: string;
  url: string;
  description?: string;
  featured: boolean;
  position: number;
}

export interface ReleaseNotes {
  version: string;
  notes: string[];
  newFeatures: string[];
  bugFixes: string[];
  improvements: string[];
  breakingChanges: string[];
  locale: string;
}

// Mobile App Analytics
export interface MobileAnalytics {
  usage: UsageAnalytics;
  performance: PerformanceAnalytics;
  user: UserAnalytics;
  device: DeviceAnalytics;
  retention: RetentionAnalytics;
  funnel: FunnelAnalytics;
  cohorts: CohortAnalytics;
  attribution: AttributionAnalytics;
  revenue: RevenueAnalytics;
  crash: CrashAnalytics;
}

export interface UsageAnalytics {
  sessions: number;
  sessionLength: number;
  pageViews: number;
  featureUsage: FeatureUsage[];
  userFlows: UserFlow[];
  events: EventAnalytics[];
  funnels: FunnelAnalytics;
}

export interface FeatureUsage {
  feature: string;
  usage: number;
  sessions: number;
  retention: number;
  engagement: number;
}

export interface UserFlow {
  name: string;
  steps: UserFlowStep[];
  conversion: number;
  dropoffs: number;
}

export interface UserFlowStep {
  step: string;
  users: number;
  dropoff: number;
  timeSpent: number;
}

export interface EventAnalytics {
  event: string;
  count: number;
  uniqueUsers: number;
  properties: EventProperty[];
  triggered: TriggerEvent[];
}

export interface EventProperty {
  name: string;
  value: any;
  count: number;
  unique: number;
}

export interface TriggerEvent {
  event: string;
  userId?: string;
  sessionId?: string;
  timestamp: Date;
  properties: any;
}

export interface PerformanceAnalytics {
  loadTime: PerformanceMetric[];
  rendering: PerformanceMetric[];
  network: PerformanceMetric[];
  memory: PerformanceMetric[];
  battery: PerformanceMetric[];
  crashes: CrashAnalytics;
  anr: ANRAnalytics;
  slowFrames: SlowFrameAnalytics;
}

export interface PerformanceMetric {
  metric: string;
  value: number;
  unit: string;
  percentile: number;
  target: number;
  trend: 'improving' | 'degrading' | 'stable';
}

export interface CrashAnalytics {
  totalCrashes: number;
  crashRate: number;
  topCrashes: TopCrash[];
  stackTraces: StackTrace[];
  affectedUsers: number;
  resolved: number;
  resolution: CrashResolution[];
}

export interface TopCrash {
  reason: string;
  stackTrace: string;
  count: number;
  affectedUsers: number;
  firstCrash: Date;
  lastCrash: Date;
  fixAvailable: boolean;
}

export interface StackTrace {
  class: string;
  method: string;
  file: string;
  line: number;
  count: number;
  percentage: number;
}

export interface CrashResolution {
  type: 'fixed' | 'workaround' | 'no_action';
  resolution: string;
  fixVersion: string;
  resolved: Date;
}

export interface ANRAnalytics {
  totalANRs: number;
  anrRate: number;
  topANRs: TopANR[];
  affectedUsers: number;
  averageANRDuration: number;
}

export interface TopANR {
  reason: string;
  stackTrace: string;
  count: number;
  affectedUsers: number;
  duration: number;
}

export interface SlowFrameAnalytics {
  totalSlowFrames: number;
  slowFrameRate: number;
  averageFrameTime: number;
  frameDrops: number;
  affectedUsers: number;
  byComponent: FrameDropComponent[];
}

export interface FrameDropComponent {
  component: string;
  slowFrames: number;
  percentage: number;
  mainThreadTime: number;
}

export interface UserAnalytics {
  demographics: Demographics;
  behavior: UserBehavior;
  engagement: UserEngagement;
  satisfaction: UserSatisfaction;
  feedback: UserFeedback[];
}

export interface Demographics {
  age: AgeDistribution;
  gender: GenderDistribution;
  location: LocationDistribution;
  device: DeviceDistribution;
  appVersion: AppVersionDistribution;
}

export interface AgeDistribution {
  ranges: AgeRange[];
  median: number;
  average: number;
}

export interface AgeRange {
  range: string;
  users: number;
  percentage: number;
}

export interface GenderDistribution {
  male: number;
  female: number;
  other: number;
  unknown: number;
  percentage: number;
}

export interface LocationDistribution {
  countries: CountryUsage[];
  regions: RegionUsage[];
  cities: CityUsage[];
}

export interface CountryUsage {
  country: string;
  users: number;
  percentage: number;
  growth: number;
}

export interface RegionUsage {
  region: string;
  users: number;
  percentage: number;
}

export interface CityUsage {
  city: string;
  users: number;
  percentage: number;
}

export interface DeviceDistribution {
  devices: DeviceUsage[];
  screenSizes: ScreenSizeDistribution[];
  operatingSystems: OperatingSystemDistribution[];
}

export interface DeviceUsage {
  device: string;
  manufacturer: string;
  users: number;
  percentage: number;
}

export interface ScreenSizeDistribution {
  resolution: string;
  width: number;
  height: number;
  users: number;
  percentage: number;
}

export interface OperatingSystemDistribution {
  os: string;
  version: string;
  users: number;
  percentage: number;
  growth: number;
}

export interface AppVersionDistribution {
  version: string;
  users: number;
  percentage: number;
  releaseDate: Date;
}

export interface UserBehavior {
  sessionLength: SessionLengthDistribution;
  frequency: UserFrequency;
  retention: UserRetention;
  churn: UserChurn;
}

export interface SessionLengthDistribution {
  ranges: SessionLengthRange[];
  median: number;
  average: number;
  total: number;
}

export interface SessionLengthRange {
  range: string;
  sessions: number;
  percentage: number;
}

export interface UserFrequency {
  daily: UserFrequencyMetric;
  weekly: UserFrequencyMetric;
  monthly: UserFrequencyMetric;
}

export interface UserFrequencyMetric {
  activeUsers: number;
  totalUsers: number;
  percentage: number;
  newUsers: number;
  returningUsers: number;
}

export interface UserRetention {
  day1: number;
  day7: number;
  day14: number;
  day30: number;
  day90: number;
  day180: number;
  day365: number;
  cohorts: RetentionCohort[];
}

export interface RetentionCohort {
  cohortDate: Date;
  users: number;
  retention: RetentionPeriod[];
}

export interface RetentionPeriod {
  day: number;
  users: number;
  retentionRate: number;
}

export interface UserChurn {
  rate: number;
  reasons: ChurnReason[];
  timeToChurn: number;
  predicted: ChurnPrediction[];
}

export interface ChurnReason {
  reason: string;
  users: number;
  percentage: number;
  impact: 'low' | 'medium' | 'high';
}

export interface ChurnPrediction {
  userId: string;
  score: number;
  probability: number;
  factors: ChurnFactor[];
}

export interface ChurnFactor {
  factor: string;
  weight: number;
  impact: number;
}

export interface UserEngagement {
  timeSpent: TimeSpentMetrics;
  featuresUsed: FeatureEngagement[];
  contentConsumed: ContentEngagement[];
  social: SocialEngagement;
}

export interface TimeSpentMetrics {
  total: number;
  average: number;
  median: number;
  distribution: TimeSpentDistribution[];
  bySession: SessionTimeSpent[];
}

export interface TimeSpentDistribution {
  ranges: TimeSpentRange[];
}

export interface TimeSpentRange {
  range: string;
  users: number;
  percentage: number;
}

export interface SessionTimeSpent {
  date: Date;
  sessionId: string;
  duration: number;
  screens: number;
  features: string[];
}

export interface FeatureEngagement {
  feature: string;
  users: number;
  sessions: number;
  averageUse: number;
  retention: number;
  satisfaction: number;
}

export interface ContentEngagement {
  contentType: string;
  views: number;
  averageTime: number;
  completionRate: number;
  shares: number;
  comments: number;
}

export interface SocialEngagement {
  shares: number;
  comments: number;
  mentions: number;
  hashtags: HashtagUsage[];
  referral: ReferralData[];
}

export interface HashtagUsage {
  hashtag: string;
  usage: number;
  engagement: number;
}

export interface ReferralData {
  source: string;
  clicks: number;
  installs: number;
  conversion: number;
  revenue: number;
}

export interface UserSatisfaction {
  rating: number;
  reviews: number;
  positive: number;
  negative: number;
  trends: SatisfactionTrend[];
  feedback: SatisfactionFeedback[];
}

export interface SatisfactionTrend {
  date: Date;
  rating: number;
  reviews: number;
  sentiment: 'positive' | 'neutral' | 'negative';
}

export interface SatisfactionFeedback {
  userId: string;
  rating: number;
  comment: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  timestamp: Date;
  category: string;
  resolved: boolean;
}

export interface UserFeedback {
  id: string;
  userId: string;
  type: 'bug' | 'feature_request' | 'complaint' | 'compliment' | 'question';
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'acknowledged' | 'in_progress' | 'resolved' | 'closed';
  assignedTo?: string;
  tags: string[];
  attachments: FeedbackAttachment[];
  metadata: FeedbackMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface FeedbackAttachment {
  id: string;
  type: 'screenshot' | 'video' | 'log' | 'file';
  url: string;
  name: string;
  size: number;
  mimeType: string;
}

export interface FeedbackMetadata {
  appVersion: string;
  deviceInfo: string;
  osVersion: string;
  userAgent: string;
  sessionId: string;
  page?: string;
  feature?: string;
  error?: string;
}

export interface DeviceAnalytics {
  devices: DeviceMetrics[];
  performance: DevicePerformance[];
  compatibility: CompatibilityMetrics;
}

export interface DeviceMetrics {
  device: string;
  manufacturer: string;
  model: string;
  os: string;
  version: string;
  users: number;
  sessions: number;
  crashRate: number;
  anrRate: number;
  performance: DevicePerformanceMetrics;
}

export interface DevicePerformanceMetrics {
  averageLoadTime: number;
  averageMemoryUsage: number;
  averageBatteryUsage: number;
  averageFPS: number;
  networkUsage: number;
  storageUsage: number;
}

export interface DevicePerformance {
  device: string;
  metrics: PerformanceMetrics;
  distribution: PerformanceDistribution[];
  trends: PerformanceTrend[];
}

export interface PerformanceDistribution {
  metric: string;
  value: number;
  percentile: number;
  unit: string;
}

export interface PerformanceTrend {
  metric: string;
  trend: 'improving' | 'degrading' | 'stable';
  change: number;
  period: string;
}

export interface CompatibilityMetrics {
  supported: CompatibilityLevel[];
  issues: CompatibilityIssue[];
  features: FeatureCompatibility[];
}

export interface CompatibilityLevel {
  level: 'excellent' | 'good' | 'fair' | 'poor' | 'unsupported';
  devices: number;
  percentage: number;
  threshold: number;
}

export interface CompatibilityIssue {
  issue: string;
  devices: string[];
  impact: 'low' | 'medium' | 'high';
  severity: 'minor' | 'major' | 'critical';
  frequency: number;
  workaround?: string;
}

export interface FeatureCompatibility {
  feature: string;
  supported: number;
  unsupported: number;
  partiallySupported: number;
  devices: CompatibilityDevice[];
}

export interface CompatibilityDevice {
  device: string;
  status: 'supported' | 'unsupported' | 'limited';
  limitations: string[];
  workarounds: string[];
}

export interface RetentionAnalytics {
  cohorts: CohortAnalytics;
  cohortsDetailed: DetailedCohort[];
  retentionPredictive: PredictiveRetention[];
  retentionMarketing: MarketingRetention[];
}

export interface CohortAnalytics {
  cohorts: RetentionCohort[];
  globalRetention: GlobalRetention;
  cohortComparison: CohortComparison[];
  insights: RetentionInsight[];
}

export interface RetentionCohort {
  cohort: string;
  users: number;
  retention: RetentionMetric[];
  size: number;
  revenue: number;
}

export interface RetentionMetric {
  period: string;
  users: number;
  retentionRate: number;
  revenue: number;
  avgRevenue: number;
  ltv: number;
}

export interface GlobalRetention {
  day1: number;
  day7: number;
  day14: number;
  day30: number;
  day90: number;
  day180: number;
  day365: number;
}

export interface CohortComparison {
  cohort1: string;
  cohort2: string;
  comparison: CohortComparisonData;
  significance: number;
}

export interface CohortComparisonData {
  day1: number;
  day7: number;
  day30: number;
  overall: number;
  improvement: number;
}

export interface RetentionInsight {
  type: 'trend' | 'anomaly' | 'opportunity' | 'risk';
  title: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
  recommendation: string;
  data: any;
}

export interface DetailedCohort {
  cohortId: string;
  startDate: Date;
  users: number;
  demographics: CohortDemographics;
  behavior: CohortBehavior;
  retention: CohortRetentionDetails;
  revenue: CohortRevenue;
  features: CohortFeatureUsage;
}

export interface CohortDemographics {
  age: CohortAgeDistribution;
  gender: CohortGenderDistribution;
  location: CohortLocationDistribution;
  device: CohortDeviceDistribution;
}

export interface CohortAgeDistribution {
  ranges: CohortAgeRange[];
  median: number;
}

export interface CohortAgeRange {
  range: string;
  users: number;
  percentage: number;
}

export interface CohortGenderDistribution {
  male: number;
  female: number;
  other: number;
  unknown: number;
}

export interface CohortLocationDistribution {
  countries: CohortCountryUsage[];
  regions: CohortRegionUsage[];
}

export interface CohortCountryUsage {
  country: string;
  users: number;
  percentage: number;
}

export interface CohortRegionUsage {
  region: string;
  users: number;
  percentage: number;
}

export interface CohortDeviceDistribution {
  devices: CohortDeviceUsage[];
  os: CohortOSUsage[];
}

export interface CohortDeviceUsage {
  device: string;
  users: number;
  percentage: number;
}

export interface CohortOSUsage {
  os: string;
  version: string;
  users: number;
  percentage: number;
}

export interface CohortBehavior {
  acquisition: AcquisitionBehavior;
  engagement: CohortEngagement;
  monetization: CohortMonetization;
}

export interface AcquisitionBehavior {
  source: string[];
  campaign: string[];
  keyword: string[];
  referrer: string[];
  social: string[];
  organic: boolean;
  paid: boolean;
  feature_flags: string[];
}

export interface CohortEngagement {
  sessions: EngagementMetrics;
  timeSpent: TimeSpentMetrics;
  features: CohortFeatureEngagement[];
  content: CohortContentEngagement[];
}

export interface EngagementMetrics {
  total: number;
  perUser: number;
  frequency: number;
  patterns: EngagementPattern[];
}

export interface EngagementPattern {
  pattern: string;
  users: number;
  frequency: number;
  retention: number;
}

export interface CohortFeatureEngagement {
  feature: string;
  users: number;
  sessions: number;
  averageUse: number;
  retention: number;
  satisfaction: number;
}

export interface CohortContentEngagement {
  contentType: string;
  views: number;
  timeSpent: number;
  completion: number;
  sharing: number;
}

export interface CohortMonetization {
  conversion: CohortConversion;
  revenue: CohortRevenue;
  pricing: CohortPricing;
  subscription: CohortSubscription;
}

export interface CohortConversion {
  freeToPaid: number;
  trialToPaid: number;
  trial: number;
  freemium: number;
  paid: number;
  upgrade: number;
  downgrade: number;
  cancellation: number;
}

export interface CohortRevenue {
  total: number;
  perUser: number;
  bySource: RevenueBySource[];
  byPeriod: RevenueByPeriod[];
  ltv: number;
  ltvByCohort: number;
  churnRevenue: number;
}

export interface RevenueBySource {
  source: string;
  revenue: number;
  users: number;
  arpu: number;
  conversion: number;
}

export interface RevenueByPeriod {
  period: string;
  revenue: number;
  users: number;
  arpu: number;
  mrr: number;
}

export interface CohortPricing {
  plan: string;
  users: number;
  revenue: number;
  avgPrice: number;
  conversion: number;
  retention: number;
}

export interface CohortSubscription {
  plan: string;
  status: string;
  duration: number;
  renewal: boolean;
  upgrade: boolean;
  churn: boolean;
}

export interface CohortRetentionDetails {
  retention: RetentionMetrics[];
  dropoffs: DropoffAnalysis[];
  reactivation: ReactivationAnalysis[];
  predicted: RetentionPrediction[];
}

export interface DropoffAnalysis {
  day: number;
  users: number;
  dropoffRate: number;
  reasons: DropoffReason[];
  interventions: Intervention[];
}

export interface DropoffReason {
  reason: string;
  users: number;
  impact: number;
  actionable: boolean;
}

export interface Intervention {
  type: 'email' | 'notification' | 'personal_contact' | 'feature_unlock';
  success: number;
  cost: number;
  roi: number;
}

export interface ReactivationAnalysis {
  period: string;
  reactivatedUsers: number;
  timeToReactivate: number;
  channels: ReactivationChannel[];
  success: number;
  cost: number;
}

export interface ReactivationChannel {
  channel: string;
  users: number;
  success: number;
  cost: number;
  roi: number;
}

export interface RetentionPrediction {
  userId: string;
  score: number;
  risk: number;
  probability: number;
  factors: RetentionFactor[];
  recommendedAction: string;
  priority: 'low' | 'medium' | 'high';
}

export interface RetentionFactor {
  factor: string;
  weight: number;
  impact: number;
  direction: 'positive' | 'negative';
}

export interface CohortFeatureUsage {
  features: CohortFeature[];
  correlation: FeatureCorrelation[];
  segmentation: FeatureSegmentation[];
}

export interface CohortFeature {
  feature: string;
  usage: number;
  adoption: number;
  retention: number;
  revenue: number;
  correlation: number;
}

export interface FeatureCorrelation {
  feature1: string;
  feature2: string;
  correlation: number;
  significance: number;
  strength: 'weak' | 'moderate' | 'strong';
}

export interface FeatureSegmentation {
  segment: string;
  features: string[];
  usage: number;
  retention: number;
  revenue: number;
  size: number;
}

export interface PredictiveRetention {
  userId: string;
  cohortId: string;
  prediction: RetentionPredictionModel;
  confidence: number;
  factors: PredictiveFactor[];
  recommendations: RetentionRecommendation[];
}

export interface RetentionPredictionModel {
  day7: number;
  day30: number;
  day90: number;
  day180: number;
  day365: number;
  riskLevel: 'low' | 'medium' | 'high';
  probability: number;
}

export interface PredictiveFactor {
  factor: string;
  importance: number;
  impact: number;
  direction: 'positive' | 'negative';
  description: string;
}

export interface RetentionRecommendation {
  type: 'feature_unlock' | 'communication' | 'discount' | 'feature_tour' | 'support';
  priority: 'low' | 'medium' | 'high';
  expectedImpact: number;
  cost: number;
  roi: number;
  successRate: number;
}

export interface MarketingRetention {
  campaigns: MarketingCampaign[];
  segments: MarketingSegment[];
  experiments: MarketingExperiment[];
  attribution: AttributionModel;
}

export interface MarketingCampaign {
  id: string;
  name: string;
  type: 'email' | 'push' | 'in_app' | 'social' | 'paid_ads';
  target: MarketingTarget;
  content: MarketingContent;
  targeting: MarketingTargeting;
  performance: MarketingPerformance;
}

export interface MarketingTarget {
  segment: string[];
  behavior: string[];
  demographics: string[];
  devices: string[];
  locations: string[];
}

export interface MarketingContent {
  subject: string;
  message: string;
  image: string;
  callToAction: string;
  personalization: PersonalizationOption[];
}

export interface PersonalizationOption {
  field: string;
  value: any;
  fallback: string;
}

export interface MarketingTargeting {
  budget: number;
  startDate: Date;
  endDate: Date;
  frequency: number;
  channel: string;
  placement: string;
}

export interface MarketingPerformance {
  users: number;
  engagement: number;
  conversion: number;
  retention: number;
  revenue: number;
  roi: number;
  cost: number;
  costPerUser: number;
  costPerConversion: number;
}

export interface MarketingSegment {
  name: string;
  criteria: SegmentCriteria[];
  users: number;
  characteristics: SegmentCharacteristics;
  behavior: SegmentBehavior;
  performance: SegmentPerformance;
}

export interface SegmentCriteria {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  value: any;
}

export interface SegmentCharacteristics {
  demographics: Demographics;
  devices: DeviceDistribution;
  location: LocationDistribution;
  acquisition: AcquisitionBehavior;
}

export interface SegmentBehavior {
  engagement: EngagementMetrics;
  features: FeatureEngagement[];
  monetization: CohortMonetization;
}

export interface SegmentPerformance {
  revenue: number;
  retention: number;
  conversion: number;
  lifetime: number;
  satisfaction: number;
}

export interface MarketingExperiment {
  name: string;
  hypothesis: string;
  variables: ExperimentVariable[];
  control: string;
  variants: ExperimentVariant[];
  metrics: ExperimentMetric[];
  results: ExperimentResult[];
}

export interface ExperimentVariable {
  name: string;
  type: 'feature' | 'content' | 'pricing' | 'targeting' | 'timing';
  values: string[];
  allocation: number[];
}

export interface ExperimentVariant {
  name: string;
  description: string;
  allocation: number;
  users: number;
  metrics: VariantMetrics;
}

export interface VariantMetrics {
  primary: number;
  secondary: number[];
  conversion: number;
  retention: number;
  revenue: number;
  engagement: number;
  satisfaction: number;
}

export interface ExperimentMetric {
  name: string;
  type: 'primary' | 'secondary' | 'guardrail';
  definition: string;
  calculation: string;
  target: number;
  threshold: number;
}

export interface ExperimentResult {
  variant: string;
  metric: string;
  value: number;
  confidence: number;
  significance: number;
  winner: boolean;
  recommendation: string;
}

export interface AttributionModel {
  model: 'last_click' | 'first_click' | 'linear' | 'time_decay' | 'position_based' | 'u_shaped' | 'data_driven';
  lookback: number;
  channels: AttributionChannel[];
  touchpoints: Touchpoint[];
}

export interface AttributionChannel {
  name: string;
  weight: number;
  conversionRate: number;
  cost: number;
  roi: number;
}

export interface Touchpoint {
  userId: string;
  sessionId: string;
  timestamp: Date;
  channel: string;
  campaign: string;
  campaignId: string;
  sessionData: any;
}

export interface FunnelAnalytics {
  funnels: FunnelAnalysis[];
  steps: FunnelStepAnalysis[];
  optimization: FunnelOptimization[];
  predictions: FunnelPrediction[];
}

export interface FunnelAnalysis {
  funnel: string;
  steps: FunnelStepMetrics[];
  conversion: FunnelConversion;
  dropoffs: FunnelDropoff[];
  optimization: FunnelOptimizationOpportunity[];
  segments: FunnelSegmentAnalysis[];
}

export interface FunnelStepMetrics {
  step: string;
  users: number;
  conversionRate: number;
  timeSpent: number;
  completionRate: number;
  dropoffRate: number;
  success: number;
}

export interface FunnelConversion {
  overall: number;
  byChannel: ConversionByChannel[];
  byDevice: ConversionByDevice[];
  bySegment: ConversionBySegment[];
  byTime: ConversionByTime[];
}

export interface ConversionByChannel {
  channel: string;
  conversion: number;
  users: number;
  revenue: number;
}

export interface ConversionByDevice {
  device: string;
  conversion: number;
  users: number;
  performance: number;
}

export interface ConversionBySegment {
  segment: string;
  conversion: number;
  users: number;
  characteristics: any;
}

export interface ConversionByTime {
  time: string;
  conversion: number;
  users: number;
  patterns: any;
}

export interface FunnelDropoff {
  step: number;
  fromStep: string;
  toStep: string;
  users: number;
  dropoffRate: number;
  reasons: DropoffReasonAnalysis[];
  cost: number;
  impact: number;
}

export interface DropoffReasonAnalysis {
  reason: string;
  frequency: number;
  users: number;
  severity: 'low' | 'medium' | 'high';
  actionable: boolean;
  recommendations: string[];
}

export interface FunnelOptimizationOpportunity {
  step: string;
  improvement: number;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  confidence: number;
  recommendations: OptimizationRecommendation[];
  projected: ProjectedImprovement[];
}

export interface OptimizationRecommendation {
  type: 'ui_change' | 'content_optimization' | 'pricing_change' | 'targeting_change' | 'timing_change';
  description: string;
  expectedImpact: number;
  implementation: ImplementationDetails;
  cost: number;
  roi: number;
}

export interface ImplementationDetails {
  effort: 'low' | 'medium' | 'high';
  time: number;
  resources: string[];
  dependencies: string[];
  risks: string[];
}

export interface ProjectedImprovement {
  metric: string;
  current: number;
  projected: number;
  improvement: number;
  confidence: number;
  timeframe: string;
}

export interface FunnelSegmentAnalysis {
  segment: string;
  characteristics: SegmentCharacteristics;
  performance: SegmentPerformanceMetrics;
  conversion: SegmentConversion;
  recommendations: SegmentRecommendation[];
}

export interface SegmentCharacteristics {
  demographics: Demographics;
  behavior: BehaviorCharacteristics;
  device: DeviceDistribution;
  location: LocationDistribution;
}

export interface BehaviorCharacteristics {
  usage_patterns: string[];
  engagement_level: string;
  feature_usage: string[];
  monetization_behavior: string;
}

export interface SegmentPerformanceMetrics {
  conversion: number;
  retention: number;
  revenue: number;
  engagement: number;
  satisfaction: number;
  time_spent: number;
}

export interface SegmentConversion {
  overall: number;
  by_step: SegmentStepConversion[];
  rate_limiters: string[];
  opportunities: string[];
}

export interface SegmentStepConversion {
  step: string;
  conversion: number;
  relative_performance: number;
  issues: string[];
}

export interface SegmentRecommendation {
  type: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  expected_impact: number;
  implementation: SegmentImplementation;
}

export interface SegmentImplementation {
  effort: 'low' | 'medium' | 'high';
  timeline: string;
  resources: string[];
  risks: string[];
}

export interface FunnelStepAnalysis {
  step: string;
  analysis: StepAnalysis;
  optimization: StepOptimization;
  prediction: StepPrediction;
}

export interface StepAnalysis {
  performance: StepPerformance;
  issues: StepIssue[];
  opportunities: StepOpportunity[];
  comparison: StepComparison[];
}

export interface StepPerformance {
  conversion: number;
  timeSpent: number;
  satisfaction: number;
  errors: number;
  abandonment: number;
  bounce: number;
  errors: number;
}

export interface StepIssue {
  issue: string;
  severity: 'low' | 'medium' | 'high';
  impact: number;
  frequency: number;
  users: number;
  solution: string;
  cost: number;
}

export interface StepOpportunity {
  opportunity: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  confidence: number;
  description: string;
  implementation: ImplementationPlan;
}

export interface ImplementationPlan {
  steps: ImplementationStep[];
  timeline: string;
  resources: string[];
  dependencies: string[];
  risks: string[];
  milestones: Milestone[];
}

export interface ImplementationStep {
  step: string;
  description: string;
  duration: number;
  resources: string[];
  deliverable: string;
  success_criteria: string[];
}

export interface Milestone {
  name: string;
  date: Date;
  description: string;
  success_criteria: string[];
  dependencies: string[];
}

export interface StepComparison {
  comparison: string;
  benchmark: number;
  current: number;
  difference: number;
  percentile: number;
  ranking: number;
  trend: 'improving' | 'degrading' | 'stable';
}

export interface StepOptimization {
  improvements: StepImprovement[];
  a_b_tests: ABTest[];
  personalization: PersonalizationStrategy[];
  automation: AutomationOpportunity[];
}

export interface StepImprovement {
  type: 'ui_ux' | 'content' | 'performance' | 'functionality' | 'accessibility';
  description: string;
  expected_impact: number;
  implementation: ImplementationDetails;
  priority: 'low' | 'medium' | 'high';
  roi: number;
}

export interface ABTest {
  name: string;
  hypothesis: string;
  variants: TestVariant[];
  metrics: TestMetric[];
  allocation: number[];
  duration: number;
  sample_size: number;
}

export interface TestVariant {
  name: string;
  description: string;
  changes: TestChange[];
  allocation: number;
  expected_impact: number;
}

export interface TestChange {
  element: string;
  change: string;
  rationale: string;
  expected_impact: number;
}

export interface TestMetric {
  name: string;
  type: 'primary' | 'secondary' | 'guardrail';
  definition: string;
  target: number;
  threshold: number;
}

export interface PersonalizationStrategy {
  segment: string;
  rules: PersonalizationRule[];
  content: PersonalizedContent[];
  expected_impact: number;
  implementation: PersonalizationImplementation;
}

export interface PersonalizationRule {
  condition: string;
  action: string;
  priority: number;
  fallback: string;
}

export interface PersonalizedContent {
  variant: string;
  content: string;
  targeting: string;
  personalization_level: 'low' | 'medium' | 'high';
}

export interface PersonalizationImplementation {
  technology: string;
  effort: 'low' | 'medium' | 'high';
  integration: string[];
  maintenance: string[];
  cost: number;
}

export interface AutomationOpportunity {
  process: string;
  automation_level: 'full' | 'partial' | 'manual';
  benefit: number;
  effort: 'low' | 'medium' | 'high';
  technology: string;
  implementation: AutomationImplementation;
}

export interface AutomationImplementation {
  tools: string[];
  integration: string[];
  training: string[];
  maintenance: string[];
  timeline: string;
}

export interface StepPrediction {
  trend: StepTrend;
  forecast: StepForecast;
  risk: StepRisk;
  opportunity: StepOpportunityPrediction;
}

export interface StepTrend {
  direction: 'improving' | 'degrading' | 'stable';
  strength: 'weak' | 'moderate' | 'strong';
  confidence: number;
  timeframe: string;
  factors: TrendFactor[];
}

export interface TrendFactor {
  factor: string;
  influence: number;
  direction: 'positive' | 'negative';
  impact: number;
}

export interface StepForecast {
  short_term: number;
  medium_term: number;
  long_term: number;
  accuracy: number;
  confidence: number;
  scenarios: ForecastScenario[];
}

export interface ForecastScenario {
  scenario: 'optimistic' | 'realistic' | 'pessimistic';
  probability: number;
  conversion: number;
  impact: number;
  factors: string[];
}

export interface StepRisk {
  level: 'low' | 'medium' | 'high';
  probability: number;
  impact: number;
  factors: RiskFactor[];
  mitigation: RiskMitigation[];
}

export interface RiskFactor {
  factor: string;
  probability: number;
  impact: number;
  timeframe: string;
  mitigation: string;
}

export interface RiskMitigation {
  strategy: string;
  cost: number;
  effectiveness: number;
  timeline: string;
  owner: string;
}

export interface StepOpportunityPrediction {
  potential: number;
  confidence: number;
  effort: 'low' | 'medium' | 'high';
  timeframe: string;
  prerequisites: string[];
  expected_outcome: string;
}

export interface FunnelOptimization {
  overall: FunnelOptimizationOverall;
  targeted: TargetedOptimization[];
  systematic: SystematicOptimization[];
  innovative: InnovativeOptimization[];
}

export interface FunnelOptimizationOverall {
  potential_improvement: number;
  confidence: number;
  priority: 'low' | 'medium' | 'high';
  recommendation: string;
  roadmap: OptimizationRoadmap;
}

export interface OptimizationRoadmap {
  phases: OptimizationPhase[];
  timeline: string;
  resources: OptimizationResource[];
  budget: number;
  expected_roi: number;
}

export interface OptimizationPhase {
  phase: string;
  objectives: string[];
  deliverables: string[];
  timeline: string;
  success_criteria: string[];
  risks: string[];
}

export interface OptimizationResource {
  role: string;
  availability: number;
  skills: string[];
  cost: number;
}

export interface TargetedOptimization {
  target: string;
  issue: string;
  solution: OptimizationSolution[];
  expected_impact: number;
  confidence: number;
  implementation: TargetedImplementation;
}

export interface OptimizationSolution {
  type: string;
  description: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  cost: number;
  roi: number;
}

export interface TargetedImplementation {
  approach: string;
  timeline: string;
  resources: string[];
  risks: string[];
  success_criteria: string[];
}

export interface SystematicOptimization {
  area: string;
  current_state: SystemState;
  target_state: TargetState;
  gap_analysis: GapAnalysis[];
  roadmap: SystemRoadmap;
}

export interface SystemState {
  performance: number;
  issues: string[];
  bottlenecks: string[];
  opportunities: string[];
}

export interface TargetState {
  performance: number;
  improvements: string[];
  requirements: string[];
  constraints: string[];
}

export interface GapAnalysis {
  gap: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  priority: 'low' | 'medium' | 'high';
  solution: string;
}

export interface SystemRoadmap {
  phases: SystemPhase[];
  timeline: string;
  investment: number;
  expected_return: number;
}

export interface SystemPhase {
  phase: string;
  objectives: string[];
  scope: string[];
  deliverables: string[];
  timeline: string;
  risks: string[];
}

export interface InnovativeOptimization {
  concept: string;
  innovation_level: 'incremental' | 'radical' | 'disruptive';
  potential_impact: number;
  feasibility: number;
  development: InnovationDevelopment;
  risk_assessment: InnovationRisk;
}

export interface InnovationDevelopment {
  concept: string;
  prototype: InnovationPrototype[];
  testing: InnovationTesting[];
  iteration: InnovationIteration[];
  validation: InnovationValidation[];
}

export interface InnovationPrototype {
  version: string;
  features: string[];
  timeline: string;
  resources: string[];
  success_criteria: string[];
}

export interface InnovationTesting {
  type: 'user_testing' | 'a_b_test' | 'focus_group' | 'expert_review';
  participants: number;
  methodology: string;
  timeline: string;
  success_criteria: string[];
}

export interface InnovationIteration {
  iteration: number;
  changes: string[];
  improvements: string[];
  feedback: string[];
  timeline: string;
}

export interface InnovationValidation {
  validation: string;
  method: string;
  criteria: string[];
  results: any;
  decision: string;
}

export interface InnovationRisk {
  risk_level: 'low' | 'medium' | 'high';
  technical_risk: number;
  market_risk: number;
  execution_risk: number;
  mitigation: InnovationMitigation[];
}

export interface InnovationMitigation {
  risk: string;
  mitigation: string;
  cost: number;
  effectiveness: number;
  owner: string;
}

export interface FunnelPrediction {
  prediction_horizon: string;
  confidence: number;
  scenarios: FunnelScenario[];
  recommendations: PredictionRecommendation[];
  monitoring: PredictionMonitoring;
}

export interface FunnelScenario {
  scenario: 'optimistic' | 'realistic' | 'pessimistic';
  probability: number;
  conversion: number;
  revenue: number;
  users: number;
  assumptions: string[];
}

export interface PredictionRecommendation {
  recommendation: string;
  priority: 'low' | 'medium' | 'high';
  impact: number;
  timeline: string;
  resources: string[];
}

export interface PredictionMonitoring {
  metrics: PredictionMetric[];
  alerts: PredictionAlert[];
  kpis: PredictionKPI[];
}

export interface PredictionMetric {
  metric: string;
  current: number;
  target: number;
  threshold: number;
  trend: string;
  alert_level: 'low' | 'medium' | 'high';
}

export interface PredictionAlert {
  alert: string;
  condition: string;
  threshold: number;
  action: string;
  escalation: string;
}

export interface PredictionKPI {
  kpi: string;
  value: number;
  target: number;
  variance: number;
  status: 'on_track' | 'at_risk' | 'off_track';
}

export interface CohortAnalytics {
  cohorts: CohortAnalysis[];
  comparison: CohortComparison;
  trends: CohortTrend[];
  predictions: CohortPrediction[];
}

export interface CohortAnalysis {
  cohort: string;
  size: number;
  retention: CohortRetentionMetrics;
  behavior: CohortBehaviorMetrics;
  monetization: CohortMonetizationMetrics;
  satisfaction: CohortSatisfactionMetrics;
}

export interface CohortRetentionMetrics {
  day1: number;
  day7: number;
  day30: number;
  day90: number;
  day180: number;
  day365: number;
  predicted: number;
  factors: RetentionFactorAnalysis[];
}

export interface RetentionFactorAnalysis {
  factor: string;
  influence: number;
  direction: 'positive' | 'negative';
  confidence: number;
  impact: number;
}

export interface CohortBehaviorMetrics {
  engagement: EngagementMetrics;
  features: CohortFeatureMetrics;
  content: CohortContentMetrics;
  social: CohortSocialMetrics;
}

export interface CohortFeatureMetrics {
  usage: FeatureUsageMetrics;
  adoption: FeatureAdoptionMetrics;
  retention: FeatureRetentionMetrics;
  satisfaction: FeatureSatisfactionMetrics;
}

export interface FeatureUsageMetrics {
  total_usage: number;
  unique_users: number;
  average_sessions: number;
  session_length: number;
  frequency: number;
  patterns: string[];
}

export interface FeatureAdoptionMetrics {
  adoption_rate: number;
  time_to_adoption: number;
  barriers: AdoptionBarrier[];
  facilitators: AdoptionFacilitator[];
  segments: AdoptionSegment[];
}

export interface AdoptionBarrier {
  barrier: string;
  impact: number;
  frequency: number;
  severity: 'low' | 'medium' | 'high';
  solution: string;
}

export interface AdoptionFacilitator {
  facilitator: string;
  impact: number;
  effectiveness: number;
  implementation: string;
}

export interface AdoptionSegment {
  segment: string;
  adoption_rate: number;
  characteristics: string[];
  barriers: string[];
  recommendations: string[];
}

export interface FeatureRetentionMetrics {
  retention_rate: number;
  engagement_retention: number;
  feature_specific_retention: number;
  correlation: FeatureCorrelation[];
}

export interface FeatureCorrelation {
  feature1: string;
  feature2: string;
  correlation: number;
  strength: 'weak' | 'moderate' | 'strong';
  direction: 'positive' | 'negative';
}

export interface FeatureSatisfactionMetrics {
  satisfaction_score: number;
  satisfaction_trend: string;
  feedback: FeatureFeedback[];
  nps: number;
  recommendation_rate: number;
}

export interface FeatureFeedback {
  type: 'positive' | 'negative' | 'neutral';
  sentiment: 'strong' | 'moderate' | 'weak';
  category: string;
  frequency: number;
}

export interface CohortContentMetrics {
  consumption: ContentConsumptionMetrics;
  engagement: ContentEngagementMetrics;
  sharing: ContentSharingMetrics;
  creation: ContentCreationMetrics;
}

export interface ContentConsumptionMetrics {
  total_time: number;
  unique_content: number;
  average_session: number;
  completion_rate: number;
  skip_rate: number;
}

export interface ContentEngagementMetrics {
  likes: number;
  comments: number;
  reactions: number;
  bookmarks: number;
  time_spent: number;
}

export interface ContentSharingMetrics {
  shares: number;
  viral_coefficient: number;
  reach: number;
  social_mentions: number;
  hashtag_usage: number;
}

export interface ContentCreationMetrics {
  created: number;
  published: number;
  quality_score: number;
  engagement: number;
  creation_patterns: string[];
}

export interface CohortSocialMetrics {
  interactions: SocialInteractionMetrics;
  network: SocialNetworkMetrics;
  influence: SocialInfluenceMetrics;
  community: SocialCommunityMetrics;
}

export interface SocialInteractionMetrics {
  total_interactions: number;
  unique_partners: number;
  average_interactions: number;
  interaction_patterns: string[];
  quality_score: number;
}

export interface SocialNetworkMetrics {
  network_size: number;
  network_density: number;
  influence_score: number;
  centrality: number;
  clustering: number;
}

export interface SocialInfluenceMetrics {
  reach: number;
  engagement_rate: number;
  sentiment: number;
  share_rate: number;
  recommendation_rate: number;
}

export interface SocialCommunityMetrics {
  membership: number;
  participation: number;
  contribution: number;
  leadership: number;
  retention: number;
}

export interface CohortMonetizationMetrics {
  conversion: ConversionMetrics;
  revenue: RevenueMetrics;
  ltv: LTVMetrics;
  pricing: PricingMetrics;
}

export interface ConversionMetrics {
  free_to_paid: number;
  trial_to_paid: number;
  upgrade_rate: number;
  downgrade_rate: number;
  cancellation_rate: number;
  reactivation_rate: number;
}

export interface RevenueMetrics {
  total_revenue: number;
  revenue_per_user: number;
  revenue_per_session: number;
  revenue_per_feature: number;
  seasonal_patterns: string[];
}

export interface LTVMetrics {
  ltv: number;
  ltv_trend: string;
  ltv_by_source: LTVBySource[];
  ltv_cohorts: LTVCohort[];
}

export interface LTVBySource {
  source: string;
  ltv: number;
  users: number;
  conversion: number;
  retention: number;
}

export interface LTVCohort {
  cohort: string;
  ltv: number;
  users: number;
  timeframe: string;
}

export interface PricingMetrics {
  average_price: number;
  price_elasticity: number;
  price_sensitivity: number;
  price_acceptance: number;
  competitor_comparison: PriceComparison[];
}

export interface PriceComparison {
  competitor: string;
  price: number;
  features: string[];
  value_score: number;
  market_share: number;
}

export interface CohortSatisfactionMetrics {
  satisfaction: SatisfactionMetrics;
  nps: NPSMetrics;
  feedback: SatisfactionFeedbackAnalysis[];
  recommendation: RecommendationMetrics;
}

export interface SatisfactionMetrics {
  overall_score: number;
  satisfaction_trend: string;
  satisfaction_distribution: SatisfactionDistribution[];
  factors: SatisfactionFactor[];
}

export interface SatisfactionDistribution {
  score_range: string;
  users: number;
  percentage: number;
  characteristics: string[];
}

export interface SatisfactionFactor {
  factor: string;
  importance: number;
  satisfaction: number;
  gap: number;
  impact: number;
}

export interface NPSMetrics {
  score: number;
  distribution: NPSDistribution[];
  trends: NPSTrend[];
  drivers: NPSDriver[];
}

export interface NPSDistribution {
  category: 'promoters' | 'passives' | 'detractors';
  users: number;
  percentage: number;
  characteristics: string[];
}

export interface NPSTrend {
  period: string;
  score: number;
  change: number;
  confidence: number;
}

export interface NPSDriver {
  driver: string;
  impact: number;
  satisfaction: number;
  correlation: number;
}

export interface SatisfactionFeedbackAnalysis {
  feedback: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  theme: string;
  frequency: number;
  severity: 'low' | 'medium' | 'high';
  actionability: number;
}

export interface RecommendationMetrics {
  recommendation_rate: number;
  referral_rate: number;
  word_of_mouth: number;
  advocacy_score: number;
  influence_network: InfluenceNetwork;
}

export interface InfluenceNetwork {
  advocates: number;
  influencers: number;
  reach: number;
  amplification: number;
  network_value: number;
}

export interface CohortComparison {
  baseline: string;
  comparison: CohortComparisonData;
  differences: CohortDifference[];
  insights: CohortInsight[];
}

export interface CohortComparisonData {
  cohorts: string[];
  metrics: string[];
  comparison_type: 'baseline' | 'segmented' | 'longitudinal' | 'cross_sectional';
  statistical_significance: number;
  confidence_level: number;
}

export interface CohortDifference {
  metric: string;
  cohort1: number;
  cohort2: number;
  difference: number;
  percentage_difference: number;
  significance: number;
  effect_size: number;
}

export interface CohortInsight {
  insight: string;
  type: 'difference' | 'similarity' | 'trend' | 'pattern' | 'anomaly';
  impact: 'low' | 'medium' | 'high';
  confidence: number;
  recommendation: string;
}

export interface CohortTrend {
  metric: string;
  trend: string;
  direction: 'increasing' | 'decreasing' | 'stable' | 'volatility';
  strength: number;
  confidence: number;
  forecast: CohortForecast;
}

export interface CohortForecast {
  short_term: number;
  medium_term: number;
  long_term: number;
  accuracy: number;
  assumptions: string[];
}

export interface CohortPrediction {
  prediction_type: string;
  prediction: CohortPredictionData;
  confidence: number;
  methodology: string;
  assumptions: PredictionAssumption[];
  validation: PredictionValidation[];
}

export interface CohortPredictionData {
  retention: number;
  behavior: any;
  monetization: any;
  satisfaction: any;
  risk_factors: string[];
  opportunities: string[];
}

export interface PredictionAssumption {
  assumption: string;
  confidence: number;
  impact: number;
  validation: string;
}

export interface PredictionValidation {
  method: string;
  results: any;
  accuracy: number;
  limitations: string[];
}

export interface AttributionAnalytics {
  model: AttributionModel;
  channels: AttributionChannelAnalysis[];
  campaigns: AttributionCampaignAnalysis[];
  customers: AttributionCustomerAnalysis[];
  optimizations: AttributionOptimization[];
}

export interface AttributionChannelAnalysis {
  channel: string;
  touchpoints: number;
  conversions: number;
  revenue: number;
  attribution_credit: number;
  efficiency: number;
  optimization_opportunities: string[];
}

export interface AttributionCampaignAnalysis {
  campaign: string;
  channels: string[];
  touchpoints: number;
  conversions: number;
  revenue: number;
  cost: number;
  roi: number;
  attribution_breakdown: AttributionBreakdown[];
}

export interface AttributionBreakdown {
  touchpoint: string;
  position: number;
  time_to_conversion: number;
  credit: number;
  influence: number;
}

export interface AttributionCustomerAnalysis {
  customer_journey: CustomerJourney;
  attribution_path: AttributionPath;
  touchpoint_analysis: TouchpointAnalysis;
  optimization_recommendations: string[];
}

export interface CustomerJourney {
  user_id: string;
  touchpoints: Touchpoint[];
  conversion: Conversion;
  timeframe: string;
  paths: JourneyPath[];
}

export interface Touchpoint {
  timestamp: Date;
  channel: string;
  campaign: string;
  interaction: string;
  context: any;
}

export interface Conversion {
  type: string;
  value: number;
  timestamp: Date;
  path: string[];
}

export interface JourneyPath {
  path: string[];
  frequency: number;
  effectiveness: number;
  optimization: string[];
}

export interface AttributionPath {
  user_id: string;
  touchpoints: AttributionTouchpoint[];
  attribution_model: string;
  credit: number;
  path_value: number;
}

export interface AttributionTouchpoint {
  position: number;
  channel: string;
  timestamp: Date;
  interaction: string;
  weight: number;
}

export interface TouchpointAnalysis {
  touchpoint: string;
  frequency: number;
  effectiveness: number;
  position_effect: number;
  timing_effect: number;
  channel_effect: number;
}

export interface AttributionOptimization {
  optimization: string;
  type: 'channel' | 'campaign' | 'touchpoint' | 'path';
  impact: number;
  effort: 'low' | 'medium' | 'high';
  confidence: number;
  implementation: OptimizationImplementation;
}

export interface OptimizationImplementation {
  strategy: string;
  timeline: string;
  resources: string[];
  metrics: string[];
  success_criteria: string[];
}

export interface RevenueAnalytics {
  revenue: RevenueMetrics;
  pricing: PricingAnalytics;
  products: ProductRevenueAnalytics;
  customers: CustomerRevenueAnalytics;
  forecasting: RevenueForecasting;
}

export interface RevenueMetrics {
  total_revenue: number;
  recurring_revenue: number;
  one_time_revenue: number;
  revenue_growth: number;
  revenue_per_user: number;
  revenue_per_session: number;
  revenue_trends: RevenueTrend[];
  seasonal_patterns: SeasonalPattern[];
}

export interface RevenueTrend {
  period: string;
  revenue: number;
  growth: number;
  users: number;
  arpu: number;
  trends: string[];
}

export interface SeasonalPattern {
  pattern: string;
  strength: number;
  predictability: number;
  impact: number;
  timeframe: string;
}

export interface PricingAnalytics {
  current_pricing: CurrentPricing;
  elasticity: PriceElasticity;
  optimization: PricingOptimization;
  competition: PricingCompetition;
  customer_response: CustomerPriceResponse;
}

export interface CurrentPricing {
  base_price: number;
  price_tiers: PriceTier[];
  pricing_models: PricingModelAnalysis[];
  value_proposition: ValueProposition;
}

export interface PriceTier {
  tier: string;
  price: number;
  users: number;
  revenue: number;
  features: string[];
  market_position: string;
}

export interface PricingModelAnalysis {
  model: string;
  conversion_rate: number;
  retention_rate: number;
  revenue_per_user: number;
  customer_satisfaction: number;
  market_share: number;
}

export interface ValueProposition {
  value_metrics: ValueMetric[];
  pricing_power: number;
  price_sensitivity: number;
  willingness_to_pay: number;
  value_perception: ValuePerception;
}

export interface ValueMetric {
  metric: string;
  value: number;
  importance: number;
  uniqueness: number;
}

export interface ValuePerception {
  perceived_value: number;
  value_gap: number;
  value_drivers: ValueDriver[];
  value_barriers: ValueBarrier[];
}

export interface ValueDriver {
  driver: string;
  impact: number;
  controllability: number;
}

export interface ValueBarrier {
  barrier: string;
  impact: number;
  solution: string;
}

export interface PriceElasticity {
  overall_elasticity: number;
  elasticity_by_segment: SegmentElasticity[];
  cross_price_elasticity: CrossPriceElasticity[];
  optimal_pricing: OptimalPricing;
}

export interface SegmentElasticity {
  segment: string;
  elasticity: number;
  price_sensitivity: number;
  volume_impact: number;
  revenue_impact: number;
}

export interface CrossPriceElasticity {
  product: string;
  elasticity: number;
  relationship: 'substitute' | 'complement' | 'independent';
  revenue_impact: number;
}

export interface OptimalPricing {
  price_points: PricePoint[];
  revenue_maximization: RevenueMaximization;
  market_share: MarketShareOptimization;
}

export interface PricePoint {
  price: number;
  volume: number;
  revenue: number;
  margin: number;
  competitiveness: number;
}

export interface RevenueMaximization {
  optimal_price: number;
  max_revenue: number;
  volume_at_optimal: number;
  margin_at_optimal: number;
}

export interface MarketShareOptimization {
  target_share: number;
  price_for_share: number;
  competitive_response: CompetitiveResponse;
}

export interface CompetitiveResponse {
  probability: number;
  price_response: number;
  feature_response: string[];
  market_impact: number;
}

export interface PricingOptimization {
  opportunities: PricingOpportunity[];
  recommendations: PricingRecommendation[];
  experiments: PricingExperiment[];
  implementation: PricingImplementation;
}

export interface PricingOpportunity {
  opportunity: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  risk: 'low' | 'medium' | 'high';
  timeline: string;
}

export interface PricingRecommendation {
  recommendation: string;
  expected_impact: number;
  confidence: number;
  implementation: ImplementationDetails;
  risks: string[];
}

export interface PricingExperiment {
  experiment: string;
  hypothesis: string;
  variants: PricingExperimentVariant[];
  metrics: ExperimentMetric[];
  duration: number;
}

export interface PricingExperimentVariant {
  variant: string;
  price: number;
  features: string[];
  targeting: string;
  allocation: number;
}

export interface ImplementationDetails {
  timeline: string;
  resources: string[];
  dependencies: string[];
  success_criteria: string[];
}

export interface PricingImplementation {
  rollout_strategy: RolloutStrategy;
  communication_plan: CommunicationPlan;
  monitoring: PricingMonitoring;
  risk_mitigation: PricingRiskMitigation;
}

export interface RolloutStrategy {
  phases: RolloutPhase[];
  timeline: string;
  market_segments: string[];
  success_criteria: string[];
}

export interface RolloutPhase {
  phase: string;
  scope: string[];
  market: string[];
  features: string[];
  timeline: string;
}

export interface CommunicationPlan {
  internal: InternalCommunication[];
  customer: CustomerCommunication[];
  external: ExternalCommunication[];
  messaging: MessagingStrategy[];
}

export interface InternalCommunication {
  audience: string;
  message: string;
  channel: string;
  timeline: string;
  owner: string;
}

export interface CustomerCommunication {
  segment: string;
  message: string;
  channel: string;
  timing: string;
  personalization: string[];
}

export interface ExternalCommunication {
  stakeholder: string;
  message: string;
  channel: string;
  timing: string;
  approval: string;
}

export interface MessagingStrategy {
  message: string;
  key_points: string[];
  tone: string;
  differentiation: string[];
}

export interface PricingMonitoring {
  kpis: PricingKPI[];
  alerts: PricingAlert[];
  dashboard: PricingDashboard[];
  reporting: PricingReporting[];
}

export interface PricingKPI {
  kpi: string;
  target: number;
  current: number;
  trend: string;
  threshold: number;
  action: string;
}

export interface PricingAlert {
  alert: string;
  condition: string;
  threshold: number;
  action: string;
  escalation: string;
}

export interface PricingDashboard {
  metric: string;
  visualization: string;
  frequency: string;
  audience: string;
}

export interface PricingReporting {
  report: string;
  frequency: string;
  audience: string;
  content: string[];
}

export interface PricingRiskMitigation {
  risks: PricingRisk[];
  strategies: RiskMitigationStrategy[];
  contingency: ContingencyPlan[];
}

export interface PricingRisk {
  risk: string;
  probability: number;
  impact: number;
  mitigation: string;
  owner: string;
}

export interface RiskMitigationStrategy {
  strategy: string;
  actions: string[];
  cost: number;
  effectiveness: number;
}

export interface ContingencyPlan {
  scenario: string;
  triggers: string[];
  actions: string[];
  timeline: string;
  resources: string[];
}

export interface PricingCompetition {
  competitor_pricing: CompetitorPricing[];
  market_position: MarketPosition;
  competitive_analysis: CompetitiveAnalysis[];
  response_strategy: CompetitiveResponseStrategy;
}

export interface CompetitorPricing {
  competitor: string;
  products: CompetitorProduct[];
  pricing_strategy: string;
  market_share: number;
  value_proposition: string;
}

export interface CompetitorProduct {
  product: string;
  price: number;
  features: string[];
  target_market: string;
  positioning: string;
}

export interface MarketPosition {
  position: string;
  price_position: string;
  value_position: string;
  differentiation: string[];
  competitive_advantages: string[];
}

export interface CompetitiveAnalysis {
  competitor: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  strategic_recommendations: string[];
}

export interface CompetitiveResponseStrategy {
  strategy: string;
  response_type: 'pricing' | 'product' | 'marketing' | 'alliance';
  timeline: string;
  resources: string[];
  expected_outcome: string;
}

export interface CustomerPriceResponse {
  response_types: CustomerResponseType[];
  behavioral_changes: BehavioralChange[];
  pricing_tolerance: PricingTolerance;
  optimization_opportunities: string[];
}

export interface CustomerResponseType {
  response: string;
  percentage: number;
  segment: string;
  impact: number;
}

export interface BehavioralChange {
  behavior: string;
  change: number;
  timeline: string;
  drivers: string[];
  mitigation: string;
}

export interface PricingTolerance {
  upper_limit: number;
  lower_limit: number;
  sweet_spot: number;
  tolerance_range: number;
  sensitivity: number;
}

export interface ProductRevenueAnalytics {
  product_performance: ProductPerformance[];
  revenue_analysis: ProductRevenueAnalysis[];
  optimization: ProductOptimization[];
  forecasting: ProductForecasting[];
}

export interface ProductPerformance {
  product: string;
  revenue: number;
  volume: number;
  growth: number;
  market_share: number;
  performance_score: number;
}

export interface ProductRevenueAnalysis {
  product: string;
  revenue_streams: RevenueStream[];
  revenue_concentration: RevenueConcentration;
  revenue_predictability: RevenuePredictability;
}

export interface RevenueStream {
  stream: string;
  revenue: number;
  growth: number;
  percentage: number;
  predictability: number;
}

export interface RevenueConcentration {
  concentration_ratio: number;
  risk_level: 'low' | 'medium' | 'high';
  diversification_opportunities: string[];
}

export interface RevenuePredictability {
  predictability_score: number;
  volatility: number;
  seasonality: number;
  trends: string[];
}

export interface ProductOptimization {
  product: string;
  opportunities: ProductOptimizationOpportunity[];
  recommendations: ProductRecommendation[];
  implementation: ProductImplementation[];
}

export interface ProductOptimizationOpportunity {
  opportunity: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  timeline: string;
  risk: string;
}

export interface ProductRecommendation {
  recommendation: string;
  expected_impact: number;
  confidence: number;
  implementation: ProductImplementationDetails;
}

export interface ProductImplementationDetails {
  timeline: string;
  resources: string[];
  dependencies: string[];
  success_criteria: string[];
}

export interface ProductImplementation {
  implementation: string;
  scope: string[];
  timeline: string;
  resources: string[];
  risks: string[];
}

export interface ProductForecasting {
  product: string;
  forecast_horizon: string;
  scenarios: ProductForecastScenario[];
  confidence: number;
  assumptions: ProductForecastAssumption[];
}

export interface ProductForecastScenario {
  scenario: 'optimistic' | 'realistic' | 'pessimistic';
  probability: number;
  revenue: number;
  volume: number;
  factors: string[];
}

export interface ProductForecastAssumption {
  assumption: string;
  confidence: number;
  impact: number;
  validation: string;
}

export interface CustomerRevenueAnalytics {
  customer_segments: CustomerSegmentRevenue[];
  customer_journey: CustomerJourneyRevenue[];
  ltv_analysis: LTVAnalysis[];
  churn_analysis: ChurnRevenueAnalysis[];
  expansion_analysis: ExpansionRevenueAnalysis[];
}

export interface CustomerSegmentRevenue {
  segment: string;
  revenue: number;
  customers: number;
  arpu: number;
  growth: number;
  retention: number;
}

export interface CustomerJourneyRevenue {
  stage: string;
  revenue: number;
  customers: number;
  conversion: number;
  value: number;
}

export interface LTVAnalysis {
  segment: string;
  ltv: number;
  cac: number;
  ltv_cac_ratio: number;
  payback_period: number;
}

export interface ChurnRevenueAnalysis {
  reason: string;
  revenue_impact: number;
  preventable_revenue: number;
  mitigation_opportunity: number;
}

export interface ExpansionRevenueAnalysis {
  type: string;
  revenue: number;
  customers: number;
  expansion_rate: number;
  potential: number;
}

export interface RevenueForecasting {
  forecast_horizon: string;
  model: RevenueForecastModel;
  scenarios: RevenueForecastScenario[];
  confidence_intervals: ConfidenceInterval[];
}

export interface RevenueForecastModel {
  type: string;
  accuracy: number;
  factors: RevenueForecastFactor[];
  validation: ModelValidation;
}

export interface RevenueForecastFactor {
  factor: string;
  impact: number;
  direction: 'positive' | 'negative';
  confidence: number;
}

export interface ModelValidation {
  historical_accuracy: number;
  cross_validation: number;
  backtesting: BacktestResult[];
}

export interface BacktestResult {
  period: string;
  predicted: number;
  actual: number;
  accuracy: number;
  error: number;
}

export interface RevenueForecastScenario {
  scenario: string;
  probability: number;
  revenue: number;
  key_drivers: string[];
  assumptions: string[];
}

export interface ConfidenceInterval {
  scenario: string;
  lower_bound: number;
  upper_bound: number;
  confidence_level: number;
  error_margin: number;
}

export interface CrashAnalytics {
  crashes: CrashAnalysis[];
  anr: ANRAnalysis[];
  performance: PerformanceAnalysis[];
  trends: CrashTrend[];
  predictions: CrashPrediction[];
  optimization: CrashOptimization[];
}

export interface CrashAnalysis {
  crash_type: string;
  frequency: number;
  impact: number;
  affected_users: number;
  devices: CrashDeviceAnalysis[];
  stack_trace: CrashStackTrace;
  resolution: CrashResolutionStatus[];
}

export interface CrashDeviceAnalysis {
  device: string;
  crashes: number;
  frequency: number;
  impact: number;
}

export interface CrashStackTrace {
  frames: StackFrame[];
  exceptions: ExceptionFrame[];
  native_frames: NativeFrame[];
}

export interface StackFrame {
  file: string;
  function: string;
  line: number;
  column: number;
  offset: number;
}

export interface ExceptionFrame {
  type: string;
  message: string;
  stack_frame: StackFrame;
}

export interface NativeFrame {
  address: string;
  module: string;
  symbol: string;
  offset: number;
}

export interface CrashResolutionStatus {
  status: string;
  resolution: string;
  version: string;
  deployed: Date;
}

export interface ANRAnalysis {
  anr_type: string;
  frequency: number;
  duration: number;
  affected_users: number;
  root_cause: ANRRootCause[];
  solutions: ANRSolution[];
}

export interface ANRRootCause {
  cause: string;
  frequency: number;
  impact: number;
  stack_trace: ANRStackTrace;
}

export interface ANRStackTrace {
  threads: ANRThread[];
  blocked_threads: ANRBlockedThread[];
  waiting_threads: ANRWaitingThread[];
}

export interface ANRThread {
  thread_id: string;
  stack_trace: StackFrame[];
  state: string;
}

export interface ANRBlockedThread {
  thread_id: string;
  lock: string;
  owner_thread: string;
}

export interface ANRWaitingThread {
  thread_id: string;
  wait_condition: string;
  timeout: number;
}

export interface ANRSolution {
  solution: string;
  impact: number;
  implementation: ANRImplementation;
  testing: ANRTesting;
}

export interface ANRImplementation {
  approach: string;
  timeline: string;
  resources: string[];
  risk: string;
}

export interface ANRTesting {
  test_cases: ANRTestCase[];
  validation: ANRValidation[];
  performance_impact: number;
}

export interface ANRTestCase {
  scenario: string;
  steps: string[];
  expected_result: string;
  priority: 'low' | 'medium' | 'high';
}

export interface ANRValidation {
  validation: string;
  method: string;
  criteria: string[];
  success: boolean;
}

export interface PerformanceAnalysis {
  metric: string;
  performance: PerformanceMetricsData;
  bottlenecks: BottleneckAnalysis[];
  optimization: PerformanceOptimization[];
}

export interface PerformanceMetricsData {
  current: number;
  target: number;
  threshold: number;
  trend: string;
  percentile: number;
}

export interface BottleneckAnalysis {
  bottleneck: string;
  impact: number;
  frequency: number;
  solutions: BottleneckSolution[];
}

export interface BottleneckSolution {
  solution: string;
  impact: number;
  effort: 'low' | 'medium' | 'high';
  implementation: ImplementationApproach;
}

export interface ImplementationApproach {
  approach: string;
  timeline: string;
  resources: string[];
  risks: string[];
}

export interface PerformanceOptimization {
  optimization: string;
  expected_improvement: number;
  implementation: PerformanceImplementation;
  monitoring: PerformanceMonitoring;
}

export interface PerformanceImplementation {
  changes: PerformanceChange[];
  testing: PerformanceChangeTesting;
  rollback: PerformanceRollback;
}

export interface PerformanceChange {
  change: string;
  area: string;
  impact: number;
  validation: string;
}

export interface PerformanceChangeTesting {
  test_scenarios: TestScenario[];
  performance_benchmarks: Benchmark[];
  regression_testing: boolean;
}

export interface TestScenario {
  scenario: string;
  steps: string[];
  expected_performance: PerformanceMetricsData;
}

export interface Benchmark {
  metric: string;
  baseline: number;
  target: number;
  tolerance: number;
}

export interface PerformanceRollback {
  triggers: RollbackTrigger[];
  procedure: RollbackProcedure;
  communication: RollbackCommunication;
}

export interface RollbackTrigger {
  trigger: string;
  condition: string;
  threshold: number;
  action: string;
}

export interface RollbackProcedure {
  steps: string[];
  timeline: string;
  resources: string[];
  validation: string[];
}

export interface RollbackCommunication {
  stakeholders: string[];
  channels: string[];
  messaging: string[];
  escalation: string[];
}

export interface PerformanceMonitoring {
  metrics: PerformanceMonitorMetric[];
  alerts: PerformanceAlert[];
  dashboard: PerformanceDashboard;
  reporting: PerformanceReporting;
}

export interface PerformanceMonitorMetric {
  metric: string;
  target: number;
  threshold: number;
  frequency: string;
  alert_conditions: AlertCondition[];
}

export interface AlertCondition {
  condition: string;
  threshold: number;
  action: string;
  escalation: string;
}

export interface PerformanceDashboard {
  dashboard_name: string;
  components: DashboardComponent[];
  refresh_rate: number;
  access: DashboardAccess;
}

export interface DashboardComponent {
  component: string;
  visualization: string;
  data_source: string;
  filters: string[];
}

export interface DashboardAccess {
  roles: string[];
  permissions: string[];
  sharing: string[];
}

export interface PerformanceReporting {
  reports: PerformanceReport[];
  scheduling: ReportScheduling[];
  distribution: ReportDistribution[];
}

export interface PerformanceReport {
  report_name: string;
  content: string[];
  format: string;
  frequency: string;
  recipients: string[];
}

export interface ReportScheduling {
  schedule: string;
  frequency: string;
  automation: boolean;
  triggers: ReportTrigger[];
}

export interface ReportTrigger {
  trigger: string;
  condition: string;
  action: string;
}

export interface ReportDistribution {
  channels: string[];
  recipients: string[];
  permissions: string[];
  automation: boolean;
}

export interface CrashTrend {
  metric: string;
  trend: string;
  direction: string;
  change: number;
  significance: number;
  forecast: CrashTrendForecast;
}

export interface CrashTrendForecast {
  short_term: number;
  medium_term: number;
  long_term: number;
  confidence: number;
  factors: string[];
}

export interface CrashPrediction {
  prediction_type: string;
  prediction: CrashPredictionData;
  confidence: number;
  methodology: string;
  validation: CrashPredictionValidation[];
}

export interface CrashPredictionData {
  crash_rate: number;
  crash_count: number;
  affected_users: number;
  peak_times: string[];
  risk_factors: string[];
}

export interface CrashPredictionValidation {
  method: string;
  accuracy: number;
  limitations: string[];
  improvements: string[];
}

export interface CrashOptimization {
  optimization: string;
  expected_improvement: number;
  implementation: CrashOptimizationImplementation;
  monitoring: CrashOptimizationMonitoring;
}

export interface CrashOptimizationImplementation {
  approach: string;
  phases: OptimizationPhase[];
  timeline: string;
  resources: string[];
}

export interface OptimizationPhase {
  phase: string;
  objectives: string[];
  deliverables: string[];
  success_criteria: string[];
  risks: string[];
}

export interface CrashOptimizationMonitoring {
  metrics: CrashOptimizationMetric[];
  alerts: CrashOptimizationAlert[];
  dashboard: CrashOptimizationDashboard;
}

export interface CrashOptimizationMetric {
  metric: string;
  baseline: number;
  target: number;
  threshold: number;
  frequency: string;
}

export interface CrashOptimizationAlert {
  alert: string;
  condition: string;
  threshold: number;
  action: string;
  escalation: string;
}

export interface CrashOptimizationDashboard {
  dashboard_name: string;
  components: CrashDashboardComponent[];
  refresh_rate: number;
  access: CrashDashboardAccess;
}

export interface CrashDashboardComponent {
  component: string;
  visualization: string;
  data_source: string;
  filters: string[];
}

export interface CrashDashboardAccess {
  roles: string[];
  permissions: string[];
  sharing: string[];
}

// Common types
export interface Vector2 {
  x: number;
  y: number;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

// Model3D type reference (from existing types)
export interface Model3D {
  id: string;
  name: string;
  description: string;
  specifications: any;
  filePath: string;
  thumbnail?: string;
  status: string;
  createdAt: Date;
  updatedAt: Date;
  metadata: any;
}