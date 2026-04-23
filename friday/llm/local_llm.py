"""
Local LLM Wrapper for JARVIS Agent System
Handles all communication with local Ollama models.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import ollama
except ImportError:
    raise ImportError("ollama is required. Install with: pip install ollama")


logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structure for LLM responses."""
    text: str
    model: str
    tokens_used: int = 0
    raw_response: Dict[str, Any] = None


class LocalLLM:
    """
    Wrapper for local Ollama models.
    Provides unified interface for all LLM operations.
    """

    def __init__(
        self,
        model: str = "mistral",
        host: str = "http://localhost:11434",
        temperature: float = 0.3,
        log_level: int = logging.INFO
    ):
        """
        Initialize LocalLLM.
        
        Args:
            model: Ollama model name
            host: Ollama server host
            temperature: Model temperature (0.0-1.0)
            log_level: Logging level
        """
        self.model = model
        self.host = host
        self.temperature = temperature
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        self.client = ollama.Client(host=host)
        self._test_connection()

    def _test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            self.logger.info(f"Testing Ollama connection at {self.host}")
            response = self.client.list()
            self.logger.info(f"✓ Ollama connected. Models: {len(response.get('models', []))}")
            return True
        except Exception as e:
            self.logger.warning(f"⚠ Ollama connection failed: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> LLMResponse:
        """
        Generate response from local LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            
        Returns:
            LLMResponse object
        """
        try:
            self.logger.debug(f"Generating with model: {self.model}")
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False,
                options={
                    "temperature": self.temperature,
                    "num_predict": max_tokens,
                }
            )
            
            text = response["message"]["content"]
            
            return LLMResponse(
                text=text,
                model=self.model,
                raw_response=response
            )

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            schema: Expected JSON schema description
            
        Returns:
            Parsed JSON dictionary
        """
        json_system = (
            "You are a JSON generator. "
            "Always respond with valid JSON only, no other text. "
            "Do not include markdown code blocks or backticks."
        )
        
        if system_prompt:
            json_system = system_prompt + "\n" + json_system
        
        if schema:
            json_system += f"\n\nExpected schema: {schema}"
        
        response = self.generate(prompt, system_prompt=json_system)
        
        try:
            # Clean response of markdown formatting
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            return json.loads(text)
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {response.text}")
            raise ValueError(f"Invalid JSON response: {e}")

    def plan_task(
        self,
        user_input: str,
        context: Optional[str] = None,
        tools_available: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create a plan for a complex task.
        
        Args:
            user_input: User request
            context: Relevant context/memory
            tools_available: List of available tools
            
        Returns:
            List of planned steps
        """
        tools_str = ""
        if tools_available:
            tools_str = f"\n\nAvailable tools: {', '.join(tools_available)}"
        
        prompt = f"""Create a detailed step-by-step plan to accomplish this task:

Task: {user_input}

{f'Context: {context}' if context else ''}
{tools_str}

Return a JSON array with steps. Each step must have:
- step (number)
- action (tool to use)
- input (what to pass to the tool)
- description (what this step does)

Example format:
[
  {{"step": 1, "action": "web_search", "input": "latest AI news", "description": "Search for recent AI updates"}},
  {{"step": 2, "action": "summarize", "input": "{{previous_result}}", "description": "Summarize the findings"}}
]

Return ONLY the JSON array, no other text."""

        return self.generate_json(prompt)

    def summarize(
        self,
        text: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> str:
        """
        Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            style: concise, detailed, bullet-points
            
        Returns:
            Summarized text
        """
        prompt = f"""Summarize the following text in {style} style, keeping it under {max_length} words:

{text}

Provide only the summary, no additional text."""

        response = self.generate(prompt)
        return response.text

    def answer_question(
        self,
        question: str,
        context: Optional[str] = None
    ) -> str:
        """
        Answer a question with optional context.
        
        Args:
            question: Question to answer
            context: Relevant context
            
        Returns:
            Answer
        """
        prompt = question
        if context:
            prompt = f"Context: {context}\n\nQuestion: {question}"
        
        response = self.generate(prompt, system_prompt="You are a helpful AI assistant.")
        return response.text

    def classify(
        self,
        text: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """
        Classify text into categories.
        
        Args:
            text: Text to classify
            categories: Possible categories
            
        Returns:
            Classification result with probabilities
        """
        prompt = f"""Classify this text into one of these categories: {', '.join(categories)}

Text: {text}

Return JSON with:
- category: the best matching category
- confidence: 0-1 confidence score
- reasoning: brief explanation"""

        return self.generate_json(prompt)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of extracted entities
        """
        prompt = f"""Extract named entities from this text and return as JSON:

Text: {text}

Return JSON with:
- persons: list of person names
- locations: list of locations
- organizations: list of organizations
- dates: list of dates mentioned
- other_entities: any other notable entities"""

        return self.generate_json(prompt)

    def generate_code(
        self,
        requirement: str,
        language: str = "python"
    ) -> str:
        """
        Generate code based on requirement.
        
        Args:
            requirement: What code to generate
            language: Programming language
            
        Returns:
            Generated code
        """
        prompt = f"""Write {language} code for:

{requirement}

Return only the code, no explanation or markdown formatting."""

        response = self.generate(prompt)
        return response.text

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        prompt = f"""Analyze the sentiment of this text and return JSON:

Text: {text}

Return JSON with:
- sentiment: positive, negative, or neutral
- score: -1.0 to 1.0
- key_emotions: list of detected emotions
- explanation: brief explanation"""

        return self.generate_json(prompt)

    def evaluate_response(
        self,
        question: str,
        answer: str,
        criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate quality of an answer.
        
        Args:
            question: Original question
            answer: The answer to evaluate
            criteria: Evaluation criteria
            
        Returns:
            Evaluation results
        """
        prompt = f"""Evaluate this answer to the question:

Question: {question}
Answer: {answer}

{f'Criteria: {criteria}' if criteria else 'Use standard quality metrics.'}

Return JSON with:
- score: 0-100 quality score
- strengths: list of strengths
- weaknesses: list of weaknesses
- suggestions: improvement suggestions"""

        return self.generate_json(prompt)

    def reason(
        self,
        problem: str,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Reason through a problem.
        
        Args:
            problem: Problem to reason about
            constraints: Constraints to consider
            
        Returns:
            Reasoning and solution
        """
        constraints_str = ""
        if constraints:
            constraints_str = f"\nConstraints: {', '.join(constraints)}"
        
        prompt = f"""Reason through this problem step-by-step:

Problem: {problem}
{constraints_str}

Return JSON with:
- analysis: detailed analysis
- steps: reasoning steps
- solution: proposed solution
- alternatives: alternative approaches"""

        return self.generate_json(prompt)

    def batch_process(
        self,
        items: List[str],
        instruction: str,
        return_json: bool = False
    ) -> List[Any]:
        """
        Process multiple items with the same instruction.
        
        Args:
            items: List of items to process
            instruction: Instruction for each item
            return_json: Whether to parse as JSON
            
        Returns:
            List of processed results
        """
        results = []
        
        for item in items:
            prompt = f"{instruction}\n\nItem: {item}"
            
            if return_json:
                result = self.generate_json(prompt)
            else:
                response = self.generate(prompt)
                result = response.text
            
            results.append(result)
        
        return results

    def conversation(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Have a multi-turn conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System instructions
            
        Returns:
            LLM response
        """
        try:
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt}
                ] + messages
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False,
                options={"temperature": self.temperature}
            )
            
            text = response["message"]["content"]
            
            return LLMResponse(
                text=text,
                model=self.model,
                raw_response=response
            )
        
        except Exception as e:
            self.logger.error(f"Conversation error: {e}")
            raise


# Backwards compatibility
MODEL = "mistral"

def generate_response(prompt: str, stream=False):
    """Legacy function for backwards compatibility."""
    llm = LocalLLM(model=MODEL)
    response = llm.generate(prompt)
    return response.text


def fallback_response(prompt: str) -> str:
    """Simple rule-based fallback."""
    if "stock" in prompt.lower():
        return "Checking markets, boss. Tech up 1.2%, energy flat."
    return "I'm having trouble connecting to my cognitive processing unit, boss. Standing by on local backup."

