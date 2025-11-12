// Sprint 6+: 3D Printing Suite Types
// Importações para impressão 3D

export interface PrintSettings {
  layerHeight: number;
  infill: number;
  printSpeed: number;
  nozzleDiameter: number;
  bedTemperature: number;
  nozzleTemperature: number;
  supportType: 'none' | 'tree' | 'manual';
  brim: boolean;
  raft: boolean;
  cooling: boolean;
  adhesionType: 'none' | 'brim' | 'raft';
  retraction: boolean;
  travelSpeed: number;
  wallThickness: number;
  topBottomLayers: number;
  printTime: number;
  materialUsage: number;
}

export interface PrintJob {
  id: string;
  modelId: string;
  modelName: string;
  settings: PrintSettings;
  status: 'queued' | 'processing' | 'generating' | 'ready' | 'printing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  estimatedTime: number;
  gcodePath?: string;
  previewPath?: string;
  printer: PrintJobPrinter;
  userId: string;
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  filamentType: string;
  filamentColor: string;
  materialCost: number;
  supportsGenerated: boolean;
  geometryAnalysis: GeometryAnalysis;
}

export interface PrintJobPrinter {
  id: string;
  name: string;
  type: 'fdm' | 'sla' | 'sls' | 'metal';
  manufacturer: string;
  maxPrintVolume: PrintVolume;
  nozzleSizes: number[];
  supportedMaterials: string[];
  status: 'idle' | 'busy' | 'offline' | 'maintenance';
  currentJobId?: string;
}

export interface PrintVolume {
  x: number;
  y: number;
  z: number;
}

export interface GeometryAnalysis {
  overhangAngles: OverhangAnalysis[];
  thinWalls: ThinWallAnalysis[];
  bridgingDistance: number;
  complexity: 'low' | 'medium' | 'high';
  supportRequired: boolean;
  printabilityScore: number;
  recommendedSettings: Partial<PrintSettings>;
  warnings: AnalysisWarning[];
}

export interface OverhangAnalysis {
  area: number;
  angle: number;
  severity: 'low' | 'medium' | 'high';
  position: Vector3;
}

export interface ThinWallAnalysis {
  position: Vector3;
  thickness: number;
  recommended: number;
  risk: 'low' | 'medium' | 'high';
}

export interface AnalysisWarning {
  type: 'overhang' | 'thin_wall' | 'large_bridge' | 'small_features';
  message: string;
  severity: 'info' | 'warning' | 'error';
  position?: Vector3;
}

export interface GCodeConfig {
  startCode: string[];
  endCode: string[];
  layerChangeCode: string[];
  retractionCode: string[];
  unretractionCode: string[];
  coordinateSystem: 'relative' | 'absolute';
  units: 'mm' | 'inches';
  precision: number;
}

export interface MaterialLibrary {
  id: string;
  name: string;
  type: 'pla' | 'abs' | 'petg' | 'tpu' | 'nylon' | 'wood' | 'metal_filament';
  properties: MaterialProperties;
  printerCompatibility: string[];
  pricePerKg: number;
  description: string;
  manufacturer: string;
  colors: MaterialColor[];
}

export interface MaterialProperties {
  glassTransitionTemp: number;
  meltingTemp: number;
  bedTemp: number;
  nozzleTemp: number;
  printSpeed: number;
  infill: number;
  cooling: boolean;
  retraction: boolean;
  warpage: 'low' | 'medium' | 'high';
  strength: 'low' | 'medium' | 'high';
  flexibility: 'low' | 'medium' | 'high';
  durability: 'low' | 'medium' | 'high';
}

export interface MaterialColor {
  id: string;
  name: string;
  hex: string;
  priceMultiplier: number;
  availability: 'in_stock' | 'limited' | 'out_of_stock';
}

export interface PrintQueue {
  id: string;
  name: string;
  printerId: string;
  jobs: PrintJob[];
  priority: number;
  createdAt: Date;
  estimatedCompletion: Date;
}

export interface SlicingResult {
  gcode: string;
  preview: string;
  metadata: SlicingMetadata;
  layers: LayerPreview[];
  supports: SupportStructure[];
}

export interface SlicingMetadata {
  estimatedTime: number;
  estimatedMaterial: number;
  layerCount: number;
  printVolume: PrintVolume;
  overhangWarnings: number;
  thinWalls: number;
  supportsGenerated: boolean;
}

export interface LayerPreview {
  layer: number;
  height: number;
  paths: PathData[];
  supports: SupportData[];
}

export interface PathData {
  type: 'perimeter' | 'infill' | 'top' | 'bottom' | 'skirt' | 'brim';
  points: Vector3[];
  speed: number;
  flow: number;
  extrusionWidth: number;
}

export interface SupportStructure {
  id: string;
  type: 'interface' | 'support' | 'tree';
  material: 'same' | 'different';
  points: Vector3[];
  density: number;
}

export interface SupportData {
  type: string;
  position: Vector3;
  height: number;
  radius: number;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface PrintCost {
  material: number;
  electricity: number;
  labor: number;
  total: number;
  currency: string;
  breakdown: CostBreakdown;
}

export interface CostBreakdown {
  materialCost: number;
  energyCost: number;
  machineTime: number;
  overhead: number;
  profit: number;
}

export interface PrintQuality {
  layers: number;
  infillPattern: 'grid' | 'hexagonal' | 'triangular' | 'cubic' | 'gyroid';
  wallType: 'looped' | 'zigzag' | 'classic';
  topBottomLayers: number;
  topSolidLayers: number;
  bottomSolidLayers: number;
  quality: 'draft' | 'low' | 'medium' | 'high' | 'ultra';
}

export interface PrinterMaintenance {
  id: string;
  printerId: string;
  type: 'routine' | 'repair' | 'calibration';
  description: string;
  scheduledAt: Date;
  completedAt?: Date;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  partsUsed: MaintenancePart[];
  cost: number;
}

export interface MaintenancePart {
  partId: string;
  name: string;
  quantity: number;
  price: number;
}

export interface PrintStatistics {
  totalPrints: number;
  successRate: number;
  averageTime: number;
  totalMaterial: number;
  totalCost: number;
  popularMaterials: MaterialUsage[];
  commonFailures: FailureData[];
}

export interface MaterialUsage {
  material: string;
  totalGrams: number;
  printsCount: number;
  cost: number;
}

export interface FailureData {
  reason: string;
  occurrences: number;
  percentage: number;
  solutions: string[];
}

// Export settings for multiple printer formats
export interface ExportSettings {
  format: 'gcode' | '3mf' | 'svg' | 'pdf';
  resolution: 'low' | 'medium' | 'high' | 'ultra';
  includeSupports: boolean;
  includeBrim: boolean;
  includeRaft: boolean;
  layerHeight?: number;
  settings: PrintSettings;
}

// Print job management
export interface PrintQueueManager {
  addJob: (job: PrintJob) => Promise<void>;
  cancelJob: (jobId: string) => Promise<void>;
  pauseJob: (jobId: string) => Promise<void>;
  resumeJob: (jobId: string) => Promise<void>;
  reorderQueue: (jobIds: string[]) => Promise<void>;
  getQueue: () => Promise<PrintJob[]>;
  getPrinterStatus: (printerId: string) => Promise<PrintJobPrinter>;
}