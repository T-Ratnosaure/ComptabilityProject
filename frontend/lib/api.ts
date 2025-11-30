/**
 * API Client for ComptabilityProject Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TaxCalculationRequest {
  tax_year: number;
  person: {
    name: string;
    nb_parts: number;
    status: string;
  };
  income: {
    professional_gross: number;
    salary: number;
    rental_income: number;
    capital_income: number;
    deductible_expenses: number;
  };
  deductions: {
    per_contributions: number;
    alimony: number;
    other_deductions: number;
  };
  social: {
    urssaf_declared_ca: number;
    urssaf_paid: number;
  };
  pas_withheld: number;
}

export interface TaxCalculationResponse {
  revenu_imposable: number;
  quotient_familial: number;
  impot: {
    impot_brut: number;
    impot_net: number;
    tmi: number;
    taux_effectif: number;
  };
  socials: {
    urssaf_expected: number;
    difference: number;
  };
  charge_totale: number;
  pas_result?: any;
  comparisons?: any;
}

export interface OptimizationRequest {
  profile: {
    status: string;
    chiffre_affaires: number;
    charges_deductibles: number;
    nb_parts: number;
    activity_type: string;
  };
  tax_result: TaxCalculationResponse;
}

export interface Recommendation {
  title: string;
  description: string;
  impact_estimated: number;
  risk: string;
  complexity: string;
  category: string;
}

export interface OptimizationResponse {
  recommendations: Recommendation[];
  potential_savings_total: number;
}

export interface LLMAnalysisRequest {
  user_id: string;
  conversation_id?: string;
  user_question: string;
  profile_data: TaxCalculationRequest;
  tax_result: TaxCalculationResponse;
  optimization_result?: OptimizationResponse;
  include_few_shot?: boolean;
  include_context?: boolean;
}

export interface LLMAnalysisResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  async calculateTax(
    data: TaxCalculationRequest
  ): Promise<TaxCalculationResponse> {
    return this.request<TaxCalculationResponse>('/api/v1/tax/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async runOptimization(
    data: OptimizationRequest
  ): Promise<OptimizationResponse> {
    return this.request<OptimizationResponse>('/api/v1/optimization/run', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeLLM(data: LLMAnalysisRequest): Promise<LLMAnalysisResponse> {
    return this.request<LLMAnalysisResponse>('/api/v1/llm/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }
}

export const apiClient = new APIClient();
