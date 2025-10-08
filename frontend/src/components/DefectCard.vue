<template>
  <div
    class="bg-white rounded-2xl shadow-card hover:shadow-lg hover:shadow-primary-500/10 hover:-translate-y-1 hover:border-primary-500 transition-all duration-300 overflow-hidden card-hover animate-slide-up hover-lift cursor-pointer border-2 border-transparent max-w-full"
    @click="$emit('view', defect)"
  >
    <!-- Card Header -->
    <div class="p-6 pb-4 relative">
      <div class="flex items-start mb-4">
        <div class="flex-1 flex items-start gap-3 pr-32">
          <div class="flex-1 mr-40">
            <div class="flex items-center gap-2 mb-2 w-56">
              <h3 class="text-lg font-semibold text-gray-900 truncate" :title="defect.title">{{ defect.title }}</h3>
              <button
                v-if="!hasRoleId(3) && (hasRoleId(2) ? defect.status !== 'В работе' : defect.status === 'В работе')"
                @click.stop="$emit('edit', defect)"
                class="p-1.5 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-md hover:bg-primary-50 flex-shrink-0"
                title="Выполнение"
              >
                <PlayIcon class="w-4 h-4" />
              </button>
            </div>
            <div class="flex items-center gap-2 mb-2 w-[350px]">
              <p class="text-gray-600 text-sm pr-40 truncate" :title="defect.description">{{ defect.description }}</p>
            </div>
            
          </div>
        </div>
        
        <div class="flex flex-col items-end space-y-2 absolute top-6 right-6">
          <span
            class="px-3 py-1 text-xs font-medium rounded-full border"
            :class="getStatusClass(defect.status)"
          >
            {{ getStatusText(defect.status) }}
          </span>
          <span
            class="px-3 py-1 text-xs font-medium rounded-full border"
            :class="getPriorityClass(defect.priority)"
          >
            {{ getPriorityText(defect.priority) }}
          </span>
        </div>
      </div>

      <!-- Defect Info -->
      <div class="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
        <div>
          <span class="font-medium">Исполнитель:</span>
          <p class="mt-1">{{ defect.assignee || 'Не назначен' }}</p>
        </div>
        <div>
          <span class="font-medium">Проект:</span>
          <p class="mt-1">{{ defect.project_name || 'Не указан' }}</p>
        </div>
        <div>
          <span class="font-medium">Создатель:</span>
          <p class="mt-1">{{ defect.creator_name || 'Неизвестно' }}</p>
        </div>
        <div>
          <span class="font-medium">Срок:</span>
          <p class="mt-1" :class="{ 'text-red-600 font-medium': isOverdue(defect.due_date) }">
            {{ formatDate(defect.due_date) }}
          </p>
        </div>
      </div>

      <!-- Attachments -->
      <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center space-x-4">
          <div v-if="defect.attachments && defect.attachments.length > 0" class="flex items-center">
            <PaperClipIcon class="w-4 h-4 mr-1" />
            {{ defect.attachments.length }}
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import {
  PlayIcon,
  PaperClipIcon
} from '@heroicons/vue/24/outline';
import { useAuth } from '../composables/useAuth';

const { hasRoleId } = useAuth();

interface Defect {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee?: string;
  due_date?: string;
  created_at?: string;
  attachments?: string[];
  project_id: number;
  project_name?: string;
  creator_id: number;
  creator_name?: string;
}

interface Props {
  defect: Defect;
}

defineProps<Props>();
defineEmits<{
  view: [defect: Defect];
  edit: [defect: Defect];
}>();

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
  if (isNaN(date.getTime())) return 'Неверная дата';

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

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>