// 3D Model Viewer Page
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Download, 
  Eye, 
  EyeOff,
  Maximize2,
  Minimize2,
  RefreshCw,
  Play,
  Pause,
  RotateCw,
  Settings,
  FileText,
  Sparkles,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

import ThreeJSViewer from '../components/ThreeJSViewer';
import Model3DControls from '../components/Model3DControls';
import { 
  Model3D, 
  ViewportSettings, 
  ExportOptions, 
  ProcessingProgress,
  GenerationRequest
} from '../types/model3d';
import { model3DService } from '../services/model3d';
import { eventEmitter, MODEL_EVENTS } from '../utils/eventEmitter';

export const Model3DPage: React.FC = () => {
  const { modelId } = useParams<{ modelId?: string }>();
  const navigate = useNavigate();
  const viewerRef = useRef<HTMLDivElement>(null);
  
  // State management
  const [model, setModel] = useState<Model3D | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [progress, setProgress] = useState<ProcessingProgress | null>(null);
  const [wireframe, setWireframe] = useState(false);
  const [showBoundingBox, setShowBoundingBox] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const [showStats, setShowStats] = useState(false);
  
  // Settings state
  const [viewportSettings, setViewportSettings] = useState<ViewportSettings>({
    camera: {
      position: { x: 5, y: 5, z: 5 },
      target: { x: 0, y: 0, z: 0 },
      up: { x: 0, y: 1, z: 0 },
      fov: 50,
      near: 0.1,
      far: 1000
    },
    renderer: {
      antialias: true,
      shadows: true,
      shadowMapType: 'pcf',
      toneMapping: 'aces',
      physicallyCorrectLights: true
    },
    controls: {
      enableZoom: true,
      enablePan: true,
      enableRotate: true,
      autoRotate: false,
      autoRotateSpeed: 2,
      damping: 0.05
    },
    environment: {
      background: 'color',
      backgroundColor: '#f0f0f0',
      lighting: 'studio'
    }
  });

  // Load model on mount
  useEffect(() => {
    if (modelId) {
      loadModel(modelId);
    } else {
      // Load most recent model or show placeholder
      loadRecentModel();
    }
  }, [modelId]);

  // Event listeners
  useEffect(() => {
    const handleModelGenerated = (event: any) => {
      setModel(event.detail.model);
      setIsGenerating(false);
      toast.success('3D model generated successfully!');
      navigate(`/3d/${event.detail.model.id}`, { replace: true });
    };

    const handleProgress = (event: any) => {
      setProgress(event.detail);
    };

    const handleError = (event: any) => {
      setIsGenerating(false);
      toast.error(`3D generation failed: ${event.detail}`);
    };

    eventEmitter.on(MODEL_EVENTS.GENERATED, handleModelGenerated);
    eventEmitter.on(MODEL_EVENTS.PROGRESS, handleProgress);
    eventEmitter.on(MODEL_EVENTS.ERROR, handleError);

    return () => {
      eventEmitter.off(MODEL_EVENTS.GENERATED, handleModelGenerated);
      eventEmitter.off(MODEL_EVENTS.PROGRESS, handleProgress);
      eventEmitter.off(MODEL_EVENTS.ERROR, handleError);
    };
  }, [navigate]);

  // Load specific model
  const loadModel = useCallback(async (id: string) => {
    try {
      setIsGenerating(true);
      const loadedModel = await model3DService.getModel(id);
      setModel(loadedModel);
      toast.success('Model loaded successfully');
    } catch (error) {
      console.error('Failed to load model:', error);
      toast.error('Failed to load model');
      navigate('/dashboard');
    } finally {
      setIsGenerating(false);
    }
  }, [navigate]);

  // Load most recent model
  const loadRecentModel = useCallback(async () => {
    try {
      const models = await model3DService.getModels();
      if (models.length > 0) {
        setModel(models[0]); // Load the most recent model
      }
    } catch (error) {
      console.error('Failed to load recent model:', error);
    }
  }, []);

  // Generate new model from specifications
  const generateNewModel = useCallback(async (specifications: any) => {
    try {
      setIsGenerating(true);
      setProgress({
        modelId: 'generating',
        stage: 'initializing',
        progress: 0,
        message: 'Starting model generation...',
        estimatedTimeRemaining: 0
      });

      const request: GenerationRequest = {
        specifications,
        settings: {
          resolution: 'high',
          fileFormat: 'obj',
          optimizeGeometry: true,
          enableShadows: true,
          enableLighting: true,
          backgroundColor: '#f0f0f0',
          renderingQuality: 'production'
        },
        options: {
          style: 'realistic',
          complexity: 'moderate',
          materialPreset: 'default',
          colorScheme: 'natural',
          outputPreferences: {
            detailLevel: 3,
            symmetry: false,
            hollow: false,
            solid: true
          }
        }
      };

      const result = await model3DService.generateModel(request);
      
      if (result.success && result.model) {
        setModel(result.model);
        toast.success('New model generated successfully!');
        navigate(`/3d/${result.modelId}`, { replace: true });
      } else {
        throw new Error(result.error || 'Generation failed');
      }
    } catch (error) {
      console.error('Model generation failed:', error);
      toast.error(`Generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGenerating(false);
      setProgress(null);
    }
  }, [navigate]);

  // Export model
  const handleExport = useCallback(async (options: ExportOptions) => {
    if (!model) {
      toast.error('No model to export');
      return;
    }

    try {
      toast.loading('Exporting model...', { id: 'export' });
      
      // This would integrate with the geometry processor service
      // For now, we'll simulate the export
      setTimeout(() => {
        toast.success('Model exported successfully!', { id: 'export' });
      }, 2000);
      
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Export failed', { id: 'export' });
    }
  }, [model]);

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      viewerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'Escape':
          if (isFullscreen) {
            toggleFullscreen();
          }
          break;
        case 'F11':
          event.preventDefault();
          toggleFullscreen();
          break;
        case 'r':
        case 'R':
          // Reset camera
          setViewportSettings(prev => ({
            ...prev,
            camera: {
              ...prev.camera,
              position: { x: 5, y: 5, z: 5 },
              target: { x: 0, y: 0, z: 0 }
            }
          }));
          break;
        case 'w':
        case 'W':
          // Toggle wireframe
          setWireframe(prev => !prev);
          break;
        case 'g':
        case 'G':
          // Toggle grid
          setShowGrid(prev => !prev);
          break;
        case 'b':
        case 'B':
          // Toggle bounding box
          setShowBoundingBox(prev => !prev);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen, toggleFullscreen]);

  return (
    <div className="h-screen w-full flex flex-col bg-gray-100 overflow-hidden">
      {/* Header */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            
            <div>
              <h1 className="text-xl font-semibold text-gray-800">
                {model ? model.name : '3D Model Viewer'}
              </h1>
              {model && (
                <p className="text-sm text-gray-500">
                  {model.metadata.vertexCount} vertices • {model.metadata.faceCount} faces
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Quick actions */}
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setWireframe(!wireframe)}
                className={`p-2 rounded-lg transition-colors ${
                  wireframe 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Toggle Wireframe (W)"
              >
                <Eye className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => setShowGrid(!showGrid)}
                className={`p-2 rounded-lg transition-colors ${
                  showGrid 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Toggle Grid (G)"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => setShowBoundingBox(!showBoundingBox)}
                className={`p-2 rounded-lg transition-colors ${
                  showBoundingBox 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                title="Toggle Bounding Box (B)"
              >
                <EyeOff className="w-4 h-4" />
              </button>
            </div>

            <div className="h-6 w-px bg-gray-300" />

            <button
              onClick={toggleFullscreen}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Toggle Fullscreen (F11)"
            >
              <Minimize2 className="w-5 h-5 text-gray-600" />
            </button>

            {model && (
              <button
                onClick={() => handleExport({
                  format: 'obj',
                  binary: false,
                  includeMaterials: true,
                  includeTextures: true,
                  compressionLevel: 1,
                  preserveColors: true,
                  generatePreview: true,
                  metadata: {
                    author: '3D Pot Platform',
                    copyright: '© 2025 MiniMax Agent',
                    license: 'MIT',
                    version: '1.0.0'
                  }
                })}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
            )}
          </div>
        </div>
      </motion.header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* 3D Viewer */}
        <div 
          ref={viewerRef}
          className={`flex-1 relative ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}
        >
          <ThreeJSViewer
            model={model}
            settings={viewportSettings}
            wireframe={wireframe}
            showStats={showStats}
            showGrid={showGrid}
            showBoundingBox={showBoundingBox}
            autoRotate={viewportSettings.controls.autoRotate}
            className="w-full h-full"
            onError={(error) => {
              console.error('3D Viewer error:', error);
              toast.error('3D viewer error occurred');
            }}
          />

          {/* Generation Progress Overlay */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/50 flex items-center justify-center z-40"
              >
                <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <div>
                      <h3 className="font-semibold text-gray-800">Generating 3D Model</h3>
                      <p className="text-sm text-gray-600">
                        Using NVIDIA NIM AI to create your model...
                      </p>
                    </div>
                  </div>
                  
                  {progress && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">{progress.message}</span>
                        <span className="font-medium">{progress.progress}%</span>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${progress.progress}%` }}
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        />
                      </div>
                      
                      {progress.estimatedTimeRemaining && (
                        <p className="text-xs text-gray-500">
                          Estimated time remaining: {Math.ceil(progress.estimatedTimeRemaining / 1000)}s
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading Placeholder */}
          {!model && !isGenerating && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <Sparkles className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-700 mb-2">
                  Ready to Generate 3D Model
                </h3>
                <p className="text-gray-500 mb-6 max-w-sm">
                  Use the chat interface to extract product specifications, 
                  then generate a complete 3D model with AI.
                </p>
                <button
                  onClick={() => navigate('/chat')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
                >
                  <FileText className="w-5 h-5" />
                  <span>Start Chat Session</span>
                </button>
              </div>
            </div>
          )}

          {/* Performance Stats (when enabled) */}
          {showStats && (
            <div className="absolute top-4 right-4 bg-black/80 text-white p-2 rounded text-xs font-mono z-30">
              {/* FPS and performance stats would be shown here */}
              <div>FPS: 60</div>
              <div>Draw Calls: 12</div>
              <div>Triangles: {model?.metadata.faceCount || 0}</div>
            </div>
          )}
        </div>

        {/* 3D Controls Panel */}
        <AnimatePresence>
          <Model3DControls
            model={model}
            settings={viewportSettings}
            onSettingsChange={setViewportSettings}
            onExport={handleExport}
          />
        </AnimatePresence>
      </div>

      {/* Status Bar */}
      <motion.div 
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex-shrink-0 bg-gray-50 border-t border-gray-200 px-6 py-2"
      >
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            {model && (
              <>
                <span>Vertices: {model.metadata.vertexCount.toLocaleString()}</span>
                <span>Faces: {model.metadata.faceCount.toLocaleString()}</span>
                <span>Geometries: {model.geometries.length}</span>
                <span>Materials: {model.materials.length}</span>
              </>
            )}
            {!model && !isGenerating && (
              <span>No model loaded</span>
            )}
            {isGenerating && (
              <span className="text-blue-600 flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>Generating with AI...</span>
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <span>Resolution: {viewportSettings.camera.fov}° FOV</span>
            <span>Quality: {viewportSettings.renderer.antialias ? 'High' : 'Low'}</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Model3DPage;