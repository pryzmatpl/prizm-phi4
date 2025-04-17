import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("run() with cancellation", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    config: { model: "any", instructions: "" },
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion,
    onItem: (item: ResponseItem) => {
      seenItems.push(item);
    },
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
});

test("cancel() aborts ongoing stream", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    config: { model: "any", instructions: "" },
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion,
    onItem: (item: ResponseItem) => seenItems.push(item),
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 