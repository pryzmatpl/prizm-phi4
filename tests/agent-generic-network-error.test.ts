import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";
import { ResponseItem } from "openai/resources/responses/responses.mjs";

test("network error is handled", async () => {
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    completionFn: async () => ({ choices: [] }),
    onItem: (i: ResponseItem) => 0,
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
  });
  // ... rest of test
});

test("generic network error", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion,
    onItem: (i: ResponseItem) => seenItems.push(i),
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
});

test("generic network error with cause", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion,
    onItem: (i: ResponseItem) => seenItems.push(i),
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 