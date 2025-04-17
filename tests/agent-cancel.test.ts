import { AgentLoop } from "../src/utils/agent/agent-loop";
import { describe, test, expect } from "@jest/globals";
import { ResponseItem } from "openai/resources/responses/responses.mjs";

describe("AgentLoop cancel tests", () => {
  test("cancel() aborts stream", async () => {
    const agent = new AgentLoop({
      model: "any",
      instructions: "",
      completionFn: async () => ({ choices: [] }),
      onItem: (item: ResponseItem) => {},
      onLoading: () => {},
      getCommandConfirmation: async () => true,
      onLastResponseId: () => {},
    });
    // ... rest of test
  });
}); 