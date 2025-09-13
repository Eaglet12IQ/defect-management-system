<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />
    
    <main class="container-responsive py-8">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 animate-fade-in">
        <div>
          <h2 class="text-3xl font-bold text-white mb-2">Дефекты</h2>
          <p class="text-white/80">Управление дефектами строительных объектов</p>
        </div>
        
        <button class="mt-4 sm:mt-0 bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Новый дефект
        </button>
      </div>

      <!-- Filters -->
      <div class="glass rounded-2xl p-6 mb-8 animate-slide-up">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search -->
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/60" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск дефектов..."
              class="w-full pl-10 pr-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            />
          </div>

          <!-- Status Filter -->
          <select
            v-model="statusFilter"
            class="px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
          >
            <option value="">Все статусы</option>
            <option value="new">Новые</option>
            <option value="in-progress">В работе</option>
            <option value="review">На проверке</option>
            <option value="closed">Закрыто</option>
          </select>

          <!-- Priority Filter -->
          <select
            v-model="priorityFilter"
            class="px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
          >
            <option value="">Все приоритеты</option>
            <option value="low">Низкий</option>
            <option value="medium">Средний</option>
            <option value="high">Высокий</option>
            <option value="critical">Критический</option>
          </select>

          <!-- Project Filter -->
          <select
            v-model="projectFilter"
            class="px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
          >
            <option value="">Все проекты</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
        </div>

        <!-- Quick Filters -->
        <div class="flex flex-wrap gap-2 mt-4">
          <button
            v-for="filter in quickFilters"
            :key="filter.key"
            @click="applyQuickFilter(filter)"
            class="px-4 py-2 text-sm font-medium rounded-lg bg-white/30 hover:bg-white/50 text-white hover:text-white transition-all duration-200"
            :class="{ 'bg-white text-primary-600': isQuickFilterActive(filter) }"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Results Summary -->
      <div class="flex items-center justify-between mb-6 animate-slide-up-delay-1">
        <p class="text-white/80">
          Найдено <span class="font-semibold">{{ filteredDefects.length }}</span> из {{ defects.length }} дефектов
        </p>
        
        <div class="flex items-center space-x-2">
          <span class="text-white/60 text-sm">Вид:</span>
          <button
            @click="viewMode = 'grid'"
            :class="viewMode === 'grid' ? 'bg-white/20 text-white' : 'text-white/60 hover:text-white'"
            class="p-2 rounded-lg transition-all duration-200"
          >
            <Squares2X2Icon class="w-5 h-5" />
          </button>
          <button
            @click="viewMode = 'list'"
            :class="viewMode === 'list' ? 'bg-white/20 text-white' : 'text-white/60 hover:text-white'"
            class="p-2 rounded-lg transition-all duration-200"
          >
            <ListBulletIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Defects Grid/List -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <DefectCard
          v-for="(defect, index) in filteredDefects"
          :key="defect.id"
          :defect="defect"
          @edit="editDefect"
          @view="viewDefect"
          class="animate-slide-up"
          :class="`animate-slide-up-delay-${Math.min(index + 1, 4)}`"
        />
      </div>

      <!-- List View -->
      <div v-else class="glass rounded-2xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-white/10 border-b border-white/20">
              <tr>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Дефект</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Статус</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Приоритет</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Исполнитель</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Срок</th>
                <th class="px-6 py-4 text-left text-sm font-semibold text-white">Действия</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10">
              <tr
                v-for="(defect, index) in filteredDefects"
                :key="defect.id"
                class="hover:bg-white/5 transition-colors duration-200 animate-slide-up"
                :class="`animate-slide-up-delay-${Math.min(index + 1, 4)}`"
              >
                <td class="px-6 py-4">
                  <div>
                    <h3 class="font-medium text-white">{{ defect.title }}</h3>
                    <p class="text-sm text-white/80 truncate max-w-xs">{{ defect.description }}</p>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span
                    class="px-3 py-1 text-xs font-medium rounded-full border"
                    :class="getStatusClass(defect.status)"
                  >
                    {{ getStatusText(defect.status) }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span
                    class="px-3 py-1 text-xs font-medium rounded-full border"
                    :class="getPriorityClass(defect.priority)"
                  >
                    {{ getPriorityText(defect.priority) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-white/80">{{ defect.assignee }}</td>
                <td class="px-6 py-4 text-sm" :class="{ 'text-red-600': isOverdue(defect.dueDate) }">
                  {{ formatDate(defect.dueDate) }}
                </td>
                <td class="px-6 py-4">
                  <div class="flex space-x-2">
                    <button
                      @click="viewDefect(defect)"
                      class="p-1 text-white/60 hover:text-white transition-colors duration-200"
                    >
                      <EyeIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click="editDefect(defect)"
                      class="p-1 text-white/60 hover:text-white transition-colors duration-200"
                    >
                      <PencilIcon class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredDefects.length === 0" class="text-center py-12 animate-fade-in">
        <ExclamationTriangleIcon class="w-16 h-16 text-white/50 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">
          {{ defects.length === 0 ? 'Дефектов пока нет' : 'Дефекты не найдены' }}
        </h3>
        <p class="text-white/70 mb-6">
          {{ defects.length === 0 ? 'Создайте первый дефект для начала работы' : 'Попробуйте изменить параметры поиска' }}
        </p>
        <button
          v-if="defects.length === 0"
          class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
        >
          <PlusIcon class="w-5 h-5 inline-block mr-2" />
          Создать дефект
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { mockDefects, mockProjects, type Defect } from '../data/mockData';
import TheHeader from '../components/TheHeader.vue';
import DefectCard from '../components/DefectCard.vue';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilIcon
} from '@heroicons/vue/24/outline';

const defects = mockDefects;
const projects = mockProjects;

// Filters
const searchQuery = ref('');
const statusFilter = ref('');
const priorityFilter = ref('');
const projectFilter = ref('');
const viewMode = ref<'grid' | 'list'>('grid');

const quickFilters = [
  { key: 'critical', label: 'Критические', filter: { priority: 'critical' } },
  { key: 'overdue', label: 'Просроченные', filter: { overdue: true } },
  { key: 'my', label: 'Мои задачи', filter: { assignee: 'current' } },
  { key: 'new', label: 'Новые', filter: { status: 'new' } }
];

const activeQuickFilter = ref('');

const filteredDefects = computed(() => {
  let result = [...defects];

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(defect =>
      defect.title.toLowerCase().includes(query) ||
      defect.description.toLowerCase().includes(query) ||
      defect.location?.toLowerCase().includes(query)
    );
  }

  // Status filter
  if (statusFilter.value) {
    result = result.filter(defect => defect.status === statusFilter.value);
  }

  // Priority filter
  if (priorityFilter.value) {
    result = result.filter(defect => defect.priority === priorityFilter.value);
  }

  // Project filter
  if (projectFilter.value) {
    result = result.filter(defect => defect.projectId === projectFilter.value);
  }

  return result;
});

const applyQuickFilter = (filter: any) => {
  if (activeQuickFilter.value === filter.key) {
    // Reset filter
    activeQuickFilter.value = '';
    statusFilter.value = '';
    priorityFilter.value = '';
    return;
  }

  activeQuickFilter.value = filter.key;
  
  if (filter.filter.status) {
    statusFilter.value = filter.filter.status;
  }
  if (filter.filter.priority) {
    priorityFilter.value = filter.filter.priority;
  }
};

const isQuickFilterActive = (filter: any) => {
  return activeQuickFilter.value === filter.key;
};

const editDefect = (defect: Defect) => {
  console.log('Editing defect:', defect.id);
  // Implement edit logic
};

const viewDefect = (defect: Defect) => {
  console.log('Viewing defect:', defect.id);
  // Implement view logic
};

const getStatusClass = (status: string) => {
  const classes = {
    'new': 'status-new',
    'in-progress': 'status-in-progress',
    'review': 'status-review',
    'closed': 'status-closed',
    'cancelled': 'status-cancelled'
  };
  return classes[status as keyof typeof classes] || 'status-new';
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

const getStatusText = (status: string) => {
  const texts = {
    'new': 'Новая',
    'in-progress': 'В работе',
    'review': 'На проверке',
    'closed': 'Закрыта',
    'cancelled': 'Отменена'
  };
  return texts[status as keyof typeof texts] || 'Неизвестно';
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
</script>