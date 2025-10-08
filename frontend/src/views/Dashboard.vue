<template>
  <div class="h-screen flex flex-col gradient-bg">
    <TheHeader />

    <main class="flex-1 container-responsive py-8 overflow-hidden">
      <!-- Welcome Section -->
      <div class="mb-8 animate-fade-in">
        <h2 class="text-3xl font-bold text-white mb-2">
          {{ safeUserRole === 4 ? 'Добро пожаловать, Super Admin!' : `Добро пожаловать, ${fio || currentUser?.username || 'Пользователь'}!` }}
        </h2>
      </div>

      <!-- Register New User Form (for role 4) -->
      <div v-if="userRole === 4" class="glass rounded-2xl p-4 mb-4 animate-slide-up max-h-96 overflow-y-auto">
        <h3 class="text-lg font-semibold text-white mb-4">Регистрация нового пользователя</h3>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Username</label>
              <input
                v-model="registerForm.username"
                type="text"
                required
                class="w-full px-3 py-2 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                placeholder="username"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Email</label>
              <input
                v-model="registerForm.email"
                type="email"
                required
                class="w-full px-3 py-2 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105"
                placeholder="email@example.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Фамилия</label>
              <input
                v-model="registerForm.last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                placeholder="Фамилия"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Имя</label>
              <input
                v-model="registerForm.first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                placeholder="Имя"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Отчество</label>
              <input
                v-model="registerForm.middle_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                placeholder="Отчество"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Аватар</label>
              <input
                ref="avatarInput"
                type="file"
                accept="image/*"
                @change="handleAvatarChange"
                class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Роль</label>
              <select
                v-model="registerForm.role"
                required
                class="w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-400 focus:scale-105 appearance-none"
              >
                <option value="" disabled>Выберите роль</option>
                <option value="1">Инженер</option>
                <option value="2">Менеджер</option>
                <option value="3">Руководитель</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Пароль</label>
              <input
                v-model="registerForm.password"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Повторите пароль</label>
              <input
                v-model="registerForm.re_password"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 hover:border-gray-300 focus:scale-105"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="isRegistering"
              class="bg-primary-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-primary-700 transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="!isRegistering">Зарегистрировать</span>
              <div v-else class="flex items-center">
                <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Регистрация...
              </div>
            </button>
          </div>

          <!-- Register Error/Success Message -->
          <div
            v-if="registerError"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            {{ registerError }}
          </div>
          <div
            v-if="registerSuccess"
            class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm animate-slide-down"
          >
            Пользователь успешно зарегистрирован!
          </div>
        </form>
      </div>

      <!-- Main Content Grid -->
      <div v-if="userRole !== 4" class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <!-- Defects Section -->
        <div class="lg:col-span-2">
          <!-- For Managers: Two separate blocks -->
          <div v-if="userRole === 2" class="space-y-6">
            <!-- New Defects -->
            <div class="glass rounded-2xl p-6 animate-slide-up">
              <div class="flex items-center mb-6">
                <h3 class="text-xl font-semibold text-blue-800 border-blue-200 border-b-4 pb-2">Новые дефекты</h3>
              </div>

              <div class="custom-scroll max-h-64 overflow-y-auto space-y-4">
                <div
                  v-if="newDefects.length === 0"
                  class="text-center text-gray-600 py-8"
                >
                  Нет новых дефектов
                </div>
                <div
                  v-for="(defect, index) in newDefects"
                  :key="defect.id"
                  class="flex items-start p-5 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 cursor-pointer"
                  @click="viewDefect(defect)"
                >
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h4 class="text-base font-medium text-gray-900 truncate">
                          {{ defect.title }}
                        </h4>
                        <p class="text-sm text-gray-700 mt-1 line-clamp-2 leading-1.4">
                          {{ defect.description }}
                        </p>
                        <div class="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                          <span>{{ defect.location }}</span>
                          <span>{{ formatDate(defect.due_date) }}</span>
                        </div>
                      </div>

                      <div class="flex flex-col items-end space-y-1 ml-4">
                        <span
                          class="px-2 py-1 text-sm font-medium rounded-full border"
                          :class="getPriorityClass(defect.priority)"
                        >
                          {{ getPriorityText(defect.priority) }}
                        </span>
                        <span class="text-sm text-gray-600">{{ defect.assignee }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Under Review Defects -->
            <div class="glass rounded-2xl p-6 animate-slide-up">
              <div class="flex items-center mb-6">
                <h3 class="text-xl font-semibold text-purple-800 border-purple-200 border-b-4 pb-2">Дефекты на проверке</h3>
              </div>

              <div class="custom-scroll max-h-64 overflow-y-auto space-y-4">
                <div
                  v-if="underReviewDefects.length === 0"
                  class="text-center text-gray-600 py-8"
                >
                  Нет дефектов на проверке
                </div>
                <div
                  v-for="(defect, index) in underReviewDefects"
                  :key="defect.id"
                  class="flex items-start p-5 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 cursor-pointer"
                  @click="viewDefect(defect)"
                >
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <h4 class="text-base font-medium text-gray-900 truncate">
                          {{ defect.title }}
                        </h4>
                        <p class="text-sm text-gray-700 mt-1 line-clamp-2 leading-1.4">
                          {{ defect.description }}
                        </p>
                        <div class="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                          <span>{{ defect.location }}</span>
                          <span>{{ formatDate(defect.due_date) }}</span>
                        </div>
                      </div>

                      <div class="flex flex-col items-end space-y-1 ml-4">
                        <span
                          class="px-2 py-1 text-sm font-medium rounded-full border"
                          :class="getPriorityClass(defect.priority)"
                        >
                          {{ getPriorityText(defect.priority) }}
                        </span>
                        <span class="text-sm text-gray-600">{{ defect.assignee }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- For Engineers: Recent Defects -->
          <div v-if="userRole === 1" class="glass rounded-2xl p-6 animate-slide-up">
            <div class="flex items-center mb-6">
              <h3 class="text-xl font-semibold text-yellow-800 border-yellow-200 border-b-4 pb-2">Дефекты в работе</h3>
            </div>

            <div class="custom-scroll max-h-64 overflow-y-auto space-y-4">
              <div
                v-if="recentDefects.length === 0"
                class="text-center text-gray-600 py-8"
              >
                Нет дефектов для отображения
              </div>
              <div
                v-for="(defect, index) in recentDefects"
                :key="defect.id"
                class="flex items-start p-5 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 cursor-pointer"
                @click="viewDefect(defect)"
              >
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <h4 class="text-base font-medium text-gray-900 truncate">
                        {{ defect.title }}
                      </h4>
                      <p class="text-sm text-gray-700 mt-1 line-clamp-2 leading-1.4">
                        {{ defect.description }}
                      </p>
                      <div class="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <span>{{ defect.location }}</span>
                        <span>{{ formatDate(defect.due_date) }}</span>
                      </div>
                    </div>

                    <div class="flex flex-col items-end space-y-1 ml-4">
                      <span
                        class="px-2 py-1 text-sm font-medium rounded-full border"
                        :class="getPriorityClass(defect.priority)"
                      >
                        {{ getPriorityText(defect.priority) }}
                      </span>
                      <span class="text-sm text-gray-600">{{ defect.assignee }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- For Leaders: Charts -->
          <div v-if="userRole === 3" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Defect Status Chart -->
            <div class="glass rounded-2xl p-4 animate-slide-up flex flex-col h-80">
              <h3 class="text-lg font-semibold text-white mb-3 flex-shrink-0">Распределение дефектов по статусам</h3>
              <div class="flex-1 min-h-0">
                <canvas ref="defectStatusChart" class="w-full h-full"></canvas>
              </div>
            </div>

            <!-- Defect Priority Chart -->
            <div class="glass rounded-2xl p-4 animate-slide-up flex flex-col h-80">
              <h3 class="text-lg font-semibold text-white mb-3 flex-shrink-0">Распределение дефектов по приоритетам</h3>
              <div class="flex-1 min-h-0">
                <canvas ref="defectPriorityChart" class="w-full h-full"></canvas>
              </div>
            </div>

            <!-- Project Status Chart -->
            <div class="glass rounded-2xl p-4 animate-slide-up flex flex-col h-80">
              <h3 class="text-lg font-semibold text-white mb-3 flex-shrink-0">Распределение проектов по статусам</h3>
              <div class="flex-1 min-h-0">
                <canvas ref="projectStatusChart" class="w-full h-full"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Stats -->
        <div class="space-y-6">
          <!-- Team Activity -->
          <div class="glass rounded-2xl p-6 animate-slide-up-delay-3">
            <h3 class="text-lg font-semibold text-white mb-4">Активность команды</h3>
            <div class="custom-scroll max-h-64 overflow-y-auto space-y-1">
              <div
                v-for="(activity, index) in teamActivity"
                :key="activity.id"
                class="flex items-center space-x-3 cursor-pointer hover:bg-white/10 transition-colors rounded-lg p-2"
                @click="viewActivity(activity)"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-white">
                    {{ activity.action }}
                    <br />
                    <span v-if="activity.changes_detail !== 'Нет данных об изменениях'" class="text-xs text-white/70 block break-words max-w-full" v-html="activity.changes_detail"></span>
                  </p>
                  <p class="text-xs text-white/70">{{ new Date(activity.timestamp).toLocaleString('ru-RU') }}</p>
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
import { computed, onMounted, ref, reactive, type Ref, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import { mockStats, mockDefects, type Defect } from '../data/mockData';
import { api } from '../utils/api';
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

const router = useRouter();

const { currentUser, hasRole } = useAuth();

const decodeJWT = (token: string) => {
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const payload = JSON.parse(atob(parts[1]));
    return payload;
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

const userRole = computed(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    const role = decodeJWT(token)?.role;
    return role ? parseInt(String(role)) : null;
  }
  return null;
});

// Helper computed for template usage to avoid type errors
const safeUserRole = computed(() => userRole.value || 0);

const stats = mockStats;
const fio = ref<string>('');
const teamActivity = ref<any[]>([]);

const registerForm = reactive({
  username: '' as string,
  email: '' as string,
  password: '' as string,
  re_password: '' as string,
  first_name: '' as string,
  last_name: '' as string,
  middle_name: '' as string,
  avatar: null as File | null,
  role: '' as string
});

const avatarInput = ref<HTMLInputElement | null>(null);

const isRegistering = ref(false);
const registerError = ref('');
const registerSuccess = ref(false);

const handleAvatarChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    registerForm.avatar = target.files[0];
  } else {
    registerForm.avatar = null;
  }
};

onMounted(async () => {
  const response = await api.get('/dashboard');
  if (response.data) {
    fio.value = response.data.fio || '';
    if (response.data.team_activity) {
      teamActivity.value = response.data.team_activity.map((a: any) => ({
        id: a.record_id,
        table_name: a.table_name,
        action: a.action,
        comment: a.comment,
        timestamp: a.timestamp,
        changes_detail: a.changes_detail,
        avatar: '' // Placeholder, can be enhanced to fetch user avatar if available
      }));
    }
    recentDefects.value = response.data.recent_defects || [];
    newDefects.value = response.data.new_defects || [];
    underReviewDefects.value = response.data.under_review_defects || [];

    // Chart data for leaders
    if (userRole.value === 3) {
      defectStatusChartData.value = response.data.defect_status_chart || [];
      defectPriorityChartData.value = response.data.defect_priority_chart || [];
      projectStatusChartData.value = response.data.project_status_chart || [];

      // Render charts after data is loaded
      nextTick(() => {
        renderCharts();
      });
    }
  }
});

const handleRegister = async () => {
  isRegistering.value = true;
  registerError.value = '';
  registerSuccess.value = false;

  try {
  // Prepare form data for multipart/form-data
  const formData = new FormData();
  formData.append('username', registerForm.username);
  formData.append('email', registerForm.email);
  formData.append('password', registerForm.password);
  formData.append('re_password', registerForm.re_password);
  if (registerForm.first_name !== undefined && registerForm.first_name !== null) formData.append('first_name', registerForm.first_name);
  if (registerForm.last_name !== undefined && registerForm.last_name !== null) formData.append('last_name', registerForm.last_name);
  if (registerForm.middle_name !== undefined && registerForm.middle_name !== null) formData.append('middle_name', registerForm.middle_name);
  if (registerForm.avatar) formData.append('avatar', registerForm.avatar);
  if (registerForm.role !== undefined && registerForm.role !== null) formData.append('role', registerForm.role);

  // Add access token to headers
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    body: formData,
    headers,
    credentials: 'include',
  });

  if (response.ok) {
    registerSuccess.value = true;
    registerForm.username = '';
    registerForm.email = '';
    registerForm.password = '';
    registerForm.re_password = '';
    registerForm.first_name = '';
    registerForm.last_name = '';
    registerForm.middle_name = '';
    registerForm.avatar = null;
    registerForm.role = '';
    if (avatarInput.value) avatarInput.value.value = '';
  } else {
    const data = await response.json();
    registerError.value = data.detail ?? 'Ошибка при регистрации';
  }
  } catch (error: any) {
    registerError.value = error.response?.data?.detail ?? 'Ошибка при регистрации';
  } finally {
    isRegistering.value = false;
  }
};

const recentDefects = ref<any[]>([]);
const newDefects = ref<any[]>([]);
const underReviewDefects = ref<any[]>([]);
const isLoadingDefects = ref(true);

// Chart data for leaders
const defectStatusChartData = ref<any[]>([]);
const defectPriorityChartData = ref<any[]>([]);
const projectStatusChartData = ref<any[]>([]);

// Chart refs
const defectStatusChart = ref<HTMLCanvasElement | null>(null);
const defectPriorityChart = ref<HTMLCanvasElement | null>(null);
const projectStatusChart = ref<HTMLCanvasElement | null>(null);





const getStatusColor = (status: string) => {
  const colors = {
    'Новый': '#1e40af', // blue-800
    'В работе': '#92400e', // yellow-800
    'На проверке': '#6b21a8', // purple-800
    'Закрыт': '#166534', // green-800
    'Отменен': '#991b1b' // red-800
  };
  return colors[status as keyof typeof colors] || '#6b7280'; // gray-500 as fallback
};

const getPriorityColor = (priority: string) => {
  const colors = {
    'Низкий': '#15803d', // green-700
    'Средний': '#a16207', // yellow-700
    'Высокий': '#c2410c', // orange-700
    'Критический': '#b91c1c' // red-700
  };
  return colors[priority as keyof typeof colors] || '#6b7280'; // gray-500 as fallback
};

const getProjectStatusColor = (status: string) => {
  const colors = {
    'Планирование': '#3b82f6', // blue-500
    'Активный': '#fbbf24', // yellow-400
    'Завершен': '#10b981', // emerald-500
    'Приостановлен': '#ef4444' // red-500
  };
  return colors[status as keyof typeof colors] || '#6b7280'; // gray-500 as fallback
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
  router.push(`/defects/${defect.id}`);
};

const navigateToCreateProject = () => {
  router.push('/create-project');
};

const navigateToCreateDefect = () => {
  router.push('/create-defect');
};

const viewActivity = (activity: any) => {
  if (activity.table_name === 'defects') {
    router.push(`/defects/${activity.id}`);
  } else if (activity.table_name === 'projects') {
    router.push(`/projects/${activity.id}`);
  }
};

// Chart rendering logic
import Chart from 'chart.js/auto';


const renderCharts = () => {
  if (defectStatusChart.value) {
    new Chart(defectStatusChart.value, {
      type: 'doughnut',
      data: {
        labels: defectStatusChartData.value.map(item => item.status),
        datasets: [{
          data: defectStatusChartData.value.map(item => item.count),
          backgroundColor: defectStatusChartData.value.map(item => getStatusColor(item.status)),
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: 'white'
            }
          }
        }
      }
    });
  }

  if (defectPriorityChart.value) {
    new Chart(defectPriorityChart.value, {
      type: 'doughnut',
      data: {
        labels: defectPriorityChartData.value.map(item => item.priority),
        datasets: [{
          data: defectPriorityChartData.value.map(item => item.count),
          backgroundColor: defectPriorityChartData.value.map(item => getPriorityColor(item.priority)),
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: 'white'
            }
          }
        }
      }
    });
  }

  if (projectStatusChart.value) {
    new Chart(projectStatusChart.value, {
      type: 'doughnut',
      data: {
        labels: projectStatusChartData.value.map(item => item.status),
        datasets: [{
          data: projectStatusChartData.value.map(item => item.count),
          backgroundColor: projectStatusChartData.value.map(item => getProjectStatusColor(item.status)),
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: 'white'
            }
          }
        }
      }
    });
  }
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

select option:first-child {
  color: #9ca3af;
}

/* Custom scrollbar for team activity */
.custom-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.5) transparent;
  border: none;
}

.custom-scroll::-webkit-scrollbar {
  width: 10px;
  background: transparent;
}

.custom-scroll::-webkit-scrollbar-track {
  background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
  border-radius: 12px;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #a3bffa, #3b82f6);
  border-radius: 12px;
  box-shadow: 0 0 6px #3b82f6;
  border: 2px solid transparent;
  background-clip: content-box;
  transition: background 0.3s ease;
}

.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #2563eb, #1e40af);
  box-shadow: 0 0 8px #1e40af;
}
</style>