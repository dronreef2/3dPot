// Event Emitter Utility for Real-time Communication
export class EventEmitter {
  private events: Map<string, Set<Function>> = new Map();

  on(event: string, listener: Function): this {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    this.events.get(event)!.add(listener);
    return this;
  }

  off(event: string, listener: Function): this {
    const eventListeners = this.events.get(event);
    if (eventListeners) {
      eventListeners.delete(listener);
      if (eventListeners.size === 0) {
        this.events.delete(event);
      }
    }
    return this;
  }

  emit(event: string, ...args: any[]): boolean {
    const eventListeners = this.events.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => {
        try {
          listener(...args);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
      return true;
    }
    return false;
  }

  once(event: string, listener: Function): this {
    const onceWrapper = (...args: any[]) => {
      listener(...args);
      this.off(event, onceWrapper);
    };
    return this.on(event, onceWrapper);
  }

  removeAllListeners(event?: string): this {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
    return this;
  }

  getMaxListeners(): number {
    return EventEmitter.defaultMaxListeners;
  }

  setMaxListeners(n: number): this {
    EventEmitter.defaultMaxListeners = n;
    return this;
  }

  private static defaultMaxListeners = 10;
}

// Create a singleton instance
export const eventEmitter = new EventEmitter();

// Event names for 3D Models
export const MODEL_EVENTS = {
  GENERATED: 'model:generated',
  PROGRESS: 'model:progress',
  ERROR: 'model:error',
  EXPORTED: 'model:exported',
  DELETED: 'model:deleted',
  UPDATED: 'model:updated'
} as const;

// WebSocket events
export const WS_EVENTS = {
  CONNECTED: 'ws:connected',
  DISCONNECTED: 'ws:disconnected',
  MESSAGE: 'ws:message',
  ERROR: 'ws:error',
  RECONNECT: 'ws:reconnect'
} as const;

// Chat events
export const CHAT_EVENTS = {
  MESSAGE_RECEIVED: 'chat:message_received',
  MESSAGE_SENT: 'chat:message_sent',
  TYPING_START: 'chat:typing_start',
  TYPING_END: 'chat:typing_end',
  SPECIFICATIONS_EXTRACTED: 'chat:specifications_extracted'
} as const;