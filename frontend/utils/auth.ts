import axios from 'axios';
import jwtDecode from 'jwt-decode';

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

interface DecodedToken {
  exp: number;
  iat: number;
  sub: string;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export const login = async (username: string, password: string): Promise<AuthTokens> => {
  try {
    const response = await api.post<AuthTokens>('/auth/login', { username, password });
    return response.data;
  } catch (error) {
    throw new Error('Failed to login. Please check your credentials and try again.');
  }
};

export const refreshAccessToken = async (refreshToken: string): Promise<string> => {
  try {
    const response = await api.post<{ accessToken: string }>('/auth/refresh', { refreshToken });
    return response.data.accessToken;
  } catch (error) {
    throw new Error('Failed to refresh access token. Please login again.');
  }
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded: DecodedToken = jwtDecode(token);
    return decoded.exp * 1000 < Date.now();
  } catch (error) {
    throw new Error('Invalid token. Please login again.');
  }
};

export const logout = async (): Promise<void> => {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    throw new Error('Failed to logout. Please try again.');
  }
};

export const getAuthHeaders = (accessToken: string): { Authorization: string } => {
  return { Authorization: `Bearer ${accessToken}` };
};