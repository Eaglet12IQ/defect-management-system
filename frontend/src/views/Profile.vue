<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="mb-8 animate-fade-in">
        <h2 class="text-3xl font-bold text-white mb-2">Профиль</h2>
        <p class="text-white/80">Управление настройками аккаунта</p>
      </div>

      <!-- Profile Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Profile Info -->
        <div class="lg:col-span-1">
          <div class="glass rounded-2xl p-6 text-center animate-slide-up">
            <div class="relative inline-block mb-4">
              <img
                :src="currentUser?.avatar || 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2'"
                :alt="currentUser?.name"
                class="w-24 h-24 rounded-full mx-auto border-4 border-white/20"
              />
              <button class="absolute bottom-0 right-0 w-8 h-8 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-all duration-200 flex items-center justify-center hover:scale-110 transform">
                <PencilIcon class="w-4 h-4" />
              </button>
            </div>
            
            <h3 class="text-xl font-bold text-white mb-1">{{ currentUser?.name }}</h3>
            <p class="text-white/80 mb-2">{{ currentUser?.email }}</p>
            <span
              class="inline-block px-3 py-1 text-sm font-medium rounded-full capitalize"
              :class="getRoleClass(currentUser?.role)"
            >
              {{ getRoleText(currentUser?.role) }}
            </span>
            
            <div class="mt-6 pt-6 border-t border-white/20">
              <div class="flex justify-center space-x-4 text-sm text-white/80">
                <div class="text-center">
                  <div class="font-bold text-white">{{ userStats.assignedTasks }}</div>
                  <div>Назначено задач</div>
                </div>
                <div class="text-center">
                  <div class="font-bold text-white">{{ userStats.completedTasks }}</div>
                  <div>Выполнено</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="glass rounded-2xl p-6 mt-6 animate-slide-up-delay-1">
            <h4 class="text-lg font-semibold text-white mb-4">Статистика</h4>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-white/80">Эффективность</span>
                <div class="flex items-center space-x-2">
                  <div class="w-20 bg-gray-200 rounded-full h-2">
                    <div class="h-2 bg-green-500 rounded-full transition-all duration-1000 ease-out animate-progress" style="width: 85%"></div>
                  </div>
                  <span class="text-sm font-medium">85%</span>
                </div>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-white/80">Активность</span>
                <div class="flex items-center space-x-2">
                  <div class="w-20 bg-gray-200 rounded-full h-2">
                    <div class="h-2 bg-blue-500 rounded-full transition-all duration-1000 ease-out animate-progress" style="width: 92%"></div>
                  </div>
                  <span class="text-sm font-medium">92%</span>
                </div>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-white/80">Качество</span>
                <div class="flex items-center space-x-2">
                  <div class="w-20 bg-gray-200 rounded-full h-2">
                    <div class="h-2 bg-purple-500 rounded-full transition-all duration-1000 ease-out animate-progress" style="width: 78%"></div>
                  </div>
                  <span class="text-sm font-medium">78%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Settings -->
          <div class="glass rounded-2xl p-6 animate-slide-up-delay-2">
            <h4 class="text-lg font-semibold text-white mb-6">Настройки профиля</h4>
            
            <form class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Имя</label>
                  <input
                    v-model="profileForm.name"
                    type="text"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Email</label>
                  <input
                    v-model="profileForm.email"
                    type="email"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Отдел</label>
                  <input
                    v-model="profileForm.department"
                    type="text"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Телефон</label>
                  <input
                    v-model="profileForm.phone"
                    type="tel"
                    class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                  />
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-white/80 mb-2">О себе</label>
                <textarea
                  v-model="profileForm.bio"
                  rows="4"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 resize-none"
                  placeholder="Расскажите о себе..."
                ></textarea>
              </div>
              
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="bg-primary-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-primary-700 transition-all duration-200 transform hover:scale-105"
                >
                  Сохранить изменения
                </button>
              </div>
            </form>
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

const profileForm = reactive({
  name: currentUser.value?.name || '',
  email: currentUser.value?.email || '',
  department: currentUser.value?.department || '',
  phone: '+7 (999) 123-45-67',
  bio: 'Опытный специалист в области управления строительными проектами. Более 5 лет опыта в контроле качества и устранении дефектов.'
});

const userStats = reactive({
  assignedTasks: 15,
  completedTasks: 28
});

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