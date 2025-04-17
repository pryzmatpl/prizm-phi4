import { AgentLoop } from "../../src/utils/agent/agent-loop.js";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct

test("interrupts and continues", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "test-model",
    instructions: "",
    approvalPolicy: ApprovalMode.SUGGEST,
    config: { model: "test-model", instructions: "" },
    completionFn: getModelCompletion,
    onItem: (item: ResponseItem) => {
      items.push(item);
    },
    onLoading: (loading: boolean) => {
      loadingHistory.push(loading);
    },
    getCommandConfirmation: () => Promise.resolve({ review: ReviewDecision.APPROVE }),
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 