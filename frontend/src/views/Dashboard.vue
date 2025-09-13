<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Welcome Section -->
      <div class="mb-8 animate-fade-in">
        <h2 class="text-3xl font-bold text-white mb-2">
          Добро пожаловать, {{ currentUser?.name }}!
        </h2>
        <p class="text-white/80">
          Обзор текущего состояния проектов и дефектов
        </p>
      </div>

      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Всего дефектов"
          :value="stats.totalDefects"
          :icon="ExclamationTriangleIcon"
          variant="primary"
          :change="8.2"
        />
        <StatCard
          title="Новые дефекты"
          :value="stats.newDefects"
          :icon="PlusCircleIcon"
          variant="warning"
          :change="12.5"
        />
        <StatCard
          title="В работе"
          :value="stats.inProgressDefects"
          :icon="ClockIcon"
          variant="secondary"
          :change="-3.1"
        />
        <StatCard
          title="Завершено"
          :value="stats.completionRate + '%'"
          :icon="CheckCircleIcon"
          variant="success"
          :change="5.7"
          :show-progress="true"
          :max-value="100"
        />
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <!-- Recent Defects -->
        <div class="lg:col-span-2">
          <div class="glass rounded-2xl p-6 animate-slide-up">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-white">Последние дефекты</h3>
              <router-link
                to="/defects"
                class="text-primary-600 hover:text-primary-700 text-sm font-medium hover:underline transition-all duration-200"
              >
                Показать все
              </router-link>
            </div>
            
            <div class="space-y-4">
              <div
                v-for="(defect, index) in recentDefects"
                :key="defect.id"
                class="flex items-start space-x-4 p-4 bg-white/50 rounded-xl hover:bg-white/70 transition-all duration-200 cursor-pointer animate-slide-up hover-lift"
                :class="`animate-slide-up-delay-${Math.min(index + 1, 4)}`"
                @click="viewDefect(defect)"
              >
                <div
                  class="w-3 h-3 rounded-full flex-shrink-0 mt-2"
                  :class="getStatusColor(defect.status)"
                ></div>
                
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <h4 class="text-sm font-medium text-white truncate">
                        {{ defect.title }}
                      </h4>
                      <p class="text-xs text-white/80 mt-1 line-clamp-2">
                        {{ defect.description }}
                      </p>
                      <div class="flex items-center space-x-4 mt-2 text-xs text-white/70">
                        <span>{{ defect.location }}</span>
                        <span>{{ formatDate(defect.createdAt) }}</span>
                      </div>
                    </div>
                    
                    <div class="flex flex-col items-end space-y-1 ml-4">
                      <span
                        class="px-2 py-1 text-xs font-medium rounded-full border"
                        :class="getPriorityClass(defect.priority)"
                      >
                        {{ getPriorityText(defect.priority) }}
                      </span>
                      <span class="text-xs text-white/70">{{ defect.assignee }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Stats -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="glass rounded-2xl p-6 animate-slide-up-delay-2">
            <h3 class="text-lg font-semibold text-white mb-4">Быстрые действия</h3>
            <div class="space-y-3">
              <button class="w-full bg-primary-600 text-white px-4 py-3 rounded-xl font-medium hover:bg-primary-700 transition-all duration-200 transform hover:scale-105 flex items-center justify-center">
                <PlusIcon class="w-5 h-5 mr-2" />
                Новый дефект
              </button>
              <button class="w-full bg-white/20 text-white px-4 py-3 rounded-xl font-medium hover:bg-white/30 border border-white/30 transition-all duration-200 transform hover:scale-105 flex items-center justify-center hover:shadow-lg">
                <DocumentTextIcon class="w-5 h-5 mr-2" />
                Создать отчет
              </button>
              <button class="w-full bg-white/20 text-white px-4 py-3 rounded-xl font-medium hover:bg-white/30 border border-white/30 transition-all duration-200 transform hover:scale-105 flex items-center justify-center hover:shadow-lg">
                <FolderPlusIcon class="w-5 h-5 mr-2" />
                Новый проект
              </button>
            </div>
          </div>

          <!-- Team Activity -->
          <div class="glass rounded-2xl p-6 animate-slide-up-delay-3">
            <h3 class="text-lg font-semibold text-white mb-4">Активность команды</h3>
            <div class="space-y-4">
              <div
                v-for="(activity, index) in teamActivity"
                :key="activity.id"
                class="flex items-center space-x-3 animate-slide-up"
                :class="`animate-slide-up-delay-${Math.min(index + 4, 4)}`"
              >
                <img
                  :src="activity.avatar"
                  :alt="activity.user"
                  class="w-8 h-8 rounded-full"
                />
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-white">
                    <span class="font-medium">{{ activity.user }}</span>
                    {{ activity.action }}
                  </p>
                  <p class="text-xs text-white/70">{{ formatTimeAgo(activity.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Critical Alerts -->
          <div v-if="criticalDefects.length > 0" class="glass rounded-2xl p-6 animate-slide-up-delay-4">
            <div class="flex items-center space-x-2 mb-4">
              <ExclamationCircleIcon class="w-5 h-5 text-red-600" />
              <h3 class="text-lg font-semibold text-white">Критические дефекты</h3>
            </div>
            <div class="space-y-3">
              <div
                v-for="defect in criticalDefects"
                :key="defect.id"
                class="p-3 bg-red-50 border border-red-200 rounded-lg cursor-pointer hover:bg-red-100 transition-colors duration-200"
                @click="viewDefect(defect)"
              >
                <h4 class="text-sm font-medium text-red-900">{{ defect.title }}</h4>
                <p class="text-xs text-red-700 mt-1">{{ defect.location }}</p>
                <div class="flex items-center justify-between mt-2">
                  <span class="text-xs text-red-600">{{ defect.assignee }}</span>
                  <span class="text-xs text-red-500">
                    {{ isOverdue(defect.dueDate) ? 'Просрочено' : formatDate(defect.dueDate) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Defects Trend -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-4">
          <h3 class="text-xl font-semibold text-white mb-6">Динамика дефектов</h3>
          <div class="h-64">
            <CanvasChart
              :data="defectsTrendData"
              type="line"
              :animated="true"
            />
          </div>
        </div>

        <!-- Status Distribution -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-4">
          <h3 class="text-xl font-semibold text-white mb-6">Распределение по статусам</h3>
          <div class="h-64">
            <CanvasChart
              :data="statusDistributionData"
              type="doughnut"
              :animated="true"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuth } from '../composables/useAuth';
import { mockStats, mockDefects, type Defect } from '../data/mockData';
import TheHeader from '../components/TheHeader.vue';
import StatCard from '../components/StatCard.vue';
import CanvasChart from '../components/CanvasChart.vue';
import {
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  PlusCircleIcon,
  ClockIcon,
  CheckCircleIcon,
  PlusIcon,
  DocumentTextIcon,
  FolderPlusIcon
} from '@heroicons/vue/24/outline';

const { currentUser } = useAuth();
const stats = mockStats;

// Recent defects (last 5)
const recentDefects = computed(() => {
  return mockDefects
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);
});

// Critical defects
const criticalDefects = computed(() => {
  return mockDefects.filter(d => d.priority === 'critical' && d.status !== 'closed');
});

// Team activity mock data
const teamActivity = computed(() => [
  {
    id: '1',
    user: 'Мария Иванова',
    action: 'закрыла дефект "Протечка кровли"',
    timestamp: '2024-01-22T14:45:00Z',
    avatar: 'https://images.pexels.com/photos/3763188/pexels-photo-3763188.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2'
  },
  {
    id: '2',
    user: 'Дмитрий Смирнов',
    action: 'взял в работу дефект "Трещина в стене"',
    timestamp: '2024-01-22T10:30:00Z',
    avatar: 'https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2'
  },
  {
    id: '3',
    user: 'Елена Козлова',
    action: 'создала новый дефект',
    timestamp: '2024-01-22T09:15:00Z',
    avatar: 'https://images.pexels.com/photos/3992656/pexels-photo-3992656.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2'
  }
]);

// Chart data
const defectsTrendData = computed(() => [
  { label: 'Дек', value: 28 },
  { label: 'Янв', value: 35 },
  { label: 'Фев', value: 43 },
  { label: 'Мар', value: 38 },
  { label: 'Апр', value: 45 },
  { label: 'Май', value: 52 }
]);

const statusDistributionData = computed(() => [
  { label: 'Новые', value: stats.newDefects, color: '#3b82f6' },
  { label: 'В работе', value: stats.inProgressDefects, color: '#f59e0b' },
  { label: 'На проверке', value: 5, color: '#8b5cf6' },
  { label: 'Закрыто', value: stats.closedDefects, color: '#10b981' }
]);

// Helper functions
const getStatusColor = (status: string) => {
  const colors = {
    'new': 'bg-blue-500',
    'in-progress': 'bg-yellow-500',
    'review': 'bg-purple-500',
    'closed': 'bg-green-500',
    'cancelled': 'bg-red-500'
  };
  return colors[status as keyof typeof colors] || 'bg-gray-500';
};

const getPriorityClass = (priority: string) => {
  const classes = {
    'low': 'priority-low',
    'medium': 'priority-medium',
    'high': 'priority-high',
    'critical': 'priority-critical'
  };
  return classes[priority as keyof typeof classes] || 'priority-medium';
};

const getPriorityText = (priority: string) => {
  const texts = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий',
    'critical': 'Критический'
  };
  return texts[priority as keyof typeof texts] || 'Средний';
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

const formatTimeAgo = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
  
  if (diffHours < 1) return 'Только что';
  if (diffHours < 24) return `${diffHours} ч. назад`;
  
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return `${diffDays} дн. назад`;
};

const isOverdue = (dateString?: string) => {
  if (!dateString) return false;
  return new Date(dateString) < new Date();
};

const viewDefect = (defect: Defect) => {
  console.log('Viewing defect:', defect.id);
  // Navigate to defect details
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