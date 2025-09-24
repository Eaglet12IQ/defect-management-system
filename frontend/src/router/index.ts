import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Projects from '../views/Projects.vue';
import ProjectDetail from '../views/ProjectDetail.vue';
import CreateProject from '../views/CreateProject.vue';
import EditProject from '../views/EditProject.vue';
import CreateDefect from '../views/CreateDefect.vue';
import Defects from '../views/Defects.vue';
import Analytics from '../views/Analytics.vue';
import Login from '../views/Login.vue';
import { useAuth } from '../composables/useAuth';
import { api } from '../utils/api';

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
      meta: { requiresAuth: true, requiresRole: '2,3' }
    },
    {
      path: '/projects/:id',
      name: 'ProjectDetail',
      component: ProjectDetail,
      meta: { requiresAuth: true, requiresRole: '2,3' }
    },
    {
      path: '/create-project',
      name: 'CreateProject',
      component: CreateProject,
      meta: { requiresAuth: true, requiresRole: '3' }
    },
    {
      path: '/projects/:id/edit',
      name: 'EditProject',
      component: EditProject,
      meta: { requiresAuth: true, requiresRole: '3' }
    },
    {
      path: '/defects',
      name: 'Defects',
      component: Defects,
      meta: { requiresAuth: true }
    },
    {
      path: '/defects/:id',
      name: 'DefectDetail',
      component: () => import('../views/DefectDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/defects/:id/edit',
      name: 'EditDefect',
      component: () => import('../views/EditDefect.vue'),
      meta: { requiresAuth: true, requiresRole: '1' }
    },
    {
      path: '/create-defect',
      name: 'CreateDefect',
      component: CreateDefect,
      meta: { requiresAuth: true, requiresRole: '1' }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: Analytics,
      meta: { requiresAuth: true }
    },
  ]
});

// Check if user can edit a project
const canEditProject = async (projectId: string): Promise<boolean> => {
  try {
    // Decode JWT to get user info
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const currentUserId = parseInt(decoded.sub);
    const userRole = decoded.role;

    // Admins can edit any project
    if (userRole === 3) return true;

    // For managers, check if they are the manager of this project
    const response = await api.get(`/projects/${projectId}`);

    if (response.data) {
      const project = response.data;
      return project.manager_id === currentUserId;
    }

    return false;
  } catch (error) {
    console.error('Error checking project permissions:', error);
    return false;
  }
};

// Check if user can view a project
const canViewProject = async (projectId: string): Promise<boolean> => {
  try {
    // Decode JWT to get user info
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const currentUserId = parseInt(decoded.sub);
    const userRole = decoded.role;

    // Admins can view any project
    if (userRole === 3) return true;

    // For managers, check if they are the manager of this project
    const response = await api.get(`/projects/${projectId}`);

    if (response.data) {
      const project = response.data;
      return project.manager_id === currentUserId;
    }

    return false;
  } catch (error) {
    console.error('Error checking project view permissions:', error);
    return false;
  }
};

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  const { hasRole } = useAuth();

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/');
  } else if (to.meta.requiresRole) {
    // Handle comma-separated roles like '2,3'
    const requiredRoles = (to.meta.requiresRole as string).split(',').map(r => r.trim());
    if (!hasRole(requiredRoles)) {
      next('/'); // Redirect to dashboard if user doesn't have required role
    } else {
      next();
    }
  } else if (to.name === 'EditProject') {
    // Check project-specific edit permissions
    const projectId = to.params.id as string;
    const canEdit = await canEditProject(projectId);
    if (!canEdit) {
      next('/projects'); // Redirect to projects list if no edit permission
    } else {
      next();
    }
  } else if (to.name === 'ProjectDetail') {
    // Check project-specific view permissions
    const projectId = to.params.id as string;
    const canView = await canViewProject(projectId);
    if (!canView) {
      next('/projects'); // Redirect to projects list if no view permission
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
