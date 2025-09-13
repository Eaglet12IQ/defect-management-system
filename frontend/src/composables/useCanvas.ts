import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useCanvas() {
  const canvasRef = ref<HTMLCanvasElement | null>(null);
  const ctx = ref<CanvasRenderingContext2D | null>(null);

  const initCanvas = () => {
    if (canvasRef.value) {
      ctx.value = canvasRef.value.getContext('2d');
      return ctx.value;
    }
    return null;
  };

  const resizeCanvas = () => {
    if (canvasRef.value) {
      const container = canvasRef.value.parentElement;
      if (container) {
        canvasRef.value.width = container.clientWidth;
        canvasRef.value.height = container.clientHeight;
      }
    }
  };

  onMounted(() => {
    initCanvas();
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeCanvas);
  });

  return {
    canvasRef,
    ctx,
    initCanvas,
    resizeCanvas
  };
}