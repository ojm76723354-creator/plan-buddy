import { api } from './auth';

export const getMe = async () => {
    const response = await api.get('/mypage/me');
    return response.data;
};

export const uploadProfileImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/mypage/upload-profile', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return response.data;
};

export const updateUsername = async (newUsername) => {
    const response = await api.put('/mypage/update-username', { new_username: newUsername });
    return response.data;
};

export const updatePassword = async (oldPassword, newPassword) => {
    const response = await api.put('/mypage/update-password', {
        old_password: oldPassword,
        new_password: newPassword
    });
    return response.data;
};
