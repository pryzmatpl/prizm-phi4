export async function getNextToken(inferResponse: any): Promise<number> {
  try {
    if (!inferResponse?.logits || !Array.isArray(inferResponse.logits) || inferResponse.logits.length === 0) {
      throw new Error("Invalid logits in inference response");
    }

    const batchLogits = inferResponse.logits;
    if (!Array.isArray(batchLogits[batchLogits.length - 1])) {
      throw new Error("Invalid logits format in last batch");
    }

    const lastTokenLogits = batchLogits[batchLogits.length - 1];
    let maxLogit = Number.NEGATIVE_INFINITY;
    let maxIndex = 0;

    for (let j = 0; j < lastTokenLogits.length; j++) {
      const logit = lastTokenLogits[j];
      if (typeof logit === 'number' && logit > maxLogit) {
        maxLogit = logit;
        maxIndex = j;
      }
    }

    return maxIndex;
  } catch (error) {
    console.error("Error processing logits:", error);
    throw error;
  }
} 