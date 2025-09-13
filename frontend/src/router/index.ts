import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Projects from '../views/Projects.vue';
import Defects from '../views/Defects.vue';
import Analytics from '../views/Analytics.vue';
import Profile from '../views/Profile.vue';
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
      component: Dashboard
    },
    {
      path: '/projects',
      name: 'Projects',
      component: Projects
    },
    {
      path: '/defects',
      name: 'Defects',
      component: Defects
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: Analytics
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile
    }
  ]
});

export default router;