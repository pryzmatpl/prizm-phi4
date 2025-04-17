import React, { useState } from 'react';

const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);
const [responses, setResponses] = useState<Array<ResponseItem>>([]); 