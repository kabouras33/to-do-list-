import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

interface WebSocketHook {
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: string) => void;
  isConnected: boolean;
  error: string | null;
}

const useWebSocket = (url: string): WebSocketHook => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };
      ws.onmessage = (event) => {
        console.log('Message received:', event.data);
      };
      ws.onerror = (err) => {
        setError('WebSocket error');
        console.error('WebSocket error:', err);
      };
      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket closed');
      };
      setSocket(ws);
    } catch (err) {
      setError('Failed to connect to WebSocket');
      console.error('Connection error:', err);
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (socket) {
      socket.close();
      setSocket(null);
    }
  }, [socket]);

  const sendMessage = useCallback((message: string) => {
    if (socket && isConnected) {
      socket.send(message);
    } else {
      setError('Cannot send message, WebSocket is not connected');
    }
  }, [socket, isConnected]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { connect, disconnect, sendMessage, isConnected, error };
};

export default useWebSocket;