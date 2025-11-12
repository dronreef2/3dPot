import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FolderIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  PauseIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  ClockIcon,
  UserIcon,
  TagIcon,
  CubeIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '@contexts/AuthContext'
import { ProjectViewer } from '@components/ProjectViewer'
import toast from 'react-hot-toast'

interface Project {
  id: string
  name: string
  description: string
  status: 'draft' | 'in_progress' | 'completed' | 'paused'
  priority: 'low' | 'medium' | 'high'
  createdBy: string
  createdAt: string
  updatedAt: string
  estimatedDuration: number // in minutes
  actualDuration?: number
  tags: string[]
  progress: number // 0-100
  devices: string[]
  materials: string[]
  thumbnail?: string
}

interface ProjectFormData {
  name: string
  description: string
  priority: 'low' | 'medium' | 'high'
  estimatedDuration: number
  tags: string[]
  devices: string[]
  materials: string[]
}

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Modelo Robótico Simples',
    description: 'Protótipo de peça para robô com funcionalidades básicas',
    status: 'in_progress',
    priority: 'high',
    createdBy: 'admin',
    createdAt: '2024-11-10T10:00:00Z',
    updatedAt: '2024-11-12T15:30:00Z',
    estimatedDuration: 120,
    actualDuration: 85,
    tags: ['robotica', 'prototipo', ' PLA'],
    progress: 65,
    devices: ['conveyor', 'filament'],
    materials: ['PLA', 'PETG']
  },
  {
    id: '2',
    name: 'Componente de Quadcopter',
    description: 'Suporte para câmera drone com ângulo ajustável',
    status: 'completed',
    priority: 'medium',
    createdBy: 'operator',
    createdAt: '2024-11-08T14:20:00Z',
    updatedAt: '2024-11-11T09:45:00Z',
    estimatedDuration: 90,
    actualDuration: 88,
    tags: ['drone', 'camera', 'aeromodelismo'],
    progress: 100,
    devices: ['qc'],
    materials: ['ABS']
  },
  {
    id: '3',
    name: 'Modelo Educacional',
    description: 'Peças didáticas para ensino de geometria',
    status: 'draft',
    priority: 'low',
    createdBy: 'viewer',
    createdAt: '2024-11-12T08:15:00Z',
    updatedAt: '2024-11-12T08:15:00Z',
    estimatedDuration: 60,
    tags: ['educacao', 'geometria', 'didatico'],
    progress: 0,
    devices: [],
    materials: ['PLA']
  }
]

export function Projects() {
  const { user, hasPermission } = useAuth()
  const [projects, setProjects] = useState<Project[]>(mockProjects)
  const [filteredProjects, setFilteredProjects] = useState<Project[]>(mockProjects)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [show3DViewer, setShow3DViewer] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  
  const canCreateProjects = hasPermission('projects:manage')

  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    priority: 'medium',
    estimatedDuration: 60,
    tags: [],
    devices: [],
    materials: []
  })

  // Filter projects based on search and filters
  useEffect(() => {
    let filtered = projects

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter)
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(project => project.priority === priorityFilter)
    }

    setFilteredProjects(filtered)
  }, [projects, searchTerm, statusFilter, priorityFilter])

  const handleCreateProject = async () => {
    if (!formData.name.trim()) {
      toast.error('Nome do projeto é obrigatório')
      return
    }

    setIsCreating(true)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      const newProject: Project = {
        id: Date.now().toString(),
        name: formData.name,
        description: formData.description,
        status: 'draft',
        priority: formData.priority,
        createdBy: user?.username || 'unknown',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        estimatedDuration: formData.estimatedDuration,
        tags: formData.tags,
        progress: 0,
        devices: formData.devices,
        materials: formData.materials
      }

      setProjects(prev => [newProject, ...prev])
      setShowCreateModal(false)
      setFormData({
        name: '',
        description: '',
        priority: 'medium',
        estimatedDuration: 60,
        tags: [],
        devices: [],
        materials: []
      })
      
      toast.success('Projeto criado com sucesso!')
    } catch (error) {
      toast.error('Erro ao criar projeto')
    } finally {
      setIsCreating(false)
    }
  }

  const handleDeleteProject = (projectId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este projeto?')) {
      setProjects(prev => prev.filter(p => p.id !== projectId))
      toast.success('Projeto excluído com sucesso!')
    }
  }

  const handleStatusChange = (projectId: string, newStatus: Project['status']) => {
    setProjects(prev => prev.map(project => 
      project.id === projectId 
        ? { ...project, status: newStatus, updatedAt: new Date().toISOString() }
        : project
    ))
    
    const statusMessages = {
      draft: 'Projeto pausado',
      in_progress: 'Projeto iniciado',
      completed: 'Projeto concluído',
      paused: 'Projeto pausado'
    }
    
    toast.success(statusMessages[newStatus])
  }

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
      case 'in_progress': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
      case 'completed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: Project['priority']) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}min`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}h ${remainingMinutes}min`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gerenciamento de Projetos 3D
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Visualize e gerencie seus projetos de impressão 3D
          </p>
        </div>
        
        {canCreateProjects && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 sm:mt-0 btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="w-5 h-5" />
            <span>Novo Projeto</span>
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar projetos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="all">Todos os Status</option>
            <option value="draft">Rascunho</option>
            <option value="in_progress">Em Andamento</option>
            <option value="completed">Concluído</option>
            <option value="paused">Pausado</option>
          </select>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="all">Todas as Prioridades</option>
            <option value="high">Alta</option>
            <option value="medium">Média</option>
            <option value="low">Baixa</option>
          </select>

          {/* Results Count */}
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            {filteredProjects.length} projeto(s) encontrado(s)
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredProjects.map((project) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              {/* Project Header */}
              <div className="p-6 pb-4">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                    {project.name}
                  </h3>
                  <div className="flex items-center space-x-1 ml-2">
                    {canCreateProjects && (
                      <>
                        <button
                          onClick={() => {
                            setSelectedProject(project)
                            setShowDetailsModal(true)
                          }}
                          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                          title="Ver detalhes"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteProject(project.id)}
                          className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                          title="Excluir"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </div>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {project.description}
                </p>

                {/* Status and Priority */}
                <div className="flex items-center space-x-2 mb-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                    {project.status === 'draft' ? 'Rascunho' :
                     project.status === 'in_progress' ? 'Em Andamento' :
                     project.status === 'completed' ? 'Concluído' : 'Pausado'}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(project.priority)}`}>
                    {project.priority === 'high' ? 'Alta' :
                     project.priority === 'medium' ? 'Média' : 'Baixa'}
                  </span>
                </div>

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 dark:text-gray-400">Progresso</span>
                    <span className="text-gray-900 dark:text-white font-medium">{project.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${project.progress}%` }}
                      transition={{ duration: 0.5 }}
                      className="bg-primary-600 h-2 rounded-full"
                    />
                  </div>
                </div>

                {/* Metadata */}
                <div className="space-y-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className="flex items-center">
                    <UserIcon className="w-4 h-4 mr-2" />
                    <span>{project.createdBy}</span>
                  </div>
                  <div className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-2" />
                    <span>Estimado: {formatDuration(project.estimatedDuration)}</span>
                    {project.actualDuration && (
                      <span className="ml-2">
                        • Real: {formatDuration(project.actualDuration)}
                      </span>
                    )}
                  </div>
                  {project.tags.length > 0 && (
                    <div className="flex items-center">
                      <TagIcon className="w-4 h-4 mr-2" />
                      <div className="flex flex-wrap gap-1">
                        {project.tags.slice(0, 2).map((tag, index) => (
                          <span
                            key={index}
                            className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {project.tags.length > 2 && (
                          <span className="text-xs">+{project.tags.length - 2}</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Project Actions */}
              {canCreateProjects && (
                <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      {project.status === 'draft' && (
                        <button
                          onClick={() => handleStatusChange(project.id, 'in_progress')}
                          className="flex items-center space-x-1 px-3 py-1 text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded hover:bg-green-200 dark:hover:bg-green-800"
                        >
                          <PlayIcon className="w-3 h-3" />
                          <span>Iniciar</span>
                        </button>
                      )}
                      {project.status === 'in_progress' && (
                        <button
                          onClick={() => handleStatusChange(project.id, 'completed')}
                          className="flex items-center space-x-1 px-3 py-1 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                        >
                          <span>Finalizar</span>
                        </button>
                      )}
                      {(project.status === 'draft' || project.status === 'in_progress') && (
                        <button
                          onClick={() => handleStatusChange(project.id, 'paused')}
                          className="flex items-center space-x-1 px-3 py-1 text-xs bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300 rounded hover:bg-yellow-200 dark:hover:bg-yellow-800"
                        >
                          <PauseIcon className="w-3 h-3" />
                          <span>Pausar</span>
                        </button>
                      )}
                    </div>

                    <div className="flex space-x-1">
                      <button
                        onClick={() => {
                          setSelectedProject(project)
                          setShow3DViewer(true)
                        }}
                        className="p-1 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"
                        title="Visualizar em 3D"
                      >
                        <CubeIcon className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        title="Download"
                      >
                        <ArrowDownTrayIcon className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        title="Compartilhar"
                      >
                        <ShareIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {filteredProjects.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            Nenhum projeto encontrado
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {searchTerm || statusFilter !== 'all' || priorityFilter !== 'all'
              ? 'Tente ajustar os filtros de busca.'
              : 'Comece criando seu primeiro projeto 3D.'}
          </p>
          {!canCreateProjects && (
            <p className="mt-2 text-xs text-yellow-600 dark:text-yellow-400">
              Você não tem permissão para criar novos projetos.
            </p>
          )}
        </motion.div>
      )}

      {/* Create Project Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Criar Novo Projeto
                </h2>
              </div>

              <div className="p-6 space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nome do Projeto *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="Ex: Prototipo Robótico V1"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Descrição
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="Descreva o projeto..."
                  />
                </div>

                {/* Priority and Duration */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Prioridade
                    </label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as any }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="low">Baixa</option>
                      <option value="medium">Média</option>
                      <option value="high">Alta</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Duração Estimada (minutos)
                    </label>
                    <input
                      type="number"
                      value={formData.estimatedDuration}
                      onChange={(e) => setFormData(prev => ({ ...prev, estimatedDuration: parseInt(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      min="1"
                    />
                  </div>
                </div>

                {/* Devices and Materials */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Dispositivos
                    </label>
                    <select
                      multiple
                      value={formData.devices}
                      onChange={(e) => setFormData(prev => ({ ...prev, devices: Array.from(e.target.selectedOptions, option => option.value) }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      size={3}
                    >
                      <option value="filament">Monitor de Filamento</option>
                      <option value="conveyor">Esteira Arduino</option>
                      <option value="qc">Estação QC</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Materiais
                    </label>
                    <select
                      multiple
                      value={formData.materials}
                      onChange={(e) => setFormData(prev => ({ ...prev, materials: Array.from(e.target.selectedOptions, option => option.value) }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      size={3}
                    >
                      <option value="PLA">PLA</option>
                      <option value="PETG">PETG</option>
                      <option value="ABS">ABS</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  disabled={isCreating}
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateProject}
                  disabled={isCreating || !formData.name.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isCreating ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Criando...
                    </div>
                  ) : (
                    'Criar Projeto'
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3D Viewer Modal */}
      <AnimatePresence>
        {show3DViewer && selectedProject && (
          <ProjectViewer
            project={selectedProject}
            onClose={() => {
              setShow3DViewer(false)
              setSelectedProject(null)
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}