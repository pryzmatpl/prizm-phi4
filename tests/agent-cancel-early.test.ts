import { AgentLoop } from "../src/utils/agent/agent-loop";
import { getModelCompletion } from "../../src/utils/model-utils"; // Assuming path is correct
import { describe, test, expect } from "@jest/globals";

test("cancel() aborts stream immediately", async () => {
  // ... mocks ...
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    completionFn: async () => ({ choices: [] }), // Add dummy completion function
    approvalPolicy: {} as any,
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
    config: { model: "any", instructions: "" },
  });
  // ... rest of test ...
}); 