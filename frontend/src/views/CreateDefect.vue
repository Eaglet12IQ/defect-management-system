<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />

    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8 animate-fade-in">
        <div>
          <h2 class="text-3xl font-bold text-white mb-2">Создание дефекта</h2>
          <p class="text-white/80">Создайте новый дефект для строительного объекта</p>
        </div>

        <button
          @click="$router.push('/defects')"
          class="bg-white/10 text-white px-6 py-3 rounded-xl font-medium hover:bg-white/20 transition-all duration-200 backdrop-blur"
        >
          <ArrowLeftIcon class="w-5 h-5 inline-block mr-2" />
          Назад к дефектам
        </button>
      </div>

      <!-- Form -->
      <div class="glass rounded-2xl p-8 animate-slide-up">
        <form @submit.prevent="submitForm" class="space-y-6">
          <!-- Title -->
          <div>
            <label for="title" class="block text-sm font-medium text-white mb-2">
              Название дефекта <span class="text-red-400">*</span>
            </label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              class="w-full px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              placeholder="Введите название дефекта"
            />
            <p v-if="errors.title" class="mt-1 text-sm text-red-400">{{ errors.title }}</p>
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-white mb-2">
              Описание дефекта <span class="text-red-400">*</span>
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="4"
              required
              class="w-full px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 resize-none"
              placeholder="Подробно опишите дефект"
            ></textarea>
            <p v-if="errors.description" class="mt-1 text-sm text-red-400">{{ errors.description }}</p>
          </div>

          <!-- Project and Priority Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Project -->
            <div>
              <label for="project" class="block text-sm font-medium text-white mb-2">
                Проект <span class="text-red-400">*</span>
              </label>
              <select
                id="project"
                v-model="form.project_id"
                required
                class="w-full px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              >
                <option value="">Выберите проект</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
              <p v-if="errors.project_id" class="mt-1 text-sm text-red-400">{{ errors.project_id }}</p>
            </div>

            <!-- Priority -->
            <div>
              <label for="priority" class="block text-sm font-medium text-white mb-2">
                Приоритет <span class="text-red-400">*</span>
              </label>
              <select
                id="priority"
                v-model="form.priority"
                required
                class="w-full px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              >
                <option value="">Выберите приоритет</option>
                <option value="Низкий">Низкий</option>
                <option value="Средний">Средний</option>
                <option value="Высокий">Высокий</option>
                <option value="Критический">Критический</option>
              </select>
              <p v-if="errors.priority" class="mt-1 text-sm text-red-400">{{ errors.priority }}</p>
            </div>
          </div>



          <!-- Attachments -->
          <div>
            <label for="attachments" class="block text-sm font-medium text-white mb-2">
              Вложения
            </label>
            <input
              id="attachments"
              ref="fileInput"
              type="file"
              multiple
              accept="image/*,.pdf,.doc,.docx"
              class="w-full px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-500 file:text-white hover:file:bg-primary-600"
            />
            <p class="mt-1 text-sm text-white/60">
              Поддерживаются изображения, PDF и документы Word
            </p>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end space-x-4 pt-6">
            <button
              type="button"
              @click="$router.push('/defects')"
              class="px-6 py-3 border border-white/20 rounded-xl text-white font-medium hover:bg-white/10 transition-all duration-200 backdrop-blur"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-8 py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <span v-if="isSubmitting" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Создание...
              </span>
              <span v-else>Создать дефект</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" :class="messageType === 'success' ? 'bg-green-500/20 border-green-500' : 'bg-red-500/20 border-red-500'" class="mt-6 border rounded-xl p-4 animate-slide-up">
        <div class="flex items-center">
          <CheckCircleIcon v-if="messageType === 'success'" class="w-5 h-5 text-green-400 mr-3" />
          <XCircleIcon v-else class="w-5 h-5 text-red-400 mr-3" />
          <p :class="messageType === 'success' ? 'text-green-100' : 'text-red-100'">{{ message }}</p>
          <button @click="message = ''" class="ml-auto text-white/60 hover:text-white">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import TheHeader from '../components/TheHeader.vue';
import { api } from '../utils/api';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline';

const router = useRouter();
const fileInput = ref<HTMLInputElement>();

// Form data
const form = ref({
  title: '',
  description: '',
  priority: '',
  project_id: ''
});

// Form validation
const errors = ref({
  title: '',
  description: '',
  priority: '',
  project_id: ''
});

// UI state
const isSubmitting = ref(false);
const message = ref('');
const messageType = ref<'success' | 'error'>('success');
const projects = ref<any[]>([]);

// Load projects on mount
onMounted(async () => {
  try {
    const response = await api.get('/projects_for_defect');
    projects.value = response.data;
  } catch (error) {
    console.error('Error loading projects:', error);
    message.value = 'Ошибка загрузки проектов';
    messageType.value = 'error';
  }
});

// Form validation
const validateForm = () => {
  let isValid = true;
  errors.value = {
    title: '',
    description: '',
    priority: '',
    project_id: ''
  };

  // Title validation
  if (!form.value.title.trim()) {
    errors.value.title = 'Название дефекта обязательно';
    isValid = false;
  } else if (form.value.title.length < 3) {
    errors.value.title = 'Название должно содержать минимум 3 символа';
    isValid = false;
  }

  // Description validation
  if (!form.value.description.trim()) {
    errors.value.description = 'Описание дефекта обязательно';
    isValid = false;
  } else if (form.value.description.length < 10) {
    errors.value.description = 'Описание должно содержать минимум 10 символов';
    isValid = false;
  }

  // Priority validation
  if (!form.value.priority) {
    errors.value.priority = 'Выберите приоритет';
    isValid = false;
  }

  // Project validation
  if (!form.value.project_id) {
    errors.value.project_id = 'Выберите проект';
    isValid = false;
  }

  return isValid;
};

// Form submission
const submitForm = async () => {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;
  message.value = '';

  try {
    const formData = new FormData();

    // Add form fields
    formData.append('title', form.value.title);
    formData.append('description', form.value.description);
    formData.append('priority', form.value.priority);
    formData.append('project_id', form.value.project_id);

    // Add files if any
    if (fileInput.value?.files) {
      for (let i = 0; i < fileInput.value.files.length; i++) {
        formData.append('attachments', fileInput.value.files[i]);
      }
    }

    const response = await api.post('/create_defect', formData);

    message.value = response.data.message;
    messageType.value = 'success';

    // Redirect to defects page after 2 seconds
    setTimeout(() => {
      router.push('/defects');
    }, 2000);

  } catch (error: any) {
    console.error('Error creating defect:', error);
    message.value = error.response?.data?.detail || 'Ошибка при создании дефекта';
    messageType.value = 'error';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
