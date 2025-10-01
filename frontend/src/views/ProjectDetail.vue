<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />

    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <div class="flex items-center space-x-3 mb-2">
            <router-link
              to="/projects"
              class="text-white/80 hover:text-white transition-colors duration-200"
            >
              <ArrowLeftIcon class="w-5 h-5" />
            </router-link>
            <h2 class="text-3xl font-bold text-white">{{ project?.name }}</h2>
          </div>
          <p class="text-white/80">Подробная информация о проекте</p>
        </div>

        <div class="flex space-x-3 mt-4 sm:mt-0">
          <button
            v-if="canEditProject"
            @click="navigateToEdit"
            class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center"
          >
            <PencilIcon class="w-5 h-5 mr-2" />
            Редактировать
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="flex items-center space-x-3 text-white">
          <div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Загрузка данных проекта...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="loadError" class="text-center py-12 animate-fade-in">
        <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Ошибка загрузки</h3>
        <p class="text-white/70 mb-6">{{ loadError }}</p>
        <router-link
          to="/projects"
          class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          Вернуться к проектам
        </router-link>
      </div>

      <!-- Project Details -->
      <div v-else-if="project" class="glass rounded-2xl p-8 animate-slide-up">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Left Column -->
          <div class="space-y-6">
            <div>
              <h3 class="text-xl font-semibold text-white mb-4">Основная информация</h3>
              <div class="space-y-4">
                <div class="flex justify-between">
                  <span class="text-white/80">Название:</span>
                  <span class="text-white font-medium">{{ project.name }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-white/80">Статус:</span>
                  <span
                    class="px-3 py-1 text-sm font-medium rounded-full border"
                    :class="getProjectStatusClass(project.status)"
                  >
                    {{ getProjectStatusText(project.status) }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-white/80">Менеджер:</span>
                  <span class="text-white font-medium">{{ project.manager_name }}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 class="text-xl font-semibold text-white mb-4">Описание</h3>
              <p class="text-white/80 leading-relaxed">{{ project.description }}</p>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-6">
            <div>
              <h3 class="text-xl font-semibold text-white mb-4">Дефекты проекта</h3>
              <div class="glass-inner rounded-xl p-4">
                <div v-if="defects.length === 0" class="text-white/80 text-center">
                  Дефекты для этого проекта пока не созданы
                </div>
                <div v-else class="space-y-3">
                  <div
                    v-for="defect in defects"
                    :key="defect.id"
                    @click="navigateToDefect(defect.id)"
                    class="cursor-pointer hover:bg-white/10 rounded-lg p-3 transition-colors duration-200 border border-white/10 hover:border-white/20"
                  >
                    <div class="flex justify-between items-start">
                      <div class="flex-1">
                        <h4 class="text-white font-medium text-sm mb-1">{{ defect.title }}</h4>
                        <p class="text-white/70 text-xs line-clamp-2">{{ defect.description }}</p>
                      </div>
                      <div class="ml-3 flex flex-col items-end space-y-1">
                        <span
                          class="px-2 py-1 text-xs font-medium rounded-full border"
                          :class="getDefectStatusClass(defect.status)"
                        >
                          {{ defect.status }}
                        </span>
                        <span
                          class="px-2 py-1 text-xs font-medium rounded-full border"
                          :class="getDefectPriorityClass(defect.priority)"
                        >
                          {{ defect.priority }}
                        </span>
                      </div>
                    </div>
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
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '../utils/api';
import { useAuth } from '../composables/useAuth';
import TheHeader from '../components/TheHeader.vue';
import { ArrowLeftIcon, ExclamationTriangleIcon, PencilIcon } from '@heroicons/vue/24/outline';

const route = useRoute();
const router = useRouter();
const projectId = route.params.id as string;
const { hasRole, hasRoleId } = useAuth();

interface Project {
  id: number;
  name: string;
  description: string;
  manager_id: number;
  manager_name: string;
  status: string;
}

interface Defect {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee: string | null;
  due_date: string | null;
  attachments: string[];
  project_id: number;
  project_name: string;
  creator_id: number;
  creator_name: string;
}

const project = ref<Project | null>(null);
const defects = ref<Defect[]>([]);
const isLoading = ref(true);
const loadError = ref('');

// Check if user can edit the project
const canEditProject = computed(() => {
  if (!project.value) return false;
  if (hasRoleId(3)) return true; // Руководитель can edit any project

  // For managers, check if they are the manager of this project
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const currentUserId = parseInt(decoded.sub);
    return currentUserId === project.value.manager_id;
  } catch (error) {
    console.error('Error decoding token:', error);
    return false;
  }
});

const getProjectStatusClass = (status: string) => {
  const classes = {
    'Планирование': 'bg-blue-100 text-blue-800 border-blue-200',
    'Активный': 'bg-green-100 text-green-800 border-green-200',
    'Завершен': 'bg-gray-100 text-gray-800 border-gray-200',
    'Приостановлен': 'bg-yellow-100 text-yellow-800 border-yellow-200'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800 border-gray-200';
};

const getProjectStatusText = (status: string) => {
  return status || 'Неизвестно';
};

const getDefectStatusClass = (status: string) => {
  const classes = {
    'NEW': 'status-new',
    'В работе': 'status-in-progress',
    'На проверке': 'status-under-review',
    'Закрыт': 'status-closed',
    'Отменен': 'status-cancelled'
  };
  return classes[status as keyof typeof classes] || 'status-new';
};

const getDefectPriorityClass = (priority: string) => {
  const classes = {
    'Низкий': 'priority-low',
    'Средний': 'priority-medium',
    'Высокий': 'priority-high',
    'Критический': 'priority-critical'
  };
  return classes[priority as keyof typeof classes] || 'priority-medium';
};

const navigateToEdit = () => {
  router.push(`/projects/${projectId}/edit`);
};

const navigateToDefect = (defectId: number) => {
  router.push(`/defects/${defectId}`);
};

onMounted(async () => {
  try {
    isLoading.value = true;
    loadError.value = '';

    // Load project data
    const projectResponse = await api.get(`/projects/${projectId}`);
    if (projectResponse.error) {
      loadError.value = projectResponse.error;
      return;
    }
    project.value = projectResponse.data;

    // Load defects for this project
    const defectsResponse = await api.get(`/defects/project/${projectId}`);
    if (defectsResponse.error) {
      console.error('Error loading defects:', defectsResponse.error);
      // Don't set loadError for defects, just log it
    } else {
      defects.value = defectsResponse.data;
    }
  } catch (error: any) {
    console.error('Error loading project:', error);
    loadError.value = error.response?.data?.detail || 'Ошибка при загрузке проекта';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-inner {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container-responsive {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style>
