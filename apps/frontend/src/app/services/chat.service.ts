import { Injectable, inject, signal, computed } from '@angular/core';
import { ApiService, ChatMessage, Agent, ChatRequest } from './api.service';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private api = inject(ApiService);

  readonly messages = signal<ChatMessage[]>([]);
  readonly currentAgent = signal<Agent | null>(null);
  readonly isLoading = signal<boolean>(false);
  readonly selectedAgentId = signal<string>('');

  readonly hasMessages = computed(() => this.messages().length > 0);
  readonly messageCount = computed(() => this.messages().length);

  setAgent(agent: Agent): void {
    this.currentAgent.set(agent);
    this.selectedAgentId.set(agent.id);
  }

  clearConversation(): void {
    this.messages.set([]);
  }

  sendMessage(content: string): void {
    const agentId = this.selectedAgentId();
    if (!content.trim() || !agentId || this.isLoading()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    this.messages.update((msgs) => [...msgs, userMessage]);
    this.isLoading.set(true);

    const history = this.messages().slice(0, -1);

    const req: ChatRequest = {
      message: content.trim(),
      agent_id: agentId,
      conversation_history: history,
    };

    this.api.sendMessage(req).subscribe({
      next: (response: any) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.content ?? response.message ?? '',
          timestamp: new Date(),
          tokens: response.tokens
            ? {
                input: response.tokens.input ?? 0,
                output: response.tokens.output ?? 0,
                cached: response.tokens.cached ?? 0,
                saved: response.tokens.saved ?? 0,
              }
            : undefined,
        };
        this.messages.update((msgs) => [...msgs, assistantMessage]);
        this.isLoading.set(false);
      },
      error: (err: any) => {
        const errorMessage: ChatMessage = {
          role: 'assistant',
          content: `Error: ${err?.error?.detail ?? err?.message ?? 'Failed to get response from the agent.'}`,
          timestamp: new Date(),
        };
        this.messages.update((msgs) => [...msgs, errorMessage]);
        this.isLoading.set(false);
      },
    });
  }
}
