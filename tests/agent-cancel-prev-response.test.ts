import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("cancel() clears previous response ID if no pending aborts", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion, // <-- Add completionFn
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: "approve" }),
    onLastResponseId: () => {},
    config: { model: "any", instructions: "" },
  });
  // ... rest of test ...
}); 