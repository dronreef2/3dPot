// Sprint 6+: Cloud Rendering Types
// Sistema de renderização distribuída na nuvem

export interface RenderJob {
  id: string;
  sessionId: string;
  modelId: string;
  userId: string;
  type: RenderJobType;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: RenderStatus;
  configuration: RenderConfiguration;
  progress: RenderProgress;
  results: RenderResult[];
  cluster: RenderCluster;
  queue: RenderQueue;
  billing: RenderBilling;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  estimatedTime?: number;
  actualTime?: number;
  error?: RenderError;
  retryCount: number;
  maxRetries: number;
  tags: string[];
  dependencies: string[];
}

export type RenderJobType = 
  | 'preview'
  | 'quality_check'
  | 'high_resolution'
  | 'animation'
  | 'vr_360'
  | 'ar_preview'
  | 'technical_drawing'
  | 'material_test'
  | 'render_pipeline'
  | 'batch_processing';

export type RenderStatus = 
  | 'queued'
  | 'pending'
  | 'assigned'
  | 'rendering'
  | 'uploading'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'timeout'
  | 'retrying'
  | 'paused';

export interface RenderConfiguration {
  resolution: Resolution;
  format: RenderFormat;
  quality: RenderQuality;
  lighting: LightingSetup;
  camera: CameraConfig;
  materials: MaterialRenderSettings;
  postProcessing: PostProcessingSettings;
  animation?: AnimationConfig;
  vr?: VRConfig;
  ar?: ARConfig;
  batch?: BatchConfig;
  custom: CustomRenderSettings;
}

export interface Resolution {
  width: number;
  height: number;
  aspectRatio: string;
  dpi: number;
  pixelRatio: number;
  custom?: boolean;
  preset?: ResolutionPreset;
}

export interface ResolutionPreset {
  name: string;
  category: 'web' | 'print' | 'mobile' | 'desktop' | '8k' | 'custom';
  width: number;
  height: number;
  dpi: number;
  optimized: boolean;
}

export type RenderFormat = 
  | 'png'
  | 'jpg'
  | 'webp'
  | 'exr'
  | 'hdr'
  | 'tiff'
  | 'bmp'
  | 'gif'
  | 'mp4'
  | 'mov'
  | 'webm'
  | 'avi';

export interface RenderQuality {
  level: 'draft' | 'medium' | 'high' | 'ultra' | 'photorealistic';
  samples: number;
  maxRayDepth: number;
  caustics: boolean;
  globalIllumination: boolean;
  ambientOcclusion: boolean;
  motionBlur: boolean;
  depthOfField: boolean;
  sss: boolean; // Subsurface Scattering
  causticsAccuracy: 'low' | 'medium' | 'high';
  rayTracing: boolean;
  denoising: boolean;
  aiEnhancement: boolean;
}

export interface LightingSetup {
  type: 'environment' | 'studio' | 'hdri' | 'three_point' | 'custom' | 'natural';
  hdri?: HDRISettings;
  lights: LightConfig[];
  environmentIntensity: number;
  globalIllumination: boolean;
  shadows: ShadowSettings;
  reflections: ReflectionSettings;
}

export interface HDRISettings {
  url: string;
  intensity: number;
  rotation: Vector3;
  blur: number;
  custom?: boolean;
}

export interface LightConfig {
  id: string;
  type: 'directional' | 'point' | 'spot' | 'area' | 'sphere' | 'cylinder';
  intensity: number;
  color: string;
  position?: Vector3;
  direction?: Vector3;
  angle?: number;
  penumbra?: number;
  decay?: number;
  castShadows: boolean;
  enabled: boolean;
}

export interface ShadowSettings {
  enabled: boolean;
  type: 'soft' | 'hard' | 'pcf' | 'vsm';
  bias: number;
  normalBias: number;
  size: number;
  mapResolution: number;
  softness: number;
  color: string;
  opacity: number;
}

export interface ReflectionSettings {
  enabled: boolean;
  type: 'screen_space' | 'planar' | 'cube_map' | 'screen_space_refraction';
  intensity: number;
  resolution: number;
  maxMips: number;
  quality: 'low' | 'medium' | 'high';
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface CameraConfig {
  type: 'perspective' | 'orthographic' | 'fisheye' | 'panoramic' | 'vr';
  position: Vector3;
  target: Vector3;
  up: Vector3;
  fov?: number;
  aspect?: number;
  near: number;
  far: number;
  focalLength?: number;
  sensorSize?: Vector3;
  whiteBalance?: string;
  exposure: ExposureSettings;
  autofocus: boolean;
  autoExposure: boolean;
}

export interface ExposureSettings {
  value: number;
  compensation: number;
  autoISO: boolean;
  maxISO: number;
  iso: number;
  shutterSpeed?: string;
}

export interface MaterialRenderSettings {
  renderEngine: 'cycles' | 'eevee' | 'octane' | 'redshift' | 'arnold' | 'vray' | 'custom';
  colorSpace: 'srgb' | 'linear' | 'ACES';
  transparency: 'alpha' | 'premultiplied' | 'channel';
  refraction: boolean;
  caustics: boolean;
  subsurface: boolean;
  anisotropic: boolean;
  clearcoat: boolean;
  iridescence: boolean;
  sheen: boolean;
  transmission: boolean;
  transmissionRoughness: boolean;
  anisotropicRoughness: boolean;
  clearcoatRoughness: boolean;
  sheenRoughness: boolean;
  customShaders: CustomShader[];
}

export interface CustomShader {
  id: string;
  name: string;
  type: 'vertex' | 'fragment' | 'compute';
  language: 'glsl' | 'hlsl' | 'cg' | 'osl';
  code: string;
  parameters: ShaderParameter[];
  inputs: ShaderInput[];
  outputs: ShaderOutput[];
}

export interface ShaderParameter {
  name: string;
  type: 'float' | 'int' | 'vec2' | 'vec3' | 'vec4' | 'mat4' | 'texture' | 'sampler';
  value: any;
  min?: number;
  max?: number;
  description: string;
}

export interface ShaderInput {
  name: string;
  type: string;
  connected?: string;
  default?: any;
}

export interface ShaderOutput {
  name: string;
  type: string;
}

export interface PostProcessingSettings {
  enabled: boolean;
  colorGrading: ColorGrading;
  toneMapping: ToneMapping;
  bloom: BloomSettings;
  vignette: VignetteSettings;
  chromaticAberration: ChromaticAberrationSettings;
  depthOfField: DepthOfFieldSettings;
  motionBlur: MotionBlurSettings;
  grain: GrainSettings;
  fxaa: boolean;
  ssr: boolean; // Screen Space Reflections
  ssgi: boolean; // Screen Space Global Illumination
  dithering: boolean;
}

export interface ColorGrading {
  enabled: boolean;
  temperature: number;
  tint: number;
  shadows: ChannelAdjustment;
  midtones: ChannelAdjustment;
  highlights: ChannelAdjustment;
  curves: ColorCurve[];
  look: string;
}

export interface ChannelAdjustment {
  red: number;
  green: number;
  blue: number;
  saturation: number;
  brightness: number;
  contrast: number;
  exposure: number;
  gamma: number;
}

export interface ColorCurve {
  name: string;
  points: Vector2[];
  enabled: boolean;
}

export interface Vector2 {
  x: number;
  y: number;
}

export interface ToneMapping {
  enabled: boolean;
  type: 'linear' | 'reinhard' | 'cinema' | 'aces' | 'filmic' | 'custom';
  exposure: number;
  whitePoint: number;
  middleGrey: number;
  custom: ToneMappingCustom;
}

export interface ToneMappingCustom {
  shoulder: number;
  midIn: number;
  midOut: number;
  highIn: number;
  highOut: number;
}

export interface BloomSettings {
  enabled: boolean;
  intensity: number;
  threshold: number;
  softKnee: number;
  radius: number;
  color: string;
  lensDirt: boolean;
  lensDirtIntensity: number;
}

export interface VignetteSettings {
  enabled: boolean;
  intensity: number;
  midPoint: number;
  roundness: number;
  feather: number;
  color: string;
}

export interface ChromaticAberrationSettings {
  enabled: boolean;
  intensity: number;
  distortion: number;
  centerX: number;
  centerY: number;
}

export interface DepthOfFieldSettings {
  enabled: boolean;
  focusDistance: number;
  focusPoint: Vector3;
  aperture: number;
  focalLength: number;
  sensorSize: number;
  bokehShape: 'circle' | 'hexagon' | 'star' | 'heart' | 'custom';
  bokehTexture?: string;
  occlusion: boolean;
  distanceBlur: boolean;
  foregroundBlur: boolean;
  backgroundBlur: boolean;
}

export interface MotionBlurSettings {
  enabled: boolean;
  intensity: number;
  samples: number;
  shutterAngle: number;
  shutterSpeed: number;
  imageBased: boolean;
  cameraMotion: boolean;
  objectMotion: boolean;
}

export interface GrainSettings {
  enabled: boolean;
  intensity: number;
  size: number;
  color: string;
  monochrome: boolean;
  animated: boolean;
  seed: number;
}

export interface AnimationConfig {
  enabled: boolean;
  duration: number;
  fps: number;
  loop: 'none' | 'loop' | 'pingpong';
  easing: 'linear' | 'ease_in' | 'ease_out' | 'ease_in_out' | 'custom';
  keyframes: AnimationKeyframe[];
  paths: AnimationPath[];
}

export interface AnimationKeyframe {
  time: number;
  property: string;
  value: any;
  interpolation: 'linear' | 'bezier' | 'ease_in' | 'ease_out';
  easing?: EasingConfig;
}

export interface EasingConfig {
  type: 'cubic' | 'elastic' | 'bounce' | 'back' | 'custom';
  duration: number;
  delay: number;
  values: number[];
}

export interface AnimationPath {
  object: string;
  type: 'position' | 'rotation' | 'scale' | 'morph';
  path: PathData[];
}

export interface PathData {
  x: number;
  y: number;
  z: number;
  time: number;
  type: 'linear' | 'curve';
  controlPoints?: Vector3[];
}

export interface VRConfig {
  enabled: boolean;
  stereoscopic: boolean;
  viewDistance: number;
  fov: number;
  lensDistortion: boolean;
  chromaticAberration: boolean;
  timeWarp: boolean;
  colorSpace: 'srgb' | 'linear' | 'dcip3';
}

export interface ARConfig {
  enabled: boolean;
  lightingEstimate: boolean;
  occlusion: boolean;
  hitTest: boolean;
  anchors: ARAnchor[];
  lighting: ARLighting;
}

export interface ARAnchor {
  id: string;
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  type: 'point' | 'plane' | 'hit_test';
  trackingState: 'tracking' | 'not_tracking' | 'stopped';
}

export interface ARLighting {
  type: 'light_estimation' | 'directional' | 'omni';
  intensity: number;
  direction?: Vector3;
  color: string;
  shadowMap: boolean;
}

export interface BatchConfig {
  enabled: boolean;
  models: string[];
  angles: CameraAngle[];
  formats: RenderFormat[];
  qualities: RenderQuality[];
  parallel: boolean;
  maxConcurrency: number;
}

export interface CameraAngle {
  name: string;
  camera: CameraConfig;
  focus: Vector3;
  distance: number;
  composition: CompositionType;
}

export type CompositionType = 'rule_of_thirds' | 'golden_ratio' | 'centered' | 'diagonal' | 'horizontal' | 'vertical' | 'custom';

export interface CustomRenderSettings {
  customShaders: CustomShader[];
  nodeGraph: NodeGraph;
  globalSettings: GlobalRenderSettings;
  performance: PerformanceSettings;
  debugging: DebugSettings;
}

export interface NodeGraph {
  nodes: GraphNode[];
  connections: GraphConnection[];
  parameters: NodeParameter[];
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
  position: Vector2;
  inputs: GraphInput[];
  outputs: GraphOutput[];
  parameters: GraphParameter[];
  enabled: boolean;
}

export interface GraphInput {
  name: string;
  type: string;
  connected?: string;
  default?: any;
}

export interface GraphOutput {
  name: string;
  type: string;
}

export interface GraphParameter {
  name: string;
  type: string;
  value: any;
  min?: number;
  max?: number;
  description: string;
}

export interface GraphConnection {
  from: string;
  to: string;
  fromPort: string;
  toPort: string;
  type: string;
}

export interface NodeParameter {
  node: string;
  parameter: string;
  value: any;
}

export interface GlobalRenderSettings {
  threadCount: number;
  memoryLimit: number;
  cacheSize: number;
  progressiveRendering: boolean;
  tileSize: number;
  seed: number;
  statisticalEstimation: boolean;
  adaptiveSampling: boolean;
  clampSamples: boolean;
}

export interface PerformanceSettings {
  optimizationLevel: 'none' | 'low' | 'medium' | 'high';
  adaptiveQuality: boolean;
  targetFPS: number;
  maxTime: number;
  autoResolution: boolean;
  dynamicResolution: boolean;
  fallbackQuality: RenderQuality;
  progressivePreview: boolean;
}

export interface DebugSettings {
  showBoundingBoxes: boolean;
  showNormals: boolean;
  showWireframe: boolean;
  showUV: boolean;
  showStatistics: boolean;
  showPerformance: boolean;
  saveIntermediate: boolean;
  debugOutput: boolean;
}

export interface RenderProgress {
  percentage: number;
  currentPass: string;
  totalPasses: number;
  currentSample: number;
  totalSamples: number;
  timeElapsed: number;
  timeRemaining: number;
  samplesPerSecond: number;
  estimatedFinish: Date;
  memoryUsed: number;
  memoryPeak: number;
  gpuUsage: GPUUsage;
  cpuUsage: CPUUsage;
  networkUpload: number;
}

export interface GPUUsage {
  index: number;
  name: string;
  utilization: number;
  memoryUsed: number;
  memoryTotal: number;
  temperature: number;
  powerDraw: number;
  fanSpeed: number;
  clock: number;
}

export interface CPUUsage {
  utilization: number;
  cores: CoreUsage[];
  temperature: number;
  powerDraw: number;
  clock: number;
}

export interface CoreUsage {
  index: number;
  utilization: number;
  frequency: number;
  temperature: number;
}

export interface RenderResult {
  id: string;
  jobId: string;
  type: 'image' | 'video' | 'animation' | '360' | 'ar' | 'vr';
  format: RenderFormat;
  url: string;
  thumbnail: string;
  metadata: ResultMetadata;
  download: DownloadInfo;
  analytics: ResultAnalytics;
  createdAt: Date;
}

export interface ResultMetadata {
  size: number;
  dimensions: Vector2;
  duration?: number;
  fps?: number;
  compression: string;
  quality: number;
  colorSpace: string;
  bitDepth: number;
  channels: number;
  hasAlpha: boolean;
  exif?: EXIFData;
  icc: string;
}

export interface EXIFData {
  camera: string;
  lens: string;
  focalLength: number;
  aperture: number;
  shutterSpeed: string;
  iso: number;
  whiteBalance: string;
  flash: boolean;
  gps: GPSData;
}

export interface GPSData {
  latitude: number;
  longitude: number;
  altitude: number;
  accuracy: number;
}

export interface DownloadInfo {
  url: string;
  expiresAt: Date;
  downloadCount: number;
  maxDownloads: number;
  watermarked: boolean;
  rights: string[];
}

export interface ResultAnalytics {
  views: number;
  downloads: number;
  likes: number;
  shares: number;
  comments: number;
  conversionRate: number;
  averageViewTime: number;
  bounceRate: number;
}

export interface RenderCluster {
  id: string;
  name: string;
  type: 'cpu' | 'gpu' | 'hybrid' | 'specialized';
  status: 'active' | 'maintenance' | 'offline' | 'upgrading';
  location: ClusterLocation;
  specifications: ClusterSpecs;
  pricing: ClusterPricing;
  queue: RenderJob[];
  capacity: ClusterCapacity;
  performance: ClusterPerformance;
  monitoring: ClusterMonitoring;
}

export interface ClusterLocation {
  region: string;
  datacenter: string;
  country: string;
  city: string;
  coordinates: Vector2;
  timezone: string;
}

export interface ClusterSpecs {
  totalNodes: number;
  cpuCores: number;
  gpuCount: number;
  gpuModel: string;
  gpuMemory: number;
  ram: number;
  storage: number;
  bandwidth: number;
  networkLatency: number;
}

export interface ClusterPricing {
  currency: string;
  costPerHour: number;
  costPerCoreHour: number;
  costPerGpuHour: number;
  minimumCharge: number;
  discountTier: DiscountTier[];
  spotPricing: boolean;
}

export interface DiscountTier {
  usage: number;
  discount: number;
  maxUsage: number;
}

export interface ClusterCapacity {
  total: number;
  available: number;
  occupied: number;
  reserved: number;
  maintenance: number;
  load: number;
  queueSize: number;
  estimatedWait: number;
}

export interface ClusterPerformance {
  averageRenderTime: number;
  successRate: number;
  throughput: number;
  efficiency: number;
  reliability: number;
  uptime: number;
}

export interface ClusterMonitoring {
  status: 'healthy' | 'warning' | 'critical' | 'offline';
  alerts: MonitoringAlert[];
  metrics: ClusterMetrics;
  maintenance: MaintenanceWindow[];
}

export interface MonitoringAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  resolved: boolean;
  resolvedAt?: Date;
  details: any;
}

export interface ClusterMetrics {
  cpuUtilization: number;
  memoryUtilization: number;
  gpuUtilization: number;
  storageUtilization: number;
  networkUtilization: number;
  temperature: number;
  errorRate: number;
  throughput: number;
  responseTime: number;
}

export interface MaintenanceWindow {
  id: string;
  title: string;
  description: string;
  startTime: Date;
  endTime: Date;
  type: 'scheduled' | 'emergency' | 'precautionary';
  impact: 'none' | 'minimal' | 'significant' | 'outage';
  affectedServices: string[];
}

export interface RenderQueue {
  position: number;
  priority: number;
  waitingTime: number;
  estimatedStart: Date;
  dependencies: string[];
  resources: ResourceRequirement[];
  scheduling: SchedulingStrategy;
}

export interface ResourceRequirement {
  type: 'cpu' | 'gpu' | 'memory' | 'storage' | 'network';
  amount: number;
  min: number;
  max: number;
  optional: boolean;
}

export interface SchedulingStrategy {
  algorithm: 'fifo' | 'priority' | 'round_robin' | 'fair_share' | 'energy_efficient' | 'cost_optimized';
  timeout: number;
  retryDelay: number;
  maxRetries: number;
  preemptive: boolean;
  batchMode: boolean;
}

export interface RenderBilling {
  usage: RenderUsage;
  cost: RenderCost;
  credits: RenderCredits;
  billing: BillingInfo;
}

export interface RenderUsage {
  computeHours: number;
  gpuHours: number;
  storageGB: number;
  bandwidthGB: number;
  requests: number;
  premiumRequests: number;
}

export interface RenderCost {
  compute: number;
  storage: number;
  bandwidth: number;
  premium: number;
  subtotal: number;
  tax: number;
  total: number;
  currency: string;
  estimated: boolean;
}

export interface RenderCredits {
  total: number;
  used: number;
  remaining: number;
  expires: Date;
  bonuses: CreditBonus[];
}

export interface CreditBonus {
  amount: number;
  reason: string;
  expires: Date;
}

export interface BillingInfo {
  period: BillingPeriod;
  nextBilling: Date;
  paymentMethod: string;
  invoiceTemplate: string;
  taxRate: number;
  currency: string;
}

export interface BillingPeriod {
  type: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly';
  start: Date;
  end: Date;
}

export interface RenderError {
  code: string;
  message: string;
  details: string;
  stackTrace?: string;
  source: 'user' | 'system' | 'network' | 'hardware';
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  resolved: boolean;
  resolution?: string;
  retryable: boolean;
  suggestions: string[];
}

// Render queue management
export interface RenderQueueManager {
  addJob: (job: RenderJob) => Promise<string>;
  cancelJob: (jobId: string) => Promise<void>;
  pauseJob: (jobId: string) => Promise<void>;
  resumeJob: (jobId: string) => Promise<void>;
  prioritizeJob: (jobId: string, priority: string) => Promise<void>;
  getQueue: (filter?: QueueFilter) => Promise<RenderJob[]>;
  estimateCost: (config: RenderConfiguration) => Promise<RenderCost>;
  getProgress: (jobId: string) => Promise<RenderProgress>;
}

export interface QueueFilter {
  status?: RenderStatus[];
  priority?: string[];
  userId?: string;
  clusterId?: string;
  type?: RenderJobType[];
  dateRange?: TimeRange;
}

// Distributed rendering infrastructure
export interface DistributedRenderer {
  submitJob: (job: RenderJob) => Promise<string>;
  cancelJob: (jobId: string) => Promise<void>;
  getStatus: (jobId: string) => Promise<RenderStatus>;
  getProgress: (jobId: string) => Promise<RenderProgress>;
  getResults: (jobId: string) => Promise<RenderResult[]>;
  getClusters: () => Promise<RenderCluster[]>;
  estimateCost: (config: RenderConfiguration) => Promise<RenderCost>;
  getUsage: (userId: string, period: TimeRange) => Promise<RenderUsage>;
  getBilling: (userId: string, period: BillingPeriod) => Promise<RenderBilling>;
}

export interface TimeRange {
  start: Date;
  end: Date;
}

// Global types for consistency
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