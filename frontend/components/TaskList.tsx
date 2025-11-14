import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Task {
  id: string;
  title: string;
  completed: boolean;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

const TaskList: React.FC = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await api.get('/tasks', {
          headers: { Authorization: `Bearer ${user.token}` }
        });
        setTasks(response.data);
      } catch (err) {
        setError('Failed to load tasks. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, [user.token]);

  const toggleTaskCompletion = async (taskId: string) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;
      const updatedTask = { ...task, completed: !task.completed };
      await api.put(`/tasks/${taskId}`, updatedTask, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setTasks(prevTasks => prevTasks.map(t => (t.id === taskId ? updatedTask : t)));
    } catch (err) {
      Alert.alert('Error', 'Failed to update task. Please try again.');
    }
  };

  const deleteTask = async (taskId: string) => {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this task?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.delete(`/tasks/${taskId}`, {
                headers: { Authorization: `Bearer ${user.token}` }
              });
              setTasks(prevTasks => prevTasks.filter(t => t.id !== taskId));
            } catch (err) {
              Alert.alert('Error', 'Failed to delete task. Please try again.');
            }
          }
        }
      ]
    );
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text className="text-red-500">{error}</Text>;
  }

  return (
    <View className="flex-1 p-4 bg-gray-100">
      <FlatList
        data={tasks}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View className="flex-row justify-between items-center p-4 mb-2 bg-white shadow-md rounded-md">
            <Text className={`flex-1 ${item.completed ? 'line-through text-gray-500' : 'text-black'}`}>
              {item.title}
            </Text>
            <TouchableOpacity
              onPress={() => toggleTaskCompletion(item.id)}
              className="p-2 bg-blue-500 rounded-full"
              accessibilityLabel={`Mark task as ${item.completed ? 'incomplete' : 'complete'}`}
            >
              <Text className="text-white">{item.completed ? 'Undo' : 'Complete'}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => deleteTask(item.id)}
              className="p-2 bg-red-500 rounded-full ml-2"
              accessibilityLabel="Delete task"
            >
              <Text className="text-white">Delete</Text>
            </TouchableOpacity>
          </View>
        )}
        ListEmptyComponent={<Text className="text-center text-gray-500">No tasks available</Text>}
      />
    </View>
  );
};

export default TaskList;