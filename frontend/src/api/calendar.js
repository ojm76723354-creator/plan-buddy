import { api } from './auth';

export const getEvents = async () => {
  const response = await api.get('/calendar/');
  return response.data;
};

export const createEvent = async (eventData) => {
  const response = await api.post('/calendar/', eventData);
  return response.data;
};

export const getFriendEvents = async (username) => {
  const response = await api.get(`/calendar/friends/${username}`);
  return response.data;
};
