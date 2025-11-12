// Sprint 6+: Marketplace Service
// Serviço completo para marketplace de modelos 3D

import axios from 'axios';
import { EventEmitter } from 'events';
import toast from 'react-hot-toast';
import { loadStripe } from '@stripe/stripe-js';

// Types
import type {
  ModelListing,
  ModelCategory,
  ModelReview,
  PurchaseTransaction,
  ModelCollection,
  SearchFilters,
  SearchResults,
  UserProfile,
  MarketplaceAnalytics,
  PricingModel
} from '@/types/marketplace';

interface MarketplaceServiceConfig {
  apiUrl: string;
  stripePublicKey: string;
  enablePayments: boolean;
  enableFileSharing: boolean;
  maxFileSize: number;
  enableUserVerification: boolean;
  enableReviews: boolean;
  enableCollections: boolean;
  maxDownloadsPerPurchase: number;
}

interface FileUploadProgress {
  fileId: string;
  fileName: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  error?: string;
}

export class MarketplaceService extends EventEmitter {
  private config: MarketplaceServiceConfig;
  private stripe: any = null;
  private currentUser: UserProfile | null = null;
  private uploads: Map<string, FileUploadProgress> = new Map();
  private searchCache: Map<string, SearchResults> = new Map();
  private isConnected = false;

  constructor(config: MarketplaceServiceConfig) {
    super();
    this.config = {
      maxFileSize: 500 * 1024 * 1024, // 500MB
      maxDownloadsPerPurchase: 5,
      enablePayments: true,
      enableFileSharing: true,
      enableUserVerification: true,
      enableReviews: true,
      enableCollections: true,
      ...config
    };
    this.initializeStripe();
  }

  private async initializeStripe() {
    if (this.config.enablePayments && this.config.stripePublicKey) {
      try {
        this.stripe = await loadStripe(this.config.stripePublicKey);
        console.log('💳 Stripe initialized for marketplace payments');
      } catch (error) {
        console.error('❌ Failed to initialize Stripe:', error);
      }
    }
  }

  // User Management
  setCurrentUser(user: UserProfile): void {
    this.currentUser = user;
  }

  async updateUserProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.put(`${this.config.apiUrl}/marketplace/users/${this.currentUser.id}`, updates);
      this.currentUser = response.data;
      this.emit('user_updated', this.currentUser);
      return this.currentUser;
    } catch (error) {
      console.error('❌ Failed to update user profile:', error);
      throw error;
    }
  }

  async verifyUser(verificationType: string, data: any): Promise<{ verified: boolean; level: string }> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/users/${this.currentUser.id}/verify`, {
        type: verificationType,
        data
      });

      // Update current user verification status
      this.currentUser.verification.status = response.data.verified ? 'verified' : 'pending';
      this.currentUser.verification.level = response.data.level;
      this.currentUser.verification.score = response.data.score;

      this.emit('user_verified', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to verify user:', error);
      throw error;
    }
  }

  // Model Listing Management
  async createListing(
    modelData: Omit<ModelListing, 'id' | 'author' | 'createdAt' | 'updatedAt' | 'downloadCount' | 'likeCount' | 'viewCount' | 'shareCount' | 'reportCount'>
  ): Promise<ModelListing> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/listings`, {
        ...modelData,
        author: this.currentUser
      });

      const listing = response.data;
      this.emit('listing_created', listing);
      toast.success('Model listing created successfully!');
      
      return listing;
    } catch (error) {
      console.error('❌ Failed to create listing:', error);
      toast.error('Failed to create model listing');
      throw error;
    }
  }

  async updateListing(listingId: string, updates: Partial<ModelListing>): Promise<ModelListing> {
    try {
      const response = await axios.put(`${this.config.apiUrl}/marketplace/listings/${listingId}`, updates);
      const listing = response.data;
      
      this.emit('listing_updated', listing);
      toast.success('Listing updated successfully!');
      
      return listing;
    } catch (error) {
      console.error('❌ Failed to update listing:', error);
      toast.error('Failed to update listing');
      throw error;
    }
  }

  async deleteListing(listingId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/listings/${listingId}`);
      this.emit('listing_deleted', listingId);
      toast.success('Listing deleted successfully');
    } catch (error) {
      console.error('❌ Failed to delete listing:', error);
      toast.error('Failed to delete listing');
      throw error;
    }
  }

  async getListing(listingId: string): Promise<ModelListing> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/${listingId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get listing:', error);
      throw error;
    }
  }

  async getUserListings(userId?: string): Promise<ModelListing[]> {
    const targetUserId = userId || this.currentUser?.id;
    if (!targetUserId) {
      throw new Error('No user ID provided');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${targetUserId}/listings`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get user listings:', error);
      throw error;
    }
  }

  async getFeaturedListings(limit: number = 10): Promise<ModelListing[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/featured`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get featured listings:', error);
      throw error;
    }
  }

  async getTrendingListings(limit: number = 20): Promise<ModelListing[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/trending`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get trending listings:', error);
      throw error;
    }
  }

  // Search and Discovery
  async searchModels(
    query: string,
    filters: SearchFilters = {},
    page: number = 1,
    pageSize: number = 20,
    sortBy: string = 'relevance'
  ): Promise<SearchResults> {
    try {
      const cacheKey = `${query}_${JSON.stringify(filters)}_${page}_${pageSize}_${sortBy}`;
      
      // Check cache first
      if (this.searchCache.has(cacheKey)) {
        return this.searchCache.get(cacheKey)!;
      }

      const response = await axios.get(`${this.config.apiUrl}/marketplace/search`, {
        params: {
          q: query,
          page,
          pageSize,
          sortBy,
          ...filters
        }
      });

      const results = response.data;
      
      // Cache results
      this.searchCache.set(cacheKey, results);
      
      // Clear cache if it gets too large
      if (this.searchCache.size > 100) {
        const firstKey = this.searchCache.keys().next().value;
        this.searchCache.delete(firstKey);
      }

      return results;
    } catch (error) {
      console.error('❌ Failed to search models:', error);
      throw error;
    }
  }

  async getSuggestions(query: string, limit: number = 5): Promise<string[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/search/suggestions`, {
        params: { q: query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get suggestions:', error);
      return [];
    }
  }

  async getRelatedListings(listingId: string, limit: number = 10): Promise<ModelListing[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/${listingId}/related`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get related listings:', error);
      throw error;
    }
  }

  // File Management
  async uploadModelFile(file: File, listingId: string): Promise<string> {
    if (!this.config.enableFileSharing) {
      throw new Error('File sharing is not enabled');
    }

    if (file.size > this.config.maxFileSize) {
      throw new Error(`File size exceeds maximum allowed (${this.config.maxFileSize / 1024 / 1024}MB)`);
    }

    try {
      const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Initialize upload progress
      this.uploads.set(fileId, {
        fileId,
        fileName: file.name,
        progress: 0,
        status: 'uploading'
      });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('listingId', listingId);
      formData.append('fileId', fileId);

      const response = await axios.post(`${this.config.apiUrl}/marketplace/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          this.updateUploadProgress(fileId, progress);
        }
      });

      const result = response.data;
      
      // Update upload status
      this.updateUploadProgress(fileId, 100, 'completed');
      
      this.emit('file_uploaded', result);
      toast.success('File uploaded successfully!');
      
      return result.fileId;
    } catch (error) {
      console.error('❌ Failed to upload file:', error);
      this.updateUploadProgress('', 0, 'failed', error.message);
      toast.error('Failed to upload file');
      throw error;
    }
  }

  async uploadModelThumbnail(file: File, listingId: string): Promise<string> {
    if (!file.type.startsWith('image/')) {
      throw new Error('Thumbnail must be an image file');
    }

    try {
      const formData = new FormData();
      formData.append('thumbnail', file);
      formData.append('listingId', listingId);

      const response = await axios.post(`${this.config.apiUrl}/marketplace/files/thumbnail`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response.data.url;
    } catch (error) {
      console.error('❌ Failed to upload thumbnail:', error);
      toast.error('Failed to upload thumbnail');
      throw error;
    }
  }

  private updateUploadProgress(fileId: string, progress: number, status?: 'uploading' | 'processing' | 'completed' | 'failed', error?: string): void {
    const upload = this.uploads.get(fileId);
    if (upload) {
      upload.progress = progress;
      if (status) upload.status = status;
      if (error) upload.error = error;
      this.uploads.set(fileId, upload);
      this.emit('upload_progress', upload);
    }
  }

  async deleteFile(fileId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/files/${fileId}`);
      toast.success('File deleted successfully');
    } catch (error) {
      console.error('❌ Failed to delete file:', error);
      toast.error('Failed to delete file');
      throw error;
    }
  }

  // Download Management
  async downloadModel(listingId: string): Promise<Blob> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/${listingId}/download`, {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      // Track download
      this.trackDownload(listingId);
      
      return response.data;
    } catch (error) {
      console.error('❌ Failed to download model:', error);
      throw error;
    }
  }

  private async trackDownload(listingId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/listings/${listingId}/download`, {
        userId: this.currentUser?.id
      });
    } catch (error) {
      console.error('Failed to track download:', error);
    }
  }

  // Purchase and Payment
  async purchaseModel(listingId: string, paymentMethodId?: string): Promise<{ transactionId: string; downloadUrl: string }> {
    if (!this.config.enablePayments) {
      throw new Error('Payments are not enabled');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/purchase`, {
        listingId,
        userId: this.currentUser?.id,
        paymentMethodId
      });

      const result = response.data;
      
      // If payment was processed, download is now available
      if (result.transactionId) {
        toast.success('Purchase completed successfully!');
        this.emit('model_purchased', result);
      }
      
      return result;
    } catch (error) {
      console.error('❌ Failed to purchase model:', error);
      toast.error('Failed to purchase model');
      throw error;
    }
  }

  async createPaymentIntent(amount: number, currency: string = 'usd', metadata: any = {}): Promise<{ clientSecret: string; paymentIntentId: string }> {
    if (!this.stripe) {
      throw new Error('Stripe not initialized');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/payments/create-intent`, {
        amount,
        currency,
        metadata: {
          ...metadata,
          userId: this.currentUser?.id
        }
      });

      const { clientSecret, paymentIntentId } = response.data;
      
      return { clientSecret, paymentIntentId };
    } catch (error) {
      console.error('❌ Failed to create payment intent:', error);
      throw error;
    }
  }

  async confirmPayment(paymentIntentId: string, paymentMethodId: string): Promise<{ success: boolean; transactionId?: string }> {
    if (!this.stripe) {
      throw new Error('Stripe not initialized');
    }

    try {
      const result = await this.stripe.confirmPayment({
        clientSecret: paymentIntentId,
        payment_method: paymentMethodId
      });

      if (result.error) {
        throw new Error(result.error.message);
      }

      return { success: true, transactionId: result.paymentIntent.id };
    } catch (error) {
      console.error('❌ Failed to confirm payment:', error);
      throw error;
    }
  }

  async getPurchases(): Promise<PurchaseTransaction[]> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${this.currentUser.id}/purchases`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get purchases:', error);
      throw error;
    }
  }

  async getSales(): Promise<PurchaseTransaction[]> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${this.currentUser.id}/sales`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get sales:', error);
      throw error;
    }
  }

  // Reviews and Ratings
  async createReview(review: Omit<ModelReview, 'id' | 'createdAt' | 'updatedAt'>): Promise<ModelReview> {
    if (!this.config.enableReviews) {
      throw new Error('Reviews are not enabled');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/reviews`, {
        ...review,
        author: this.currentUser
      });

      const newReview = response.data;
      this.emit('review_created', newReview);
      toast.success('Review posted successfully!');
      
      return newReview;
    } catch (error) {
      console.error('❌ Failed to create review:', error);
      toast.error('Failed to post review');
      throw error;
    }
  }

  async updateReview(reviewId: string, updates: Partial<ModelReview>): Promise<ModelReview> {
    try {
      const response = await axios.put(`${this.config.apiUrl}/marketplace/reviews/${reviewId}`, updates);
      const review = response.data;
      
      this.emit('review_updated', review);
      toast.success('Review updated successfully!');
      
      return review;
    } catch (error) {
      console.error('❌ Failed to update review:', error);
      toast.error('Failed to update review');
      throw error;
    }
  }

  async deleteReview(reviewId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/reviews/${reviewId}`);
      this.emit('review_deleted', reviewId);
      toast.success('Review deleted successfully');
    } catch (error) {
      console.error('❌ Failed to delete review:', error);
      toast.error('Failed to delete review');
      throw error;
    }
  }

  async getReviews(listingId: string, page: number = 1, pageSize: number = 10): Promise<{ reviews: ModelReview[]; total: number }> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/${listingId}/reviews`, {
        params: { page, pageSize }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get reviews:', error);
      throw error;
    }
  }

  async voteReview(reviewId: string, helpful: boolean): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/reviews/${reviewId}/vote`, { helpful });
      toast.success('Vote recorded');
    } catch (error) {
      console.error('❌ Failed to vote on review:', error);
      throw error;
    }
  }

  // Collections Management
  async createCollection(collection: Omit<ModelCollection, 'id' | 'createdAt' | 'updatedAt'>): Promise<ModelCollection> {
    if (!this.config.enableCollections) {
      throw new Error('Collections are not enabled');
    }

    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/collections`, {
        ...collection,
        authorId: this.currentUser?.id
      });

      const newCollection = response.data;
      this.emit('collection_created', newCollection);
      toast.success('Collection created successfully!');
      
      return newCollection;
    } catch (error) {
      console.error('❌ Failed to create collection:', error);
      toast.error('Failed to create collection');
      throw error;
    }
  }

  async updateCollection(collectionId: string, updates: Partial<ModelCollection>): Promise<ModelCollection> {
    try {
      const response = await axios.put(`${this.config.apiUrl}/marketplace/collections/${collectionId}`, updates);
      const collection = response.data;
      
      this.emit('collection_updated', collection);
      toast.success('Collection updated successfully!');
      
      return collection;
    } catch (error) {
      console.error('❌ Failed to update collection:', error);
      toast.error('Failed to update collection');
      throw error;
    }
  }

  async deleteCollection(collectionId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/collections/${collectionId}`);
      this.emit('collection_deleted', collectionId);
      toast.success('Collection deleted successfully');
    } catch (error) {
      console.error('❌ Failed to delete collection:', error);
      toast.error('Failed to delete collection');
      throw error;
    }
  }

  async addToCollection(collectionId: string, listingId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/collections/${collectionId}/items`, {
        listingId
      });
      
      this.emit('item_added_to_collection', { collectionId, listingId });
      toast.success('Added to collection');
    } catch (error) {
      console.error('❌ Failed to add to collection:', error);
      toast.error('Failed to add to collection');
      throw error;
    }
  }

  async removeFromCollection(collectionId: string, listingId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/collections/${collectionId}/items/${listingId}`);
      
      this.emit('item_removed_from_collection', { collectionId, listingId });
      toast.success('Removed from collection');
    } catch (error) {
      console.error('❌ Failed to remove from collection:', error);
      toast.error('Failed to remove from collection');
      throw error;
    }
  }

  async getCollections(userId?: string): Promise<ModelCollection[]> {
    const targetUserId = userId || this.currentUser?.id;
    if (!targetUserId) {
      throw new Error('No user ID provided');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${targetUserId}/collections`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get collections:', error);
      throw error;
    }
  }

  // Favorites and Wishlist
  async addToFavorites(listingId: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/listings/${listingId}/favorite`);
      
      this.emit('added_to_favorites', listingId);
      toast.success('Added to favorites');
    } catch (error) {
      console.error('❌ Failed to add to favorites:', error);
      toast.error('Failed to add to favorites');
      throw error;
    }
  }

  async removeFromFavorites(listingId: string): Promise<void> {
    try {
      await axios.delete(`${this.config.apiUrl}/marketplace/listings/${listingId}/favorite`);
      
      this.emit('removed_from_favorites', listingId);
      toast.success('Removed from favorites');
    } catch (error) {
      console.error('❌ Failed to remove from favorites:', error);
      toast.error('Failed to remove from favorites');
      throw error;
    }
  }

  async getFavorites(): Promise<string[]> {
    if (!this.currentUser) {
      throw new Error('No current user set');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${this.currentUser.id}/favorites`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get favorites:', error);
      throw error;
    }
  }

  // Categories and Organization
  async getCategories(): Promise<ModelCategory[]> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/categories`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get categories:', error);
      throw error;
    }
  }

  async createCategory(category: Omit<ModelCategory, 'id'>): Promise<ModelCategory> {
    try {
      const response = await axios.post(`${this.config.apiUrl}/marketplace/categories`, category);
      const newCategory = response.data;
      
      this.emit('category_created', newCategory);
      toast.success('Category created successfully!');
      
      return newCategory;
    } catch (error) {
      console.error('❌ Failed to create category:', error);
      toast.error('Failed to create category');
      throw error;
    }
  }

  // Analytics and Insights
  async getListingAnalytics(listingId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/listings/${listingId}/analytics`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get listing analytics:', error);
      throw error;
    }
  }

  async getUserAnalytics(userId?: string): Promise<any> {
    const targetUserId = userId || this.currentUser?.id;
    if (!targetUserId) {
      throw new Error('No user ID provided');
    }

    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/users/${targetUserId}/analytics`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get user analytics:', error);
      throw error;
    }
  }

  async getMarketplaceAnalytics(timeframe: string = '30d'): Promise<MarketplaceAnalytics> {
    try {
      const response = await axios.get(`${this.config.apiUrl}/marketplace/analytics`, {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get marketplace analytics:', error);
      throw error;
    }
  }

  // Reporting and Moderation
  async reportListing(listingId: string, reason: string, description?: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/listings/${listingId}/report`, {
        reason,
        description,
        reporterId: this.currentUser?.id
      });
      
      toast.success('Report submitted successfully');
    } catch (error) {
      console.error('❌ Failed to report listing:', error);
      toast.error('Failed to submit report');
      throw error;
    }
  }

  async reportReview(reviewId: string, reason: string, description?: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/reviews/${reviewId}/report`, {
        reason,
        description,
        reporterId: this.currentUser?.id
      });
      
      toast.success('Report submitted successfully');
    } catch (error) {
      console.error('❌ Failed to report review:', error);
      toast.error('Failed to submit report');
      throw error;
    }
  }

  // Social Features
  async shareListing(listingId: string, platform: string): Promise<void> {
    const listing = await this.getListing(listingId);
    const shareUrl = `${window.location.origin}/marketplace/listing/${listingId}`;
    const shareText = `Check out this amazing 3D model: ${listing.title}`;

    try {
      let url = '';
      switch (platform) {
        case 'twitter':
          url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
          break;
        case 'facebook':
          url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
          break;
        case 'linkedin':
          url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
          break;
        case 'copy':
          await navigator.clipboard.writeText(shareUrl);
          toast.success('Link copied to clipboard!');
          return;
        default:
          throw new Error('Unsupported platform');
      }

      window.open(url, '_blank', 'width=600,height=400');
      
      // Track share
      this.trackShare(listingId, platform);
    } catch (error) {
      console.error('❌ Failed to share listing:', error);
      toast.error('Failed to share listing');
      throw error;
    }
  }

  private async trackShare(listingId: string, platform: string): Promise<void> {
    try {
      await axios.post(`${this.config.apiUrl}/marketplace/listings/${listingId}/share`, {
        platform,
        userId: this.currentUser?.id
      });
    } catch (error) {
      console.error('Failed to track share:', error);
    }
  }

  // Utility Functions
  private getAuthToken(): string {
    // Get token from localStorage or context
    return localStorage.getItem('auth_token') || '';
  }

  clearSearchCache(): void {
    this.searchCache.clear();
  }

  clearUploadCache(): void {
    this.uploads.clear();
  }

  // Getters
  getCurrentUser(): UserProfile | null {
    return this.currentUser;
  }

  getUploadProgress(fileId: string): FileUploadProgress | undefined {
    return this.uploads.get(fileId);
  }

  getAllUploads(): FileUploadProgress[] {
    return Array.from(this.uploads.values());
  }

  isPaymentsEnabled(): boolean {
    return this.config.enablePayments;
  }

  isFileSharingEnabled(): boolean {
    return this.config.enableFileSharing;
  }

  isUserVerified(): boolean {
    return this.currentUser?.verification.status === 'verified';
  }

  // Cleanup
  destroy(): void {
    this.clearSearchCache();
    this.clearUploadCache();
    this.removeAllListeners();
  }
}

// Service instance
export const marketplaceService = new MarketplaceService({
  apiUrl: process.env.VITE_API_URL || 'http://localhost:8000',
  stripePublicKey: process.env.VITE_STRIPE_PUBLIC_KEY || '',
  enablePayments: true,
  enableFileSharing: true,
  enableUserVerification: true,
  enableReviews: true,
  enableCollections: true
});