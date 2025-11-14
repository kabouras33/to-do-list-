import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, FlatList, ActivityIndicator, Alert, TouchableOpacity } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { useNavigation } from 'react-router-dom';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

interface Task {
  id: string;
  title: string;
  completed: boolean;
}

const App: React.FC = () => {
  const { user, login, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigation = useNavigation();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks');
        setTasks(response.data);
      } catch (err) {
        setError('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, []);

  const handleAddTask = async () => {
    if (!newTaskTitle.trim()) {
      Alert.alert('Validation Error', 'Task title cannot be empty');
      return;
    }
    try {
      const response = await api.post('/tasks', { title: newTaskTitle });
      setTasks([...tasks, response.data]);
      setNewTaskTitle('');
    } catch (err) {
      setError('Failed to add task');
    }
  };

  const handleToggleTask = async (taskId: string) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (task) {
        const response = await api.patch(`/tasks/${taskId}`, { completed: !task.completed });
        setTasks(tasks.map(t => t.id === taskId ? response.data : t));
      }
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    Alert.alert('Confirm Delete', 'Are you sure you want to delete this task?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await api.delete(`/tasks/${taskId}`);
            setTasks(tasks.filter(t => t.id !== taskId));
          } catch (err) {
            setError('Failed to delete task');
          }
        }
      }
    ]);
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text style={{ color: 'red' }}>{error}</Text>;
  }

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>To-Do List</Text>
      <TextInput
        placeholder="New Task"
        value={newTaskTitle}
        onChangeText={setNewTaskTitle}
        style={{ borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 10 }}
      />
      <Button title="Add Task" onPress={handleAddTask} />
      <FlatList
        data={tasks}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View style={{ flexDirection: 'row', alignItems: 'center', marginVertical: 10 }}>
            <TouchableOpacity onPress={() => handleToggleTask(item.id)}>
              <Text style={{ textDecorationLine: item.completed ? 'line-through' : 'none' }}>{item.title}</Text>
            </TouchableOpacity>
            <Button title="Delete" color="red" onPress={() => handleDeleteTask(item.id)} />
          </View>
        )}
      />
      <Button title="Logout" onPress={logout} />
    </View>
  );
};

export default App;