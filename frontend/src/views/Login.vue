<template>
  <div class="min-h-screen gradient-bg flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8 animate-fade-in">
        <div class="w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center mx-auto mb-4">
          <BuildingOfficeIcon class="w-8 h-8 text-primary-600" />
        </div>
        <h1 class="text-2xl font-bold text-white">СистемаКонтроля</h1>
        <p class="text-white/80 mt-2">Управление дефектами строительных объектов</p>
      </div>

      <!-- Login Form -->
      <div class="glass rounded-2xl p-8 animate-slide-up">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-white/80 mb-2">
              Email или Username
            </label>
            <input
              v-model="username"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
              placeholder="email@example.com или username"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-white/80 mb-2">
              Пароль
            </label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-xl font-medium hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 hover:shadow-lg"
          >
            <span v-if="!isLoading">Войти</span>
            <div v-else class="flex items-center justify-center">
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Вход...
            </div>
          </button>

          <!-- Error Message -->
          <div
            v-if="error"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ error }}
          </div>
        </form>
      </div>


    </div>

    <!-- Background Animation -->
    <div class="fixed inset-0 -z-10 overflow-hidden">
      <div class="absolute -inset-10 opacity-20">
        <div class="absolute top-1/4 left-1/4 w-72 h-72 bg-white rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
        <div class="absolute top-1/3 right-1/4 w-72 h-72 bg-yellow-200 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import { BuildingOfficeIcon } from '@heroicons/vue/24/outline';

const router = useRouter();
const { login } = useAuth();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

const handleLogin = async () => {
  isLoading.value = true;
  error.value = '';

  try {
    const result = await login(username.value, password.value);

    if (result === true) {
      router.push('/');
    } else {
      error.value = typeof result === 'string' ? result : 'Произошла ошибка при входе';
    }
  } catch (err) {
    error.value = 'Произошла ошибка при входе';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
@keyframes blob {
  0%, 100% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

</style>