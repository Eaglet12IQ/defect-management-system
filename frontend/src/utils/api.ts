const API_BASE_URL = 'http://localhost:8000/api';

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    // Check for new access token in headers
    const newToken = response.headers.get('New-Access-Token');
    if (newToken) {
      localStorage.setItem('access_token', newToken);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      let errorMessage: string;
      if (Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((d: any) => d.msg.replace('Value error, ', '')).join(', ');
      } else {
        errorMessage = errorData.detail || `HTTP ${response.status}`;
      }
      return { error: errorMessage };
    }

    const data = await response.json();
    return { data };
  }

  async post<T = any>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        credentials: 'include', // Include cookies for refresh token
        body: JSON.stringify(body),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  async get<T = any>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
        credentials: 'include',
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  async put<T = any>(endpoint: string, body: any): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        credentials: 'include', // Include cookies for refresh token
        body: JSON.stringify(body),
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  // Add other methods as needed (DELETE, etc.)
}

export const api = new ApiClient(API_BASE_URL);
