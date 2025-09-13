<template>
  <div class="glass rounded-2xl p-6 card-hover animate-slide-up">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-white/80 mb-1">{{ title }}</p>
        <div class="flex items-baseline space-x-2">
          <p class="text-2xl font-bold text-white">{{ displayValue }}</p>
          <span
            v-if="change !== undefined"
            class="text-sm font-medium flex items-center"
            :class="change >= 0 ? 'text-green-600' : 'text-red-600'"
          >
            <component
              :is="change >= 0 ? ArrowUpIcon : ArrowDownIcon"
              class="w-4 h-4 mr-1"
            />
            {{ Math.abs(change) }}%
          </span>
        </div>
        
        <!-- Progress bar for percentage values -->
        <div v-if="showProgress && maxValue" class="mt-3">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="h-2 rounded-full transition-all duration-1000 ease-out"
              :class="getProgressColor()"
              :style="{ width: `${(parseFloat(value.toString()) / maxValue) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
      
      <div class="flex-shrink-0 ml-4">
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center"
          :class="getIconBackground()"
        >
          <component :is="icon" class="w-6 h-6" :class="getIconColor()" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/24/outline';

interface Props {
  title: string;
  value: number | string;
  icon: any;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  change?: number;
  showProgress?: boolean;
  maxValue?: number;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  showProgress: false
});

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString();
  }
  return props.value;
});

const getIconBackground = () => {
  const backgrounds = {
    primary: 'bg-primary-100',
    secondary: 'bg-secondary-100',
    success: 'bg-green-100',
    warning: 'bg-yellow-100',
    danger: 'bg-red-100'
  };
  return backgrounds[props.variant];
};

const getIconColor = () => {
  const colors = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600'
  };
  return colors[props.variant];
};

const getProgressColor = () => {
  const colors = {
    primary: 'bg-primary-500',
    secondary: 'bg-secondary-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500'
  };
  return colors[props.variant];
};
</script>