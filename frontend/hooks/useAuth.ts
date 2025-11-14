import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

interface User {
  id: string;
  name: string;
  email: string;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

const useAuth = () => {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: false,
    error: null
  });

  const { user, login, logout } = useAuth();

  const authenticate = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await api.post('/auth/login', { email, password });
      const userData: User = response.data;
      login(userData);
      setState({ user: userData, loading: false, error: null });
    } catch (error) {
      setState({
        user: null,
        loading: false,
        error: error.response?.data?.message || 'Authentication failed'
      });
    }
  }, [login]);

  const signOut = useCallback(() => {
    logout();
    setState({ user: null, loading: false, error: null });
  }, [logout]);

  useEffect(() => {
    const fetchUser = async () => {
      setState(prev => ({ ...prev, loading: true }));
      try {
        const response = await api.get('/auth/me');
        setState({ user: response.data, loading: false, error: null });
      } catch {
        setState({ user: null, loading: false, error: 'Failed to fetch user' });
      }
    };
    fetchUser();
  }, []);

  return {
    user: state.user,
    loading: state.loading,
    error: state.error,
    authenticate,
    signOut
  };
};

export default useAuth;