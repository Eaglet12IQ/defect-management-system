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
        
        <router-link
          v-if="!hasRoleId(3) && !hasRoleId(2)"
          to="/create-defect"
          class="mt-4 sm:mt-0 bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center"
        >
          <PlusIcon class="w-5 h-5 mr-2" />
          Новый дефект
        </router-link>
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
            <option value="Новый">Новый</option>
            <option value="В работе">В работе</option>
            <option value="На проверке">На проверке</option>
            <option value="Закрыт">Закрыт</option>
            <option value="Отменен">Отменен</option>
          </select>

          <!-- Priority Filter -->
          <select
            v-model="priorityFilter"
            class="px-4 py-3 border border-white/20 rounded-xl bg-white/50 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
          >
            <option value="">Все приоритеты</option>
            <option value="Низкий">Низкий</option>
            <option value="Средний">Средний</option>
            <option value="Высокий">Высокий</option>
            <option value="Критический">Критический</option>
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


      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12 animate-fade-in">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        <p class="text-white/70 mt-4">Загрузка дефектов...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 animate-fade-in">
        <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Ошибка загрузки</h3>
        <p class="text-white/70 mb-6">{{ error }}</p>
        <button
          @click="loadDefects"
          class="bg-primary-500 text-white px-6 py-3 rounded-xl font-medium hover:bg-primary-600 transition-all duration-200"
        >
          Попробовать снова
        </button>
      </div>

      <!-- Results Summary -->
      <div v-else class="flex items-center justify-between mb-6 animate-slide-up-delay-1">
        <p class="text-white/80">
          Найдено <span class="font-semibold">{{ filteredDefects.length }}</span> из {{ defects.length }} дефектов
        </p>
      </div>

      <!-- Defects Content -->
      <div v-if="!isLoading && !error">
        <!-- Defects Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
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

        <!-- Empty State -->
        <div v-if="filteredDefects.length === 0" class="text-center py-12 animate-fade-in">
          <ExclamationTriangleIcon class="w-16 h-16 text-white/50 mx-auto mb-4" />
          <h3 class="text-xl font-semibold text-white mb-2">
            {{ defects.length === 0 ? 'Дефектов пока нет' : 'Дефекты не найдены' }}
          </h3>
          <p class="text-white/70 mb-6">
            {{ defects.length === 0 ? (canCreateDefect ? 'Создайте первый дефект для начала работы' : '') : 'Попробуйте изменить параметры поиска' }}
          </p>
          <!-- Removed create defect button as per user request -->
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import TheHeader from '../components/TheHeader.vue';
import DefectCard from '../components/DefectCard.vue';
import { api } from '../utils/api';
import { useAuth } from '../composables/useAuth';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline';

const { hasRoleId } = useAuth();

const canCreateDefect = computed(() => !hasRoleId(3) && !hasRoleId(2));

const router = useRouter();
const defects = ref<any[]>([]);
const projects = ref<any[]>([]);
const isLoading = ref(true);
const error = ref('');

// Filters
const searchQuery = ref('');
const statusFilter = ref('');
const priorityFilter = ref('');
const projectFilter = ref('');

// Load data on component mount
onMounted(async () => {
  await loadDefects();
  await loadProjects();
});

const loadDefects = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    const response = await api.get('/defects');
    defects.value = response.data;
  } catch (err: any) {
    console.error('Error loading defects:', err);
    error.value = 'Ошибка при загрузке дефектов';
  } finally {
    isLoading.value = false;
  }
};

const loadProjects = async () => {
  try {
    const response = await api.get('/projects');
    projects.value = response.data;
  } catch (err: any) {
    console.error('Error loading projects:', err);
    // Projects are used for filtering, so we can continue without them
  }
};



const filteredDefects = computed(() => {
  let result = [...defects.value];

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(defect =>
      defect.title.toLowerCase().includes(query) ||
      defect.description.toLowerCase().includes(query) ||
      defect.project_name?.toLowerCase().includes(query)
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
    result = result.filter(defect => defect.project_id === projectFilter.value);
  }

  return result;
});



const editDefect = (defect: any) => {
  router.push(`/defects/${defect.id}/edit`);
};

const viewDefect = (defect: any) => {
  router.push(`/defects/${defect.id}`);
};

const getStatusClass = (status: string) => {
  const classes = {
    'Новый': 'status-new',
    'В работе': 'status-in-progress',
    'На проверке': 'status-under-review',
    'Закрыт': 'status-closed',
    'Отменен': 'status-cancelled'
  };
  return classes[status as keyof typeof classes] || 'status-new';
};

const getPriorityClass = (priority: string) => {
  const classes = {
    'Низкий': 'priority-low',
    'Средний': 'priority-medium',
    'Высокий': 'priority-high',
    'Критический': 'priority-critical'
  };
  return classes[priority as keyof typeof classes] || 'priority-medium';
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
</script>