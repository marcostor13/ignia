import { Component, inject, OnInit, signal } from '@angular/core';
import { ApiService, Agent } from '../../services/api.service';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-agent-selector',
  standalone: true,
  imports: [],
  templateUrl: './agent-selector.component.html',
  styleUrl: './agent-selector.component.scss',
})
export class AgentSelectorComponent implements OnInit {
  private api = inject(ApiService);
  chatService = inject(ChatService);

  agents = signal<Agent[]>([]);
  isLoading = signal<boolean>(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.loadAgents();
  }

  loadAgents(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.api.getAgents().subscribe({
      next: (agents) => {
        this.agents.set(agents);
        this.isLoading.set(false);
        // Auto-select first agent
        if (agents.length > 0 && !this.chatService.selectedAgentId()) {
          this.selectAgent(agents[0]);
        }
      },
      error: (err) => {
        this.error.set('Failed to load agents. Is the backend running?');
        this.isLoading.set(false);
        // Load demo agents for development
        const demoAgents: Agent[] = [
          {
            id: 'claude-general',
            name: 'Claude General',
            description: 'A general-purpose AI assistant powered by Claude Sonnet with broad knowledge and capabilities.',
            model: 'claude-sonnet-4-5',
            skills: ['reasoning', 'writing', 'analysis', 'code'],
          },
          {
            id: 'gemini-researcher',
            name: 'Gemini Researcher',
            description: 'Research-focused agent powered by Gemini Pro for deep information gathering and synthesis.',
            model: 'gemini-pro',
            skills: ['research', 'summarization', 'fact-checking'],
          },
        ];
        this.agents.set(demoAgents);
        if (!this.chatService.selectedAgentId()) {
          this.selectAgent(demoAgents[0]);
        }
      },
    });
  }

  selectAgent(agent: Agent): void {
    this.chatService.setAgent(agent);
  }

  isSelected(agent: Agent): boolean {
    return this.chatService.selectedAgentId() === agent.id;
  }

  getModelClass(model: string): string {
    const lower = model.toLowerCase();
    if (lower.includes('claude')) return 'model--claude';
    if (lower.includes('gemini')) return 'model--gemini';
    if (lower.includes('gpt')) return 'model--gpt';
    return 'model--other';
  }

  getModelLabel(model: string): string {
    const lower = model.toLowerCase();
    if (lower.includes('claude')) return 'Claude';
    if (lower.includes('gemini')) return 'Gemini';
    if (lower.includes('gpt-4')) return 'GPT-4';
    if (lower.includes('gpt')) return 'GPT';
    return model;
  }
}
