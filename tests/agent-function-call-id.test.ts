import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";

test("function call ID is preserved", async () => {
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    completionFn: async () => ({ choices: [] }),
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 