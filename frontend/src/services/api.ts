import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  User, 
  Mission, 
  ThreatIntelligence, 
  Incident, 
  ComplianceFramework, 
  SystemHealth,
  ApiResponse,
  PaginatedResponse 
} from '../types';
import { getSecureStorage, removeSecureStorage } from '../lib/utils';
import toast from 'react-hot-toast';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        const token = getSecureStorage<string>('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          removeSecureStorage('auth_token');
          removeSecureStorage('refresh_token');
          removeSecureStorage('user_data');
          window.location.href = '/login';
        } else if (error.response?.status === 403) {
          toast.error('Access denied. Insufficient permissions.');
        } else if (error.response?.status >= 500) {
          toast.error('Server error. Please try again later.');
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request method
  private async request<T>(method: string, url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.api.request({
        method,
        url,
        data,
      });
      return response.data;
    } catch (error) {
      console.error(`API ${method} ${url} error:`, error);
      throw error;
    }
  }

  // Authentication endpoints
  auth = {
    login: async (username: string, password: string, mfaCode?: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/login', { username, password, mfaCode });
    },

    logout: async (token: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/logout', { token });
    },

    refreshToken: async (refreshToken: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/refresh', { refreshToken });
    },

    validateToken: async (token: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/validate', { token });
    },

    changePassword: async (currentPassword: string, newPassword: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/change-password', { currentPassword, newPassword });
    },

    enableMFA: async (): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/mfa/enable');
    },

    disableMFA: async (mfaCode: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/mfa/disable', { mfaCode });
    },

    verifyMFA: async (mfaCode: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/auth/mfa/verify', { mfaCode });
    },
  };

  // Mission Control endpoints
  missions = {
    getAll: async (page = 1, limit = 20): Promise<PaginatedResponse<Mission>> => {
      const response = await this.request<PaginatedResponse<Mission>>('GET', `/missions?page=${page}&limit=${limit}`);
      return response.data;
    },

    getById: async (id: string): Promise<ApiResponse<Mission>> => {
      return this.request('GET', `/missions/${id}`);
    },

    create: async (mission: Partial<Mission>): Promise<ApiResponse<Mission>> => {
      return this.request('POST', '/missions', mission);
    },

    update: async (id: string, mission: Partial<Mission>): Promise<ApiResponse<Mission>> => {
      return this.request('PUT', `/missions/${id}`, mission);
    },

    delete: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('DELETE', `/missions/${id}`);
    },

    start: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/missions/${id}/start`);
    },

    pause: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/missions/${id}/pause`);
    },

    abort: async (id: string, reason: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/missions/${id}/abort`, { reason });
    },

    approve: async (id: string, objectiveId: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/missions/${id}/approve/${objectiveId}`);
    },

    emergencyStop: async (): Promise<ApiResponse<any>> => {
      return this.request('POST', '/missions/emergency-stop');
    },
  };

  // Threat Intelligence endpoints
  threats = {
    getAll: async (page = 1, limit = 20, filters?: any): Promise<PaginatedResponse<ThreatIntelligence>> => {
      const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, String(value));
        });
      }
      const response = await this.request<PaginatedResponse<ThreatIntelligence>>('GET', `/threats?${params}`);
      return response.data;
    },

    getById: async (id: string): Promise<ApiResponse<ThreatIntelligence>> => {
      return this.request('GET', `/threats/${id}`);
    },

    create: async (threat: Partial<ThreatIntelligence>): Promise<ApiResponse<ThreatIntelligence>> => {
      return this.request('POST', '/threats', threat);
    },

    update: async (id: string, threat: Partial<ThreatIntelligence>): Promise<ApiResponse<ThreatIntelligence>> => {
      return this.request('PUT', `/threats/${id}`, threat);
    },

    delete: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('DELETE', `/threats/${id}`);
    },

    search: async (query: string): Promise<ApiResponse<ThreatIntelligence[]>> => {
      return this.request('GET', `/threats/search?q=${encodeURIComponent(query)}`);
    },

    getFeeds: async (): Promise<ApiResponse<any[]>> => {
      return this.request('GET', '/threats/feeds');
    },

    syncFeeds: async (): Promise<ApiResponse<any>> => {
      return this.request('POST', '/threats/feeds/sync');
    },

    analyzeIOC: async (ioc: string, type: string): Promise<ApiResponse<any>> => {
      return this.request('POST', '/threats/analyze', { ioc, type });
    },
  };

  // Incident Response endpoints
  incidents = {
    getAll: async (page = 1, limit = 20, filters?: any): Promise<PaginatedResponse<Incident>> => {
      const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, String(value));
        });
      }
      const response = await this.request<PaginatedResponse<Incident>>('GET', `/incidents?${params}`);
      return response.data;
    },

    getById: async (id: string): Promise<ApiResponse<Incident>> => {
      return this.request('GET', `/incidents/${id}`);
    },

    create: async (incident: Partial<Incident>): Promise<ApiResponse<Incident>> => {
      return this.request('POST', '/incidents', incident);
    },

    update: async (id: string, incident: Partial<Incident>): Promise<ApiResponse<Incident>> => {
      return this.request('PUT', `/incidents/${id}`, incident);
    },

    delete: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('DELETE', `/incidents/${id}`);
    },

    assign: async (id: string, assignee: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/incidents/${id}/assign`, { assignee });
    },

    escalate: async (id: string, reason: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/incidents/${id}/escalate`, { reason });
    },

    close: async (id: string, resolution: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/incidents/${id}/close`, { resolution });
    },

    addEvidence: async (id: string, evidence: any): Promise<ApiResponse<any>> => {
      return this.request('POST', `/incidents/${id}/evidence`, evidence);
    },

    generateReport: async (id: string, format: 'pdf' | 'csv'): Promise<Blob> => {
      const response = await this.api.get(`/incidents/${id}/report?format=${format}`, {
        responseType: 'blob',
      });
      return response.data;
    },
  };

  // Compliance endpoints
  compliance = {
    getFrameworks: async (): Promise<ApiResponse<ComplianceFramework[]>> => {
      return this.request('GET', '/compliance/frameworks');
    },

    getFramework: async (id: string): Promise<ApiResponse<ComplianceFramework>> => {
      return this.request('GET', `/compliance/frameworks/${id}`);
    },

    updateControl: async (frameworkId: string, controlId: string, data: any): Promise<ApiResponse<any>> => {
      return this.request('PUT', `/compliance/frameworks/${frameworkId}/controls/${controlId}`, data);
    },

    runAssessment: async (frameworkId: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/compliance/frameworks/${frameworkId}/assess`);
    },

    generateReport: async (frameworkId: string, format: 'pdf' | 'csv'): Promise<Blob> => {
      const response = await this.api.get(`/compliance/frameworks/${frameworkId}/report?format=${format}`, {
        responseType: 'blob',
      });
      return response.data;
    },

    uploadEvidence: async (frameworkId: string, controlId: string, file: File): Promise<ApiResponse<any>> => {
      const formData = new FormData();
      formData.append('file', file);
      return this.request('POST', `/compliance/frameworks/${frameworkId}/controls/${controlId}/evidence`, formData);
    },
  };

  // System Monitoring endpoints
  monitoring = {
    getSystemHealth: async (): Promise<ApiResponse<SystemHealth>> => {
      return this.request('GET', '/monitoring/health');
    },

    getMetrics: async (timeRange: string = '1h'): Promise<ApiResponse<any>> => {
      return this.request('GET', `/monitoring/metrics?range=${timeRange}`);
    },

    getAlerts: async (page = 1, limit = 20): Promise<PaginatedResponse<any>> => {
      const response = await this.request<PaginatedResponse<any>>('GET', `/monitoring/alerts?page=${page}&limit=${limit}`);
      return response.data;
    },

    acknowledgeAlert: async (alertId: string): Promise<ApiResponse<any>> => {
      return this.request('POST', `/monitoring/alerts/${alertId}/acknowledge`);
    },

    createAlert: async (alert: any): Promise<ApiResponse<any>> => {
      return this.request('POST', '/monitoring/alerts', alert);
    },

    getNetworkTopology: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/monitoring/network/topology');
    },

    getTrafficAnalysis: async (timeRange: string = '1h'): Promise<ApiResponse<any>> => {
      return this.request('GET', `/monitoring/network/traffic?range=${timeRange}`);
    },
  };

  // User Management endpoints
  users = {
    getAll: async (page = 1, limit = 20): Promise<PaginatedResponse<User>> => {
      const response = await this.request<PaginatedResponse<User>>('GET', `/users?page=${page}&limit=${limit}`);
      return response.data;
    },

    getById: async (id: string): Promise<ApiResponse<User>> => {
      return this.request('GET', `/users/${id}`);
    },

    create: async (user: Partial<User>): Promise<ApiResponse<User>> => {
      return this.request('POST', '/users', user);
    },

    update: async (id: string, user: Partial<User>): Promise<ApiResponse<User>> => {
      return this.request('PUT', `/users/${id}`, user);
    },

    delete: async (id: string): Promise<ApiResponse<any>> => {
      return this.request('DELETE', `/users/${id}`);
    },

    updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
      return this.request('PUT', '/users/profile', data);
    },
  };

  // Configuration endpoints
  config = {
    get: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/config');
    },

    update: async (config: any): Promise<ApiResponse<any>> => {
      return this.request('PUT', '/config', config);
    },

    backup: async (): Promise<Blob> => {
      const response = await this.api.get('/config/backup', {
        responseType: 'blob',
      });
      return response.data;
    },

    restore: async (file: File): Promise<ApiResponse<any>> => {
      const formData = new FormData();
      formData.append('file', file);
      return this.request('POST', '/config/restore', formData);
    },
  };

  // Analytics endpoints
  analytics = {
    getDashboardStats: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/analytics/dashboard');
    },

    getThreatTrends: async (timeRange: string = '7d'): Promise<ApiResponse<any>> => {
      return this.request('GET', `/analytics/threats/trends?range=${timeRange}`);
    },

    getIncidentMetrics: async (timeRange: string = '7d'): Promise<ApiResponse<any>> => {
      return this.request('GET', `/analytics/incidents/metrics?range=${timeRange}`);
    },

    getComplianceScores: async (): Promise<ApiResponse<any>> => {
      return this.request('GET', '/analytics/compliance/scores');
    },

    exportData: async (type: string, format: 'csv' | 'json', timeRange?: string): Promise<Blob> => {
      const params = new URLSearchParams({ format });
      if (timeRange) params.append('range', timeRange);
      
      const response = await this.api.get(`/analytics/export/${type}?${params}`, {
        responseType: 'blob',
      });
      return response.data;
    },
  };
}

// Export API instance
export const api = new ApiService();

// Export individual API modules for convenience
export const {
  auth: authApi,
  missions: missionApi,
  threats: threatApi,
  incidents: incidentApi,
  compliance: complianceApi,
  monitoring: monitoringApi,
  users: userApi,
  config: configApi,
  analytics: analyticsApi,
} = api;