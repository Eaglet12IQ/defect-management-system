<template>
  <div class="w-full h-full relative">
    <canvas
      ref="canvasRef"
      class="w-full h-full"
      @mousemove="onMouseMove"
      @mouseleave="onMouseLeave"
    ></canvas>
    
    <!-- Tooltip -->
    <div
      v-if="tooltip.show"
      class="absolute pointer-events-none z-10 bg-black/80 text-white text-xs px-2 py-1 rounded shadow-lg backdrop-blur"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      {{ tooltip.text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive } from 'vue';
import { useCanvas } from '../composables/useCanvas';

interface Props {
  data: Array<{ label: string; value: number; color?: string }>;
  type?: 'bar' | 'line' | 'doughnut';
  animated?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'bar',
  animated: true
});

const { canvasRef, ctx } = useCanvas();
const animationProgress = ref(0);
const tooltip = reactive({
  show: false,
  x: 0,
  y: 0,
  text: ''
});

let animationFrameId: number;

const colors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
];

onMounted(() => {
  if (props.animated) {
    startAnimation();
  } else {
    animationProgress.value = 1;
    drawChart();
  }
});

watch(() => props.data, () => {
  if (props.animated) {
    animationProgress.value = 0;
    startAnimation();
  } else {
    drawChart();
  }
}, { deep: true });

const startAnimation = () => {
  const startTime = Date.now();
  const duration = 1000;

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing function
    animationProgress.value = 1 - Math.pow(1 - progress, 3);
    
    drawChart();
    
    if (progress < 1) {
      animationFrameId = requestAnimationFrame(animate);
    }
  };
  
  animate();
};

const drawChart = () => {
  if (!ctx.value || !canvasRef.value) return;

  const canvas = canvasRef.value;
  const context = ctx.value;
  
  // Clear canvas
  context.clearRect(0, 0, canvas.width, canvas.height);
  
  if (props.data.length === 0) return;

  switch (props.type) {
    case 'bar':
      drawBarChart(context, canvas);
      break;
    case 'line':
      drawLineChart(context, canvas);
      break;
    case 'doughnut':
      drawDoughnutChart(context, canvas);
      break;
  }
};

const drawBarChart = (context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
  const padding = 40;
  const chartWidth = canvas.width - padding * 2;
  const chartHeight = canvas.height - padding * 2;
  const barWidth = chartWidth / props.data.length * 0.8;
  const barSpacing = chartWidth / props.data.length * 0.2;
  
  const maxValue = Math.max(...props.data.map(d => d.value));
  
  props.data.forEach((item, index) => {
    const barHeight = (item.value / maxValue) * chartHeight * animationProgress.value;
    const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
    const y = canvas.height - padding - barHeight;
    
    const gradient = context.createLinearGradient(0, y, 0, y + barHeight);
    const color = item.color || colors[index % colors.length];
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, color + '80');
    
    context.fillStyle = gradient;
    context.fillRect(x, y, barWidth, barHeight);
    
    // Draw labels
    context.fillStyle = '#6b7280';
    context.font = '12px Inter';
    context.textAlign = 'center';
    context.fillText(item.label, x + barWidth / 2, canvas.height - padding / 2);
    
    // Draw values
    context.fillStyle = '#374151';
    context.font = 'bold 11px Inter';
    context.fillText(
      Math.round(item.value * animationProgress.value).toString(),
      x + barWidth / 2,
      y - 5
    );
  });
};

const drawLineChart = (context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
  const padding = 40;
  const chartWidth = canvas.width - padding * 2;
  const chartHeight = canvas.height - padding * 2;
  
  const maxValue = Math.max(...props.data.map(d => d.value));
  const stepX = chartWidth / (props.data.length - 1);
  
  // Draw grid lines
  context.strokeStyle = '#e5e7eb';
  context.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = padding + (chartHeight / 5) * i;
    context.beginPath();
    context.moveTo(padding, y);
    context.lineTo(canvas.width - padding, y);
    context.stroke();
  }
  
  // Draw line
  context.strokeStyle = '#3b82f6';
  context.lineWidth = 3;
  context.beginPath();
  
  const animatedLength = props.data.length * animationProgress.value;
  
  props.data.forEach((item, index) => {
    if (index > animatedLength) return;
    
    const x = padding + index * stepX;
    const y = canvas.height - padding - (item.value / maxValue) * chartHeight;
    
    if (index === 0) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  });
  
  context.stroke();
  
  // Draw points
  props.data.forEach((item, index) => {
    if (index > animatedLength) return;
    
    const x = padding + index * stepX;
    const y = canvas.height - padding - (item.value / maxValue) * chartHeight;
    
    context.fillStyle = '#3b82f6';
    context.beginPath();
    context.arc(x, y, 4, 0, 2 * Math.PI);
    context.fill();
    
    // Draw labels
    context.fillStyle = '#6b7280';
    context.font = '12px Inter';
    context.textAlign = 'center';
    context.fillText(item.label, x, canvas.height - padding / 2);
  });
};

const drawDoughnutChart = (context: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(canvas.width, canvas.height) / 3;
  const innerRadius = radius * 0.6;
  
  const total = props.data.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = -Math.PI / 2;
  
  props.data.forEach((item, index) => {
    const sliceAngle = (item.value / total) * 2 * Math.PI * animationProgress.value;
    const color = item.color || colors[index % colors.length];
    
    // Draw slice
    context.fillStyle = color;
    context.beginPath();
    context.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
    context.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
    context.closePath();
    context.fill();
    
    // Draw label
    const labelAngle = currentAngle + sliceAngle / 2;
    const labelRadius = radius + 20;
    const labelX = centerX + Math.cos(labelAngle) * labelRadius;
    const labelY = centerY + Math.sin(labelAngle) * labelRadius;
    
    context.fillStyle = '#374151';
    context.font = '12px Inter';
    context.textAlign = 'center';
    context.fillText(item.label, labelX, labelY);
    
    currentAngle += sliceAngle;
  });
  
  // Draw center text
  context.fillStyle = '#1f2937';
  context.font = 'bold 16px Inter';
  context.textAlign = 'center';
  context.fillText('Общее', centerX, centerY - 10);
  context.font = '20px Inter';
  context.fillText(Math.round(total * animationProgress.value).toString(), centerX, centerY + 10);
};

const onMouseMove = (event: MouseEvent) => {
  if (!canvasRef.value) return;
  
  const rect = canvasRef.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  
  // Simple tooltip logic for bar charts
  if (props.type === 'bar') {
    const padding = 40;
    const chartWidth = canvasRef.value.width - padding * 2;
    const barWidth = chartWidth / props.data.length * 0.8;
    const barSpacing = chartWidth / props.data.length * 0.2;
    
    for (let i = 0; i < props.data.length; i++) {
      const barX = padding + i * (barWidth + barSpacing) + barSpacing / 2;
      
      if (x >= barX && x <= barX + barWidth) {
        tooltip.show = true;
        tooltip.x = event.clientX - rect.left;
        tooltip.y = event.clientY - rect.top - 30;
        tooltip.text = `${props.data[i].label}: ${props.data[i].value}`;
        return;
      }
    }
  }
  
  tooltip.show = false;
};

const onMouseLeave = () => {
  tooltip.show = false;
};
</script>