"""
Equation Extractor Module
Uses Ollama LLM to identify and extract mathematical equations from text.
"""

import json
import logging
import re
from typing import List, Dict, Optional

try:
    import ollama
except ImportError:
    raise ImportError("ollama is required. Install it with: pip install ollama")


logger = logging.getLogger(__name__)


class EquationExtractor:
    """Extract mathematical equations from text using Ollama LLM."""

    def __init__(
        self,
        model: str = "mistral",
        host: str = "http://localhost:11434",
        log_level: int = logging.INFO
    ):
        """
        Initialize EquationExtractor.
        
        Args:
            model: Ollama model to use (default: mistral)
            host: Ollama server host and port
            log_level: Logging level
        """
        self.model = model
        self.host = host
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        # Configure ollama client
        self.client = ollama.Client(host=host)
        
        # Test connection
        self._test_connection()

    def _test_connection(self) -> bool:
        """
        Test connection to Ollama server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Testing connection to Ollama at {self.host}")
            # Attempt a simple list models call
            response = self.client.list()
            self.logger.info(f"Ollama connection successful. Available models: {len(response.get('models', []))}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to connect to Ollama: {e}")
            self.logger.warning(f"Make sure Ollama is running at {self.host}")
            return False

    def extract_equations(self, text: str) -> List[str]:
        """
        Extract mathematical equations from text using Ollama LLM.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of extracted equations
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided for equation extraction")
            return []

        # First, try to extract equations using regex patterns
        simple_equations = self._extract_equations_regex(text)
        
        # Then use LLM to find more sophisticated equations
        llm_equations = self._extract_equations_llm(text)
        
        # Combine and deduplicate
        all_equations = simple_equations + llm_equations
        unique_equations = list(dict.fromkeys(all_equations))  # Remove duplicates while preserving order
        
        self.logger.info(f"Extracted {len(unique_equations)} unique equations")
        return unique_equations

    def _extract_equations_regex(self, text: str) -> List[str]:
        """
        Extract equations using regex patterns.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of equations found by regex
        """
        equations = []
        
        # Pattern for equations: x + y = z, 2x^2 + 3x - 5 = 0, etc.
        patterns = [
            r"[a-zA-Z0-9\s\+\-\*/\(\)\.^=]+=[a-zA-Z0-9\s\+\-\*/\(\)\.^]+",  # Basic equation
            r"\b[a-zA-Z]\s*=\s*[\d\+\-\*/\(\)\.^]+\b",  # Simple variable assignment
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                match = match.strip()
                if match and "=" in match:
                    equations.append(match)
        
        self.logger.debug(f"Regex extraction found {len(equations)} equations")
        return equations

    def _extract_equations_llm(self, text: str, max_length: int = 2000) -> List[str]:
        """
        Use Ollama LLM to extract equations from text.
        
        Args:
            text: Text content to analyze
            max_length: Maximum length of text to send to LLM
            
        Returns:
            List of equations extracted by LLM
        """
        try:
            # Truncate text if too long
            if len(text) > max_length:
                text = text[:max_length]
            
            prompt = f"""Analyze the following text and extract ALL mathematical equations.
Return ONLY the equations in a JSON array format, nothing else.

Text:
{text}

Return ONLY valid JSON array of equation strings. Example: ["x + 2 = 5", "2y^2 - 3y + 1 = 0"]
If no equations found, return: []"""

            self.logger.debug("Sending request to Ollama for equation extraction")
            
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.3,  # Low temperature for consistency
                    "top_p": 0.9,
                }
            )
            
            result_text = response["response"].strip()
            self.logger.debug(f"LLM response: {result_text}")
            
            # Try to extract JSON array from response
            equations = self._parse_json_response(result_text)
            
            self.logger.debug(f"LLM extraction found {len(equations)} equations")
            return equations

        except Exception as e:
            self.logger.warning(f"LLM extraction failed: {e}")
            return []

    def _parse_json_response(self, response: str) -> List[str]:
        """
        Parse JSON array from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            List of equations
        """
        try:
            # Try to find JSON array in response
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                equations = json.loads(json_str)
                
                # Ensure all items are strings
                equations = [str(eq).strip() for eq in equations if eq]
                return equations
            
            return []
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            return []

    def extract_with_context(self, text: str) -> List[Dict[str, str]]:
        """
        Extract equations with surrounding context.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of dicts with 'equation' and 'context' keys
        """
        equations = self.extract_equations(text)
        result = []
        
        for equation in equations:
            # Find context around equation in original text
            if equation in text:
                idx = text.find(equation)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(equation) + 100)
                context = text[start:end]
                
                result.append({
                    "equation": equation,
                    "context": context.strip()
                })
            else:
                result.append({
                    "equation": equation,
                    "context": ""
                })
        
        return result

    def validate_equation(self, equation: str) -> bool:
        """
        Validate if a string looks like a valid equation.
        
        Args:
            equation: Equation string to validate
            
        Returns:
            True if equation appears valid
        """
        if not equation or "=" not in equation:
            return False
        
        # Check for basic equation structure
        parts = equation.split("=")
        if len(parts) != 2:
            return False
        
        # Check if both sides have some content
        if not parts[0].strip() or not parts[1].strip():
            return False
        
        return True
