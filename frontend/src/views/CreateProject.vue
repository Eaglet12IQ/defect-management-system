<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />

    <main class="container-responsive py-8 flex items-center justify-center min-h-[calc(100vh-200px)]">
      <div class="w-full max-w-2xl animate-fade-in">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-center space-x-4 mb-4">
            <router-link
              to="/projects"
              class="text-white/80 hover:text-white transition-colors duration-200 flex items-center space-x-2"
            >
              <ArrowLeftIcon class="w-5 h-5" />
              <span>Назад к проектам</span>
            </router-link>
          </div>
          <div class="text-center">
            <h2 class="text-3xl font-bold text-white mb-2">Создание нового проекта</h2>
            <p class="text-white/80">Заполните информацию о строительном объекте</p>
          </div>
        </div>

        <!-- Create Project Form -->
        <div class="glass rounded-2xl p-8 animate-slide-up">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Project Name -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Название проекта *
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                placeholder="Введите название проекта"
                :class="{ 'border-red-300 focus:ring-red-500': errors.name }"
              />
              <p v-if="errors.name" class="mt-1 text-sm text-red-400">{{ errors.name }}</p>
            </div>

            <!-- Project Description -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Описание проекта *
              </label>
              <textarea
                v-model="form.description"
                rows="4"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 resize-none"
                placeholder="Опишите проект, его цели и особенности"
                :class="{ 'border-red-300 focus:ring-red-500': errors.description }"
              ></textarea>
              <p v-if="errors.description" class="mt-1 text-sm text-red-400">{{ errors.description }}</p>
            </div>

            <!-- Manager Selection -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Менеджер проекта *
              </label>
              <select
                v-model="form.manager_id"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 appearance-none"
                :class="{ 'border-red-300 focus:ring-red-500': errors.manager_id }"
              >
                <option value="" disabled>Выберите менеджера проекта</option>
                <option
                  v-for="manager in availableManagers"
                  :key="manager.id"
                  :value="manager.id"
                >
                  {{ manager.first_name }} {{ manager.last_name }} ({{ manager.username }})
                </option>
              </select>
              <p v-if="errors.manager_id" class="mt-1 text-sm text-red-400">{{ errors.manager_id }}</p>
            </div>

            <!-- Project Status -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Статус проекта *
              </label>
              <select
                v-model="form.status"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 appearance-none"
                :class="{ 'border-red-300 focus:ring-red-500': errors.status }"
              >
                <option value="" disabled>Выберите статус проекта</option>
                <option value="Планирование">Планирование</option>
                <option value="Активный">Активный</option>
                <option value="Завершен">Завершен</option>
                <option value="Приостановлен">Приостановлен</option>
              </select>
              <p v-if="errors.status" class="mt-1 text-sm text-red-400">{{ errors.status }}</p>
            </div>

            <!-- Form Actions -->
            <div class="flex flex-col sm:flex-row sm:justify-end space-y-3 sm:space-y-0 sm:space-x-4 pt-6">
              <router-link
                to="/projects"
                class="px-6 py-3 text-white/80 hover:text-white border border-white/30 rounded-xl font-medium transition-all duration-200 hover:bg-white/10 text-center"
              >
                Отмена
              </router-link>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="bg-primary-600 text-white px-8 py-3 rounded-xl font-medium hover:bg-primary-700 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
              >
                <span v-if="!isSubmitting">Создать проект</span>
                <div v-else class="flex items-center">
                  <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Создание...
                </div>
              </button>
            </div>
          </form>

          <!-- Success/Error Messages -->
          <div
            v-if="successMessage"
            class="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ successMessage }}
          </div>
          <div
            v-if="errorMessage"
            class="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ errorMessage }}
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../utils/api';
import TheHeader from '../components/TheHeader.vue';
import { ArrowLeftIcon } from '@heroicons/vue/24/outline';

const router = useRouter();

interface Manager {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  role: number;
}

const form = reactive({
  name: '',
  description: '',
  manager_id: '',
  status: 'Планирование'
});

const errors = reactive({
  name: '',
  description: '',
  manager_id: '',
  status: ''
});

const availableManagers = ref<Manager[]>([]);
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

// Load available managers on component mount
onMounted(async () => {
  try {
    const response = await api.get('/managers');
    if (response.data) {
      availableManagers.value = response.data;
    }
  } catch (error) {
    console.error('Error loading managers:', error);
    errorMessage.value = 'Ошибка при загрузке списка руководителей';
  }
});

const validateForm = () => {
  errors.name = '';
  errors.description = '';
  errors.manager_id = '';

  let isValid = true;

  if (!form.name.trim()) {
    errors.name = 'Название проекта обязательно для заполнения';
    isValid = false;
  } else if (form.name.trim().length < 3) {
    errors.name = 'Название проекта должно содержать минимум 3 символа';
    isValid = false;
  }

  if (!form.description.trim()) {
    errors.description = 'Описание проекта обязательно для заполнения';
    isValid = false;
  } else if (form.description.trim().length < 10) {
    errors.description = 'Описание проекта должно содержать минимум 10 символов';
    isValid = false;
  }

  if (!form.manager_id) {
    errors.manager_id = 'Выберите руководителя проекта';
    isValid = false;
  }

  return isValid;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const projectData = {
      name: form.name.trim(),
      description: form.description.trim(),
      manager_id: parseInt(form.manager_id),
      status: form.status
    };

    const response = await api.post('/create_project', projectData);

    if (response.error) {
      errorMessage.value = response.error;
    } else {
      successMessage.value = 'Проект успешно создан!';
      // Reset form
      form.name = '';
      form.description = '';
      form.manager_id = '';

      // Redirect to projects page after a short delay
      setTimeout(() => {
        router.push('/projects');
      }, 1500);
    }
  } catch (error: any) {
    console.error('Error creating project:', error);
    errorMessage.value = error.response?.data?.detail || 'Ошибка при создании проекта';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container-responsive {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

select option:first-child {
  color: #9ca3af;
}
</style>
