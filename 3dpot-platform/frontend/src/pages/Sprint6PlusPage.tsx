// Sprint 6+ Main Page
// Página principal integrada para todas as funcionalidades Sprint 6+

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Printer,
  Users,
  ShoppingCart,
  Cloud,
  Smartphone,
  Cube,
  Zap,
  Shield,
  Clock,
  TrendingUp,
  Download,
  Eye,
  Star,
  Settings,
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Play,
  Pause,
  Volume2,
  Video,
  Monitor,
  FileText,
  BarChart3,
  DollarSign,
  Package,
  Globe,
  Wifi,
  WifiOff,
  CheckCircle,
  AlertTriangle,
  X,
  ExternalLink,
  Camera,
  Mic,
  MicOff,
  VideoOff,
  Users2,
  MessageSquare,
  ThumbsUp,
  Share2,
  Bookmark,
  Heart,
  Eye as ViewIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Filter as FilterIcon,
  CloudUpload,
  HardDrive,
  Cpu,
  Zap as ZapIcon,
  Activity,
  TrendingUp as TrendingUpIcon,
  DollarSign as DollarIcon
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

// Services
import { print3DService } from '@/services/print3dService';
import { collaborationService } from '@/services/collaborationService';
import { cloudRenderingService } from '@/services/cloudRenderingService';
import { marketplaceService } from '@/services/marketplaceService';

// Types
import type { PrintJob, CollaborativeSession, RenderJob, ModelListing } from '@/types/printing3d';

const Sprint6PlusPage: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [printJobs, setPrintJobs] = useState<PrintJob[]>([]);
  const [collaborativeSessions, setCollaborativeSessions] = useState<CollaborativeSession[]>([]);
  const [renderJobs, setRenderJobs] = useState<RenderJob[]>([]);
  const [marketplaceListings, setMarketplaceListings] = useState<ModelListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [notifications, setNotifications] = useState<any[]>([]);

  // Service status states
  const [servicesStatus, setServicesStatus] = useState({
    printing3D: { connected: false, jobs: 0 },
    collaboration: { connected: false, sessions: 0, activeUsers: 0 },
    cloudRendering: { connected: false, jobs: 0, queuePosition: 0 },
    marketplace: { connected: false, listings: 0, transactions: 0 }
  });

  useEffect(() => {
    initializeServices();
    loadInitialData();
  }, []);

  const initializeServices = async () => {
    try {
      setLoading(true);

      // Initialize services
      print3DService.on('job_updated', handleJobUpdate);
      print3DService.on('status_changed', handleStatusChange);
      
      collaborationService.on('session_joined', handleSessionJoined);
      collaborationService.on('user_joined', handleUserJoined);
      collaborationService.on('collaboration_event', handleCollaborationEvent);
      
      cloudRenderingService.on('job_updated', handleRenderJobUpdate);
      cloudRenderingService.on('result_ready', handleResultReady);
      cloudRenderingService.on('progress_updated', handleProgressUpdate);
      
      marketplaceService.on('listing_created', handleListingCreated);
      marketplaceService.on('model_purchased', handleModelPurchased);
      marketplaceService.on('file_uploaded', handleFileUploaded);

      // Check service connections
      updateServicesStatus();
      
    } catch (error) {
      console.error('Failed to initialize services:', error);
      addNotification('Failed to initialize services', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadInitialData = async () => {
    try {
      // Load data from services
      const printQueue = print3DService.getQueueJobs();
      const renderQueue = cloudRenderingService.getActiveJobs();
      const userListings = await marketplaceService.getUserListings();
      
      setPrintJobs(printQueue);
      setRenderJobs(renderQueue);
      setMarketplaceListings(userListings);
      
    } catch (error) {
      console.error('Failed to load initial data:', error);
      addNotification('Failed to load data', 'error');
    }
  };

  // Event handlers
  const handleJobUpdate = (job: PrintJob) => {
    setPrintJobs(prev => {
      const index = prev.findIndex(j => j.id === job.id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = job;
        return updated;
      }
      return [...prev, job];
    });
    addNotification(`Print job ${job.modelName} status: ${job.status}`, 'info');
  };

  const handleSessionJoined = (session: CollaborativeSession) => {
    setCollaborativeSessions(prev => [...prev, session]);
    addNotification(`Joined collaboration session: ${session.modelName}`, 'success');
  };

  const handleUserJoined = (user: any) => {
    addNotification(`${user.username} joined the session`, 'info');
  };

  const handleRenderJobUpdate = (job: RenderJob) => {
    setRenderJobs(prev => {
      const index = prev.findIndex(j => j.id === job.id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = job;
        return updated;
      }
      return [...prev, job];
    });
  };

  const handleResultReady = (result: any) => {
    addNotification('Render completed and ready for download!', 'success');
  };

  const handleStatusChange = ({ jobId, status }: any) => {
    addNotification(`Status changed: ${status}`, 'info');
  };

  const handleListingCreated = (listing: any) => {
    setMarketplaceListings(prev => [...prev, listing]);
    addNotification(`New model listed: ${listing.title}`, 'success');
  };

  const handleModelPurchased = (purchase: any) => {
    addNotification('Model purchased successfully!', 'success');
  };

  const handleFileUploaded = (file: any) => {
    addNotification(`File uploaded: ${file.fileName}`, 'success');
  };

  const handleCollaborationEvent = (event: any) => {
    // Handle real-time collaboration events
    console.log('Collaboration event:', event);
  };

  const handleProgressUpdate = (progress: any) => {
    // Handle render progress updates
    console.log('Render progress:', progress);
  };

  const updateServicesStatus = () => {
    setServicesStatus({
      printing3D: {
        connected: true,
        jobs: print3DService.getQueueJobs().length
      },
      collaboration: {
        connected: collaborationService.isConnected(),
        sessions: collaborativeSessions.length,
        activeUsers: collaborationService.getParticipants().length
      },
      cloudRendering: {
        connected: cloudRenderingService.isConnected(),
        jobs: cloudRenderingService.getActiveJobCount(),
        queuePosition: 0
      },
      marketplace: {
        connected: true,
        listings: marketplaceListings.length,
        transactions: 0
      }
    });
  };

  const addNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };
    setNotifications(prev => [notification, ...prev].slice(0, 5));
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  // Service actions
  const createPrintJob = async () => {
    try {
      const jobId = await print3DService.submitJob({
        modelId: 'sample-model',
        modelName: 'Sample Model',
        settings: {
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
        },
        printer: {
          id: 'default-printer',
          name: 'Default Printer',
          type: 'fdm',
          manufacturer: 'Unknown',
          maxPrintVolume: { x: 200, y: 200, z: 200 },
          nozzleSizes: [0.4],
          supportedMaterials: ['PLA', 'ABS'],
          status: 'idle'
        },
        userId: 'current-user',
        filamentType: 'PLA',
        filamentColor: 'White',
        materialCost: 5.00,
        supportsGenerated: false,
        geometryAnalysis: {
          overhangAngles: [],
          thinWalls: [],
          bridgingDistance: 0,
          complexity: 'low',
          supportRequired: false,
          printabilityScore: 95,
          recommendedSettings: {},
          warnings: []
        }
      });
      
      addNotification(`Print job created with ID: ${jobId}`, 'success');
    } catch (error) {
      console.error('Failed to create print job:', error);
      addNotification('Failed to create print job', 'error');
    }
  };

  const createCollaborationSession = async () => {
    try {
      const sessionId = await collaborationService.createSession('sample-model', {
        id: 'current-user',
        username: 'Current User',
        displayName: 'Current User',
        email: 'user@example.com',
        avatar: '',
        bio: '',
        location: '',
        website: '',
        socialLinks: [],
        verification: { status: 'verified', level: 'email', badges: [], score: 100 },
        statistics: {
          models: 10,
          downloads: 100,
          followers: 50,
          following: 25,
          collections: 5,
          reviews: 20,
          revenue: 1000,
          rating: 4.8,
          reputation: 1000,
          experience: { current: 100, nextLevel: 1000, name: 'Expert', title: '3D Model Expert', benefits: [], requirements: [] },
          achievements: []
        },
        subscription: { plan: 'pro', status: 'active', currentPeriodEnd: new Date(), autoRenewal: true, features: [], paymentMethod: undefined },
        preferences: {
          privacy: { profileVisibility: 'public', showEmail: false, showLocation: false, showWebsite: false, allowMessages: true, allowDownloads: true },
          notifications: {
            email: { newModel: true, newReview: true, sale: true, message: true, marketing: false, security: true },
            push: { newModel: true, newReview: true, sale: true, message: true, collaboration: true },
            inApp: { newModel: true, newReview: true, sale: true, message: true, collaboration: true, system: true }
          },
          marketplace: { defaultCategory: 'general', autoPublish: false, requireApproval: true, allowBundles: true, allowCustomization: true, pricingPreference: 'recommended' },
          collaboration: { autoJoin: false, defaultRole: 'viewer', allowScreenShare: true, allowVoiceChat: true, allowVideoChat: true, maxParticipants: 10 }
        },
        createdAt: new Date(),
        lastActive: new Date(),
        banned: false,
        bannedUntil: undefined,
        banReason: undefined
      });
      
      addNotification(`Collaboration session created: ${sessionId}`, 'success');
    } catch (error) {
      console.error('Failed to create collaboration session:', error);
      addNotification('Failed to create collaboration session', 'error');
    }
  };

  const submitRenderJob = async () => {
    try {
      const jobId = await cloudRenderingService.submitJob('sample-model', {
        resolution: { width: 1920, height: 1080, aspectRatio: '16:9', dpi: 96, pixelRatio: 1 },
        format: 'png' as any,
        quality: {
          level: 'high' as any,
          samples: 64,
          maxRayDepth: 3,
          caustics: true,
          globalIllumination: true,
          ambientOcclusion: true,
          motionBlur: false,
          depthOfField: true,
          sss: false,
          causticsAccuracy: 'medium' as any,
          rayTracing: true,
          denoising: true,
          aiEnhancement: true
        },
        lighting: {
          type: 'environment' as any,
          hdri: { url: '', intensity: 1, rotation: { x: 0, y: 0, z: 0 }, blur: 0, custom: false },
          lights: [],
          environmentIntensity: 1,
          globalIllumination: true,
          shadows: { enabled: true, type: 'soft' as any, bias: 0.001, normalBias: 0.01, size: 2048, mapResolution: 1024, softness: 0, color: '#000000', opacity: 1 },
          reflections: { enabled: true, type: 'screen_space' as any, intensity: 1, resolution: 512, maxMips: 5, quality: 'medium' as any }
        },
        camera: {
          type: 'perspective' as any,
          position: { x: 5, y: 5, z: 5 },
          target: { x: 0, y: 0, z: 0 },
          up: { x: 0, y: 1, z: 0 },
          fov: 50,
          near: 0.1,
          far: 1000,
          exposure: { value: 0, compensation: 0, autoISO: false, maxISO: 3200, iso: 100 }
        },
        materials: {
          renderEngine: 'cycles' as any,
          colorSpace: 'srgb' as any,
          transparency: 'alpha' as any,
          refraction: true,
          caustics: true,
          subsurface: false,
          anisotropic: false,
          clearcoat: false,
          iridescence: false,
          sheen: false,
          transmission: false,
          transmissionRoughness: false,
          anisotropicRoughness: false,
          clearcoatRoughness: false,
          sheenRoughness: false,
          customShaders: []
        },
        postProcessing: {
          enabled: true,
          colorGrading: {
            enabled: true,
            temperature: 0,
            tint: 0,
            shadows: { red: 0, green: 0, blue: 0, saturation: 0, brightness: 0, contrast: 0, exposure: 0, gamma: 0 },
            midtones: { red: 0, green: 0, blue: 0, saturation: 0, brightness: 0, contrast: 0, exposure: 0, gamma: 0 },
            highlights: { red: 0, green: 0, blue: 0, saturation: 0, brightness: 0, contrast: 0, exposure: 0, gamma: 0 },
            curves: [],
            look: ''
          },
          toneMapping: {
            enabled: true,
            type: 'aces' as any,
            exposure: 1,
            whitePoint: 1,
            middleGrey: 0.18,
            custom: { shoulder: 0, midIn: 0, midOut: 0, highIn: 0, highOut: 0 }
          },
          bloom: {
            enabled: false,
            intensity: 0,
            threshold: 1,
            softKnee: 0.5,
            radius: 0,
            color: '#ffffff',
            lensDirt: false,
            lensDirtIntensity: 0
          },
          vignette: {
            enabled: false,
            intensity: 0,
            midPoint: 0.5,
            roundness: 1,
            feather: 0.4,
            color: '#000000'
          },
          chromaticAberration: {
            enabled: false,
            intensity: 0,
            distortion: 0,
            centerX: 0.5,
            centerY: 0.5
          },
          depthOfField: {
            enabled: false,
            focusDistance: 10,
            focusPoint: { x: 0, y: 0, z: 0 },
            aperture: 2.8,
            focalLength: 50,
            sensorSize: 36,
            bokehShape: 'circle' as any,
            bokehTexture: '',
            occlusion: false,
            distanceBlur: false,
            foregroundBlur: false,
            backgroundBlur: false
          },
          motionBlur: {
            enabled: false,
            intensity: 0,
            samples: 1,
            shutterAngle: 0,
            shutterSpeed: 0,
            imageBased: false,
            cameraMotion: false,
            objectMotion: false
          },
          grain: {
            enabled: false,
            intensity: 0,
            size: 1,
            color: '#000000',
            monochrome: false,
            animated: false,
            seed: 0
          },
          fxaa: true,
          ssr: false,
          ssgi: false,
          dithering: true
        },
        custom: {
          customShaders: [],
          nodeGraph: { nodes: [], connections: [], parameters: [] },
          globalSettings: {
            threadCount: 8,
            memoryLimit: 8192,
            cacheSize: 1024,
            progressiveRendering: true,
            tileSize: 32,
            seed: 0,
            statisticalEstimation: true,
            adaptiveSampling: true,
            clampSamples: true
          },
          performance: {
            optimizationLevel: 'medium' as any,
            adaptiveQuality: true,
            targetFPS: 30,
            maxTime: 3600,
            autoResolution: true,
            dynamicResolution: false,
            fallbackQuality: { level: 'medium' as any, samples: 16, maxRayDepth: 2, caustics: false, globalIllumination: false, ambientOcclusion: false, motionBlur: false, depthOfField: false, sss: false, causticsAccuracy: 'low' as any, rayTracing: false, denoising: true, aiEnhancement: false },
            progressivePreview: true
          },
          debugging: {
            showBoundingBoxes: false,
            showNormals: false,
            showWireframe: false,
            showUV: false,
            showStatistics: false,
            showPerformance: false,
            saveIntermediate: false,
            debugOutput: false
          }
        }
      });
      
      addNotification(`Render job submitted: ${jobId}`, 'success');
    } catch (error) {
      console.error('Failed to submit render job:', error);
      addNotification('Failed to submit render job', 'error');
    }
  };

  const createMarketplaceListing = async () => {
    try {
      const listing = await marketplaceService.createListing({
        title: 'Sample 3D Model',
        description: 'A sample 3D model for testing',
        shortDescription: 'Sample model',
        category: {
          id: 'general',
          name: 'General',
          slug: 'general',
          description: 'General models',
          icon: 'cube',
          color: '#3b82f6',
          sortOrder: 1,
          isActive: true,
          featured: false,
          subcategories: []
        },
        tags: ['sample', 'test', '3d'],
        model: {
          id: 'sample-model',
          name: 'Sample Model',
          description: 'Sample description',
          specifications: {},
          filePath: '',
          status: 'draft',
          createdAt: new Date(),
          updatedAt: new Date(),
          metadata: {}
        },
        pricing: {
          type: 'free' as any,
          price: 0,
          currency: 'USD',
          originalPrice: 0,
          discountPercentage: 0,
          subscription: undefined,
          bundle: undefined,
          paymentModel: 'one_time' as any,
          taxRate: 0,
          fees: { platform: 0, payment: 0, author: 0, taxes: 0, net: 0 }
        },
        media: {
          preview: '',
          thumbnails: [],
          screenshots: [],
          videos: [],
          heroImage: '',
          modelPreview: '',
          animatedGif: '',
          arPreview: '',
          vrPreview: ''
        },
        files: [],
        license: {
          type: 'cc0' as any,
          description: 'Public domain',
          terms: [],
          restrictions: [],
          attribution: '',
          commercialUse: true,
          modifications: true,
          distribution: true,
          creator: 'Unknown',
          copyright: '',
          lastModified: new Date()
        },
        statistics: {
          downloads: { total: 0, recent: 0, trend: 'stable' as any, byFormat: [], byCountry: [], averagePerDay: 0, peakDate: new Date() },
          ratings: { average: 0, count: 0, distribution: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }, trend: 'stable' as any, verifiedOnly: false },
          views: { total: 0, recent: 0, unique: 0, averageTime: 0, bounceRate: 0, traffic: { direct: 0, search: 0, social: 0, referral: 0, marketplace: 0 } },
          popularity: { score: 0, rank: 0, categoryRank: 0, trending: false, trendingScore: 0, ageDays: 0, maturity: 'new' as any },
          revenue: { total: 0, recent: 0, averagePerMonth: 0, projected: 0, byProduct: [] },
          engagement: { likes: 0, comments: 0, shares: 0, saves: 0, collections: 0, follows: 0, averageRatingTime: 0, commentEngagement: 0 }
        },
        quality: {
          technical: {
            geometry: { triangles: 0, vertices: 0, normals: true, degenerateFaces: false, duplicateVertices: false, manifold: true, waterTight: true, clean: true, score: 100 },
            textures: { resolution: '1024x1024', format: 'png', compression: 0.9, seams: false, matching: true, tiling: false, colorSpace: 'sRGB', score: 100 },
            materials: { realistic: true, consistent: true, optimized: true, pbr: true, maps: [], score: 100 },
            uv: { exists: true, islands: 1, islandsCount: 1, overlapped: false, flipped: false, stretched: false, score: 100 },
            topology: { quads: 0, triangles: 0, nGons: 0, poles: 0, distortion: 0, smoothing: true, organic: false, hardEdges: false, score: 100 }
          },
          artistic: {
            design: { originality: 0.8, complexity: 0.7, attention: 0.9, innovation: 0.6, concept: 0.8, execution: 0.9, score: 0.8 },
            style: { consistency: 0.9, aesthetics: 0.8, visual: 0.9, originality: 0.7, score: 0.8 },
            composition: { balance: 0.8, harmony: 0.9, contrast: 0.7, rhythm: 0.8, emphasis: 0.8, score: 0.8 }
          },
          commercial: { marketability: 0.8, utility: 0.9, production: 0.8, licensing: 0.9, competition: 0.7, score: 0.8 },
          overall: { technical: 100, artistic: 80, commercial: 80, overall: 87, grade: 'B' as any, certifications: [] }
        },
        reviews: [],
        status: 'pending' as any,
        featured: false,
        verified: false,
        updatedAt: new Date(),
        publishedAt: undefined,
        scheduledAt: undefined,
        expirationDate: undefined,
        downloadCount: 0,
        likeCount: 0,
        viewCount: 0,
        shareCount: 0,
        reportCount: 0,
        featuredUntil: undefined,
        adminNotes: undefined
      });
      
      addNotification(`Marketplace listing created: ${listing.title}`, 'success');
    } catch (error) {
      console.error('Failed to create marketplace listing:', error);
      addNotification('Failed to create marketplace listing', 'error');
    }
  };

  // Render components
  const ServiceStatusCard = ({ title, status, icon: Icon, color }: any) => (
    <Card className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-800 dark:to-slate-900">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-2">
          {status.connected ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          )}
          <span className="text-xs text-muted-foreground">
            {status.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {status.jobs !== undefined && (
          <div className="mt-2 text-xs text-muted-foreground">
            Active: {status.jobs}
          </div>
        )}
        {status.sessions !== undefined && (
          <div className="mt-1 text-xs text-muted-foreground">
            Sessions: {status.sessions}
          </div>
        )}
        {status.activeUsers !== undefined && (
          <div className="mt-1 text-xs text-muted-foreground">
            Users: {status.activeUsers}
          </div>
        )}
        {status.queuePosition !== undefined && (
          <div className="mt-1 text-xs text-muted-foreground">
            Queue: #{status.queuePosition}
          </div>
        )}
        {status.listings !== undefined && (
          <div className="mt-1 text-xs text-muted-foreground">
            Listings: {status.listings}
          </div>
        )}
        {status.transactions !== undefined && (
          <div className="mt-1 text-xs text-muted-foreground">
            Sales: {status.transactions}
          </div>
        )}
      </CardContent>
    </Card>
  );

  const QuickActionsGrid = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Button
        onClick={createPrintJob}
        className="h-24 flex-col space-y-2 bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
      >
        <Printer className="h-6 w-6" />
        <span className="text-xs">New Print Job</span>
      </Button>

      <Button
        onClick={createCollaborationSession}
        className="h-24 flex-col space-y-2 bg-gradient-to-br from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
      >
        <Users className="h-6 w-6" />
        <span className="text-xs">Start Collaboration</span>
      </Button>

      <Button
        onClick={submitRenderJob}
        className="h-24 flex-col space-y-2 bg-gradient-to-br from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700"
      >
        <Cloud className="h-6 w-6" />
        <span className="text-xs">Cloud Render</span>
      </Button>

      <Button
        onClick={createMarketplaceListing}
        className="h-24 flex-col space-y-2 bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700"
      >
        <ShoppingCart className="h-6 w-6" />
        <span className="text-xs">Sell Model</span>
      </Button>
    </div>
  );

  const RecentActivity = () => (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Activity</CardTitle>
        <CardDescription>Latest events across all services</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {notifications.slice(0, 5).map((notification) => (
            <div key={notification.id} className="flex items-center space-x-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
              <div className={`w-2 h-2 rounded-full ${
                notification.type === 'success' ? 'bg-green-500' :
                notification.type === 'error' ? 'bg-red-500' :
                notification.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
              }`} />
              <div className="flex-1">
                <p className="text-sm font-medium">{notification.message}</p>
                <p className="text-xs text-muted-foreground">
                  {notification.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {notifications.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const StatsOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <Printer className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Print Jobs</p>
              <p className="text-2xl font-bold">{printJobs.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Active Sessions</p>
              <p className="text-2xl font-bold">{collaborativeSessions.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <Cloud className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Render Jobs</p>
              <p className="text-2xl font-bold">{renderJobs.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center">
            <ShoppingCart className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Marketplace Items</p>
              <p className="text-2xl font-bold">{marketplaceListings.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Initializing Sprint 6+ Features...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Header */}
      <div className="border-b bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Sprint 6+ Features
                </h1>
                <p className="text-sm text-muted-foreground">
                  Advanced 3D Platform Capabilities
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                <CheckCircle className="h-3 w-3 mr-1" />
                All Services Active
              </Badge>
              
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <StatsOverview />

        {/* Service Status */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Service Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ServiceStatusCard
              title="3D Printing"
              status={servicesStatus.printing3D}
              icon={Printer}
              color="text-blue-500"
            />
            <ServiceStatusCard
              title="Collaboration"
              status={servicesStatus.collaboration}
              icon={Users}
              color="text-green-500"
            />
            <ServiceStatusCard
              title="Cloud Rendering"
              status={servicesStatus.cloudRendering}
              icon={Cloud}
              color="text-purple-500"
            />
            <ServiceStatusCard
              title="Marketplace"
              status={servicesStatus.marketplace}
              icon={ShoppingCart}
              color="text-orange-500"
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <QuickActionsGrid />
        </div>

        {/* Main Content Tabs */}
        <div className="mt-8">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="printing">3D Printing</TabsTrigger>
              <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
              <TabsTrigger value="rendering">Cloud Rendering</TabsTrigger>
              <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <RecentActivity />
                
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Feature Overview</CardTitle>
                    <CardDescription>What's new in Sprint 6+</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start space-x-3">
                        <Printer className="h-5 w-5 text-blue-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium">3D Printing Suite</h4>
                          <p className="text-sm text-muted-foreground">
                            Complete print management with G-code generation, material tracking, and printer control.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <Users className="h-5 w-5 text-green-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Real-time Collaboration</h4>
                          <p className="text-sm text-muted-foreground">
                            Multi-user editing, video chat, screen sharing, and version control.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <Cloud className="h-5 w-5 text-purple-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Cloud Rendering</h4>
                          <p className="text-sm text-muted-foreground">
                            Distributed rendering with GPU clusters, batch processing, and automated optimization.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <ShoppingCart className="h-5 w-5 text-orange-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium">Marketplace Platform</h4>
                          <p className="text-sm text-muted-foreground">
                            Sell and buy 3D models with secure payments, reviews, and collections.
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="printing" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    3D Printing Queue
                    <Button size="sm" onClick={createPrintJob}>
                      <Plus className="h-4 w-4 mr-2" />
                      New Job
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {printJobs.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Printer className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No print jobs in queue</p>
                      <Button onClick={createPrintJob} className="mt-4">
                        Create First Job
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {printJobs.map((job) => (
                        <div key={job.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{job.modelName}</h4>
                            <Badge variant={
                              job.status === 'completed' ? 'default' :
                              job.status === 'printing' ? 'destructive' : 'secondary'
                            }>
                              {job.status}
                            </Badge>
                          </div>
                          <Progress value={job.progress} className="mb-2" />
                          <p className="text-sm text-muted-foreground">
                            Progress: {job.progress}%
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="collaboration" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Collaboration Sessions
                    <Button size="sm" onClick={createCollaborationSession}>
                      <Plus className="h-4 w-4 mr-2" />
                      New Session
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {collaborativeSessions.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No active sessions</p>
                      <Button onClick={createCollaborationSession} className="mt-4">
                        Start First Session
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {collaborativeSessions.map((session) => (
                        <div key={session.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{session.modelName}</h4>
                            <Badge variant="outline">
                              {session.participants.length} users
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Status: {session.status}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="rendering" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Cloud Render Jobs
                    <Button size="sm" onClick={submitRenderJob}>
                      <Plus className="h-4 w-4 mr-2" />
                      New Render
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {renderJobs.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Cloud className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No render jobs</p>
                      <Button onClick={submitRenderJob} className="mt-4">
                        Submit First Render
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {renderJobs.map((job) => (
                        <div key={job.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">Render Job {job.id.slice(0, 8)}</h4>
                            <Badge variant="outline">
                              {job.type}
                            </Badge>
                          </div>
                          <Progress value={job.progress.percentage} className="mb-2" />
                          <p className="text-sm text-muted-foreground">
                            {job.progress.currentPass}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="marketplace" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Marketplace Listings
                    <Button size="sm" onClick={createMarketplaceListing}>
                      <Plus className="h-4 w-4 mr-2" />
                      List Model
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {marketplaceListings.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <ShoppingCart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No marketplace listings</p>
                      <Button onClick={createMarketplaceListing} className="mt-4">
                        Create First Listing
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {marketplaceListings.map((listing) => (
                        <div key={listing.id} className="border rounded-lg p-4">
                          <h4 className="font-medium mb-2">{listing.title}</h4>
                          <p className="text-sm text-muted-foreground mb-2">
                            {listing.shortDescription}
                          </p>
                          <div className="flex items-center justify-between">
                            <Badge variant={
                              listing.pricing.type === 'free' ? 'secondary' : 'default'
                            }>
                              {listing.pricing.type === 'free' ? 'Free' : `$${listing.pricing.price}`}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {listing.statistics.downloads.total} downloads
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Sprint6PlusPage;