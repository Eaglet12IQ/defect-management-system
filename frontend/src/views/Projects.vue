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
        
        <button class="mt-4 sm:mt-0 bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Новый проект
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Активные проекты"
          :value="activeProjects.length"
          :icon="FolderOpenIcon"
          variant="primary"
        />
        <StatCard
          title="Всего дефектов"
          :value="totalDefects"
          :icon="ExclamationTriangleIcon"
          variant="warning"
        />
        <StatCard
          title="Средний прогресс"
          :value="averageProgress + '%'"
          :icon="ChartBarIcon"
          variant="success"
          :show-progress="true"
          :max-value="100"
        />
      </div>

      <!-- Projects Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="(project, index) in projects"
          :key="project.id"
          class="bg-white rounded-2xl shadow-card hover:shadow-card-hover transition-all duration-300 overflow-hidden card-hover animate-slide-up hover-lift"
          :class="`animate-slide-up-delay-${Math.min(index + 1, 4)}`"
        >
          <!-- Project Header -->
          <div class="p-6 pb-4">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ project.name }}</h3>
                <p class="text-gray-600 text-sm line-clamp-2 mb-3">{{ project.description }}</p>
              </div>
              
              <span
                class="px-3 py-1 text-xs font-medium rounded-full border flex-shrink-0"
                :class="getProjectStatusClass(project.status)"
              >
                {{ getProjectStatusText(project.status) }}
              </span>
            </div>

            <!-- Progress -->
            <div class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Прогресс</span>
                <span class="text-sm font-bold text-gray-900">{{ project.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all duration-1000 ease-out"
                  :class="getProgressColorClass(project.status)"
                  :style="{ width: `${project.progress}%` }"
                ></div>
              </div>
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
              <div class="col-span-2">
                <span class="font-medium">Период:</span>
                <p class="mt-1">{{ formatDateRange(project.startDate, project.endDate) }}</p>
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
                <button class="p-2 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-primary-50">
                  <EyeIcon class="w-4 h-4" />
                </button>
                <button class="p-2 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-primary-50">
                  <PencilIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Project Footer -->
          <div class="px-6 py-4 bg-gray-50 border-t">
            <div class="flex items-center justify-between">
              <div class="flex items-center text-sm text-gray-500">
                <CalendarIcon class="w-4 h-4 mr-1" />
                Создан {{ formatDate(project.startDate) }}
              </div>
              
              <button class="text-primary-600 hover:text-primary-700 text-sm font-medium hover:underline transition-all duration-200">
                Подробнее
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="projects.length === 0" class="text-center py-12 animate-fade-in">
        <FolderOpenIcon class="w-16 h-16 text-white/50 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Проектов пока нет</h3>
        <p class="text-white/70 mb-6">Создайте первый проект для начала работы</p>
        <button class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Создать проект
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { mockProjects } from '../data/mockData';
import TheHeader from '../components/TheHeader.vue';
import StatCard from '../components/StatCard.vue';
import {
  FolderOpenIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline';

const projects = mockProjects;

const activeProjects = computed(() => {
  return projects.filter(p => p.status === 'active');
});

const totalDefects = computed(() => {
  return projects.reduce((sum, project) => sum + project.defectsCount, 0);
});

const averageProgress = computed(() => {
  if (projects.length === 0) return 0;
  return Math.round(projects.reduce((sum, project) => sum + project.progress, 0) / projects.length);
});

const getProjectStatusClass = (status: string) => {
  const classes = {
    'planning': 'bg-blue-100 text-blue-800 border-blue-200',
    'active': 'bg-green-100 text-green-800 border-green-200',
    'completed': 'bg-gray-100 text-gray-800 border-gray-200',
    'paused': 'bg-yellow-100 text-yellow-800 border-yellow-200'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800 border-gray-200';
};

const getProjectStatusText = (status: string) => {
  const texts = {
    'planning': 'Планирование',
    'active': 'Активный',
    'completed': 'Завершен',
    'paused': 'Приостановлен'
  };
  return texts[status as keyof typeof texts] || 'Неизвестно';
};

const getProgressColorClass = (status: string) => {
  const classes = {
    'planning': 'bg-blue-500',
    'active': 'bg-green-500',
    'completed': 'bg-gray-500',
    'paused': 'bg-yellow-500'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-500';
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const formatDateRange = (startDate: string, endDate?: string) => {
  const start = formatDate(startDate);
  if (!endDate) return `с ${start}`;
  return `${start} - ${formatDate(endDate)}`;
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