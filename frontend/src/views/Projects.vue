<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in">
        <div>
          <h2 class="text-3xl font-bold text-white mb-2">Проекты</h2>
          <p class="text-white/80">Управление строительными объектами</p>
        </div>
        
        <button
          v-if="hasRole('3')"
          @click="navigateToCreateProject"
          class="mt-4 sm:mt-0 bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Новый проект
        </button>
      </div>



      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="flex items-center space-x-3 text-white">
          <div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          <span>Загрузка проектов...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="errorMessage" class="text-center py-12 animate-fade-in">
        <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Ошибка загрузки</h3>
        <p class="text-white/70 mb-6">{{ errorMessage }}</p>
        <button
          @click="fetchProjects"
          class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Projects Grid -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="(project, index) in projects"
          :key="project.id"
          @click="navigateToProjectDetail(project.id)"
          class="bg-white rounded-2xl shadow-card hover:shadow-lg hover:shadow-primary-500/10 hover:-translate-y-1 hover:border-primary-500 transition-all duration-300 overflow-hidden card-hover animate-slide-up hover-lift cursor-pointer border-2 border-transparent hover:border-primary-500"
          :class="`animate-slide-up-delay-${Math.min(index + 1, 4)}`"
        >
          <!-- Project Header -->
          <div class="p-6 pb-4">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <h3 class="text-xl font-semibold text-gray-900">{{ project.name }}</h3>
                  <button
                    v-if="canEditProject(project.manager_id)"
                    @click.stop="navigateToProjectEdit(project.id)"
                    class="p-1 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-primary-50"
                    title="Редактировать проект"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                </div>
                <p class="text-gray-600 text-sm line-clamp-2 mb-3">{{ project.description }}</p>
              </div>

              <span
                class="px-3 py-1 text-xs font-medium rounded-full border flex-shrink-0"
                :class="getProjectStatusClass(project.status)"
              >
                {{ getProjectStatusText(project.status) }}
              </span>
            </div>



            <!-- Project Info -->
            <div class="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
              <div>
                <span class="font-medium">Менеджер:</span>
                <p class="mt-1">{{ project.manager }}</p>
              </div>
              <div>
                <span class="font-medium">Дефектов:</span>
                <p class="mt-1 font-semibold">{{ project.defectsCount }}</p>
              </div>
            </div>

            <!-- Team Avatars -->
            <div class="flex items-center justify-between">
              <div class="flex -space-x-2">
                <img
                  v-for="member in project.team.slice(0, 4)"
                  :key="member.id"
                  :src="member.avatar || 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2'"
                  :alt="member.name"
                  :title="member.name"
                  class="w-8 h-8 rounded-full border-2 border-white hover:border-primary-200 transition-all duration-200 hover:scale-110 cursor-pointer"
                />
                <div
                  v-if="project.team.length > 4"
                  class="w-8 h-8 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center text-xs font-medium text-gray-600"
                  :title="`+${project.team.length - 4} участников`"
                >
                  +{{ project.team.length - 4 }}
                </div>
              </div>

              <div class="flex space-x-2">
                <!-- Edit button moved to project title -->
              </div>
            </div>
          </div>


        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!isLoading && !errorMessage && projects.length === 0" class="text-center py-12 animate-fade-in">
        <FolderOpenIcon class="w-16 h-16 text-white/50 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Проектов пока нет</h3>
        <p class="text-white/70 mb-6">Создайте первый проект для начала работы</p>
        <button
          v-if="hasRole('3')"
          @click="navigateToCreateProject"
          class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Создать проект
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../utils/api';
import { useAuth } from '../composables/useAuth';
import TheHeader from '../components/TheHeader.vue';
import {
  PlusIcon,
  PencilIcon
} from '@heroicons/vue/24/outline';

const router = useRouter();
const { hasRole } = useAuth();

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'Планирование' | 'Активный' | 'Завершен' | 'Приостановлен';
  manager: string;
  manager_id: number;
  startDate: string;
  endDate?: string;
  progress: number;
  defectsCount: number;
  team: any[];
}

interface ApiProject {
  id: number;
  name: string;
  description: string;
  manager_id: number;
  manager_name: string;
  status: string;
}

const projects = ref<Project[]>([]);
const isLoading = ref(true);
const errorMessage = ref('');

const fetchProjects = async () => {
  try {
    isLoading.value = true;
    errorMessage.value = '';
    const response = await api.get('/projects');

    if (response.error) {
      errorMessage.value = response.error;
    } else {
      // Transform API response to match UI format
      projects.value = response.data.map((apiProject: ApiProject) => ({
        id: apiProject.id.toString(),
        name: apiProject.name,
        description: apiProject.description,
        status: apiProject.status as 'Планирование' | 'Активный' | 'Завершен' | 'Приостановлен',
        manager: apiProject.manager_name,
        manager_id: apiProject.manager_id,
        startDate: new Date().toISOString().split('T')[0], // Default date since API doesn't provide it
        progress: 0, // Default progress since API doesn't provide it
        defectsCount: 0, // Default defects count since API doesn't provide it
        team: [] // Default empty team since API doesn't provide it
      }));
    }
  } catch (error: any) {
    console.error('Error fetching projects:', error);
    errorMessage.value = error.response?.data?.detail || 'Ошибка при загрузке проектов';
  } finally {
    isLoading.value = false;
  }
};

// Check if user can edit a project
const canEditProject = (projectManagerId: number) => {
  if (hasRole('3')) return true; // Admins can edit any project

  // For managers, check if they are the manager of this project
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const currentUserId = parseInt(decoded.sub);
    return currentUserId === projectManagerId;
  } catch (error) {
    console.error('Error decoding token:', error);
    return false;
  }
};

onMounted(() => {
  fetchProjects();
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

const getProgressColorClass = (status: string) => {
  const classes = {
    'Планирование': 'bg-blue-500',
    'Активный': 'bg-green-500',
    'Завершен': 'bg-gray-500',
    'Приостановлен': 'bg-yellow-500'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-500';
};



const navigateToCreateProject = () => {
  router.push('/create-project');
};

const navigateToProjectDetail = (projectId: string | number) => {
  router.push(`/projects/${projectId}`);
};

const navigateToProjectEdit = (projectId: string | number) => {
  router.push(`/projects/${projectId}/edit`);
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>