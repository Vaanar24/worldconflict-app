import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private eventHandlers: ((event: any) => void)[] = [];

  connect() {
    if (this.socket?.connected) return;

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const baseURL = API_URL.replace('/api/v1', '');
    
    console.log('WebSocket connecting to:', baseURL);
    
    this.socket = io(baseURL, {
      path: '/api/v1/events/ws',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 10,
      withCredentials: false
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected successfully');
    });

    this.socket.on('event', (event: any) => {
      console.log('New event received via WebSocket:', event);
      this.eventHandlers.forEach(handler => handler(event));
    });

    this.socket.on('connect_error', (error) => {
      console.log('WebSocket connection error:', error.message);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  onEvent(handler: (event: any) => void) {
    this.eventHandlers.push(handler);
    return () => {
      this.eventHandlers = this.eventHandlers.filter(h => h !== handler);
    };
  }

  isConnected() {
    return this.socket?.connected || false;
  }
}

export const websocketService = new WebSocketService();