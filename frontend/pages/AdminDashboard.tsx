import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, FlatList, Alert, ActivityIndicator } from 'react-native';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://ai-codepeak.com/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

interface User {
  id: string;
  name: string;
  email: string;
}

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    fetchUsers();
  }, [currentPage]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/users?page=${currentPage}&query=${searchQuery}`);
      setUsers(response.data.users);
      setTotalPages(response.data.totalPages);
      setError(null);
    } catch (err) {
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchUsers();
  };

  const handleDelete = async (userId: string) => {
    try {
      await api.delete(`/users/${userId}`);
      Alert.alert('Success', 'User deleted successfully');
      fetchUsers();
    } catch {
      Alert.alert('Error', 'Failed to delete user. Please try again.');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <View className="p-4 bg-gray-100 min-h-screen">
      <View className="flex flex-row justify-between items-center mb-4">
        <Text className="text-2xl font-bold">Admin Dashboard</Text>
        <Button title="Logout" onPress={handleLogout} />
      </View>
      <View className="mb-4">
        <TextInput
          placeholder="Search users..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          className="border p-2 rounded"
        />
        <Button title="Search" onPress={handleSearch} />
      </View>
      {loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : error ? (
        <Text className="text-red-500">{error}</Text>
      ) : (
        <FlatList
          data={users}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View className="bg-white p-4 mb-2 rounded shadow">
              <Text className="text-lg font-semibold">{item.name}</Text>
              <Text className="text-gray-600">{item.email}</Text>
              <Button title="Delete" onPress={() => handleDelete(item.id)} />
            </View>
          )}
          ListEmptyComponent={<Text className="text-center text-gray-500">No users found.</Text>}
        />
      )}
      <View className="flex flex-row justify-between mt-4">
        <Button
          title="Previous"
          disabled={currentPage === 1}
          onPress={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
        />
        <Text>{`Page ${currentPage} of ${totalPages}`}</Text>
        <Button
          title="Next"
          disabled={currentPage === totalPages}
          onPress={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
        />
      </View>
    </View>
  );
};

export default AdminDashboard;