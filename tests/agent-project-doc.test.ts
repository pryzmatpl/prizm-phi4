import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";
import { AppConfig } from "../src/utils/config";

test("project doc is handled", async () => {
  const agent = new AgentLoop({
    model: "o3", // arbitrary
    instructions: "",
    completionFn: async () => ({ choices: [] }),
    onItem: () => {},
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
  });
  // ... rest of test ...
}); 