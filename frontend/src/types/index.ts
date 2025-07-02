// Core Authentication & User Types
export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  lastLogin: Date;
  mfaEnabled: boolean;
  status: 'active' | 'inactive' | 'suspended';
}

export interface UserRole {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
}

// Mission & Agent Types
export interface Mission {
  id: string;
  name: string;
  description: string;
  status: MissionStatus;
  priority: Priority;
  createdAt: Date;
  updatedAt: Date;
  assignedOperator: string;
  objectives: MissionObjective[];
  timeline: MissionEvent[];
  safetyRules: SafetyRule[];
}

export interface MissionObjective {
  id: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  deadline: Date;
  requiresApproval: boolean;
}

export interface MissionEvent {
  id: string;
  timestamp: Date;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  operator?: string;
  agentAction?: string;
  metadata?: Record<string, any>;
}

export interface SafetyRule {
  id: string;
  rule: string;
  priority: number;
  enabled: boolean;
  description: string;
}

export type MissionStatus = 'planning' | 'active' | 'paused' | 'completed' | 'aborted';
export type Priority = 'low' | 'medium' | 'high' | 'critical';

// Threat Intelligence Types
export interface ThreatIntelligence {
  id: string;
  source: string;
  type: ThreatType;
  indicators: IOC[];
  severity: Severity;
  confidence: number;
  timestamp: Date;
  description: string;
  mitigation: string[];
  tags: string[];
}

export interface IOC {
  id: string;
  type: 'ip' | 'domain' | 'url' | 'hash' | 'email' | 'file';
  value: string;
  context: string;
  firstSeen: Date;
  lastSeen: Date;
  malicious: boolean;
}

export type ThreatType = 'malware' | 'phishing' | 'apt' | 'insider' | 'ddos' | 'vulnerability' | 'other';
export type Severity = 'low' | 'medium' | 'high' | 'critical';

// Incident Response Types
export interface Incident {
  id: string;
  title: string;
  description: string;
  status: IncidentStatus;
  severity: Severity;
  priority: Priority;
  category: IncidentCategory;
  assignedTo: string;
  reporter: string;
  createdAt: Date;
  updatedAt: Date;
  timeline: IncidentEvent[];
  artifacts: Evidence[];
  affectedSystems: string[];
  estimatedImpact: Impact;
}

export interface IncidentEvent {
  id: string;
  timestamp: Date;
  actor: string;
  action: string;
  description: string;
  evidence?: string[];
}

export interface Evidence {
  id: string;
  type: 'log' | 'screenshot' | 'file' | 'network' | 'memory' | 'other';
  name: string;
  hash: string;
  collected: Date;
  chain: string;
  metadata: Record<string, any>;
}

export interface Impact {
  confidentiality: 'none' | 'low' | 'medium' | 'high';
  integrity: 'none' | 'low' | 'medium' | 'high';
  availability: 'none' | 'low' | 'medium' | 'high';
  financial: number;
  reputation: 'none' | 'low' | 'medium' | 'high';
}

export type IncidentStatus = 'new' | 'investigating' | 'containment' | 'eradication' | 'recovery' | 'closed';
export type IncidentCategory = 'security' | 'privacy' | 'availability' | 'integrity' | 'compliance' | 'other';

// Compliance Types
export interface ComplianceFramework {
  id: string;
  name: string;
  version: string;
  description: string;
  controls: ComplianceControl[];
  score: number;
  lastAssessment: Date;
}

export interface ComplianceControl {
  id: string;
  name: string;
  description: string;
  status: ComplianceStatus;
  evidence: string[];
  lastReview: Date;
  responsible: string;
  maturity: MaturityLevel;
}

export type ComplianceStatus = 'compliant' | 'non-compliant' | 'partially-compliant' | 'not-assessed';
export type MaturityLevel = 'initial' | 'repeatable' | 'defined' | 'managed' | 'optimizing';

// System Monitoring Types
export interface SystemHealth {
  timestamp: Date;
  cpu: number;
  memory: number;
  disk: number;
  network: NetworkMetrics;
  processes: number;
  alerts: SystemAlert[];
}

export interface NetworkMetrics {
  inbound: number;
  outbound: number;
  connections: number;
  latency: number;
}

export interface SystemAlert {
  id: string;
  type: 'performance' | 'security' | 'error' | 'warning';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
  severity: Severity;
}

// Analytics & Visualization Types
export interface ChartData {
  labels: string[];
  datasets: Dataset[];
}

export interface Dataset {
  label: string;
  data: number[];
  backgroundColor?: string;
  borderColor?: string;
  fill?: boolean;
}

export interface NetworkNode {
  id: string;
  label: string;
  group: string;
  level: number;
  title?: string;
  color?: string;
}

export interface NetworkEdge {
  from: string;
  to: string;
  label?: string;
  color?: string;
  width?: number;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: Date;
  id: string;
}

// Configuration Types
export interface SRAConfig {
  features: {
    threatIntelligence: boolean;
    incidentResponse: boolean;
    compliance: boolean;
    systemMonitoring: boolean;
    networkVisualization: boolean;
  };
  security: {
    mfaRequired: boolean;
    sessionTimeout: number;
    passwordPolicy: PasswordPolicy;
  };
  integrations: {
    misp: boolean;
    alienVault: boolean;
    atomicRedTeam: boolean;
    caldera: boolean;
  };
}

export interface PasswordPolicy {
  minLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSpecialChars: boolean;
  maxAge: number;
}