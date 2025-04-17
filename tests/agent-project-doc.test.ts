import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("includes project doc content", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "o3", // arbitrary
    instructions: "",
    config: mockConfig,
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion, // <-- Add completionFn
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 