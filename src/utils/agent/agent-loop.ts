import {
  ResponseItem,
  ResponseOutputMessage,
  ResponseInputMessageContentList as ResponseInputMessageContent,
} from "openai/resources/responses/responses.mjs";

export interface AgentLoopParams {
  model: string;
  instructions: string;
  completionFn: CompletionFunction;
  onItem: (item: ResponseItem) => void;
  onLoading: (loading: boolean) => void;
  getCommandConfirmation: () => Promise<boolean>;
  onLastResponseId: (id: string | null) => void;
}

export class AgentLoop {
  private model: string;
  private instructions: string;
  private completionFn: CompletionFunction;
  private onItem: (item: ResponseItem) => void;
  private onLoading: (loading: boolean) => void;
  private onLastResponseId: (id: string | null) => void;
  private getCommandConfirmation: () => Promise<boolean>;

  constructor({
    model,
    instructions,
    completionFn,
    onItem,
    onLoading,
    getCommandConfirmation,
    onLastResponseId,
  }: AgentLoopParams) {
    this.model = model;
    this.instructions = instructions;
    this.completionFn = completionFn;
    this.onItem = onItem;
    this.onLoading = onLoading;
    this.getCommandConfirmation = getCommandConfirmation;
    this.onLastResponseId = onLastResponseId;
  }

  private async processResponse(response: ResponseOutputMessage): Promise<void> {
    const { content, role, name, function_call } = response;
  }
} 