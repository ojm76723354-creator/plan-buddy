import { api } from './auth';

export const getFriends = async () => {
  const response = await api.get('/friends/list');
  return response.data;
};

export const requestFriend = async (targetUsername) => {
  const response = await api.post('/friends/request', { target_username: targetUsername });
  return response.data;
};

export const acceptFriend = async (friendshipId) => {
  const response = await api.post(`/friends/${friendshipId}/accept`);
  return response.data;
};
