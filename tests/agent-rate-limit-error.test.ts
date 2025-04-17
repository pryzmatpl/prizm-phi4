import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

it("should retry with exponential backoff", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion, // <-- Add completionFn
    onItem: (i: ResponseItem) => seenItems.push(i),
    onLoading: () => {},
    getCommandConfirmation: () =>
      Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 