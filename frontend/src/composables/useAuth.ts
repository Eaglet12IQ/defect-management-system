import { ref, reactive } from 'vue';
import { readonly } from 'vue';
import { mockUsers, type User } from '../data/mockData';

const currentUser = ref<User | null>(mockUsers[0]);
const isAuthenticated = ref(true);

export function useAuth() {
  const login = async (email: string, password: string): Promise<boolean> => {
    // Имитация запроса к API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const user = mockUsers.find(u => u.email === email);
    if (user && password === 'password') {
      currentUser.value = user;
      isAuthenticated.value = true;
      return true;
    }
    
    return false;
  };

  const logout = () => {
    currentUser.value = null;
    isAuthenticated.value = false;
  };

  const getCurrentUser = () => currentUser.value;
  
  const hasRole = (role: string | string[]) => {
    if (!currentUser.value) return false;
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
    hasRole
  };
}