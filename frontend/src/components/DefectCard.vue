<template>
  <div class="bg-white rounded-2xl shadow-card hover:shadow-card-hover transition-all duration-300 overflow-hidden card-hover animate-slide-up hover-lift">
    <!-- Card Header -->
    <div class="p-6 pb-4">
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{{ defect.title }}</h3>
          <p class="text-gray-600 text-sm line-clamp-3 mb-3">{{ defect.description }}</p>
        </div>
        
        <div class="flex flex-col items-end space-y-2 ml-4">
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
          <p class="mt-1">{{ defect.assignee }}</p>
        </div>
        <div>
          <span class="font-medium">Локация:</span>
          <p class="mt-1">{{ defect.location || 'Не указана' }}</p>
        </div>
        <div>
          <span class="font-medium">Категория:</span>
          <p class="mt-1">{{ defect.category }}</p>
        </div>
        <div>
          <span class="font-medium">Срок:</span>
          <p class="mt-1" :class="{ 'text-red-600 font-medium': isOverdue(defect.dueDate) }">
            {{ formatDate(defect.dueDate) }}
          </p>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="defect.tags.length > 0" class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="tag in defect.tags.slice(0, 3)"
          :key="tag"
          class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md"
        >
          {{ tag }}
        </span>
        <span
          v-if="defect.tags.length > 3"
          class="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded-md"
        >
          +{{ defect.tags.length - 3 }}
        </span>
      </div>

      <!-- Attachments & Comments -->
      <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center space-x-4">
          <div v-if="defect.attachments.length > 0" class="flex items-center">
            <PaperClipIcon class="w-4 h-4 mr-1" />
            {{ defect.attachments.length }}
          </div>
          <div v-if="defect.comments.length > 0" class="flex items-center">
            <ChatBubbleLeftIcon class="w-4 h-4 mr-1" />
            {{ defect.comments.length }}
          </div>
        </div>
        
        <span>{{ formatDate(defect.createdAt) }}</span>
      </div>
    </div>

    <!-- Card Footer -->
    <div class="px-6 py-4 bg-gray-50 border-t flex items-center justify-between">
      <div class="text-sm text-gray-600">
        Создал: {{ defect.reporter }}
      </div>
      
      <div class="flex space-x-2">
        <button
          @click="$emit('view', defect)"
          class="p-2 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-primary-50"
          title="Просмотр"
        >
          <EyeIcon class="w-4 h-4" />
        </button>
        <button
          @click="$emit('edit', defect)"
          class="p-2 text-gray-400 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-primary-50"
          title="Редактировать"
        >
          <PencilIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Defect } from '../data/mockData';
import {
  EyeIcon,
  PencilIcon,
  PaperClipIcon,
  ChatBubbleLeftIcon
} from '@heroicons/vue/24/outline';

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