<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />

    <main class="container-responsive py-8">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="flex items-center space-x-3 text-white">
          <div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Загрузка дефекта...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 animate-fade-in">
        <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Ошибка загрузки</h3>
        <p class="text-white/70 mb-6">{{ error }}</p>
        <button
          @click="loadDefect"
          class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Defect Content -->
      <div v-else-if="defect" class="animate-fade-in">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <div class="flex items-center space-x-3 mb-2">
              <button
                @click="goBack"
                class="text-white/80 hover:text-white transition-colors duration-200"
              >
                <ArrowLeftIcon class="w-5 h-5" />
              </button>
              <h2 class="text-3xl font-bold text-white">{{ defect.title }}</h2>
            </div>
            <p class="text-white/80">Подробная информация о дефекте</p>
          </div>

          <div class="flex space-x-3 mt-4 sm:mt-0">
            <button
              @click="editDefect"
              class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center"
            >
              <PencilIcon class="w-5 h-5 mr-2" />
              Редактировать
            </button>
          </div>
        </div>

        <!-- Defect Card -->
        <div class="glass rounded-2xl p-8 animate-slide-up">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Left Column -->
            <div>
              <h3 class="text-xl font-semibold text-white mb-4">Основная информация</h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Название</label>
                  <p class="text-white text-lg">{{ defect.title }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Описание</label>
                  <p class="text-white">{{ defect.description }}</p>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-white/80 mb-2">Статус</label>
                    <span
                      class="px-3 py-1 text-sm font-medium rounded-full border inline-block"
                      :class="getStatusClass(defect.status)"
                    >
                      {{ getStatusText(defect.status) }}
                    </span>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-white/80 mb-2">Приоритет</label>
                    <span
                      class="px-3 py-1 text-sm font-medium rounded-full border inline-block"
                      :class="getPriorityClass(defect.priority)"
                    >
                      {{ getPriorityText(defect.priority) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Column -->
            <div>
              <h3 class="text-xl font-semibold text-white mb-4">Дополнительная информация</h3>

              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Исполнитель</label>
                  <p class="text-white">{{ defect.assignee || 'Не назначен' }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Проект</label>
                  <p class="text-white">{{ defect.project_name || 'Не указан' }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Создатель</label>
                  <p class="text-white">{{ defect.creator_name || 'Неизвестно' }}</p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-white/80 mb-2">Срок выполнения</label>
                  <p class="text-white" :class="{ 'text-red-400': isOverdue(defect.due_date) }">
                    {{ formatDate(defect.due_date) }}
                  </p>
                </div>

                <div v-if="defect.attachments && defect.attachments.length > 0">
                  <label class="block text-sm font-medium text-white/80 mb-2">Вложения</label>
                  <div class="flex items-center space-x-2">
                    <PaperClipIcon class="w-5 h-5 text-white/60" />
                    <span class="text-white">{{ defect.attachments.length }} файлов</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TheHeader from '../components/TheHeader.vue';
import { api } from '../utils/api';
import {
  ArrowLeftIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  PaperClipIcon
} from '@heroicons/vue/24/outline';

const route = useRoute();
const router = useRouter();
const defect = ref<any>(null);
const isLoading = ref(true);
const error = ref('');

const defectId = route.params.id as string;

const loadDefect = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    const response = await api.get(`/defects/${defectId}`);
    defect.value = response.data;
  } catch (err: any) {
    console.error('Error loading defect:', err);
    error.value = 'Ошибка при загрузке дефекта';
  } finally {
    isLoading.value = false;
  }
};

const editDefect = () => {
  router.push(`/defects/${defectId}/edit`);
};

const goBack = () => {
  router.push('/defects');
};

const getStatusClass = (status: string) => {
  const classes = {
    'Новый': 'bg-blue-100 text-blue-800 border-blue-200',
    'В работе': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'На проверке': 'bg-purple-100 text-purple-800 border-purple-200',
    'Закрыт': 'bg-green-100 text-green-800 border-green-200',
    'Отменен': 'bg-red-100 text-red-800 border-red-200'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800 border-gray-200';
};

const getPriorityClass = (priority: string) => {
  const classes = {
    'Низкий': 'bg-green-100 text-green-800 border-green-200',
    'Средний': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'Высокий': 'bg-red-100 text-red-800 border-red-200',
    'Критический': 'bg-red-200 text-red-900 border-red-300'
  };
  return classes[priority as keyof typeof classes] || 'bg-gray-100 text-gray-800 border-gray-200';
};

const getStatusText = (status: string) => {
  const texts = {
    'Новый': 'Новый',
    'В работе': 'В работе',
    'На проверке': 'На проверке',
    'Закрыт': 'Закрыт',
    'Отменен': 'Отменен'
  };
  return texts[status as keyof typeof texts] || 'Неизвестно';
};

const getPriorityText = (priority: string) => {
  const texts = {
    'Низкий': 'Низкий',
    'Средний': 'Средний',
    'Высокий': 'Высокий',
    'Критический': 'Критический'
  };
  return texts[priority as keyof typeof texts] || 'Средний';
};

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Не указан';

  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const isOverdue = (dateString?: string) => {
  if (!dateString) return false;
  return new Date(dateString) < new Date();
};

onMounted(() => {
  loadDefect();
});
</script>
