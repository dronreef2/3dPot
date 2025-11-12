// Sprint 6+: Marketplace Platform Types
// Marketplace para compartilhamento e venda de modelos 3D

export interface ModelListing {
  id: string;
  title: string;
  description: string;
  shortDescription: string;
  category: ModelCategory;
  subcategory?: string;
  tags: string[];
  model: Model3D;
  author: UserProfile;
  pricing: PricingModel;
  media: MediaAssets;
  files: FileInfo[];
  license: LicenseInfo;
  statistics: ModelStatistics;
  quality: ModelQuality;
  reviews: ModelReview[];
  status: ListingStatus;
  featured: boolean;
  verified: boolean;
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  scheduledAt?: Date;
  expirationDate?: Date;
  downloadCount: number;
  likeCount: number;
  viewCount: number;
  shareCount: number;
  reportCount: number;
  featuredUntil?: Date;
  adminNotes?: string;
}

export interface ModelCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  parentId?: string;
  icon: string;
  color: string;
  sortOrder: number;
  isActive: boolean;
  featured: boolean;
  subcategories: ModelCategory[];
}

export interface PricingModel {
  type: 'free' | 'paid' | 'freemium' | 'subscription';
  price: number;
  currency: string;
  originalPrice?: number;
  discountPercentage?: number;
  subscription?: SubscriptionInfo;
  bundle?: BundleInfo;
  paymentModel: 'one_time' | 'recurring' | 'per_download';
  taxRate?: number;
  fees: PriceBreakdown;
}

export interface SubscriptionInfo {
  plan: 'monthly' | 'yearly' | 'lifetime';
  price: number;
  currency: string;
  trialDays: number;
  features: SubscriptionFeature[];
}

export interface SubscriptionFeature {
  name: string;
  included: boolean;
  limit?: number;
  description: string;
}

export interface BundleInfo {
  id: string;
  name: string;
  originalPrice: number;
  bundlePrice: number;
  savings: number;
  items: string[]; // model IDs
  validUntil?: Date;
  limitedQuantity?: number;
  purchasedCount: number;
}

export interface PriceBreakdown {
  platform: number; // platform fee
  payment: number; // payment processing fee
  author: number; // author's share
  taxes: number;
  net: number;
}

export interface MediaAssets {
  preview: string;
  thumbnails: ThumbnailInfo[];
  screenshots: ScreenshotInfo[];
  videos: VideoInfo[];
  heroImage: string;
  modelPreview: string;
  animatedGif?: string;
  arPreview?: string;
  vrPreview?: string;
}

export interface ThumbnailInfo {
  size: 'small' | 'medium' | 'large' | 'custom';
  width: number;
  height: number;
  url: string;
  generatedAt: Date;
}

export interface ScreenshotInfo {
  id: string;
  title: string;
  description?: string;
  url: string;
  thumbnailUrl: string;
  angle: string;
  lighting: string;
  background: string;
  featured: boolean;
  sortOrder: number;
}

export interface VideoInfo {
  id: string;
  title: string;
  description?: string;
  url: string;
  thumbnailUrl: string;
  duration: number;
  format: 'mp4' | 'webm' | 'mov';
  resolution: string;
  featured: boolean;
}

export interface FileInfo {
  id: string;
  name: string;
  format: 'obj' | 'stl' | 'ply' | 'gltf' | '3mf' | 'fbx' | 'dae' | 'x3d';
  size: number;
  url: string;
  downloadCount: number;
  previewAvailable: boolean;
  lowPoly?: boolean;
  highPoly?: boolean;
  wireframe?: boolean;
  textures?: FileTexture[];
  materials?: FileMaterial[];
  generatedAt: Date;
}

export interface FileTexture {
  id: string;
  name: string;
  type: 'diffuse' | 'normal' | 'specular' | 'roughness' | 'metallic' | 'emissive' | 'alpha';
  url: string;
  size: number;
  format: 'png' | 'jpg' | 'tga' | 'exr' | 'hdr';
  resolution: string;
}

export interface FileMaterial {
  id: string;
  name: string;
  type: 'standard' | 'pbr' | 'procedural' | 'subsurface' | 'emission';
  properties: MaterialProperties;
  textures: string[];
}

export interface MaterialProperties {
  roughness?: number;
  metallic?: number;
  emission?: number;
  transmission?: number;
  ior?: number;
  color?: string;
  shader?: string;
}

export interface LicenseInfo {
  type: 'cc0' | 'cc_by' | 'cc_by_sa' | 'cc_by_nc' | 'custom' | 'proprietary';
  description: string;
  terms: string[];
  restrictions: string[];
  attribution?: string;
  commercialUse: boolean;
  modifications: boolean;
  distribution: boolean;
  creator: string;
  copyright: string;
  lastModified: Date;
}

export interface ModelStatistics {
  downloads: DownloadStats;
  ratings: RatingStats;
  views: ViewStats;
  popularity: PopularityStats;
  revenue: RevenueStats;
  engagement: EngagementStats;
}

export interface DownloadStats {
  total: number;
  recent: number;
  trend: 'up' | 'down' | 'stable';
  byFormat: FormatDownload[];
  byCountry: CountryDownload[];
  averagePerDay: number;
  peakDate: Date;
}

export interface FormatDownload {
  format: string;
  count: number;
  percentage: number;
}

export interface CountryDownload {
  country: string;
  count: number;
  percentage: number;
}

export interface RatingStats {
  average: number;
  count: number;
  distribution: RatingDistribution;
  trend: 'up' | 'down' | 'stable';
  verifiedOnly: boolean;
}

export interface RatingDistribution {
  5: number;
  4: number;
  3: number;
  2: number;
  1: number;
}

export interface ViewStats {
  total: number;
  recent: number;
  unique: number;
  averageTime: number;
  bounceRate: number;
  traffic: TrafficStats;
}

export interface TrafficStats {
  direct: number;
  search: number;
  social: number;
  referral: number;
  marketplace: number;
}

export interface PopularityStats {
  score: number;
  rank: number;
  categoryRank: number;
  trending: boolean;
  trendingScore: number;
  ageDays: number;
  maturity: 'new' | 'growing' | 'mature' | 'declining';
}

export interface RevenueStats {
  total: number;
  recent: number;
  averagePerMonth: number;
  projected: number;
  byProduct: ProductRevenue[];
}

export interface ProductRevenue {
  product: string;
  revenue: number;
  count: number;
  percentage: number;
}

export interface EngagementStats {
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  collections: number;
  follows: number;
  averageRatingTime: number;
  commentEngagement: number;
}

export interface ModelQuality {
  technical: TechnicalQuality;
  artistic: ArtisticQuality;
  commercial: CommercialQuality;
  overall: QualityScore;
}

export interface TechnicalQuality {
  geometry: GeometryQuality;
  textures: TextureQuality;
  materials: MaterialQuality;
  uv: UVQuality;
  topology: TopologyQuality;
}

export interface GeometryQuality {
  triangles: number;
  vertices: number;
  normals: boolean;
  degenerateFaces: boolean;
  duplicateVertices: boolean;
  manifold: boolean;
  waterTight: boolean;
  clean: boolean;
  score: number;
}

export interface TextureQuality {
  resolution: string;
  format: string;
  compression: number;
  seams: boolean;
  matching: boolean;
  tiling: boolean;
  colorSpace: string;
  score: number;
}

export interface MaterialQuality {
  realistic: boolean;
  consistent: boolean;
  optimized: boolean;
  pbr: boolean;
  maps: string[];
  score: number;
}

export interface UVQuality {
  exists: boolean;
  islands: number;
  islandsCount: number;
  overlapped: boolean;
  flipped: boolean;
  stretched: boolean;
  score: number;
}

export interface TopologyQuality {
  quads: number;
  triangles: number;
  nGons: number;
  poles: number;
  distortion: number;
  smoothing: boolean;
  organic: boolean;
  hardEdges: boolean;
  score: number;
}

export interface ArtisticQuality {
  design: DesignQuality;
  style: StyleQuality;
  composition: CompositionQuality;
}

export interface DesignQuality {
  originality: number;
  complexity: number;
  attention: number;
  innovation: number;
  concept: number;
  execution: number;
  score: number;
}

export interface StyleQuality {
  consistency: number;
  aesthetics: number;
  visual: number;
  originality: number;
  score: number;
}

export interface CompositionQuality {
  balance: number;
  harmony: number;
  contrast: number;
  rhythm: number;
  emphasis: number;
  score: number;
}

export interface CommercialQuality {
  marketability: number;
  utility: number;
  production: number;
  licensing: number;
  competition: number;
  score: number;
}

export interface QualityScore {
  technical: number;
  artistic: number;
  commercial: number;
  overall: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  certifications: QualityCertification[];
}

export interface QualityCertification {
  type: 'technical' | 'artistic' | 'commercial' | 'compliance';
  level: 'bronze' | 'silver' | 'gold' | 'platinum';
  issued: Date;
  expires?: Date;
  verified: boolean;
}

export interface ModelReview {
  id: string;
  author: UserProfile;
  rating: number;
  title: string;
  content: string;
  pros: string[];
  cons: string[];
  images: string[];
  verified: boolean;
  helpful: number;
  notHelpful: number;
  status: 'active' | 'pending' | 'deleted' | 'hidden';
  adminResponse?: AdminResponse;
  createdAt: Date;
  updatedAt: Date;
}

export interface AdminResponse {
  content: string;
  author: string;
  timestamp: Date;
}

export interface UserProfile {
  id: string;
  username: string;
  displayName: string;
  email: string;
  avatar?: string;
  bio?: string;
  location?: string;
  website?: string;
  socialLinks: SocialLink[];
  verification: UserVerification;
  statistics: UserStatistics;
  subscription: UserSubscription;
  preferences: UserPreferences;
  createdAt: Date;
  lastActive: Date;
  banned: boolean;
  bannedUntil?: Date;
  banReason?: string;
}

export interface SocialLink {
  platform: 'twitter' | 'instagram' | 'facebook' | 'youtube' | 'dribbble' | 'behance' | 'deviantart' | 'linkedin';
  url: string;
  verified: boolean;
}

export interface UserVerification {
  status: 'verified' | 'pending' | 'rejected' | 'none';
  level: 'none' | 'email' | 'phone' | 'identity' | 'professional';
  badges: VerificationBadge[];
  score: number;
}

export interface VerificationBadge {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  issued: Date;
  verified: boolean;
}

export interface UserStatistics {
  models: number;
  downloads: number;
  followers: number;
  following: number;
  collections: number;
  reviews: number;
  revenue: number;
  rating: number;
  reputation: number;
  experience: ExperienceLevel;
  achievements: UserAchievement[];
}

export interface ExperienceLevel {
  current: number;
  nextLevel: number;
  name: string;
  title: string;
  benefits: string[];
  requirements: string[];
}

export interface UserAchievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  unlocked: Date;
  progress: number;
  maxProgress: number;
}

export interface UserSubscription {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'expired' | 'cancelled' | 'pending';
  currentPeriodEnd: Date;
  autoRenewal: boolean;
  features: SubscriptionFeature[];
  paymentMethod?: PaymentMethod;
}

export interface UserPreferences {
  privacy: PrivacySettings;
  notifications: NotificationSettings;
  marketplace: MarketplaceSettings;
  collaboration: CollaborationSettings;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'friends';
  showEmail: boolean;
  showLocation: boolean;
  showWebsite: boolean;
  allowMessages: boolean;
  allowDownloads: boolean;
}

export interface NotificationSettings {
  email: EmailNotifications;
  push: PushNotifications;
  inApp: InAppNotifications;
}

export interface EmailNotifications {
  newModel: boolean;
  newReview: boolean;
  sale: boolean;
  message: boolean;
  marketing: boolean;
  security: boolean;
}

export interface PushNotifications {
  newModel: boolean;
  newReview: boolean;
  sale: boolean;
  message: boolean;
  collaboration: boolean;
}

export interface InAppNotifications {
  newModel: boolean;
  newReview: boolean;
  sale: boolean;
  message: boolean;
  collaboration: boolean;
  system: boolean;
}

export interface MarketplaceSettings {
  defaultCategory: string;
  autoPublish: boolean;
  requireApproval: boolean;
  allowBundles: boolean;
  allowCustomization: boolean;
  pricingPreference: 'min' | 'recommended' | 'max';
}

export interface CollaborationSettings {
  autoJoin: boolean;
  defaultRole: 'viewer' | 'editor' | 'commentator';
  allowScreenShare: boolean;
  allowVoiceChat: boolean;
  allowVideoChat: boolean;
  maxParticipants: number;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'paypal' | 'stripe' | 'crypto';
  last4?: string;
  brand?: string;
  expMonth?: number;
  expYear?: number;
  isDefault: boolean;
}

export type ListingStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'suspended' | 'deleted' | 'expired' | 'archived';

// Marketplace analytics and management
export interface MarketplaceAnalytics {
  totalRevenue: number;
  totalDownloads: number;
  totalModels: number;
  totalUsers: number;
  activeUsers: number;
  growth: GrowthMetrics;
  topPerformers: TopPerformer[];
  categories: CategoryAnalytics[];
  trends: TrendAnalytics[];
}

export interface GrowthMetrics {
  revenue: number;
  downloads: number;
  users: number;
  models: number;
  period: 'day' | 'week' | 'month' | 'quarter' | 'year';
}

export interface TopPerformer {
  type: 'model' | 'user' | 'category';
  id: string;
  name: string;
  metric: number;
  change: number;
  position: number;
}

export interface CategoryAnalytics {
  categoryId: string;
  name: string;
  models: number;
  downloads: number;
  revenue: number;
  growth: number;
  competition: number;
  saturation: number;
}

export interface TrendAnalytics {
  trend: 'rising' | 'declining' | 'stable' | 'seasonal';
  strength: number;
  timeframe: string;
  keywords: string[];
  models: string[];
}

export interface PurchaseTransaction {
  id: string;
  modelId: string;
  buyerId: string;
  sellerId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'disputed';
  paymentMethod: PaymentMethod;
  downloadLimit: number;
  downloadCount: number;
  createdAt: Date;
  completedAt?: Date;
  refundedAt?: Date;
  disputeReason?: string;
  metadata: TransactionMetadata;
}

export interface TransactionMetadata {
  ip: string;
  userAgent: string;
  referrer: string;
  campaign?: string;
  coupon?: string;
  discount: number;
  platformFee: number;
  paymentFee: number;
  netAmount: number;
}

// Collection and wishlist management
export interface ModelCollection {
  id: string;
  name: string;
  description?: string;
  authorId: string;
  models: string[];
  tags: string[];
  isPublic: boolean;
  isFeatured: boolean;
  thumbnail?: string;
  coverImage?: string;
  downloadCount: number;
  likeCount: number;
  viewCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Wishlist {
  id: string;
  userId: string;
  models: string[];
  collections: string[];
  tags: string[];
  autoRefresh: boolean;
  notifications: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Search and discovery
export interface SearchFilters {
  categories?: string[];
  priceRange?: PriceRange;
  formats?: string[];
  license?: string[];
  rating?: number;
  downloadCount?: number;
  createdWithin?: TimeRange;
  featured?: boolean;
  verified?: boolean;
  qualityScore?: number;
  fileSize?: FileSizeRange;
  complexity?: ComplexityLevel[];
}

export interface PriceRange {
  min: number;
  max: number;
  currency?: string;
}

export interface TimeRange {
  type: 'days' | 'weeks' | 'months' | 'years';
  value: number;
}

export interface FileSizeRange {
  min: number;
  max: number;
  unit: 'bytes' | 'kb' | 'mb' | 'gb';
}

export interface ComplexityLevel {
  name: 'simple' | 'moderate' | 'complex' | 'advanced';
  weight: number;
}

export interface SearchResults {
  query: string;
  results: ModelListing[];
  total: number;
  page: number;
  pageSize: number;
  filters: SearchFilters;
  suggestions: string[];
  related: string[];
  trending: string[];
  facets: SearchFacets;
  sortBy: SortOption;
}

export interface SearchFacets {
  categories: FacetItem[];
  priceRange: FacetItem[];
  formats: FacetItem[];
  ratings: FacetItem[];
  licenses: FacetItem[];
  tags: FacetItem[];
}

export interface FacetItem {
  value: string;
  count: number;
  selected: boolean;
}

export type SortOption = 'relevance' | 'popularity' | 'newest' | 'rating' | 'price_low' | 'price_high' | 'name' | 'downloads';

// Vector3 type for consistency
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

// Model3D type reference (from existing types)
export interface Model3D {
  id: string;
  name: string;
  description: string;
  specifications: any;
  filePath: string;
  thumbnail?: string;
  status: string;
  createdAt: Date;
  updatedAt: Date;
  metadata: any;
}