import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("terminate() stops agent loop", async () => {
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

test("terminate() prevents subsequent runs", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    config: { model: "any", instructions: "" },
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion,
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 