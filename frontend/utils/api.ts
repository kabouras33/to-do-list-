import axios, { AxiosInstance, AxiosResponse } from 'axios';

interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

interface Task {
  id: string;
  title: string;
  completed: boolean;
}

interface User {
  id: string;
  name: string;
  email: string;
}

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

export const fetchTasks = async (): Promise<Task[]> => {
  try {
    const response: AxiosResponse<ApiResponse<Task[]>> = await api.get('/tasks');
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw new Error('Failed to fetch tasks. Please try again later.');
  }
};

export const createTask = async (title: string): Promise<Task> => {
  if (!title.trim()) {
    throw new Error('Task title cannot be empty.');
  }
  try {
    const response: AxiosResponse<ApiResponse<Task>> = await api.post('/tasks', { title });
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('Error creating task:', error);
    throw new Error('Failed to create task. Please try again later.');
  }
};

export const updateTask = async (taskId: string, completed: boolean): Promise<Task> => {
  try {
    const response: AxiosResponse<ApiResponse<Task>> = await api.put(`/tasks/${taskId}`, { completed });
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('Error updating task:', error);
    throw new Error('Failed to update task. Please try again later.');
  }
};

export const deleteTask = async (taskId: string): Promise<void> => {
  try {
    const response: AxiosResponse<ApiResponse<null>> = await api.delete(`/tasks/${taskId}`);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('Error deleting task:', error);
    throw new Error('Failed to delete task. Please try again later.');
  }
};

export const fetchUser = async (): Promise<User> => {
  try {
    const response: AxiosResponse<ApiResponse<User>> = await api.get('/user');
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('Error fetching user:', error);
    throw new Error('Failed to fetch user. Please try again later.');
  }
};