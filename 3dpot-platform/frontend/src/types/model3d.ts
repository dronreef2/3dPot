// Types for 3D Model Generation System
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Material {
  id: string;
  name: string;
  color: string;
  metalness?: number;
  roughness?: number;
  transparent?: boolean;
  opacity?: number;
  textureUrl?: string;
  normalMapUrl?: string;
  emissive?: string;
  emissiveIntensity?: number;
}

export interface Geometry {
  id: string;
  type: 'box' | 'sphere' | 'cylinder' | 'cone' | 'torus' | 'custom';
  parameters: {
    width?: number;
    height?: number;
    depth?: number;
    radius?: number;
    segments?: number;
    [key: string]: any;
  };
  position: Vector3;
  rotation: Vector3;
  scale: Vector3;
  materialId: string;
  vertices?: number[];
  faces?: number[];
  normals?: number[];
  uvs?: number[];
}

export interface Model3D {
  id: string;
  name: string;
  description: string;
  specId: string;
  geometries: Geometry[];
  materials: Material[];
  settings: ModelSettings;
  metadata: ModelMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface ModelSettings {
  resolution: 'low' | 'medium' | 'high' | 'ultra';
  fileFormat: 'stl' | 'obj' | 'gltf' | 'objmtl';
  optimizeGeometry: boolean;
  enableShadows: boolean;
  enableLighting: boolean;
  backgroundColor: string;
  cameraPosition: Vector3;
  renderingQuality: 'draft' | 'preview' | 'production';
}

export interface ModelMetadata {
  vertexCount: number;
  faceCount: number;
  fileSize: number;
  processingTime: number;
  qualityScore: number;
  nvidiaNimVersion: string;
  optimizationLevel: 'none' | 'basic' | 'advanced';
  compressionRatio?: number;
}

export interface GenerationRequest {
  specifications: ExtractedSpecs;
  settings: Partial<ModelSettings>;
  options: GenerationOptions;
}

export interface GenerationOptions {
  style: 'realistic' | 'stylized' | 'technical' | 'artistic';
  complexity: 'simple' | 'moderate' | 'complex' | 'intricate';
  materialPreset: 'default' | 'metallic' | 'ceramic' | 'glass' | 'fabric';
  colorScheme: 'monochrome' | 'colorful' | 'natural' | 'custom';
  customColors?: string[];
  outputPreferences: {
    detailLevel: 1 | 2 | 3 | 4 | 5;
    symmetry: boolean;
    hollow: boolean;
    solid: boolean;
  };
}

export interface GenerationResponse {
  success: boolean;
  modelId?: string;
  model?: Model3D;
  error?: string;
  warnings?: string[];
  processingTime: number;
  nvidiaNimRequestId: string;
}

export interface ProcessingProgress {
  modelId: string;
  stage: 'initializing' | 'analyzing' | 'generating' | 'optimizing' | 'exporting' | 'completed' | 'error';
  progress: number; // 0-100
  message: string;
  estimatedTimeRemaining?: number;
}

export interface ViewportSettings {
  camera: {
    position: Vector3;
    target: Vector3;
    up: Vector3;
    fov: number;
    near: number;
    far: number;
  };
  renderer: {
    antialias: boolean;
    shadows: boolean;
    shadowMapType: 'basic' | 'pcf' | 'vsm';
    toneMapping: 'none' | 'linear' | 'reinhard' | 'cineon' | 'aces';
    physicallyCorrectLights: boolean;
  };
  controls: {
    enableZoom: boolean;
    enablePan: boolean;
    enableRotate: boolean;
    autoRotate: boolean;
    autoRotateSpeed: number;
    damping: number;
  };
  environment: {
    background: 'color' | 'gradient' | 'hdri' | 'transparent';
    backgroundColor?: string;
    environmentMap?: string;
    lighting: 'basic' | 'studio' | 'outdoor' | 'custom';
    lightPosition?: Vector3;
    lightIntensity?: number;
  };
}

export interface ExportOptions {
  format: 'stl' | 'obj' | 'gltf' | 'objmtl' | 'ply';
  binary: boolean;
  includeMaterials: boolean;
  includeTextures: boolean;
  compressionLevel: 0 | 1 | 2 | 3;
  preserveColors: boolean;
  generatePreview: boolean;
  metadata: {
    author: string;
    copyright: string;
    license: string;
    version: string;
  };
}

export interface GeometryProcessor {
  optimize(): Promise<void>;
  decimate(factor: number): Promise<void>;
  smoothShading(): Promise<void>;
  generateNormals(): Promise<void>;
  compress(level: number): Promise<ArrayBuffer>;
  validate(): Promise<boolean>;
}

export interface NVIDIAConfig {
  apiKey: string;
  endpoint: string;
  model: string;
  maxTokens: number;
  temperature: number;
  timeout: number;
  retries: number;
}

export interface AIAnalysis {
  complexity: 'simple' | 'moderate' | 'complex';
  recommendedSettings: {
    resolution: string;
    segmentCount: number;
    optimizationLevel: string;
  };
  estimatedProcessingTime: number;
  potentialIssues: string[];
  optimizationSuggestions: string[];
}

export interface BatchGenerationRequest {
  requests: GenerationRequest[];
  parallel: boolean;
  maxConcurrent: number;
  onProgress?: (modelId: string, progress: ProcessingProgress) => void;
  onComplete?: (result: GenerationResponse) => void;
  onError?: (modelId: string, error: string) => void;
}