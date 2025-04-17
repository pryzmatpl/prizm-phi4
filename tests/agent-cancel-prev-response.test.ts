import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";

test("cancel() aborts previous response", async () => {
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    completionFn: async () => ({ choices: [] }),
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
    config: { model: "any", instructions: "" },
  });
  // ... rest of test ...
}); 