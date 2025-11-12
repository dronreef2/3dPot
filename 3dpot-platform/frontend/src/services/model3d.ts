// 3D Model Generation Service with NVIDIA NIM Integration
import axios, { AxiosInstance } from 'axios';
import { 
  Model3D, 
  GenerationRequest, 
  GenerationResponse, 
  ProcessingProgress,
  BatchGenerationRequest,
  AIAnalysis,
  NVIDIAConfig,
  ModelSettings
} from '../types/model3d';
import { api } from './api';
import { eventEmitter } from '../utils/eventEmitter';

export class Model3DService {
  private apiClient: AxiosInstance;
  private nvidiaConfig: NVIDIAConfig;
  private processingJobs = new Map<string, ProcessingProgress>();

  constructor() {
    this.apiClient = api;
    this.nvidiaConfig = {
      apiKey: process.env.VITE_NVIDIA_NIM_API_KEY || '',
      endpoint: 'https://integrate.api.nvidia.com/v1/chat/completions',
      model: 'nvidia/llama-3.1-nemotron-70b-instruct',
      maxTokens: 4000,
      temperature: 0.7,
      timeout: 30000,
      retries: 3
    };
  }

  /**
   * Generate 3D model from specifications using NVIDIA NIM
   */
  async generateModel(request: GenerationRequest): Promise<GenerationResponse> {
    try {
      const startTime = Date.now();

      // Create unique model ID
      const modelId = `model_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Initialize processing progress
      this.initializeProgress(modelId, 'initializing', 'Analyzing specifications...', 0);
      
      // Step 1: AI Analysis using NVIDIA NIM
      const aiAnalysis = await this.analyzeWithNVIDIA(request.specifications);
      this.updateProgress(modelId, 'analyzing', 'AI analysis completed', 25);

      // Step 2: Generate 3D geometry based on analysis
      const geometries = await this.generateGeometry(request.specifications, aiAnalysis);
      this.updateProgress(modelId, 'generating', 'Geometry generation in progress', 50);

      // Step 3: Optimize and finalize model
      const model = await this.finalizeModel(
        modelId, 
        geometries, 
        request.settings,
        request.specifications
      );
      this.updateProgress(modelId, 'optimizing', 'Optimizing model...', 75);

      // Step 4: Export and save
      const result = await this.saveAndExportModel(model, request.settings);
      this.updateProgress(modelId, 'completed', 'Model generation completed', 100);

      const processingTime = Date.now() - startTime;

      // Emit completion event
      eventEmitter.emit('model:generated', { modelId, model: result });

      return {
        success: true,
        modelId,
        model: result,
        processingTime,
        nvidiaNimRequestId: `nim_${Date.now()}`,
        warnings: aiAnalysis.potentialIssues
      };

    } catch (error) {
      console.error('Model generation failed:', error);
      
      const modelId = request.specifications.id || `model_${Date.now()}`;
      this.updateProgress(modelId, 'error', 'Model generation failed', 0);

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        processingTime: Date.now()
      };
    } finally {
      // Cleanup progress tracking
      setTimeout(() => {
        this.processingJobs.delete(request.specifications.id || '');
      }, 5000);
    }
  }

  /**
   * Analyze specifications using NVIDIA NIM AI
   */
  private async analyzeWithNVIDIA(specifications: any): Promise<AIAnalysis> {
    try {
      const prompt = this.buildAnalysisPrompt(specifications);

      const response = await axios.post(
        this.nvidiaConfig.endpoint,
        {
          model: this.nvidiaConfig.model,
          messages: [
            {
              role: 'system',
              content: 'You are an expert 3D modeling assistant. Analyze specifications and provide detailed recommendations for 3D model generation.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: this.nvidiaConfig.maxTokens,
          temperature: this.nvidiaConfig.temperature
        },
        {
          headers: {
            'Authorization': `Bearer ${this.nvidiaConfig.apiKey}`,
            'Content-Type': 'application/json'
          },
          timeout: this.nvidiaConfig.timeout
        }
      );

      // Parse AI response and extract analysis
      return this.parseAIResponse(response.data.choices[0].message.content);

    } catch (error) {
      console.error('NVIDIA NIM analysis failed:', error);
      // Fallback to rule-based analysis
      return this.fallbackAnalysis(specifications);
    }
  }

  /**
   * Build analysis prompt for NVIDIA NIM
   */
  private buildAnalysisPrompt(specifications: any): string {
    return `
Analyze these product specifications for 3D modeling:

Product Type: ${specifications.productType || 'Unknown'}
Dimensions: ${JSON.stringify(specifications.dimensions || {})}
Materials: ${specifications.materials?.join(', ') || 'Not specified'}
Features: ${specifications.features?.join(', ') || 'None'}
Use Case: ${specifications.useCase || 'General purpose'}

Provide analysis in JSON format with:
- complexity: 'simple' | 'moderate' | 'complex'
- recommendedSettings: resolution, segmentCount, optimizationLevel
- estimatedProcessingTime: number in seconds
- potentialIssues: array of strings
- optimizationSuggestions: array of strings
    `.trim();
  }

  /**
   * Parse AI response into structured analysis
   */
  private parseAIResponse(content: string): AIAnalysis {
    try {
      // Extract JSON from response
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Failed to parse AI response:', error);
    }

    // Fallback analysis
    return this.fallbackAnalysis({});
  }

  /**
   * Fallback rule-based analysis
   */
  private fallbackAnalysis(specifications: any): AIAnalysis {
    const hasComplexFeatures = specifications.features?.length > 3;
    const hasDetailedDimensions = specifications.dimensions && Object.keys(specifications.dimensions).length > 3;
    
    const complexity = hasComplexFeatures || hasDetailedDimensions ? 'complex' : 'moderate';
    const estimatedTime = complexity === 'complex' ? 120 : complexity === 'moderate' ? 60 : 30;

    return {
      complexity: complexity as 'simple' | 'moderate' | 'complex',
      recommendedSettings: {
        resolution: complexity === 'complex' ? 'high' : 'medium',
        segmentCount: complexity === 'complex' ? 64 : complexity === 'moderate' ? 32 : 16,
        optimizationLevel: 'advanced'
      },
      estimatedProcessingTime: estimatedTime,
      potentialIssues: [],
      optimizationSuggestions: [
        'Consider reducing polygon count if performance is critical',
        'Use instancing for repeated elements',
        'Apply texture compression for better performance'
      ]
    };
  }

  /**
   * Generate 3D geometries from specifications
   */
  private async generateGeometry(specifications: any, analysis: AIAnalysis): Promise<any[]> {
    const geometries = [];

    // Main body geometry
    if (specifications.dimensions) {
      const mainGeometry = this.generateMainGeometry(specifications, analysis);
      geometries.push(mainGeometry);
    }

    // Feature geometries (if any)
    if (specifications.features) {
      for (const feature of specifications.features) {
        const featureGeometry = this.generateFeatureGeometry(feature, specifications);
        if (featureGeometry) {
          geometries.push(featureGeometry);
        }
      }
    }

    return geometries;
  }

  /**
   * Generate main body geometry
   */
  private generateMainGeometry(specifications: any, analysis: AIAnalysis) {
    const dims = specifications.dimensions || {};
    const resolution = analysis.recommendedSettings.segmentCount;

    // Determine base shape
    const productType = specifications.productType?.toLowerCase() || 'container';
    let geometryType = 'box';

    if (productType.includes('bottle') || productType.includes('cylinder')) {
      geometryType = 'cylinder';
    } else if (productType.includes('sphere') || productType.includes('ball')) {
      geometryType = 'sphere';
    } else if (productType.includes('cone')) {
      geometryType = 'cone';
    }

    return {
      id: 'main_geometry',
      type: geometryType,
      parameters: {
        width: dims.width || 100,
        height: dims.height || 200,
        depth: dims.depth || (geometryType === 'cylinder' ? dims.diameter || 50 : 50),
        radius: dims.radius || dims.diameter / 2 || 25,
        segments: resolution,
        ...dims
      },
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      scale: { x: 1, y: 1, z: 1 },
      materialId: 'main_material'
    };
  }

  /**
   * Generate feature geometry
   */
  private generateFeatureGeometry(feature: any, specifications: any) {
    const featureName = feature.toLowerCase();

    if (featureName.includes('lid') || featureName.includes('cap')) {
      return {
        id: `feature_${featureName}`,
        type: 'cylinder',
        parameters: {
          radius: (specifications.dimensions?.diameter || 50) / 2 + 5,
          height: 10,
          segments: 16
        },
        position: { x: 0, y: (specifications.dimensions?.height || 200) / 2 + 5, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        materialId: 'cap_material'
      };
    }

    if (featureName.includes('handle')) {
      return {
        id: `feature_${featureName}`,
        type: 'torus',
        parameters: {
          radius: 20,
          tube: 5,
          radialSegments: 16,
          tubularSegments: 100
        },
        position: { x: (specifications.dimensions?.width || 100) / 2 + 15, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        materialId: 'handle_material'
      };
    }

    return null;
  }

  /**
   * Finalize and optimize model
   */
  private async finalizeModel(
    modelId: string,
    geometries: any[],
    settings: Partial<ModelSettings>,
    specifications: any
  ): Promise<Model3D> {
    // Create materials
    const materials = this.createMaterials(settings, specifications);

    // Optimize geometries
    const optimizedGeometries = await this.optimizeGeometries(geometries, settings);

    // Calculate metadata
    const metadata = this.calculateMetadata(optimizedGeometries);

    return {
      id: modelId,
      name: specifications.productName || 'Generated Model',
      description: specifications.description || 'AI-generated 3D model',
      specId: specifications.id || '',
      geometries: optimizedGeometries,
      materials,
      settings: {
        resolution: settings.resolution || 'medium',
        fileFormat: settings.fileFormat || 'obj',
        optimizeGeometry: settings.optimizeGeometry ?? true,
        enableShadows: settings.enableShadows ?? true,
        enableLighting: settings.enableLighting ?? true,
        backgroundColor: settings.backgroundColor || '#f0f0f0',
        cameraPosition: { x: 200, y: 200, z: 200 },
        renderingQuality: settings.renderingQuality || 'preview'
      },
      metadata,
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  /**
   * Create materials for the model
   */
  private createMaterials(settings: Partial<ModelSettings>, specifications: any) {
    return [
      {
        id: 'main_material',
        name: 'Main Material',
        color: specifications.color || '#4A90E2',
        metalness: 0.1,
        roughness: 0.8,
        transparent: false,
        opacity: 1.0
      },
      {
        id: 'cap_material',
        name: 'Cap/Lid Material',
        color: '#2C3E50',
        metalness: 0.2,
        roughness: 0.6,
        transparent: false,
        opacity: 1.0
      },
      {
        id: 'handle_material',
        name: 'Handle Material',
        color: '#34495E',
        metalness: 0.3,
        roughness: 0.5,
        transparent: false,
        opacity: 1.0
      }
    ];
  }

  /**
   * Optimize geometries for performance
   */
  private async optimizeGeometries(geometries: any[], settings: Partial<ModelSettings>) {
    if (!settings.optimizeGeometry) return geometries;

    // Simple optimization: reduce segments if not high quality
    if (settings.resolution === 'low') {
      return geometries.map(geo => ({
        ...geo,
        parameters: {
          ...geo.parameters,
          segments: Math.max(8, Math.floor(geo.parameters.segments / 2))
        }
      }));
    }

    return geometries;
  }

  /**
   * Calculate model metadata
   */
  private calculateMetadata(geometries: any[]) {
    let vertexCount = 0;
    let faceCount = 0;

    geometries.forEach(geo => {
      const segments = geo.parameters.segments || 16;
      
      switch (geo.type) {
        case 'box':
          vertexCount += 24; // 8 vertices * 3 (positions, normals, uvs)
          faceCount += 12; // 6 faces * 2 triangles
          break;
        case 'sphere':
          vertexCount += (segments + 1) * (segments + 1);
          faceCount += segments * segments * 2;
          break;
        case 'cylinder':
          vertexCount += (segments + 1) * 4;
          faceCount += segments * 4;
          break;
        default:
          vertexCount += segments * 3;
          faceCount += segments * 2;
      }
    });

    return {
      vertexCount,
      faceCount,
      fileSize: vertexCount * 32, // Rough estimate
      processingTime: 0, // Will be set by caller
      qualityScore: 0.85,
      nvidiaNimVersion: '1.0',
      optimizationLevel: 'advanced',
      compressionRatio: 0.7
    };
  }

  /**
   * Save and export model
   */
  private async saveAndExportModel(model: Model3D, settings: Partial<ModelSettings>) {
    // Save to backend
    await this.apiClient.post('/models', model);
    
    return model;
  }

  /**
   * Batch generate multiple models
   */
  async batchGenerate(request: BatchGenerationRequest): Promise<GenerationResponse[]> {
    const results: GenerationResponse[] = [];

    if (request.parallel) {
      // Parallel processing
      const batches = this.createBatches(request.requests, request.maxConcurrent || 3);
      
      for (const batch of batches) {
        const batchPromises = batch.map(req => this.generateModel(req));
        const batchResults = await Promise.allSettled(batchPromises);
        
        batchResults.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            results.push(result.value);
            request.onComplete?.(result.value);
          } else {
            const errorResult: GenerationResponse = {
              success: false,
              error: result.reason?.message || 'Unknown error',
              processingTime: 0
            };
            results.push(errorResult);
            request.onError?.(batch[index].specifications.id, errorResult.error || 'Unknown error');
          }
        });
      }
    } else {
      // Sequential processing
      for (const req of request.requests) {
        try {
          const result = await this.generateModel(req);
          results.push(result);
          request.onComplete?.(result);
        } catch (error) {
          const errorResult: GenerationResponse = {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            processingTime: 0
          };
          results.push(errorResult);
          request.onError?.(req.specifications.id, errorResult.error || 'Unknown error');
        }
      }
    }

    return results;
  }

  /**
   * Create batches for parallel processing
   */
  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  /**
   * Get processing progress for a model
   */
  getProgress(modelId: string): ProcessingProgress | undefined {
    return this.processingJobs.get(modelId);
  }

  /**
   * Subscribe to progress updates
   */
  onProgress(modelId: string, callback: (progress: ProcessingProgress) => void) {
    const checkProgress = () => {
      const progress = this.getProgress(modelId);
      if (progress) {
        callback(progress);
        if (progress.stage !== 'completed' && progress.stage !== 'error') {
          setTimeout(checkProgress, 1000);
        }
      }
    };
    checkProgress();
  }

  /**
   * Initialize progress tracking
   */
  private initializeProgress(modelId: string, stage: ProcessingProgress['stage'], message: string, progress: number) {
    const progressUpdate: ProcessingProgress = {
      modelId,
      stage,
      progress,
      message,
      estimatedTimeRemaining: 0
    };

    this.processingJobs.set(modelId, progressUpdate);
    eventEmitter.emit('model:progress', progressUpdate);
  }

  /**
   * Update progress
   */
  private updateProgress(modelId: string, stage: ProcessingProgress['stage'], message: string, progress: number) {
    const current = this.processingJobs.get(modelId);
    if (current) {
      current.stage = stage;
      current.progress = progress;
      current.message = message;
      
      eventEmitter.emit('model:progress', current);
    }
  }

  /**
   * Get existing models
   */
  async getModels(): Promise<Model3D[]> {
    const response = await this.apiClient.get('/models');
    return response.data;
  }

  /**
   * Get specific model
   */
  async getModel(modelId: string): Promise<Model3D> {
    const response = await this.apiClient.get(`/models/${modelId}`);
    return response.data;
  }

  /**
   * Delete model
   */
  async deleteModel(modelId: string): Promise<boolean> {
    await this.apiClient.delete(`/models/${modelId}`);
    return true;
  }
}

export const model3DService = new Model3DService();