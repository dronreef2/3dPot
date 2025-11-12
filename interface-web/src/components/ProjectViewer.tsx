import { useState, useRef, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Environment, Grid, Text, Box, Sphere } from '@react-three/drei'
import { motion } from 'framer-motion'
import {
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
  ArrowPathIcon,
  EyeIcon,
  CommandLineIcon,
  CubeIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline'

// 3D Model Component
function ModelViewer({ project }: { project: any }) {
  const [selectedPart, setSelectedPart] = useState<string | null>(null)
  const [modelData, setModelData] = useState<any>(null)

  // Sample 3D model data based on project
  useEffect(() => {
    // In a real app, this would load from the project data
    const mockModelData = {
      parts: [
        {
          id: 'base',
          name: 'Base',
          position: [0, 0, 0],
          size: [2, 0.1, 2],
          color: '#8B5CF6',
          type: 'box'
        },
        {
          id: 'support',
          name: 'Suporte',
          position: [0, 1, 0],
          size: [0.1, 2, 0.1],
          color: '#F59E0B',
          type: 'box'
        },
        {
          id: 'sensor',
          name: 'Sensor',
          position: [0.5, 1.5, 0],
          size: [0.2, 0.2, 0.2],
          color: '#EF4444',
          type: 'sphere'
        }
      ]
    }
    setModelData(mockModelData)
  }, [project])

  const handlePartClick = (partId: string) => {
    setSelectedPart(selectedPart === partId ? null : partId)
  }

  if (!modelData) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando modelo 3D...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <PerspectiveCamera makeDefault position={[5, 5, 5]} />
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={2}
        maxDistance={20}
      />
      
      {/* Environment and Lighting */}
      <Environment preset="studio" />
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <directionalLight position={[-10, -10, -5]} intensity={0.5} />
      
      {/* Ground Grid */}
      <Grid
        args={[20, 20]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#6366f1"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#6366f1"
        fadeDistance={30}
        fadeStrength={1}
      />
      
      {/* 3D Model Parts */}
      {modelData.parts.map((part: any) => (
        <group key={part.id}>
          {part.type === 'box' ? (
            <Box
              position={part.position}
              args={part.size}
              onClick={() => handlePartClick(part.id)}
            >
              <meshStandardMaterial 
                color={selectedPart === part.id ? '#FFFFFF' : part.color}
                emissive={selectedPart === part.id ? part.color : '#000000'}
                emissiveIntensity={selectedPart === part.id ? 0.3 : 0}
              />
            </Box>
          ) : (
            <Sphere
              position={part.position}
              args={part.size.map(size => size / 2)}
              onClick={() => handlePartClick(part.id)}
            >
              <meshStandardMaterial 
                color={selectedPart === part.id ? '#FFFFFF' : part.color}
                emissive={selectedPart === part.id ? part.color : '#000000'}
                emissiveIntensity={selectedPart === part.id ? 0.3 : 0}
              />
            </Sphere>
          )}
          
          {/* Part Label */}
          {selectedPart === part.id && (
            <Text
              position={[part.position[0], part.position[1] + 0.5, part.position[2]]}
              fontSize={0.2}
              color="#FFFFFF"
              anchorX="center"
              anchorY="middle"
            >
              {part.name}
            </Text>
          )}
        </group>
      ))}
      
      {/* Project Title */}
      <Text
        position={[0, 3, 0]}
        fontSize={0.5}
        color="#6366F1"
        anchorX="center"
        anchorY="middle"
      >
        {project.name}
      </Text>
    </>
  )
}

// Viewer Controls Component
function ViewerControls({ onReset, onToggleWireframe }: { 
  onReset: () => void
  onToggleWireframe: () => void 
}) {
  return (
    <div className="absolute top-4 right-4 flex flex-col space-y-2">
      <button
        onClick={onReset}
        className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        title="Resetar visualização"
      >
        <ArrowPathIcon className="w-5 h-5 text-gray-700 dark:text-gray-300" />
      </button>
      <button
        onClick={onToggleWireframe}
        className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        title="Alternar wireframe"
      >
        <CubeIcon className="w-5 h-5 text-gray-700 dark:text-gray-300" />
      </button>
    </div>
  )
}

// Properties Panel Component
function PropertiesPanel({ selectedPart, onClose }: { 
  selectedPart: any
  onClose: () => void 
}) {
  if (!selectedPart) return null

  return (
    <motion.div
      initial={{ x: 300 }}
      animate={{ x: 0 }}
      className="w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Propriedades da Peça
        </h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          ×
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nome
          </label>
          <p className="text-sm text-gray-900 dark:text-white">{selectedPart.name}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo
          </label>
          <p className="text-sm text-gray-900 dark:text-white capitalize">{selectedPart.type}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Posição
          </label>
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <div>X: {selectedPart.position[0].toFixed(2)}</div>
            <div>Y: {selectedPart.position[1].toFixed(2)}</div>
            <div>Z: {selectedPart.position[2].toFixed(2)}</div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Dimensões
          </label>
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <div>Comprimento: {selectedPart.size[0].toFixed(2)}</div>
            <div>Largura: {selectedPart.size[1].toFixed(2)}</div>
            <div>Altura: {selectedPart.size[2].toFixed(2)}</div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Cor
          </label>
          <div className="flex items-center space-x-2">
            <div 
              className="w-6 h-6 rounded border border-gray-300"
              style={{ backgroundColor: selectedPart.color }}
            />
            <span className="text-sm text-gray-900 dark:text-white">{selectedPart.color}</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Volume
          </label>
          <p className="text-sm text-gray-900 dark:text-white">
            {((selectedPart.size[0] * selectedPart.size[1] * selectedPart.size[2]) / 1000).toFixed(3)} cm³
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Material Estimado
          </label>
          <p className="text-sm text-gray-900 dark:text-white">
            {(selectedPart.size[0] * selectedPart.size[1] * selectedPart.size[2] * 1.24 / 1000).toFixed(3)}g PLA
          </p>
        </div>
      </div>
    </motion.div>
  )
}

interface ProjectViewerProps {
  project: any
  onClose: () => void
}

export function ProjectViewer({ project, onClose }: ProjectViewerProps) {
  const [selectedPart, setSelectedPart] = useState<any>(null)
  const [showWireframe, setShowWireframe] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const handleReset = () => {
    // Reset camera position (would need to access OrbitControls)
    console.log('Reset view')
  }

  const handleToggleWireframe = () => {
    setShowWireframe(!showWireframe)
    // Would need to update material props in 3D scene
  }

  const mockProjectDetails = {
    ...project,
    stats: {
      totalParts: 3,
      totalVolume: '4.125 cm³',
      totalWeight: '5.12g',
      estimatedTime: '45 min',
      supportRequired: true
    }
  }

  return (
    <div className="fixed inset-0 bg-gray-900 z-50">
      <div className="absolute top-0 left-0 right-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Voltar
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                {project.name}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Visualizador 3D - {project.status === 'draft' ? 'Rascunho' : 'Concluído'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Project Stats */}
            <div className="hidden md:flex items-center space-x-6 text-sm">
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  {mockProjectDetails.stats.totalParts}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Peças</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  {mockProjectDetails.stats.totalVolume}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Volume</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  {mockProjectDetails.stats.totalWeight}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Peso</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-gray-900 dark:text-white">
                  {mockProjectDetails.stats.estimatedTime}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Tempo</div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                <MagnifyingGlassPlusIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                <MagnifyingGlassMinusIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                <AdjustmentsHorizontalIcon className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                <CommandLineIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 3D Canvas */}
      <div className="absolute inset-0 pt-20">
        <Canvas
          ref={canvasRef}
          camera={{ position: [5, 5, 5], fov: 75 }}
          style={{ background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)' }}
        >
          <ModelViewer project={mockProjectDetails} />
        </Canvas>

        {/* 3D Controls Overlay */}
        <ViewerControls
          onReset={handleReset}
          onToggleWireframe={handleToggleWireframe}
        />

        {/* Help Panel */}
        <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white p-3 rounded-lg text-sm max-w-xs">
          <h4 className="font-medium mb-2">Controles do Mouse:</h4>
          <ul className="space-y-1 text-xs">
            <li>• Clique e arraste para rotacionar</li>
            <li>• Scroll para zoom</li>
            <li>• Clique nas peças para selecionar</li>
            <li>• Clique duplo para centralizar</li>
          </ul>
        </div>
      </div>

      {/* Properties Panel */}
      {selectedPart && (
        <div className="absolute top-20 right-4 z-20">
          <PropertiesPanel
            selectedPart={selectedPart}
            onClose={() => setSelectedPart(null)}
          />
        </div>
      )}

      {/* Bottom Toolbar */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 px-4 py-2">
        <div className="flex items-center space-x-4">
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm">
            Iniciar Impressão
          </button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm">
            Exportar STL
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
            Simular Impressão
          </button>
        </div>
      </div>
    </div>
  )
}