export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'manager' | 'engineer' | 'observer';
  avatar?: string;
  department?: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'completed' | 'paused';
  manager: string;
  startDate: string;
  endDate?: string;
  progress: number;
  defectsCount: number;
  team: User[];
}

export interface Defect {
  id: string;
  title: string;
  description: string;
  status: 'new' | 'in-progress' | 'review' | 'closed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  projectId: string;
  assignee: string;
  reporter: string;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  location?: string;
  category: string;
  attachments: string[];
  comments: Comment[];
  tags: string[];
}

export interface Comment {
  id: string;
  author: string;
  content: string;
  createdAt: string;
  attachments?: string[];
}

export interface Stats {
  totalDefects: number;
  newDefects: number;
  inProgressDefects: number;
  closedDefects: number;
  criticalDefects: number;
  overdueTasks: number;
  activeProjects: number;
  completionRate: number;
}

// Mock Users
export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Александр Петров',
    email: 'a.petrov@systemcontrol.ru',
    role: 'manager',
    avatar: 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2',
    department: 'Управление проектами'
  },
  {
    id: '2',
    name: 'Мария Иванова',
    email: 'm.ivanova@systemcontrol.ru',
    role: 'engineer',
    avatar: 'https://images.pexels.com/photos/3763188/pexels-photo-3763188.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2',
    department: 'Инженерный отдел'
  },
  {
    id: '3',
    name: 'Дмитрий Смирнов',
    email: 'd.smirnov@systemcontrol.ru',
    role: 'engineer',
    avatar: 'https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2',
    department: 'Инженерный отдел'
  },
  {
    id: '4',
    name: 'Елена Козлова',
    email: 'e.kozlova@systemcontrol.ru',
    role: 'observer',
    avatar: 'https://images.pexels.com/photos/3992656/pexels-photo-3992656.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=2',
    department: 'Контроль качества'
  }
];

// Mock Projects
export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'ЖК "Северная звезда"',
    description: 'Жилой комплекс премиум-класса из 3 корпусов',
    status: 'active',
    manager: 'Александр Петров',
    startDate: '2024-01-15',
    endDate: '2024-12-15',
    progress: 65,
    defectsCount: 23,
    team: mockUsers.slice(0, 3)
  },
  {
    id: '2',
    name: 'Бизнес-центр "Прогресс"',
    description: '15-этажное офисное здание класса A',
    status: 'active',
    manager: 'Александр Петров',
    startDate: '2024-02-01',
    endDate: '2024-10-01',
    progress: 42,
    defectsCount: 17,
    team: [mockUsers[0], mockUsers[2], mockUsers[3]]
  },
  {
    id: '3',
    name: 'Торговый комплекс "Центр"',
    description: 'Многофункциональный торговый центр',
    status: 'planning',
    manager: 'Александр Петров',
    startDate: '2024-04-01',
    endDate: '2025-02-01',
    progress: 15,
    defectsCount: 3,
    team: [mockUsers[0], mockUsers[1]]
  }
];

// Mock Defects
export const mockDefects: Defect[] = [
  {
    id: '1',
    title: 'Трещина в стене на 5 этаже',
    description: 'Обнаружена горизонтальная трещина длиной около 1.2 метра в несущей стене корпуса А, 5 этаж, квартира 51.',
    status: 'new',
    priority: 'high',
    projectId: '1',
    assignee: 'Мария Иванова',
    reporter: 'Елена Козлова',
    createdAt: '2024-01-20T09:30:00Z',
    updatedAt: '2024-01-20T09:30:00Z',
    dueDate: '2024-01-25T18:00:00Z',
    location: 'Корпус А, 5 этаж, кв. 51',
    category: 'Конструктивные дефекты',
    attachments: ['crack_photo_1.jpg', 'crack_photo_2.jpg'],
    tags: ['стена', 'трещина', 'несущая'],
    comments: [
      {
        id: '1',
        author: 'Елена Козлова',
        content: 'Дефект обнаружен во время планового обхода. Требует немедленного внимания.',
        createdAt: '2024-01-20T09:35:00Z'
      }
    ]
  },
  {
    id: '2',
    title: 'Протечка кровли в корпусе Б',
    description: 'Протечка воды через кровельное покрытие в районе технического этажа. Возможное нарушение гидроизоляции.',
    status: 'in-progress',
    priority: 'critical',
    projectId: '1',
    assignee: 'Дмитрий Смирнов',
    reporter: 'Мария Иванова',
    createdAt: '2024-01-18T14:20:00Z',
    updatedAt: '2024-01-21T10:15:00Z',
    dueDate: '2024-01-22T18:00:00Z',
    location: 'Корпус Б, технический этаж',
    category: 'Кровельные работы',
    attachments: ['leak_photo.jpg', 'roof_damage.jpg'],
    tags: ['кровля', 'протечка', 'гидроизоляция'],
    comments: [
      {
        id: '2',
        author: 'Мария Иванова',
        content: 'Протечка усилилась после последних дождей.',
        createdAt: '2024-01-18T14:25:00Z'
      },
      {
        id: '3',
        author: 'Дмитрий Смирнов',
        content: 'Начал осмотр кровли. Предварительно - повреждение в районе примыкания.',
        createdAt: '2024-01-21T10:20:00Z'
      }
    ]
  },
  {
    id: '3',
    title: 'Неровность пола в офисном блоке',
    description: 'Значительные перепады уровня пола в офисных помещениях 3-го этажа. Превышение допустимых норм.',
    status: 'review',
    priority: 'medium',
    projectId: '2',
    assignee: 'Мария Иванова',
    reporter: 'Александр Петров',
    createdAt: '2024-01-19T11:45:00Z',
    updatedAt: '2024-01-22T16:30:00Z',
    dueDate: '2024-01-28T18:00:00Z',
    location: '3 этаж, офисный блок',
    category: 'Отделочные работы',
    attachments: ['floor_measurement.pdf'],
    tags: ['пол', 'неровность', 'офис'],
    comments: []
  },
  {
    id: '4',
    title: 'Неисправность вентиляционной системы',
    description: 'Отсутствует тяга в вентиляционных каналах подземного паркинга. Нарушение воздухообмена.',
    status: 'closed',
    priority: 'high',
    projectId: '1',
    assignee: 'Дмитрий Смирнов',
    reporter: 'Елена Козлова',
    createdAt: '2024-01-15T08:30:00Z',
    updatedAt: '2024-01-22T14:45:00Z',
    dueDate: '2024-01-20T18:00:00Z',
    location: 'Подземный паркинг',
    category: 'Инженерные системы',
    attachments: ['ventilation_report.pdf'],
    tags: ['вентиляция', 'паркинг', 'воздухообмен'],
    comments: [
      {
        id: '4',
        author: 'Дмитрий Смирнов',
        content: 'Проблема решена. Прочищены вентканалы, заменены поврежденные элементы.',
        createdAt: '2024-01-22T14:45:00Z'
      }
    ]
  }
];

// Mock Stats
export const mockStats: Stats = {
  totalDefects: 43,
  newDefects: 8,
  inProgressDefects: 12,
  closedDefects: 21,
  criticalDefects: 3,
  overdueTasks: 2,
  activeProjects: 2,
  completionRate: 78.5
};

export const currentUser = mockUsers[0];