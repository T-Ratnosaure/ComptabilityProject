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
  tax_year: number;
  impot: {
    revenu_imposable: number;
    part_income: number;
    impot_brut: number;
    impot_net: number;
    tmi: number;
    tax_reductions: Record<string, number>;
    per_deduction_applied: number;
    per_deduction_excess: number;
    per_plafond_detail: any;
    tranches_detail: Array<{
      rate: number;
      income_in_bracket: number;
      tax_in_bracket: number;
    }>;
    pas_withheld: number;
    due_now: number;
  };
  socials: {
    urssaf_expected: number;
    urssaf_paid: number;
    delta: number;
    rate_used: number;
  };
  comparisons?: {
    micro_vs_reel?: {
      regime_actuel: string;
      regime_compare: string;
      impot_actuel: number;
      impot_compare: number;
      charge_totale_actuelle: number;
      charge_totale_comparee: number;
      economie_potentielle: number;
      pourcentage_economie: number;
      recommendation: string;
      justification: string;
    };
  };
  warnings?: string[];
  metadata?: any;
}

export interface OptimizationContext {
  investment_capacity: number;
  risk_tolerance: string;
  stable_income: boolean;
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
  context?: OptimizationContext;
}

export interface Recommendation {
  title: string;
  description: string;
  impact_estimated: number;
  risk: string;
  complexity: string;
  category: string;
  required_investment?: number;
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
