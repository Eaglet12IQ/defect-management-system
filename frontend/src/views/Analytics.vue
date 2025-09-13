<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in">
        <div>
          <h2 class="text-3xl font-bold text-white mb-2">Аналитика</h2>
          <p class="text-white/80">Отчеты и статистика по дефектам</p>
        </div>
        
        <div class="flex items-center space-x-4 mt-4 sm:mt-0">
          <select class="px-4 py-2 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-white/50">
            <option>Последние 30 дней</option>
            <option>Последние 3 месяца</option>
            <option>За год</option>
          </select>
          
          <button class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
            <DocumentArrowDownIcon class="w-5 h-5 inline-block mr-2" />
            Экспорт
          </button>
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Всего дефектов"
          :value="stats.totalDefects"
          :icon="ExclamationTriangleIcon"
          variant="primary"
          :change="12.5"
        />
        <StatCard
          title="Критических"
          :value="stats.criticalDefects"
          :icon="ExclamationCircleIcon"
          variant="danger"
          :change="-8.2"
        />
        <StatCard
          title="Просрочено"
          :value="stats.overdueTasks"
          :icon="ClockIcon"
          variant="warning"
          :change="3.1"
        />
        <StatCard
          title="Выполнено"
          :value="stats.completionRate + '%'"
          :icon="CheckCircleIcon"
          variant="success"
          :change="5.7"
          :show-progress="true"
          :max-value="100"
        />
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Defects Trend -->
        <div class="glass rounded-2xl p-6 animate-slide-up">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-semibold text-white">Динамика дефектов</h3>
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 bg-primary-500 rounded-full"></div>
              <span class="text-sm text-white/80">Создано</span>
              <div class="w-3 h-3 bg-secondary-500 rounded-full ml-4"></div>
              <span class="text-sm text-white/80">Закрыто</span>
            </div>
          </div>
          <div class="h-80">
            <CanvasChart
              :data="defectsTrendData"
              type="line"
              :animated="true"
            />
          </div>
        </div>

        <!-- Priority Distribution -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-1">
          <h3 class="text-xl font-semibold text-white mb-6">Распределение по приоритетам</h3>
          <div class="h-80">
            <CanvasChart
              :data="priorityData"
              type="doughnut"
              :animated="true"
            />
          </div>
        </div>
      </div>

      <!-- Additional Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <!-- Status Distribution -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-2">
          <h3 class="text-xl font-semibold text-white mb-6">Статусы дефектов</h3>
          <div class="h-64">
            <CanvasChart
              :data="statusData"
              type="bar"
              :animated="true"
            />
          </div>
        </div>

        <!-- Team Performance -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-3">
          <h3 class="text-xl font-semibold text-white mb-6">Производительность команды</h3>
          <div class="space-y-4">
            <div
              v-for="member in teamPerformance"
              :key="member.name"
              class="flex items-center justify-between"
            >
              <div class="flex items-center space-x-3">
                <img
                  :src="member.avatar"
                  :alt="member.name"
                  class="w-8 h-8 rounded-full"
                />
                <span class="text-sm font-medium text-white">{{ member.name }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-20 bg-gray-200 rounded-full h-2">
                  <div
                    class="h-2 rounded-full transition-all duration-1000 ease-out"
                    :class="getPerformanceColor(member.performance)"
                    :style="{ width: `${member.performance}%` }"
                  ></div>
                </div>
                <span class="text-sm text-white/80 w-8">{{ member.closed }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Project Health -->
        <div class="glass rounded-2xl p-6 animate-slide-up-delay-4">
          <h3 class="text-xl font-semibold text-white mb-6">Здоровье проектов</h3>
          <div class="space-y-4">
            <div
              v-for="project in projectHealth"
              :key="project.name"
              class="p-4 bg-white/50 rounded-xl"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-white">{{ project.name }}</span>
                <div
                  class="w-3 h-3 rounded-full"
                  :class="getHealthColor(project.health)"
                ></div>
              </div>
              <div class="flex items-center justify-between text-xs text-white/80">
                <span>{{ project.defects }} дефектов</span>
                <span>{{ project.progress }}% готово</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="glass rounded-2xl p-6 animate-slide-up-delay-4">
        <h3 class="text-xl font-semibold text-white mb-6">Временная шкала</h3>
        <div class="relative">
          <!-- Timeline line -->
          <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          
          <div class="space-y-6">
            <div
              v-for="(event, index) in timelineEvents"
              :key="event.id"
              class="flex items-start space-x-4 animate-slide-up"
              :class="`animate-slide-up-delay-${Math.min(index + 4, 4)}`"
            >
              <div
                class="w-4 h-4 rounded-full border-2 border-white flex-shrink-0 mt-1"
                :class="getEventColor(event.type)"
              ></div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <h4 class="text-sm font-medium text-white">{{ event.title }}</h4>
                  <span class="text-xs text-white/70">{{ formatEventDate(event.date) }}</span>
                </div>
                <p class="text-sm text-white/80 mt-1">{{ event.description }}</p>
                <div class="flex items-center space-x-2 mt-2">
                  <span
                    class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="getEventTypeClass(event.type)"
                  >
                    {{ event.type }}
                  </span>
                  <span class="text-xs text-white/70">{{ event.project }}</span>
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
import { computed } from 'vue';
import { mockStats, mockUsers, mockProjects } from '../data/mockData';
import TheHeader from '../components/TheHeader.vue';
import StatCard from '../components/StatCard.vue';
import CanvasChart from '../components/CanvasChart.vue';
import {
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  ClockIcon,
  CheckCircleIcon,
  DocumentArrowDownIcon
} from '@heroicons/vue/24/outline';

const stats = mockStats;

// Chart data
const defectsTrendData = computed(() => [
  { label: 'Окт', value: 32 },
  { label: 'Ноя', value: 28 },
  { label: 'Дек', value: 35 },
  { label: 'Янв', value: 43 },
  { label: 'Фев', value: 38 },
  { label: 'Мар', value: 45 }
]);

const priorityData = computed(() => [
  { label: 'Низкий', value: 15, color: '#10b981' },
  { label: 'Средний', value: 18, color: '#f59e0b' },
  { label: 'Высокий', value: 8, color: '#f97316' },
  { label: 'Критический', value: 3, color: '#ef4444' }
]);

const statusData = computed(() => [
  { label: 'Новые', value: stats.newDefects, color: '#3b82f6' },
  { label: 'В работе', value: stats.inProgressDefects, color: '#f59e0b' },
  { label: 'Проверка', value: 5, color: '#8b5cf6' },
  { label: 'Закрыто', value: stats.closedDefects, color: '#10b981' }
]);

// Team performance data
const teamPerformance = computed(() => [
  {
    name: 'Мария Иванова',
    avatar: 'https://images.pexels.com/photos/3763188/pexels-photo-3763188.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2',
    closed: 15,
    performance: 85
  },
  {
    name: 'Дмитрий Смирнов',
    avatar: 'https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2',
    closed: 12,
    performance: 72
  },
  {
    name: 'Елена Козлова',
    avatar: 'https://images.pexels.com/photos/3992656/pexels-photo-3992656.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2',
    closed: 8,
    performance: 58
  }
]);

// Project health data
const projectHealth = computed(() => [
  { name: 'ЖК "Северная звезда"', health: 'good', defects: 23, progress: 65 },
  { name: 'БЦ "Прогресс"', health: 'warning', defects: 17, progress: 42 },
  { name: 'ТК "Центр"', health: 'good', defects: 3, progress: 15 }
]);

// Timeline events
const timelineEvents = computed(() => [
  {
    id: '1',
    title: 'Критический дефект устранен',
    description: 'Протечка кровли в корпусе Б полностью устранена',
    type: 'Закрытие',
    project: 'ЖК "Северная звезда"',
    date: '2024-01-22T14:45:00Z'
  },
  {
    id: '2',
    title: 'Новый дефект зарегистрирован',
    description: 'Трещина в стене на 5 этаже требует внимания',
    type: 'Создание',
    project: 'ЖК "Северная звезда"',
    date: '2024-01-20T09:30:00Z'
  },
  {
    id: '3',
    title: 'Дефект отправлен на проверку',
    description: 'Неровность пола исправлена, ожидает проверки',
    type: 'Проверка',
    project: 'БЦ "Прогресс"',
    date: '2024-01-19T16:20:00Z'
  }
]);

const getPerformanceColor = (performance: number) => {
  if (performance >= 80) return 'bg-green-500';
  if (performance >= 60) return 'bg-yellow-500';
  return 'bg-red-500';
};

const getHealthColor = (health: string) => {
  const colors = {
    good: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500'
  };
  return colors[health as keyof typeof colors] || 'bg-gray-500';
};

const getEventColor = (type: string) => {
  const colors = {
    'Создание': 'bg-blue-500',
    'Закрытие': 'bg-green-500',
    'Проверка': 'bg-purple-500'
  };
  return colors[type as keyof typeof colors] || 'bg-gray-500';
};

const getEventTypeClass = (type: string) => {
  const classes = {
    'Создание': 'bg-blue-100 text-blue-800',
    'Закрытие': 'bg-green-100 text-green-800',
    'Проверка': 'bg-purple-100 text-purple-800'
  };
  return classes[type as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

const formatEventDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'Вчера';
  if (diffDays === 2) return 'Позавчера';
  if (diffDays <= 7) return `${diffDays} дн. назад`;
  
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};
</script>