<template>
  <div class="min-h-screen gradient-bg">
    <TheHeader />

    <main class="container-responsive py-8 flex items-center justify-center min-h-[calc(100vh-200px)]">
      <div class="w-full max-w-2xl animate-fade-in">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-center space-x-4 mb-4">
            <router-link
              :to="`/defects/${defectId}`"
              class="text-white/80 hover:text-white transition-colors duration-200 flex items-center space-x-2"
            >
              <ArrowLeftIcon class="w-5 h-5" />
              <span>Назад к дефекту</span>
            </router-link>
          </div>
          <div class="text-center">
            <h2 class="text-3xl font-bold text-white mb-2">Редактирование дефекта</h2>
            <p class="text-white/80">Измените информацию о дефекте</p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="glass rounded-2xl p-8 animate-slide-up text-center">
          <div class="flex items-center justify-center space-x-3 text-white">
            <div class="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Загрузка данных дефекта...</span>
          </div>
        </div>

        <!-- Access Denied State -->
        <div v-else-if="accessDenied" class="glass rounded-2xl p-8 animate-slide-up text-center">
          <div class="text-red-400 mb-4">
            <ExclamationTriangleIcon class="w-16 h-16 mx-auto mb-4" />
            <h3 class="text-xl font-semibold mb-2">Отказано в доступе</h3>
            <p class="mb-6">У вас нет прав для редактирования этого дефекта</p>
          </div>
          <router-link
            to="/defects"
            class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Вернуться к дефектам
          </router-link>
        </div>

        <!-- Error State -->
        <div v-else-if="loadError" class="glass rounded-2xl p-8 animate-slide-up text-center">
          <div class="text-red-400 mb-4">
            <ExclamationTriangleIcon class="w-16 h-16 mx-auto mb-4" />
            <h3 class="text-xl font-semibold mb-2">Ошибка загрузки</h3>
            <p class="mb-6">{{ loadError }}</p>
          </div>
          <router-link
            to="/defects"
            class="bg-white text-primary-600 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            Вернуться к дефектам
          </router-link>
        </div>

        <!-- Edit Defect Form -->
        <div v-else class="glass rounded-2xl p-8 animate-slide-up">
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <!-- Defect Title -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Название дефекта *
              </label>
              <input
                v-model="form.title"
                type="text"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                placeholder="Введите название дефекта"
                :class="{ 'border-red-300 focus:ring-red-500': errors.title }"
              />
              <p v-if="errors.title" class="mt-1 text-sm text-red-400">{{ errors.title }}</p>
            </div>

            <!-- Defect Description -->
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">
                Описание дефекта *
              </label>
              <textarea
                v-model="form.description"
                rows="4"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 resize-none"
                placeholder="Опишите дефект подробно"
                :class="{ 'border-red-300 focus:ring-red-500': errors.description }"
              ></textarea>
              <p v-if="errors.description" class="mt-1 text-sm text-red-400">{{ errors.description }}</p>
            </div>

            <!-- Priority (for all users) -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-white/80 mb-2">
                Приоритет *
              </label>
              <select
                v-model="form.priority"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 appearance-none"
                :class="{ 'border-red-300 focus:ring-red-500': errors.priority }"
              >
                <option value="" disabled>Выберите приоритет</option>
                <option value="Низкий">Низкий</option>
                <option value="Средний">Средний</option>
                <option value="Высокий">Высокий</option>
                <option value="Критический">Критический</option>
              </select>
              <p v-if="errors.priority" class="mt-1 text-sm text-red-400">{{ errors.priority }}</p>
            </div>

            <!-- Status (only for managers and admins) -->
            <div v-if="!hasRole('1')" class="mb-6">
              <label class="block text-sm font-medium text-white/80 mb-2">
                Статус *
              </label>
              <select
                v-model="form.status"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 appearance-none"
                :class="{ 'border-red-300 focus:ring-red-500': errors.status }"
              >
                <option value="" disabled>Выберите статус</option>
                <option value="Новый">Новый</option>
                <option value="В работе">В работе</option>
                <option value="На проверке">На проверке</option>
                <option value="Закрыт">Закрыт</option>
                <option value="Отменен">Отменен</option>
              </select>
              <p v-if="errors.status" class="mt-1 text-sm text-red-400">{{ errors.status }}</p>
            </div>

            <!-- Assignee and Due Date (only for managers and admins) -->
            <div v-if="!hasRole('1')" class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Assignee -->
              <div>
                <label class="block text-sm font-medium text-white/80 mb-2">
                  Исполнитель
                </label>
                <input
                  v-model="form.assignee"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                  placeholder="Имя исполнителя"
                  :class="{ 'border-red-300 focus:ring-red-500': errors.assignee }"
                />
                <p v-if="errors.assignee" class="mt-1 text-sm text-red-400">{{ errors.assignee }}</p>
              </div>

              <!-- Due Date -->
              <div>
                <label class="block text-sm font-medium text-white/80 mb-2">
                  Срок выполнения
                </label>
                <input
                  v-model="form.due_date"
                  type="date"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                  :class="{ 'border-red-300 focus:ring-red-500': errors.due_date }"
                />
                <p v-if="errors.due_date" class="mt-1 text-sm text-red-400">{{ errors.due_date }}</p>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="flex flex-col sm:flex-row sm:justify-end space-y-3 sm:space-y-0 sm:space-x-4 pt-6">
              <router-link
                :to="`/defects/${defectId}`"
                class="px-6 py-3 text-white/80 hover:text-white border border-white/30 rounded-xl font-medium transition-all duration-200 hover:bg-white/10 text-center"
              >
                Отмена
              </router-link>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="bg-primary-600 text-white px-8 py-3 rounded-xl font-medium hover:bg-primary-700 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
              >
                <span v-if="!isSubmitting">Сохранить изменения</span>
                <div v-else class="flex items-center">
                  <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Сохранение...
                </div>
              </button>
            </div>
          </form>

          <!-- Success/Error Messages -->
          <div
            v-if="successMessage"
            class="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ successMessage }}
          </div>
          <div
            v-if="errorMessage"
            class="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ errorMessage }}
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '../utils/api';
import { useAuth } from '../composables/useAuth';
import TheHeader from '../components/TheHeader.vue';
import { ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline';

const { hasRole } = useAuth();

const route = useRoute();
const router = useRouter();
const defectId = route.params.id as string;

interface Defect {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee?: string;
  due_date?: string;
  project_id: number;
  project_name?: string;
  creator_id: number;
  creator_name?: string;
}

const form = reactive({
  title: '',
  description: '',
  status: 'Новый',
  priority: 'Средний',
  assignee: '',
  due_date: ''
});

const errors = reactive({
  title: '',
  description: '',
  status: '',
  priority: '',
  assignee: '',
  due_date: ''
});

const isLoading = ref(true);
const loadError = ref('');
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const accessDenied = ref(false);

// Load defect data on component mount
onMounted(async () => {
  try {
    const response = await api.get(`/defects/${defectId}`);
    if (response.data) {
      const defect: Defect = response.data;

      form.title = defect.title;
      form.description = defect.description;
      form.status = defect.status;
      form.priority = defect.priority;
      form.assignee = defect.assignee || '';
      form.due_date = defect.due_date ? defect.due_date.split('T')[0] : '';
    }
  } catch (error: any) {
    console.error('Error loading defect:', error);
    // Check if it's an access denied error
    if (error.response?.status === 403) {
      accessDenied.value = true;
    } else {
      loadError.value = error.response?.data?.detail || 'Ошибка при загрузке дефекта';
    }
  } finally {
    isLoading.value = false;
  }
});

const validateForm = () => {
  errors.title = '';
  errors.description = '';
  errors.status = '';
  errors.priority = '';

  let isValid = true;

  if (!form.title.trim()) {
    errors.title = 'Название дефекта обязательно для заполнения';
    isValid = false;
  } else if (form.title.trim().length < 3) {
    errors.title = 'Название дефекта должно содержать минимум 3 символа';
    isValid = false;
  }

  if (!form.description.trim()) {
    errors.description = 'Описание дефекта обязательно для заполнения';
    isValid = false;
  } else if (form.description.trim().length < 10) {
    errors.description = 'Описание дефекта должно содержать минимум 10 символов';
    isValid = false;
  }

  // Validate priority for all users
  if (!form.priority) {
    errors.priority = 'Выберите приоритет дефекта';
    isValid = false;
  }

  // Only validate status for managers and admins
  if (!hasRole('1')) {
    if (!form.status) {
      errors.status = 'Выберите статус дефекта';
      isValid = false;
    }
  }

  return isValid;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const defectData: any = {
      defect_id: parseInt(defectId),
      title: form.title.trim(),
      description: form.description.trim(),
      priority: form.priority
    };

    // Only include additional fields for managers and admins
    if (!hasRole('1')) {
      defectData.status = form.status;
      defectData.assignee = form.assignee.trim() || null;
      defectData.due_date = form.due_date || null;
    }

    const response = await api.put('/edit_defect', defectData);

    if (response.error) {
      errorMessage.value = response.error;
    } else {
      successMessage.value = 'Дефект успешно обновлен!';
      // Redirect to defect detail page after a short delay
      setTimeout(() => {
        router.push(`/defects/${defectId}`);
      }, 1500);
    }
  } catch (error: any) {
    console.error('Error updating defect:', error);
    errorMessage.value = error.response?.data?.detail || 'Ошибка при обновлении дефекта';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container-responsive {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

select option:first-child {
  color: #9ca3af;
}
</style>
