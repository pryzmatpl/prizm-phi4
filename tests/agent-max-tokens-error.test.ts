import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("max_tokens error", async () => {
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