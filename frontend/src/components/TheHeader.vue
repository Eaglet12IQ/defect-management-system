<template>
  <header class="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-40">
    <div class="container-responsive">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
            <BuildingOfficeIcon class="w-6 h-6 text-white" />
          </div>
          <div class="hidden sm:block">
            <h1 class="text-xl font-bold text-white">СистемаКонтроля</h1>
            <p class="text-sm text-white/70">Управление дефектами</p>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center justify-center space-x-1 flex-1">
          <router-link
            v-for="item in navigationItems"
            :key="item.name"
            :to="item.path"
            class="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200 transform hover:scale-105"
            :class="{ 'bg-white/20 text-white': $route.path === item.path }"
          >
            <component :is="item.icon" class="w-4 h-4 inline-block mr-2" />
            {{ item.name }}
          </router-link>
        </nav>

        <!-- User Menu -->
          <div class="flex items-center space-x-1">
          <!-- User Avatar -->
  <div
    class="flex items-center space-x-1 rounded-lg p-2"
  >
    <img
      :src="userData?.avatar || 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=40&h=40&dpr=2'"
      :alt="userData?.username"
      class="w-8 h-8 rounded-full border-2 border-white/20 hover:border-white/40 transition-all duration-200"
    />
    <div class="hidden sm:block flex items-center h-9">
      <p class="text-sm font-medium text-white hover:text-white/80 transition-colors duration-200 leading-8">
        {{ userData?.username }}
      </p>
    </div>
    <button
      @click="handleLogout"
      title="Выйти из аккаунта"
      class="ml-3 p-1 rounded-md text-white hover:text-red-500 transition-colors duration-200"
    >
      <ArrowRightOnRectangleIcon class="w-6 h-6" />
    </button>
  </div>

          <!-- Mobile menu button -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200"
          >
            <Bars3Icon v-if="!showMobileMenu" class="w-6 h-6" />
            <XMarkIcon v-else class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-show="showMobileMenu" class="md:hidden mt-2 pb-4">
          <div class="flex flex-col space-y-2">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.path"
              @click="showMobileMenu = false"
              class="flex items-center px-4 py-3 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200"
              :class="{ 'bg-white/20 text-white': $route.path === item.path }"
            >
              <component :is="item.icon" class="w-5 h-5 mr-3" />
              {{ item.name }}
            </router-link>
            <button
              @click="handleLogout"
              class="flex items-center px-4 py-3 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 transition-all duration-200"
            >
              <ArrowRightOnRectangleIcon class="w-5 h-5 mr-3" />
              Выйти
            </button>
          </div>
        </div>
      </transition>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import {
  BuildingOfficeIcon,
  HomeIcon,
  FolderOpenIcon,
  ExclamationTriangleIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline';

const decodeJWT = (token: string) => {
  const payload = token.split('.')[1];
  const decoded = JSON.parse(atob(payload));
  return decoded;
};

const userData = computed(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    return decodeJWT(token);
  }
  return null;
});

const { logout } = useAuth();
const router = useRouter();
const showMobileMenu = ref(false);

const navigationItems = computed(() => {
  const allItems = [
    { name: 'Дашборд', path: '/', icon: HomeIcon },
    { name: 'Проекты', path: '/projects', icon: FolderOpenIcon },
    { name: 'Дефекты', path: '/defects', icon: ExclamationTriangleIcon },
  ];

  // Role 4 (some special role) - only dashboard
  if (userData.value?.role === 4) {
    return allItems.filter(item => item.name === 'Дашборд');
  }

  // Role 1 (Engineers) - hide Projects navigation
  if (userData.value?.role === 1) {
    return allItems.filter(item => item.name !== 'Проекты');
  }

  return allItems;
});

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
};

const goToProfile = () => {
  router.push('/profile');
};

const handleLogout = async () => {
  await logout();
  router.push('/login');
};
</script>