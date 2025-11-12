// 3D Model Controls Component
import React, { useState, useCallback } from 'react';
import { 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Move3D, 
  Eye, 
  EyeOff,
  Download,
  Settings,
  Grid3X3,
  Sun,
  Moon,
  RotateCw,
  MoveHorizontal,
  Maximize2,
  Minimize2,
  Layers,
  FileDown,
  RefreshCw,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ViewportSettings, ExportOptions, Model3D } from '../types/model3d';
import { model3DService } from '../services/model3d';
import toast from 'react-hot-toast';

interface Model3DControlsProps {
  model: Model3D | null;
  settings: ViewportSettings;
  onSettingsChange: (settings: ViewportSettings) => void;
  onExport?: (options: ExportOptions) => void;
  className?: string;
}

export const Model3DControls: React.FC<Model3DControlsProps> = ({
  model,
  settings,
  onSettingsChange,
  onExport,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState<'view' | 'export' | 'settings'>('view');
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
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
  });

  // Camera controls
  const resetCamera = useCallback(() => {
    const newSettings = {
      ...settings,
      camera: {
        ...settings.camera,
        position: { x: 5, y: 5, z: 5 },
        target: { x: 0, y: 0, z: 0 }
      }
    };
    onSettingsChange(newSettings);
    toast.success('Camera reset to default position');
  }, [settings, onSettingsChange]);

  const zoomIn = useCallback(() => {
    const currentPos = settings.camera.position;
    const newSettings = {
      ...settings,
      camera: {
        ...settings.camera,
        position: {
          x: currentPos.x * 0.8,
          y: currentPos.y * 0.8,
          z: currentPos.z * 0.8
        }
      }
    };
    onSettingsChange(newSettings);
  }, [settings, onSettingsChange]);

  const zoomOut = useCallback(() => {
    const currentPos = settings.camera.position;
    const newSettings = {
      ...settings,
      camera: {
        ...settings.camera,
        position: {
          x: currentPos.x * 1.25,
          y: currentPos.y * 1.25,
          z: currentPos.z * 1.25
        }
      }
    };
    onSettingsChange(newSettings);
  }, [settings, onSettingsChange]);

  // View controls
  const toggleWireframe = useCallback(() => {
    // This would need to be passed as a prop to ThreeJSViewer
    toast.info('Wireframe mode will be available in the viewer');
  }, []);

  const toggleBoundingBox = useCallback(() => {
    // This would need to be passed as a prop to ThreeJSViewer
    toast.info('Bounding box display will be available in the viewer');
  }, []);

  const toggleAutoRotate = useCallback(() => {
    const newSettings = {
      ...settings,
      controls: {
        ...settings.controls,
        autoRotate: !settings.controls.autoRotate
      }
    };
    onSettingsChange(newSettings);
    toast.success(`Auto-rotate ${!settings.controls.autoRotate ? 'enabled' : 'disabled'}`);
  }, [settings, onSettingsChange]);

  const toggleGrid = useCallback(() => {
    // This would need to be passed as a prop to ThreeJSViewer
    toast.info('Grid toggle will be available in the viewer');
  }, []);

  // Lighting controls
  const changeLighting = useCallback((lighting: ViewportSettings['environment']['lighting']) => {
    const newSettings = {
      ...settings,
      environment: {
        ...settings.environment,
        lighting
      }
    };
    onSettingsChange(newSettings);
    toast.success(`Lighting changed to ${lighting}`);
  }, [settings, onSettingsChange]);

  // Environment controls
  const changeBackground = useCallback((background: ViewportSettings['environment']['background']) => {
    const newSettings = {
      ...settings,
      environment: {
        ...settings.environment,
        background,
        backgroundColor: background === 'color' ? '#f0f0f0' : undefined
      }
    };
    onSettingsChange(newSettings);
    toast.success(`Background changed to ${background}`);
  }, [settings, onSettingsChange]);

  // Export functions
  const handleExport = useCallback(async () => {
    if (!model) {
      toast.error('No model to export');
      return;
    }

    try {
      toast.loading('Exporting model...', { id: 'export' });
      
      // This would trigger the actual export
      if (onExport) {
        await onExport(exportOptions);
        toast.success('Model exported successfully!', { id: 'export' });
      } else {
        toast.info('Export functionality will be implemented', { id: 'export' });
      }
    } catch (error) {
      toast.error('Export failed', { id: 'export' });
    }
  }, [model, exportOptions, onExport]);

  // Preset views
  const setViewPreset = useCallback((preset: 'front' | 'back' | 'left' | 'right' | 'top' | 'bottom' | 'isometric') => {
    const positions = {
      front: { x: 0, y: 0, z: 10 },
      back: { x: 0, y: 0, z: -10 },
      left: { x: -10, y: 0, z: 0 },
      right: { x: 10, y: 0, z: 0 },
      top: { x: 0, y: 10, z: 0 },
      bottom: { x: 0, y: -10, z: 0 },
      isometric: { x: 8, y: 8, z: 8 }
    };

    const position = positions[preset];
    const newSettings = {
      ...settings,
      camera: {
        ...settings.camera,
        position
      }
    };
    
    onSettingsChange(newSettings);
    toast.success(`View set to ${preset}`);
  }, [settings, onSettingsChange]);

  if (!isExpanded) {
    return (
      <motion.div
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className={`fixed left-4 top-1/2 -translate-y-1/2 z-50 ${className}`}
      >
        <button
          onClick={() => setIsExpanded(true)}
          className="p-3 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg border hover:bg-white transition-colors"
        >
          <Settings className="w-5 h-5 text-gray-700" />
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -300, opacity: 0 }}
      className={`fixed left-4 top-1/2 -translate-y-1/2 w-80 z-50 ${className}`}
    >
      <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-xl border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <h3 className="font-semibold">3D Controls</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(false)}
              className="p-1 hover:bg-white/20 rounded"
            >
              <Minimize2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          {[
            { id: 'view', label: 'View', icon: Eye },
            { id: 'export', label: 'Export', icon: Download },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 p-3 text-sm font-medium transition-colors ${
                activeTab === id
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-4 max-h-96 overflow-y-auto">
          <AnimatePresence mode="wait">
            {/* View Controls */}
            {activeTab === 'view' && (
              <motion.div
                key="view"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="space-y-4"
              >
                {/* Camera Controls */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Camera</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={resetCamera}
                      className="flex items-center justify-center space-x-1 p-2 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>Reset</span>
                    </button>
                    <button
                      onClick={zoomIn}
                      className="flex items-center justify-center space-x-1 p-2 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <ZoomIn className="w-3 h-3" />
                      <span>Zoom In</span>
                    </button>
                    <button
                      onClick={zoomOut}
                      className="flex items-center justify-center space-x-1 p-2 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <ZoomOut className="w-3 h-3" />
                      <span>Zoom Out</span>
                    </button>
                    <button
                      onClick={toggleAutoRotate}
                      className={`flex items-center justify-center space-x-1 p-2 text-xs rounded transition-colors ${
                        settings.controls.autoRotate
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 hover:bg-gray-200'
                      }`}
                    >
                      <RotateCw className="w-3 h-3" />
                      <span>Auto</span>
                    </button>
                  </div>
                </div>

                {/* Preset Views */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Views</h4>
                  <div className="grid grid-cols-3 gap-1">
                    {[
                      { id: 'front', label: 'Front' },
                      { id: 'back', label: 'Back' },
                      { id: 'left', label: 'Left' },
                      { id: 'right', label: 'Right' },
                      { id: 'top', label: 'Top' },
                      { id: 'bottom', label: 'Bottom' },
                      { id: 'isometric', label: 'Iso', full: true }
                    ].map(({ id, label, full }) => (
                      <button
                        key={id}
                        onClick={() => setViewPreset(id as any)}
                        className={`p-2 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors ${
                          full ? 'col-span-3' : ''
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Display Options */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Display</h4>
                  <div className="space-y-2">
                    <button
                      onClick={toggleWireframe}
                      className="w-full flex items-center justify-between p-2 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <span>Wireframe</span>
                      <ToggleLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={toggleBoundingBox}
                      className="w-full flex items-center justify-between p-2 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <span>Bounding Box</span>
                      <ToggleLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={toggleGrid}
                      className="w-full flex items-center justify-between p-2 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    >
                      <span>Grid</span>
                      <Grid3X3 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Lighting */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Lighting</h4>
                  <div className="grid grid-cols-2 gap-1">
                    {[
                      { id: 'basic', label: 'Basic', icon: Sun },
                      { id: 'studio', label: 'Studio', icon: Sun },
                      { id: 'outdoor', label: 'Outdoor', icon: Sun },
                      { id: 'custom', label: 'Custom', icon: Settings }
                    ].map(({ id, label, icon: Icon }) => (
                      <button
                        key={id}
                        onClick={() => changeLighting(id as any)}
                        className={`flex items-center justify-center space-x-1 p-2 text-xs rounded transition-colors ${
                          settings.environment.lighting === id
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 hover:bg-gray-200'
                        }`}
                      >
                        <Icon className="w-3 h-3" />
                        <span>{label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Export Controls */}
            {activeTab === 'export' && (
              <motion.div
                key="export"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="space-y-4"
              >
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Format</h4>
                  <select
                    value={exportOptions.format}
                    onChange={(e) => setExportOptions({ ...exportOptions, format: e.target.value as any })}
                    className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="obj">OBJ</option>
                    <option value="stl">STL</option>
                    <option value="gltf">GLTF</option>
                    <option value="objmtl">OBJ+MTL</option>
                    <option value="ply">PLY</option>
                  </select>
                </div>

                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Options</h4>
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={exportOptions.binary}
                        onChange={(e) => setExportOptions({ ...exportOptions, binary: e.target.checked })}
                        className="rounded"
                      />
                      <span className="text-sm">Binary format</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={exportOptions.includeMaterials}
                        onChange={(e) => setExportOptions({ ...exportOptions, includeMaterials: e.target.checked })}
                        className="rounded"
                      />
                      <span className="text-sm">Include materials</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={exportOptions.includeTextures}
                        onChange={(e) => setExportOptions({ ...exportOptions, includeTextures: e.target.checked })}
                        className="rounded"
                      />
                      <span className="text-sm">Include textures</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={exportOptions.preserveColors}
                        onChange={(e) => setExportOptions({ ...exportOptions, preserveColors: e.target.checked })}
                        className="rounded"
                      />
                      <span className="text-sm">Preserve colors</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Compression</h4>
                  <select
                    value={exportOptions.compressionLevel}
                    onChange={(e) => setExportOptions({ ...exportOptions, compressionLevel: Number(e.target.value) as any })}
                    className="w-full p-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value={0}>None</option>
                    <option value={1}>Basic</option>
                    <option value={2}>Medium</option>
                    <option value={3}>High</option>
                  </select>
                </div>

                <button
                  onClick={handleExport}
                  disabled={!model}
                  className="w-full flex items-center justify-center space-x-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Export Model</span>
                </button>

                {!model && (
                  <p className="text-sm text-gray-500 text-center">
                    Load a model to enable export
                  </p>
                )}
              </motion.div>
            )}

            {/* Settings */}
            {activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="space-y-4"
              >
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Background</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: 'color', label: 'Color' },
                      { id: 'gradient', label: 'Gradient' },
                      { id: 'hdri', label: 'HDRI' },
                      { id: 'transparent', label: 'Transparent' }
                    ].map(({ id, label }) => (
                      <button
                        key={id}
                        onClick={() => changeBackground(id as any)}
                        className={`p-2 text-xs rounded transition-colors ${
                          settings.environment.background === id
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 hover:bg-gray-200'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Renderer</h4>
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.renderer.antialias}
                        onChange={(e) => onSettingsChange({
                          ...settings,
                          renderer: { ...settings.renderer, antialias: e.target.checked }
                        })}
                        className="rounded"
                      />
                      <span className="text-sm">Antialiasing</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.renderer.shadows}
                        onChange={(e) => onSettingsChange({
                          ...settings,
                          renderer: { ...settings.renderer, shadows: e.target.checked }
                        })}
                        className="rounded"
                      />
                      <span className="text-sm">Shadows</span>
                    </label>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Performance</h4>
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.controls.enableZoom}
                        onChange={(e) => onSettingsChange({
                          ...settings,
                          controls: { ...settings.controls, enableZoom: e.target.checked }
                        })}
                        className="rounded"
                      />
                      <span className="text-sm">Enable zoom</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.controls.enablePan}
                        onChange={(e) => onSettingsChange({
                          ...settings,
                          controls: { ...settings.controls, enablePan: e.target.checked }
                        })}
                        className="rounded"
                      />
                      <span className="text-sm">Enable pan</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={settings.controls.enableRotate}
                        onChange={(e) => onSettingsChange({
                          ...settings,
                          controls: { ...settings.controls, enableRotate: e.target.checked }
                        })}
                        className="rounded"
                      />
                      <span className="text-sm">Enable rotate</span>
                    </label>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Model Info */}
        {model && (
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <div className="text-sm">
              <div className="font-medium text-gray-800 mb-1">{model.name}</div>
              <div className="text-gray-600">
                {model.metadata.vertexCount} vertices • {model.metadata.faceCount} faces
              </div>
              <div className="text-gray-500 text-xs mt-1">
                {model.geometries.length} geometries • {model.materials.length} materials
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default Model3DControls;