import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("reports thinking time correctly", async () => {
  // ... mocks ...
    const agent = new AgentLoop({
      config: {} as any,
      model: "any",
      instructions: "",
      approvalPolicy: ApprovalMode.SUGGEST,
      completionFn: getModelCompletion, // <-- Add completionFn
      onItem: (i: ResponseItem) => seenItems.push(i),
      onLoading: () => {},
      getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
      onLastResponseId: () => {},
    });
  // ... rest of test ...
}); 