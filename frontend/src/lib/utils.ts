import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow } from 'date-fns';
import type { Severity, Priority } from '@/types';

// Tailwind class name utility
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return format(d, 'MMM dd, yyyy HH:mm');
}

export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}

export function formatDuration(milliseconds: number): string {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}

// Severity and priority styling
export function getSeverityColor(severity: Severity): string {
  switch (severity) {
    case 'critical':
      return 'text-danger-400 bg-danger-900/20 border-danger-500';
    case 'high':
      return 'text-warning-400 bg-warning-900/20 border-warning-500';
    case 'medium':
      return 'text-warning-300 bg-warning-900/10 border-warning-600';
    case 'low':
      return 'text-success-400 bg-success-900/20 border-success-500';
    default:
      return 'text-gray-400 bg-gray-900/20 border-gray-500';
  }
}

export function getPriorityColor(priority: Priority): string {
  switch (priority) {
    case 'critical':
      return 'text-danger-400 bg-danger-900/20 border-danger-500';
    case 'high':
      return 'text-warning-400 bg-warning-900/20 border-warning-500';
    case 'medium':
      return 'text-primary-400 bg-primary-900/20 border-primary-500';
    case 'low':
      return 'text-success-400 bg-success-900/20 border-success-500';
    default:
      return 'text-gray-400 bg-gray-900/20 border-gray-500';
  }
}

export function getSeverityBadgeClass(severity: Severity): string {
  const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border';
  return cn(baseClass, getSeverityColor(severity));
}

export function getPriorityBadgeClass(priority: Priority): string {
  const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border';
  return cn(baseClass, getPriorityColor(priority));
}

// Security utilities
export function generateSecureId(): string {
  return crypto.randomUUID();
}

export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+=/gi, '')
    .trim();
}

export function maskSensitiveData(data: string, visibleChars: number = 4): string {
  if (data.length <= visibleChars * 2) return data;
  const start = data.substring(0, visibleChars);
  const end = data.substring(data.length - visibleChars);
  const masked = '*'.repeat(data.length - visibleChars * 2);
  return `${start}${masked}${end}`;
}

// Data validation utilities
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidIP(ip: string): boolean {
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  return ipv4Regex.test(ip) || ipv6Regex.test(ip);
}

export function isValidHash(hash: string, type: 'md5' | 'sha1' | 'sha256' = 'sha256'): boolean {
  const patterns = {
    md5: /^[a-fA-F0-9]{32}$/,
    sha1: /^[a-fA-F0-9]{40}$/,
    sha256: /^[a-fA-F0-9]{64}$/,
  };
  return patterns[type].test(hash);
}

// Number formatting utilities
export function formatBytes(bytes: number): string {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}

// Chart data utilities
export function generateTimeSeriesLabels(count: number, interval: 'minute' | 'hour' | 'day' = 'hour'): string[] {
  const labels: string[] = [];
  const now = new Date();
  
  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(now);
    switch (interval) {
      case 'minute':
        date.setMinutes(date.getMinutes() - i);
        labels.push(format(date, 'HH:mm'));
        break;
      case 'hour':
        date.setHours(date.getHours() - i);
        labels.push(format(date, 'HH:mm'));
        break;
      case 'day':
        date.setDate(date.getDate() - i);
        labels.push(format(date, 'MMM dd'));
        break;
    }
  }
  
  return labels;
}

export function generateRandomData(count: number, min: number = 0, max: number = 100): number[] {
  return Array.from({ length: count }, () => Math.floor(Math.random() * (max - min + 1)) + min);
}

// Color utilities for charts
export const chartColors = {
  primary: '#0ea5e9',
  danger: '#ef4444',
  warning: '#f59e0b',
  success: '#22c55e',
  info: '#06b6d4',
  purple: '#8b5cf6',
  pink: '#ec4899',
  indigo: '#6366f1',
};

export function getChartColorByIndex(index: number): string {
  const colors = Object.values(chartColors);
  return colors[index % colors.length];
}

// Local storage utilities with encryption-like behavior
export function setSecureStorage(key: string, value: any): void {
  try {
    const jsonValue = JSON.stringify(value);
    const encoded = btoa(jsonValue); // Simple encoding, not actual encryption
    localStorage.setItem(`sra_${key}`, encoded);
  } catch (error) {
    console.error('Failed to save to secure storage:', error);
  }
}

export function getSecureStorage<T>(key: string): T | null {
  try {
    const encoded = localStorage.getItem(`sra_${key}`);
    if (!encoded) return null;
    const jsonValue = atob(encoded);
    return JSON.parse(jsonValue);
  } catch (error) {
    console.error('Failed to read from secure storage:', error);
    return null;
  }
}

export function removeSecureStorage(key: string): void {
  localStorage.removeItem(`sra_${key}`);
}

// Array utilities
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

export function sortBy<T>(array: T[], key: keyof T, direction: 'asc' | 'desc' = 'asc'): T[] {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
}

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}