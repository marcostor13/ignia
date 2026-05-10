import {
  Component,
  inject,
  signal,
  computed,
  effect,
  ViewChild,
  ElementRef,
  AfterViewChecked,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { AgentSelectorComponent } from '../agent-selector/agent-selector.component';

interface ParsedBlock {
  type: 'text' | 'code';
  content: string;
  language?: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule, AgentSelectorComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent implements AfterViewChecked {
  @ViewChild('messagesEnd') messagesEnd!: ElementRef<HTMLDivElement>;
  @ViewChild('inputField') inputField!: ElementRef<HTMLTextAreaElement>;

  chatService = inject(ChatService);

  inputText = signal<string>('');
  private shouldScroll = false;

  readonly messages = this.chatService.messages;
  readonly isLoading = this.chatService.isLoading;
  readonly currentAgent = this.chatService.currentAgent;

  readonly canSend = computed(
    () =>
      this.inputText().trim().length > 0 &&
      !!this.chatService.selectedAgentId() &&
      !this.isLoading()
  );

  constructor() {
    effect(() => {
      const _ = this.messages();
      this.shouldScroll = true;
    });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement?.scrollIntoView({ behavior: 'smooth' });
    } catch {
      // noop
    }
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  sendMessage(): void {
    const text = this.inputText().trim();
    if (!text || !this.canSend()) return;
    this.chatService.sendMessage(text);
    this.inputText.set('');
  }

  clearChat(): void {
    this.chatService.clearConversation();
  }

  parseContent(content: string): ParsedBlock[] {
    const blocks: ParsedBlock[] = [];
    const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        blocks.push({
          type: 'text',
          content: content.slice(lastIndex, match.index),
        });
      }
      blocks.push({
        type: 'code',
        language: match[1] || 'plaintext',
        content: match[2].trim(),
      });
      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < content.length) {
      blocks.push({ type: 'text', content: content.slice(lastIndex) });
    }

    return blocks.length > 0 ? blocks : [{ type: 'text', content }];
  }

  formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  trackByIndex(index: number): number {
    return index;
  }
}
