<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="mb-8 animate-fade-in">
        <h2 class="text-3xl font-bold text-white mb-2">Профиль</h2>
      </div>

      <!-- Profile Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Profile Info -->
        <div class="lg:col-span-1">
          <div class="glass rounded-2xl p-6 text-center animate-slide-up">
            <div class="relative inline-block mb-4">
              <img
                :src="currentUser?.avatar || 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2'"
                :alt="currentUser?.username"
                class="w-24 h-24 rounded-full mx-auto border-4 border-white/20"
              />
              <button class="absolute bottom-0 right-0 w-8 h-8 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-all duration-200 flex items-center justify-center hover:scale-110 transform">
                <PencilIcon class="w-4 h-4" />
              </button>
            </div>
            
            <h3 class="text-xl font-bold text-white mb-1">{{ currentUser?.username }}</h3>
            <p class="text-white/80 mb-2">{{ currentUser?.email }}</p>
            <span
              class="inline-block px-3 py-1 text-sm font-medium rounded-full capitalize"
              :class="getRoleClass(currentUser?.role)"
            >
              {{ getRoleText(currentUser?.role) }}
            </span>
          </div>


        </div>


      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useAuth } from '../composables/useAuth';
import TheHeader from '../components/TheHeader.vue';
import { PencilIcon } from '@heroicons/vue/24/outline';

const { currentUser } = useAuth();

const getRoleClass = (role?: string) => {
  const classes = {
    'admin': 'bg-red-100 text-red-800',
    'manager': 'bg-blue-100 text-blue-800',
    'engineer': 'bg-green-100 text-green-800',
    'observer': 'bg-yellow-100 text-yellow-800'
  };
  return classes[role as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

const getRoleText = (role?: string) => {
  const texts = {
    'admin': 'Администратор',
    'manager': 'Менеджер',
    'engineer': 'Инженер',
    'observer': 'Наблюдатель'
  };
  return texts[role as keyof typeof texts] || 'Пользователь';
};
</script>