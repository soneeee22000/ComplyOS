const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface RequestOptions {
  method?: string;
  body?: unknown;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body } = options;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export interface AISystem {
  id: string;
  name: string;
  description: string;
  department: string;
  use_case: string;
  risk_level: string | null;
  annex_category: string | null;
  classification_reasoning: string | null;
  confidence_score: number | null;
  overall_compliance_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface ClassificationResult {
  risk_level: string;
  annex_category: string;
  confidence_score: number;
  reasoning: string;
  cited_articles: string[];
  requires_compliance: boolean;
}

export interface ComplianceGap {
  requirement: string;
  article: string;
  status: string;
  severity: string;
  description: string;
  remediation: string;
  estimated_effort: string;
}

export interface GapAnalysisResult {
  system_id: string;
  overall_score: number;
  gaps: ComplianceGap[];
  summary: string;
  priority_actions: string[];
}

export interface SubRequirementStatus {
  sub_requirement_id: string;
  paragraph: string;
  title: string;
  status: string;
  severity: string;
  finding: string;
  remediation: string;
  estimated_effort: string;
  evidence_required: string[];
}

export interface ArticleStatus {
  article_id: string;
  article_title: string;
  article_status: string;
  sub_requirement_statuses: SubRequirementStatus[];
}

export interface CrossReferenceFinding {
  source_article: string;
  target_article: string;
  relationship: string;
  finding: string;
}

export interface EnhancedGapAnalysisResult {
  system_id: string;
  overall_score: number;
  summary: string;
  priority_actions: string[];
  requirement_statuses: ArticleStatus[];
  cross_reference_findings: CrossReferenceFinding[];
}

export interface RequirementTreeResponse {
  risk_level: string;
  annex_category: string | null;
  total_articles: number;
  total_sub_requirements: number;
  articles: Record<string, unknown>[];
}

export interface DashboardMetrics {
  total_systems: number;
  high_risk_count: number;
  limited_risk_count: number;
  minimal_risk_count: number;
  unclassified_count: number;
  average_compliance_score: number;
  days_until_deadline: number;
  critical_gaps_count: number;
}

export interface ChatResponse {
  answer: string;
  cited_articles: string[];
  confidence: number;
}

export const api = {
  getSystems: () => request<AISystem[]>("/systems"),

  createSystem: (data: {
    name: string;
    description: string;
    department: string;
    use_case: string;
  }) => request<AISystem>("/systems", { method: "POST", body: data }),

  getSystem: (id: string) => request<AISystem>(`/systems/${id}`),

  classifySystem: (id: string) =>
    request<ClassificationResult>(`/systems/${id}/classify`, {
      method: "POST",
    }),

  analyzeSystem: (id: string) =>
    request<EnhancedGapAnalysisResult>(`/systems/${id}/analyze`, {
      method: "POST",
    }),

  getRequirementTree: (riskLevel: string, annexCategory?: string) =>
    request<RequirementTreeResponse>(
      `/ontology/requirements?risk_level=${riskLevel}${annexCategory ? `&annex_category=${annexCategory}` : ""}`,
    ),

  generateDocs: (systemId: string, docType: string) =>
    request<{ id: string; content: string; generated_at: string }>(
      `/systems/${systemId}/generate-docs`,
      { method: "POST", body: { system_id: systemId, doc_type: docType } },
    ),

  getDashboard: () => request<DashboardMetrics>("/dashboard"),

  chat: (message: string, systemId?: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: { message, system_id: systemId },
    }),
};
