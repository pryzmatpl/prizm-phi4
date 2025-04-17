import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("cancel() correctly aborts in-flight requests", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    config: { model: "any", instructions: "" },
    approvalPolicy: ApprovalMode.SUGGEST,
    completionFn: getModelCompletion, // <-- Add completionFn
    onItem: (i: ResponseItem) => seenItems.push(i),
    onLoading: () => {},
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 