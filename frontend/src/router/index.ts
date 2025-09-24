import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Projects from '../views/Projects.vue';
import CreateProject from '../views/CreateProject.vue';
import Defects from '../views/Defects.vue';
import Analytics from '../views/Analytics.vue';
import Login from '../views/Login.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
      meta: { requiresAuth: true }
    },
    {
      path: '/projects',
      name: 'Projects',
      component: Projects,
      meta: { requiresAuth: true }
    },
    {
      path: '/create-project',
      name: 'CreateProject',
      component: CreateProject,
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/:id/edit',
      name: 'EditProject',
      component: CreateProject,
      meta: { requiresAuth: true }
    },
    {
      path: '/defects',
      name: 'Defects',
      component: Defects,
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: Analytics,
      meta: { requiresAuth: true }
    },
  ]
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;
