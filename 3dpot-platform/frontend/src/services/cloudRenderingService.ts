// Sprint 6+: Cloud Rendering Service
// Serviço completo para renderização distribuída na nuvem

import { EventEmitter } from 'events';
import toast from 'react-hot-toast';
import { apiService } from './api';
import { API_ENDPOINTS } from '@/utils/config';

// Types
import type {
  RenderJob,
  RenderCluster,
  RenderConfiguration,
  RenderResult,
  RenderProgress,
  RenderBilling,
  RenderQueue,
  DistributedRenderer,
  RenderQueueFilter,
  RenderUsage
} from '@/types/cloudRendering';

interface CloudRenderingServiceConfig {
  apiUrl: string;
  wsUrl: string;
  maxConcurrentJobs: number;
  defaultTimeout: number;
  enableGPU: boolean;
  enableAutoScaling: boolean;
  preferredRegion: string;
}

export class CloudRenderingService extends EventEmitter {
  private config: CloudRenderingServiceConfig;
  private jobs: Map<string, RenderJob> = new Map();
  private clusters: Map<string, RenderCluster> = new Map();
  private queue: RenderJob[] = [];
  private activeJobs: Set<string> = new Set();
  private completedJobs: Set<string> = new Set();
  private failedJobs: Set<string> = new Set();
  private results: Map<string, RenderResult[]> = new Map();
  private currentUser: string | null = null;
  private ws: WebSocket | null = null;
  private isConnected = false;
  private pollInterval: NodeJS.Timeout | null = null;

  constructor(config: CloudRenderingServiceConfig) {
    super();
    this.config = {
      maxConcurrentJobs: 5,
      defaultTimeout: 30 * 60 * 1000, // 30 minutes
      enableGPU: true,
      enableAutoScaling: true,
      preferredRegion: 'us-east-1',
      ...config
    };
    this.initializeConnection();
  }

  private async initializeConnection() {
    try {
      await this.connectWebSocket();
      await this.loadClusters();
      await this.loadUserJobs();
      console.log('☁️ Cloud Rendering service connected');
    } catch (error) {
      console.error('❌ Failed to connect Cloud Rendering service:', error);
      this.reconnectWebSocket();
    }
  }

  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.config.wsUrl}/cloud-rendering`);
        
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
      console.log('🔄 Reconnecting Cloud Rendering WebSocket...');
      this.initializeConnection().catch(console.error);
    }, 5000);
  }

  private handleWebSocketMessage(data: any) {
    switch (data.type) {
      case 'job_update':
        this.handleJobUpdate(data.payload);
        break;
      case 'progress_update':
        this.handleProgressUpdate(data.payload);
        break;
      case 'cluster_status':
        this.handleClusterStatus(data.payload);
        break;
      case 'queue_update':
        this.handleQueueUpdate(data.payload);
        break;
      case 'result_ready':
        this.handleResultReady(data.payload);
        break;
      case 'billing_update':
        this.handleBillingUpdate(data.payload);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  private handleJobUpdate(job: RenderJob) {
    this.jobs.set(job.id, job);
    
    // Update job sets
    this.activeJobs.delete(job.id);
    this.completedJobs.delete(job.id);
    this.failedJobs.delete(job.id);
    
    switch (job.status) {
      case 'rendering':
      case 'uploading':
      case 'processing':
        this.activeJobs.add(job.id);
        break;
      case 'completed':
        this.completedJobs.add(job.id);
        break;
      case 'failed':
      case 'timeout':
        this.failedJobs.add(job.id);
        break;
    }

    this.emit('job_updated', job);
    this.updateJobStatusToast(job);
  }

  private handleProgressUpdate(progress: RenderProgress) {
    const job = this.jobs.get(progress.jobId || '');
    if (job && progress.jobId === job.id) {
      job.progress = progress;
      this.emit('progress_updated', progress);
    }
  }

  private handleClusterStatus(cluster: RenderCluster) {
    this.clusters.set(cluster.id, cluster);
    this.emit('cluster_status_changed', cluster);
  }

  private handleQueueUpdate(queue: RenderQueue) {
    this.queue = queue.jobs || [];
    this.emit('queue_updated', queue);
  }

  private handleResultReady(result: RenderResult) {
    const results = this.results.get(result.jobId) || [];
    results.push(result);
    this.results.set(result.jobId, results);
    
    this.emit('result_ready', result);
    
    if (this.currentUser) {
      toast.success('Render completed and ready for download!');
    }
  }

  private handleBillingUpdate(billing: RenderBilling) {
    this.emit('billing_updated', billing);
  }

  private updateJobStatusToast(job: RenderJob) {
    const statusMessages: Record<string, string> = {
      queued: 'Job queued for rendering',
      pending: 'Job pending approval',
      assigned: 'Job assigned to cluster',
      rendering: 'Rendering in progress...',
      uploading: 'Uploading results...',
      completed: 'Render completed successfully!',
      failed: 'Render failed',
      cancelled: 'Render cancelled',
      timeout: 'Render timeout',
      retrying: 'Retrying render...',
      paused: 'Render paused'
    };

    if (statusMessages[job.status]) {
      if (job.status === 'completed') {
        toast.success(statusMessages[job.status]);
      } else if (job.status === 'failed' || job.status === 'timeout') {
        toast.error(statusMessages[job.status]);
      } else if (job.status === 'rendering') {
        // Don't spam progress messages
        return;
      } else {
        toast.info(statusMessages[job.status]);
      }
    }
  }

  // Job Management
  async submitJob(
    modelId: string,
    configuration: RenderConfiguration,
    priority: 'low' | 'normal' | 'high' | 'urgent' = 'normal'
  ): Promise<string> {
    try {
      const jobData = {
        modelId,
        configuration,
        priority,
        userId: this.currentUser,
        timeout: this.config.defaultTimeout
      };

      const jobResponse = await apiService.submitRenderJob(jobData);
      const jobId = jobResponse.id;
      
      // Create local job record
      const job: RenderJob = {
        id: jobId,
        sessionId: jobResponse.sessionId,
        modelId,
        userId: this.currentUser!,
        type: this.determineJobType(configuration),
        priority,
        status: 'queued',
        configuration,
        progress: {
          percentage: 0,
          currentPass: 'initializing',
          totalPasses: 1,
          currentSample: 0,
          totalSamples: 1,
          timeElapsed: 0,
          timeRemaining: 0,
          estimatedFinish: new Date(),
          samplesPerSecond: 0,
          memoryUsed: 0,
          memoryPeak: 0,
          gpuUsage: {
            index: 0,
            name: 'Unknown',
            utilization: 0,
            memoryUsed: 0,
            memoryTotal: 0,
            temperature: 0,
            powerDraw: 0,
            fanSpeed: 0,
            clock: 0
          },
          cpuUsage: {
            utilization: 0,
            cores: [],
            temperature: 0,
            powerDraw: 0,
            clock: 0
          },
          networkUpload: 0
        },
        results: [],
        cluster: {
          id: '',
          name: '',
          type: 'cpu',
          status: 'active',
          location: {
            region: this.config.preferredRegion,
            datacenter: '',
            country: '',
            city: '',
            coordinates: { x: 0, y: 0 },
            timezone: 'UTC'
          },
          specifications: {
            totalNodes: 1,
            cpuCores: 1,
            gpuCount: 0,
            gpuModel: '',
            gpuMemory: 0,
            ram: 0,
            storage: 0,
            bandwidth: 0,
            networkLatency: 0
          },
          pricing: {
            currency: 'USD',
            costPerHour: 0,
            costPerCoreHour: 0,
            costPerGpuHour: 0,
            minimumCharge: 0,
            discountTier: [],
            spotPricing: false
          },
          queue: {
            position: 0,
            priority: 0,
            waitingTime: 0,
            estimatedStart: new Date(),
            dependencies: [],
            resources: [],
            scheduling: {
              algorithm: 'fifo',
              timeout: 0,
              retryDelay: 0,
              maxRetries: 0,
              preemptive: false,
              batchMode: false
            }
          },
          capacity: {
            total: 1,
            available: 1,
            occupied: 0,
            reserved: 0,
            maintenance: 0,
            load: 0,
            queueSize: 0,
            estimatedWait: 0
          },
          performance: {
            averageRenderTime: 0,
            successRate: 100,
            throughput: 0,
            efficiency: 100,
            reliability: 100,
            uptime: 100
          },
          monitoring: {
            status: 'healthy',
            alerts: [],
            metrics: {
              cpuUtilization: 0,
              memoryUtilization: 0,
              gpuUtilization: 0,
              storageUtilization: 0,
              networkUtilization: 0,
              temperature: 0,
              errorRate: 0,
              throughput: 0,
              responseTime: 0
            },
            maintenance: []
          }
        },
        queue: {
          position: 0,
          priority: this.getPriorityValue(priority),
          waitingTime: 0,
          estimatedStart: new Date(Date.now() + 60000), // 1 minute estimate
          dependencies: [],
          resources: [],
          scheduling: {
            algorithm: 'fifo',
            timeout: this.config.defaultTimeout,
            retryDelay: 5000,
            maxRetries: 3,
            preemptive: false,
            batchMode: false
          }
        },
        billing: {
          usage: {
            computeHours: 0,
            gpuHours: 0,
            storageGB: 0,
            bandwidthGB: 0,
            requests: 1,
            premiumRequests: 0
          },
          cost: {
            compute: 0,
            storage: 0,
            bandwidth: 0,
            premium: 0,
            subtotal: 0,
            tax: 0,
            total: 0,
            currency: 'USD',
            estimated: true
          },
          credits: {
            total: 1000,
            used: 0,
            remaining: 1000,
            expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
            bonuses: []
          },
          billing: {
            type: 'hourly',
            start: new Date(),
            end: new Date(),
            nextBilling: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
            paymentMethod: 'default',
            invoiceTemplate: 'standard',
            taxRate: 0,
            currency: 'USD'
          }
        },
        createdAt: new Date(),
        estimatedTime: this.estimateRenderTime(configuration),
        retryCount: 0,
        maxRetries: 3,
        tags: [],
        dependencies: []
      };

      this.jobs.set(jobId, job);
      this.queue.push(job);

      this.emit('job_created', job);
      toast.success('Render job submitted successfully!');
      
      return jobId;
    } catch (error) {
      console.error('❌ Failed to submit render job:', error);
      toast.error('Failed to submit render job');
      throw error;
    }
  }

  private determineJobType(configuration: RenderConfiguration): any {
    if (configuration.vr?.enabled) return 'vr_360';
    if (configuration.ar?.enabled) return 'ar_preview';
    if (configuration.animation?.enabled) return 'animation';
    if (configuration.quality.level === 'photorealistic') return 'high_resolution';
    if (configuration.quality.level === 'draft') return 'preview';
    return 'quality_check';
  }

  private getPriorityValue(priority: string): number {
    const priorityValues = {
      low: 1,
      normal: 2,
      high: 3,
      urgent: 4
    };
    return priorityValues[priority as keyof typeof priorityValues] || 2;
  }

  private estimateRenderTime(configuration: RenderConfiguration): number {
    // Simple estimation based on resolution and quality
    const baseTime = 30; // 30 seconds base
    const resolutionMultiplier = (configuration.resolution.width * configuration.resolution.height) / (1920 * 1080);
    const qualityMultiplier = {
      draft: 0.5,
      medium: 1,
      high: 2,
      ultra: 3,
      photorealistic: 5
    }[configuration.quality.level];

    return Math.round(baseTime * resolutionMultiplier * qualityMultiplier);
  }

  async cancelJob(jobId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}`);
      
      const job = this.jobs.get(jobId);
      if (job) {
        job.status = 'cancelled';
        this.activeJobs.delete(jobId);
        this.emit('job_cancelled', job);
      }
      
      toast.success('Render job cancelled');
    } catch (error) {
      console.error('❌ Failed to cancel render job:', error);
      toast.error('Failed to cancel render job');
      throw error;
    }
  }

  async pauseJob(jobId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/pause`);
      
      const job = this.jobs.get(jobId);
      if (job) {
        job.status = 'paused';
        this.activeJobs.delete(jobId);
        this.emit('job_paused', job);
      }
      
      toast.success('Render job paused');
    } catch (error) {
      console.error('❌ Failed to pause render job:', error);
      toast.error('Failed to pause render job');
      throw error;
    }
  }

  async resumeJob(jobId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/resume`);
      
      const job = this.jobs.get(jobId);
      if (job) {
        job.status = 'rendering';
        this.activeJobs.add(jobId);
        this.emit('job_resumed', job);
      }
      
      toast.success('Render job resumed');
    } catch (error) {
      console.error('❌ Failed to resume render job:', error);
      toast.error('Failed to resume render job');
      throw error;
    }
  }

  async retryJob(jobId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/retry`);
      
      const job = this.jobs.get(jobId);
      if (job) {
        job.status = 'queued';
        job.retryCount++;
        this.failedJobs.delete(jobId);
        this.emit('job_retried', job);
      }
      
      toast.success('Render job retry initiated');
    } catch (error) {
      console.error('❌ Failed to retry render job:', error);
      toast.error('Failed to retry render job');
      throw error;
    }
  }

  // Cluster Management
  async loadClusters(): Promise<RenderCluster[]> {
    try {
      const clusters = await apiService.getRenderClusters();

      this.clusters.clear();
      clusters.forEach((cluster: RenderCluster) => {
        this.clusters.set(cluster.id, cluster);
      });

      return clusters;
    } catch (error) {
      console.error('❌ Failed to load clusters:', error);
      throw error;
    }
  }

  async getBestCluster(configuration: RenderConfiguration): Promise<RenderCluster | null> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/cloud-rendering/clusters/select`, {
        configuration,
        userRegion: this.config.preferredRegion,
        gpuRequired: this.config.enableGPU && (this.needsGPU(configuration) || configuration.quality.level === 'photorealistic')
      });

      return response.data;
    } catch (error) {
      console.error('❌ Failed to get best cluster:', error);
      return null;
    }
  }

  private needsGPU(configuration: RenderConfiguration): boolean {
    return configuration.quality.level === 'ultra' || 
           configuration.quality.level === 'photorealistic' ||
           configuration.animation?.enabled ||
           configuration.postProcessing?.enabled;
  }

  // Queue Management
  async getQueue(filter?: RenderQueueFilter): Promise<RenderJob[]> {
    try {
      const params = new URLSearchParams();
      if (filter?.status) params.append('status', filter.status.join(','));
      if (filter?.priority) params.append('priority', filter.priority.join(','));
      if (filter?.userId) params.append('userId', filter.userId);

      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/queue?${params}`);
      this.queue = response.data;
      return this.queue;
    } catch (error) {
      console.error('❌ Failed to get queue:', error);
      throw error;
    }
  }

  async prioritizeJob(jobId: string, newPriority: 'low' | 'normal' | 'high' | 'urgent'): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/prioritize`, {
        priority: newPriority
      });
      
      const job = this.jobs.get(jobId);
      if (job) {
        job.priority = newPriority;
        this.emit('job_prioritized', { jobId, priority: newPriority });
      }
      
      toast.success('Job priority updated');
    } catch (error) {
      console.error('❌ Failed to prioritize job:', error);
      toast.error('Failed to prioritize job');
      throw error;
    }
  }

  // Cost Estimation
  async estimateCost(configuration: RenderConfiguration): Promise<any> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/cloud-rendering/estimate-cost`, {
        configuration,
        userRegion: this.config.preferredRegion,
        useSpotPricing: true
      });

      return response.data;
    } catch (error) {
      console.error('❌ Failed to estimate cost:', error);
      throw error;
    }
  }

  // Batch Processing
  async submitBatchJob(
    configurations: RenderConfiguration[],
    batchName: string,
    priority: 'low' | 'normal' | 'high' | 'urgent' = 'normal'
  ): Promise<string> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/cloud-rendering/batch`, {
        configurations,
        batchName,
        priority,
        userId: this.currentUser
      });

      const batchId = response.data.id;
      
      // Create batch job record
      const batchJob: RenderJob = {
        id: batchId,
        sessionId: response.data.sessionId,
        modelId: 'batch',
        userId: this.currentUser!,
        type: 'batch_processing',
        priority,
        status: 'queued',
        configuration: {
          ...configurations[0],
          batch: {
            enabled: true,
            models: configurations.map((_, i) => `config_${i}`),
            angles: [],
            formats: configurations[0].format ? [configurations[0].format] : [],
            qualities: configurations.map(c => c.quality),
            parallel: true,
            maxConcurrency: this.config.maxConcurrentJobs
          }
        },
        progress: {
          percentage: 0,
          currentPass: `Processing batch (${configurations.length} jobs)`,
          totalPasses: configurations.length,
          currentSample: 0,
          totalSamples: configurations.length,
          timeElapsed: 0,
          timeRemaining: configurations.length * 60, // Estimate 1 minute per job
          estimatedFinish: new Date(Date.now() + configurations.length * 60 * 1000),
          samplesPerSecond: 0,
          memoryUsed: 0,
          memoryPeak: 0,
          gpuUsage: {
            index: 0,
            name: 'Batch Processing',
            utilization: 0,
            memoryUsed: 0,
            memoryTotal: 0,
            temperature: 0,
            powerDraw: 0,
            fanSpeed: 0,
            clock: 0
          },
          cpuUsage: {
            utilization: 0,
            cores: [],
            temperature: 0,
            powerDraw: 0,
            clock: 0
          },
          networkUpload: 0
        },
        results: [],
        cluster: {
          id: '',
          name: 'Batch Processing Cluster',
          type: 'cpu',
          status: 'active',
          location: {
            region: this.config.preferredRegion,
            datacenter: 'Batch DC',
            country: 'US',
            city: 'Any',
            coordinates: { x: 0, y: 0 },
            timezone: 'UTC'
          },
          specifications: {
            totalNodes: configurations.length,
            cpuCores: configurations.length * 8,
            gpuCount: 0,
            gpuModel: '',
            gpuMemory: 0,
            ram: configurations.length * 32,
            storage: configurations.length * 100,
            bandwidth: 1000,
            networkLatency: 0
          },
          pricing: {
            currency: 'USD',
            costPerHour: configurations.length * 2, // $2 per hour per node
            costPerCoreHour: configurations.length * 0.05,
            costPerGpuHour: 0,
            minimumCharge: 0,
            discountTier: [],
            spotPricing: true
          },
          queue: {
            position: 0,
            priority: this.getPriorityValue(priority),
            waitingTime: 0,
            estimatedStart: new Date(),
            dependencies: [],
            resources: [],
            scheduling: {
              algorithm: 'fair_share',
              timeout: this.config.defaultTimeout,
              retryDelay: 5000,
              maxRetries: 3,
              preemptive: false,
              batchMode: true
            }
          },
          capacity: {
            total: configurations.length,
            available: configurations.length,
            occupied: 0,
            reserved: 0,
            maintenance: 0,
            load: 0,
            queueSize: configurations.length,
            estimatedWait: 0
          },
          performance: {
            averageRenderTime: configurations.length * 60,
            successRate: 98,
            throughput: configurations.length,
            efficiency: 90,
            reliability: 99,
            uptime: 99.9
          },
          monitoring: {
            status: 'healthy',
            alerts: [],
            metrics: {
              cpuUtilization: 50,
              memoryUtilization: 60,
              gpuUtilization: 0,
              storageUtilization: 30,
              networkUtilization: 20,
              temperature: 0,
              errorRate: 2,
              throughput: configurations.length,
              responseTime: 100
            },
            maintenance: []
          }
        },
        queue: {
          position: 0,
          priority: this.getPriorityValue(priority),
          waitingTime: 0,
          estimatedStart: new Date(),
          dependencies: [],
          resources: [],
          scheduling: {
            algorithm: 'fair_share',
            timeout: this.config.defaultTimeout,
            retryDelay: 5000,
            maxRetries: 3,
            preemptive: false,
            batchMode: true
          }
        },
        billing: {
          usage: {
            computeHours: configurations.length,
            gpuHours: 0,
            storageGB: configurations.length * 10,
            bandwidthGB: configurations.length * 1,
            requests: configurations.length,
            premiumRequests: 0
          },
          cost: {
            compute: configurations.length * 2,
            storage: configurations.length * 0.1,
            bandwidth: configurations.length * 0.05,
            premium: 0,
            subtotal: configurations.length * 2.15,
            tax: 0,
            total: configurations.length * 2.15,
            currency: 'USD',
            estimated: true
          },
          credits: {
            total: 1000,
            used: configurations.length * 2.15,
            remaining: 1000 - (configurations.length * 2.15),
            expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
            bonuses: []
          },
          billing: {
            type: 'hourly',
            start: new Date(),
            end: new Date(),
            nextBilling: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
            paymentMethod: 'default',
            invoiceTemplate: 'standard',
            taxRate: 0,
            currency: 'USD'
          }
        },
        createdAt: new Date(),
        estimatedTime: configurations.length * 60,
        retryCount: 0,
        maxRetries: 3,
        tags: ['batch'],
        dependencies: []
      };

      this.jobs.set(batchId, batchJob);
      this.queue.push(batchJob);

      this.emit('batch_job_created', batchJob);
      toast.success(`Batch job submitted with ${configurations.length} renders!`);
      
      return batchId;
    } catch (error) {
      console.error('❌ Failed to submit batch job:', error);
      toast.error('Failed to submit batch job');
      throw error;
    }
  }

  // Results Management
  async getResults(jobId: string): Promise<RenderResult[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/results`);
      const results = response.data;
      
      this.results.set(jobId, results);
      return results;
    } catch (error) {
      console.error('❌ Failed to get results:', error);
      throw error;
    }
  }

  async downloadResult(resultId: string): Promise<Blob> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/results/${resultId}/download`, {
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to download result:', error);
      toast.error('Failed to download result');
      throw error;
    }
  }

  async deleteResult(resultId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/cloud-rendering/results/${resultId}`);
      toast.success('Result deleted');
    } catch (error) {
      console.error('❌ Failed to delete result:', error);
      toast.error('Failed to delete result');
      throw error;
    }
  }

  // Billing and Usage
  async getUsage(userId: string, period: { start: Date; end: Date }): Promise<RenderUsage> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/usage/${userId}`, {
        params: {
          start: period.start.toISOString(),
          end: period.end.toISOString()
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get usage:', error);
      throw error;
    }
  }

  async getBilling(userId: string, period: { start: Date; end: Date }): Promise<RenderBilling> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/billing/${userId}`, {
        params: {
          start: period.start.toISOString(),
          end: period.end.toISOString()
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get billing:', error);
      throw error;
    }
  }

  // Analytics and Monitoring
  async getJobAnalytics(jobId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/jobs/${jobId}/analytics`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get job analytics:', error);
      throw error;
    }
  }

  async getClusterPerformance(clusterId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/clusters/${clusterId}/performance`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get cluster performance:', error);
      throw error;
    }
  }

  async getGlobalAnalytics(timeframe: string = '24h'): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/analytics`, {
        params: { timeframe }
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get global analytics:', error);
      throw error;
    }
  }

  // User Management
  setCurrentUser(userId: string): void {
    this.currentUser = userId;
  }

  private async loadUserJobs(): Promise<void> {
    if (!this.currentUser) return;

    try {
      const response = await axios.get(`${this.config.apiUrl}/cloud-rendering/jobs`, {
        params: { userId: this.currentUser }
      });

      const jobs = response.data;
      this.jobs.clear();
      jobs.forEach((job: RenderJob) => {
        this.jobs.set(job.id, job);
      });
    } catch (error) {
      console.error('Failed to load user jobs:', error);
    }
  }

  // Start/Stop Polling
  startPolling(interval: number = 5000): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    this.pollInterval = setInterval(async () => {
      if (this.currentUser) {
        await this.loadUserJobs();
      }
    }, interval);
  }

  stopPolling(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }

  // Getters
  getJobs(): RenderJob[] {
    return Array.from(this.jobs.values());
  }

  getJob(jobId: string): RenderJob | undefined {
    return this.jobs.get(jobId);
  }

  getClusters(): RenderCluster[] {
    return Array.from(this.clusters.values());
  }

  getCluster(clusterId: string): RenderCluster | undefined {
    return this.clusters.get(clusterId);
  }

  getQueueJobs(): RenderJob[] {
    return [...this.queue];
  }

  getActiveJobs(): RenderJob[] {
    return Array.from(this.activeJobs).map(id => this.jobs.get(id)).filter(Boolean) as RenderJob[];
  }

  getCompletedJobs(): RenderJob[] {
    return Array.from(this.completedJobs).map(id => this.jobs.get(id)).filter(Boolean) as RenderJob[];
  }

  getFailedJobs(): RenderJob[] {
    return Array.from(this.failedJobs).map(id => this.jobs.get(id)).filter(Boolean) as RenderJob[];
  }

  getJobResults(jobId: string): RenderResult[] {
    return this.results.get(jobId) || [];
  }

  isConnected(): boolean {
    return this.isConnected;
  }

  getActiveJobCount(): number {
    return this.activeJobs.size;
  }

  getQueuePosition(jobId: string): number {
    return this.queue.findIndex(job => job.id === jobId) + 1;
  }

  // Cleanup
  destroy(): void {
    this.stopPolling();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.jobs.clear();
    this.clusters.clear();
    this.queue = [];
    this.activeJobs.clear();
    this.completedJobs.clear();
    this.failedJobs.clear();
    this.results.clear();
    this.currentUser = null;
    
    this.removeAllListeners();
  }
}

// Configuration presets
export const RENDER_PRESETS = {
  preview: {
    resolution: { width: 1280, height: 720, aspectRatio: '16:9', dpi: 72, pixelRatio: 1 },
    quality: {
      level: 'draft' as const,
      samples: 16,
      maxRayDepth: 2,
      caustics: false,
      globalIllumination: false,
      ambientOcclusion: false,
      motionBlur: false,
      depthOfField: false,
      sss: false,
      causticsAccuracy: 'low' as const,
      rayTracing: false,
      denoising: false,
      aiEnhancement: false
    }
  },
  medium: {
    resolution: { width: 1920, height: 1080, aspectRatio: '16:9', dpi: 96, pixelRatio: 1 },
    quality: {
      level: 'high' as const,
      samples: 64,
      maxRayDepth: 3,
      caustics: true,
      globalIllumination: true,
      ambientOcclusion: true,
      motionBlur: false,
      depthOfField: true,
      sss: false,
      causticsAccuracy: 'medium' as const,
      rayTracing: true,
      denoising: true,
      aiEnhancement: true
    }
  },
  high: {
    resolution: { width: 3840, height: 2160, aspectRatio: '16:9', dpi: 150, pixelRatio: 1 },
    quality: {
      level: 'ultra' as const,
      samples: 256,
      maxRayDepth: 5,
      caustics: true,
      globalIllumination: true,
      ambientOcclusion: true,
      motionBlur: true,
      depthOfField: true,
      sss: true,
      causticsAccuracy: 'high' as const,
      rayTracing: true,
      denoising: true,
      aiEnhancement: true
    }
  },
  photorealistic: {
    resolution: { width: 7680, height: 4320, aspectRatio: '16:9', dpi: 300, pixelRatio: 1 },
    quality: {
      level: 'photorealistic' as const,
      samples: 1024,
      maxRayDepth: 8,
      caustics: true,
      globalIllumination: true,
      ambientOcclusion: true,
      motionBlur: true,
      depthOfField: true,
      sss: true,
      causticsAccuracy: 'high' as const,
      rayTracing: true,
      denoising: true,
      aiEnhancement: true
    }
  }
};

// Service instance
export const cloudRenderingService = new CloudRenderingService({
  apiUrl: API_ENDPOINTS.CLOUD_RENDERING.BASE,
  wsUrl: API_ENDPOINTS.CLOUD_RENDERING.BASE.replace('/api', '/ws')
});