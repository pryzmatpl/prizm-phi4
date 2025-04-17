import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";
import { ResponseItem } from "openai/resources/responses/responses.mjs";

test("thinking time is handled", async () => {
  const agent = new AgentLoop({
    model: "any",
    instructions: "",
    completionFn: async () => ({ choices: [] }),
    onItem: (i: ResponseItem) => 0,
    onLoading: () => {},
    getCommandConfirmation: async () => true,
    onLastResponseId: () => {},
  });
  // ... rest of test
}); 