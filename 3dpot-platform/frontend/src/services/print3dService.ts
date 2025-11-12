// Sprint 6+: 3D Printing Service
// Serviço completo para impressão 3D

import { EventEmitter } from 'events';
import toast from 'react-hot-toast';
import { apiService } from './api';
import { API_ENDPOINTS } from '@/utils/config';

// Types
import type {
  PrintJob,
  PrintSettings,
  PrinterConfig,
  PrintQueue,
  SlicingResult,
  MaterialLibrary,
  GCodeConfig,
  PrintQuality,
  MaterialProperties
} from '@/types/printing3d';

interface Print3DServiceConfig {
  apiUrl: string;
  wsUrl: string;
  maxRetries: number;
  retryDelay: number;
  enableHardware: boolean;
  enableCloudPrint: boolean;
}

export class Print3DService extends EventEmitter {
  private config: Print3DServiceConfig;
  private queue: PrintJob[] = [];
  private printers: Map<string, PrinterConfig> = new Map();
  private materials: MaterialLibrary[] = [];
  private currentJobs: Map<string, PrintJob> = new Map();
  private ws: WebSocket | null = null;
  private isConnected = false;

  constructor(config: Print3DServiceConfig) {
    super();
    this.config = {
      maxRetries: 3,
      retryDelay: 1000,
      enableHardware: true,
      enableCloudPrint: true,
      ...config
    };
    this.initializeConnection();
    this.loadPrinters();
    this.loadMaterials();
  }

  private async initializeConnection() {
    try {
      await this.connectWebSocket();
      console.log('🔌 3D Printing service connected');
    } catch (error) {
      console.error('❌ Failed to connect 3D Printing service:', error);
      this.reconnectWebSocket();
    }
  }

  private async connectWebSocket() {
    return new Promise<void>((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.config.wsUrl}/printing`);
        
        this.ws.onopen = () => {
          this.isConnected = true;
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.emit('disconnected');
          this.reconnectWebSocket();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private reconnectWebSocket() {
    setTimeout(() => {
      console.log('🔄 Reconnecting 3D Printing WebSocket...');
      this.initializeConnection().catch(console.error);
    }, this.config.retryDelay);
  }

  private handleWebSocketMessage(data: any) {
    switch (data.type) {
      case 'job_update':
        this.handleJobUpdate(data.payload);
        break;
      case 'printer_status':
        this.handlePrinterStatus(data.payload);
        break;
      case 'queue_update':
        this.handleQueueUpdate(data.payload);
        break;
      case 'slice_progress':
        this.handleSliceProgress(data.payload);
        break;
      case 'print_progress':
        this.handlePrintProgress(data.payload);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  private handleJobUpdate(job: PrintJob) {
    this.currentJobs.set(job.id, job);
    this.emit('job_updated', job);
    this.updateJobStatus(job.id, job.status);
  }

  private handlePrinterStatus(printer: PrinterConfig) {
    this.printers.set(printer.id, printer);
    this.emit('printer_status_changed', printer);
  }

  private handleQueueUpdate(queue: PrintQueue) {
    this.queue = queue.jobs;
    this.emit('queue_updated', queue);
  }

  private handleSliceProgress(progress: { jobId: string; progress: number; stage: string }) {
    const job = this.currentJobs.get(progress.jobId);
    if (job) {
      job.progress = progress.progress;
      this.emit('slice_progress', progress);
    }
  }

  private handlePrintProgress(progress: { jobId: string; progress: number; layer: number; totalLayers: number }) {
    const job = this.currentJobs.get(progress.jobId);
    if (job) {
      job.progress = progress.progress;
      this.emit('print_progress', progress);
    }
  }

  private updateJobStatus(jobId: string, status: string) {
    const job = this.currentJobs.get(jobId);
    if (!job) return;

    const statusMessages: Record<string, string> = {
      queued: 'Job added to queue',
      processing: 'Processing job...',
      generating: 'Generating G-code...',
      ready: 'Ready to print',
      printing: 'Printing in progress',
      completed: 'Print completed successfully!',
      failed: 'Print failed',
      cancelled: 'Print cancelled'
    };

    if (statusMessages[status]) {
      toast.success(statusMessages[status]);
    }

    this.emit('status_changed', { jobId, status });
  }

  // Print Job Management
  async submitJob(jobConfig: Omit<PrintJob, 'id' | 'status' | 'progress' | 'createdAt'>): Promise<string> {
    try {
      const response = await apiService.submitPrintJob(jobConfig);
      const jobId = response.id;

      const newJob: PrintJob = {
        ...jobConfig,
        id: jobId,
        status: 'queued',
        progress: 0,
        createdAt: new Date()
      };

      this.currentJobs.set(jobId, newJob);
      this.queue.push(newJob);

      this.emit('job_created', newJob);
      toast.success('Print job submitted successfully!');
      
      return jobId;
    } catch (error) {
      console.error('❌ Failed to submit print job:', error);
      toast.error('Failed to submit print job');
      throw error;
    }
  }

  async cancelJob(jobId: string): Promise<void> {
    try {
      await apiService.cancelJob(jobId);
      
      const job = this.currentJobs.get(jobId);
      if (job) {
        job.status = 'cancelled';
        this.emit('job_cancelled', job);
      }
      
      this.removeFromQueue(jobId);
      toast.success('Print job cancelled');
    } catch (error) {
      console.error('❌ Failed to cancel print job:', error);
      toast.error('Failed to cancel print job');
      throw error;
    }
  }

  async pauseJob(jobId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/print/jobs/${jobId}/pause`);
      
      const job = this.currentJobs.get(jobId);
      if (job) {
        job.status = 'paused';
        this.emit('job_paused', job);
      }
      
      toast.success('Print job paused');
    } catch (error) {
      console.error('❌ Failed to pause print job:', error);
      toast.error('Failed to pause print job');
      throw error;
    }
  }

  async resumeJob(jobId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/print/jobs/${jobId}/resume`);
      
      const job = this.currentJobs.get(jobId);
      if (job) {
        job.status = 'printing';
        this.emit('job_resumed', job);
      }
      
      toast.success('Print job resumed');
    } catch (error) {
      console.error('❌ Failed to resume print job:', error);
      toast.error('Failed to resume print job');
      throw error;
    }
  }

  private removeFromQueue(jobId: string) {
    this.queue = this.queue.filter(job => job.id !== jobId);
    this.currentJobs.delete(jobId);
  }

  // Printer Management
  async loadPrinters(): Promise<PrinterConfig[]> {
    try {
      const printers = await apiService.getPrinters();

      this.printers.clear();
      printers.forEach((printer: PrinterConfig) => {
        this.printers.set(printer.id, printer);
      });

      return printers;
    } catch (error) {
      console.error('❌ Failed to load printers:', error);
      throw error;
    }
  }

  async getPrinterStatus(printerId: string): Promise<PrinterConfig> {
    try {
      const printer = await apiService.getPrinterStatus(printerId);
      
      this.printers.set(printerId, printer);
      return printer;
    } catch (error) {
      console.error('❌ Failed to get printer status:', error);
      throw error;
    }
  }

  async calibratePrinter(printerId: string, calibrationType: string): Promise<void> {
    try {
      await apiService.calibratePrinter(printerId, calibrationType);
      
      toast.success('Printer calibration started');
    } catch (error) {
      console.error('❌ Failed to calibrate printer:', error);
      toast.error('Failed to calibrate printer');
      throw error;
    }
  }

  // Material Management
  async loadMaterials(): Promise<MaterialLibrary[]> {
    try {
      this.materials = await apiService.getMaterials();
      return this.materials;
    } catch (error) {
      console.error('❌ Failed to load materials:', error);
      throw error;
    }
  }

  getMaterialsByType(type: string): MaterialLibrary[] {
    return this.materials.filter(material => material.type === type);
  }

  getMaterialById(id: string): MaterialLibrary | undefined {
    return this.materials.find(material => material.id === id);
  }

  async estimatePrintTime(settings: PrintSettings, modelData: any): Promise<number> {
    try {
      const response = await apiService.estimatePrintTime(settings, modelData);
      return response.estimatedTime;
    } catch (error) {
      console.error('❌ Failed to estimate print time:', error);
      throw error;
    }
  }

  async estimateMaterialUsage(settings: PrintSettings, modelData: any): Promise<number> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/print/estimate-material`, {
        settings,
        modelData
      });
      return response.data.materialUsage;
    } catch (error) {
      console.error('❌ Failed to estimate material usage:', error);
      throw error;
    }
  }

  // Slicing and G-code Generation
  async sliceModel(
    modelId: string, 
    settings: PrintSettings
  ): Promise<SlicingResult> {
    try {
      const response = await apiService.sliceModel(modelId, settings);
      
      return response;
    } catch (error) {
      console.error('❌ Failed to slice model:', error);
      toast.error('Failed to slice model');
      throw error;
    }
  }

  async generateGCode(
    modelId: string, 
    settings: PrintSettings
  ): Promise<string> {
    try {
      const response = await apiService.generateGCode(modelId, settings);
      
      return response.gcode;
    } catch (error) {
      console.error('❌ Failed to generate G-code:', error);
      toast.error('Failed to generate G-code');
      throw error;
    }
  }

  async optimizeGCode(gcode: string, settings: PrintSettings): Promise<string> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/print/optimize-gcode`, {
        gcode,
        settings
      });
      
      return response.data.optimizedGcode;
    } catch (error) {
      console.error('❌ Failed to optimize G-code:', error);
      throw error;
    }
  }

  // Quality Control and Analysis
  async analyzePrintability(modelData: any): Promise<any> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/print/analyze-printability`, {
        modelData
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to analyze printability:', error);
      throw error;
    }
  }

  async detectPrintIssues(jobId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/jobs/${jobId}/issues`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to detect print issues:', error);
      throw error;
    }
  }

  // Support Generation
  async generateSupports(
    modelId: string, 
    settings: PrintSettings
  ): Promise<any> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/print/generate-supports`, {
        modelId,
        settings
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to generate supports:', error);
      toast.error('Failed to generate supports');
      throw error;
    }
  }

  async optimizeSupports(supports: any): Promise<any> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/print/optimize-supports`, {
        supports
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to optimize supports:', error);
      throw error;
    }
  }

  // Print Queue Management
  async getQueue(): Promise<PrintJob[]> {
    try {
      this.queue = await apiService.getPrintQueue();
      return this.queue;
    } catch (error) {
      console.error('❌ Failed to get queue:', error);
      throw error;
    }
  }

  async reorderQueue(jobIds: string[]): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/print/queue/reorder`, {
        jobIds
      });
      
      // Update local queue order
      this.queue.sort((a, b) => jobIds.indexOf(a.id) - jobIds.indexOf(b.id));
      this.emit('queue_reordered', this.queue);
      
      toast.success('Queue reordered successfully');
    } catch (error) {
      console.error('❌ Failed to reorder queue:', error);
      toast.error('Failed to reorder queue');
      throw error;
    }
  }

  // Cloud Printing (Beta)
  async submitToCloudPrint(
    jobConfig: Omit<PrintJob, 'id' | 'status' | 'progress' | 'createdAt'>,
    cloudProvider: string = 'default'
  ): Promise<string> {
    if (!this.config.enableCloudPrint) {
      throw new Error('Cloud printing is not enabled');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/print/cloud/submit`, {
        ...jobConfig,
        provider: cloudProvider
      });
      
      const jobId = response.data.cloudJobId;
      toast.success('Print job submitted to cloud printing service');
      
      return jobId;
    } catch (error) {
      console.error('❌ Failed to submit to cloud print:', error);
      toast.error('Failed to submit to cloud printing');
      throw error;
    }
  }

  async trackCloudJob(cloudJobId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/cloud/jobs/${cloudJobId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to track cloud job:', error);
      throw error;
    }
  }

  // Print Statistics and Analytics
  async getPrintStatistics(userId: string, period: string = '30d'): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/statistics/${userId}`, {
        params: { period }
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get print statistics:', error);
      throw error;
    }
  }

  async getFailureAnalysis(jobId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/jobs/${jobId}/failure-analysis`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get failure analysis:', error);
      throw error;
    }
  }

  // File Management
  async uploadPrintFile(file: File, jobId: string): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('jobId', jobId);

      const response = await axios.post(`${this.config.apiUrl}/print/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data.fileId;
    } catch (error) {
      console.error('❌ Failed to upload print file:', error);
      toast.error('Failed to upload print file');
      throw error;
    }
  }

  async downloadGCode(jobId: string): Promise<Blob> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/jobs/${jobId}/gcode`, {
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to download G-code:', error);
      toast.error('Failed to download G-code');
      throw error;
    }
  }

  async downloadPrintPreview(jobId: string): Promise<string> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/jobs/${jobId}/preview`);
      return response.data.previewUrl;
    } catch (error) {
      console.error('❌ Failed to get print preview:', error);
      throw error;
    }
  }

  // Hardware Integration
  async connectToPrinter(printerId: string, connectionType: string = 'usb'): Promise<void> {
    if (!this.config.enableHardware) {
      throw new Error('Hardware integration is not enabled');
    }

    try {
      await axios.post(`${this.config.apiUrl}/print/hardware/connect`, {
        printerId,
        connectionType
      });
      
      toast.success('Printer connected successfully');
    } catch (error) {
      console.error('❌ Failed to connect to printer:', error);
      toast.error('Failed to connect to printer');
      throw error;
    }
  }

  async disconnectPrinter(printerId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/print/hardware/disconnect`, {
        printerId
      });
      
      toast.success('Printer disconnected');
    } catch (error) {
      console.error('❌ Failed to disconnect printer:', error);
      toast.error('Failed to disconnect printer');
      throw error;
    }
  }

  async getHardwareStatus(printerId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/print/hardware/status/${printerId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get hardware status:', error);
      throw error;
    }
  }

  // Getters
  getPrinters(): PrinterConfig[] {
    return Array.from(this.printers.values());
  }

  getPrinter(printerId: string): PrinterConfig | undefined {
    return this.printers.get(printerId);
  }

  getQueueJobs(): PrintJob[] {
    return [...this.queue];
  }

  getJob(jobId: string): PrintJob | undefined {
    return this.currentJobs.get(jobId);
  }

  isConnectedToHardware(): boolean {
    return this.isConnected && this.config.enableHardware;
  }

  isCloudPrintingEnabled(): boolean {
    return this.config.enableCloudPrint;
  }

  // Cleanup
  destroy(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.removeAllListeners();
    this.currentJobs.clear();
    this.queue = [];
  }
}

// Default settings presets
export const DEFAULT_PRINT_SETTINGS: PrintSettings = {
  layerHeight: 0.2,
  infill: 20,
  printSpeed: 50,
  nozzleDiameter: 0.4,
  bedTemperature: 60,
  nozzleTemperature: 200,
  supportType: 'none',
  brim: false,
  raft: false,
  cooling: true,
  adhesionType: 'none',
  retraction: true,
  travelSpeed: 200,
  wallThickness: 0.8,
  topBottomLayers: 3,
  printTime: 0,
  materialUsage: 0
};

// Quality presets
export const QUALITY_PRESETS = {
  draft: {
    layerHeight: 0.3,
    infill: 15,
    printSpeed: 60,
    topBottomLayers: 2
  },
  normal: {
    layerHeight: 0.2,
    infill: 20,
    printSpeed: 50,
    topBottomLayers: 3
  },
  fine: {
    layerHeight: 0.15,
    infill: 30,
    printSpeed: 40,
    topBottomLayers: 4
  },
  ultra: {
    layerHeight: 0.1,
    infill: 40,
    printSpeed: 30,
    topBottomLayers: 5
  }
};

// Material presets
export const MATERIAL_PRESETS = {
  PLA: {
    bedTemperature: 60,
    nozzleTemperature: 200,
    printSpeed: 50,
    cooling: true,
    retraction: true
  },
  ABS: {
    bedTemperature: 90,
    nozzleTemperature: 240,
    printSpeed: 40,
    cooling: false,
    retraction: true
  },
  PETG: {
    bedTemperature: 70,
    nozzleTemperature: 230,
    printSpeed: 45,
    cooling: true,
    retraction: true
  },
  TPU: {
    bedTemperature: 50,
    nozzleTemperature: 210,
    printSpeed: 25,
    cooling: true,
    retraction: false
  }
};

// Service instance
export const print3DService = new Print3DService({
  apiUrl: API_ENDPOINTS.PRINTING.BASE,
  wsUrl: `${API_ENDPOINTS.COLLABORATION.WS('printing')}`
});