import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  skills: string[];
}

export interface Skill {
  name: string;
  description: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: {
    input: number;
    output: number;
    cached: number;
    saved: number;
  };
}

export interface ChatRequest {
  message: string;
  agent_id: string;
  conversation_history: ChatMessage[];
}

export interface TokenStats {
  total_input_tokens: number;
  total_output_tokens: number;
  total_cached_tokens: number;
  total_tokens_saved: number;
  total_cost_usd: number;
  savings_percentage: number;
  records: any[];
}

export interface CompressResult {
  compressed: string;
  original_tokens: number;
  compressed_tokens: number;
  ratio: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = '/api';

  getAgents(): Observable<Agent[]> {
    return this.http.get<Agent[]>(`${this.baseUrl}/agents`);
  }

  getSkills(): Observable<Skill[]> {
    return this.http.get<Skill[]>(`${this.baseUrl}/skills`);
  }

  sendMessage(req: ChatRequest): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/chat`, req);
  }

  getTokenStats(): Observable<TokenStats> {
    return this.http.get<TokenStats>(`${this.baseUrl}/token-stats`);
  }

  compressPrompt(text: string): Observable<CompressResult> {
    return this.http.post<CompressResult>(`${this.baseUrl}/compress`, { text });
  }
}
