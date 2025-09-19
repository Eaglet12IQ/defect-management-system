import { ref, readonly } from 'vue';
import { api } from '../utils/api';

interface User {
  username: string;
  avatar?: string;
  role?: string;
}

const currentUser = ref<User | null>(null);
const isAuthenticated = ref(false);

function decodeJWT(token: string) {
  const payload = token.split('.')[1];
  const decoded = JSON.parse(atob(payload));
  return decoded;
}

function loadUserFromStorage() {
  const token = localStorage.getItem('access_token');
  if (token) {
    const decoded = decodeJWT(token);
    currentUser.value = {
      username: decoded.username,
      avatar: '',
      role: String(decoded.role),
    };
    isAuthenticated.value = true;
  }
}

export function useAuth() {
  loadUserFromStorage();

  const login = async (username: string, password: string): Promise<boolean | string> => {
    try {
      const response = await api.post('/auth/login', { username, password });
      if (response.error) {
        return response.error;
      }
      const { access_token, username: userName, avatar } = response.data;
      localStorage.setItem('access_token', access_token);
      const decoded = decodeJWT(access_token);
      currentUser.value = { username: userName, avatar, role: String(decoded.role) };
      isAuthenticated.value = true;
      return true;
    } catch (error) {
      return error instanceof Error ? error.message : 'Неизвестная ошибка';
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout', {});
    } catch {
      // ignore errors on logout
    }
    localStorage.removeItem('access_token');
    currentUser.value = null;
    isAuthenticated.value = false;
  };

  const getCurrentUser = () => currentUser.value;

  const hasRole = (role: string | string[]) => {
    if (!currentUser.value || !currentUser.value.role) return false;
    if (Array.isArray(role)) {
      return role.includes(currentUser.value.role);
    }
    return currentUser.value.role === role;
  };

  return {
    currentUser: readonly(currentUser),
    isAuthenticated: readonly(isAuthenticated),
    login,
    logout,
    getCurrentUser,
    hasRole,
  };
}
