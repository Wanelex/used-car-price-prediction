"""
LLM Service for Mechanical Buyability Analysis
Provides expert automotive engineering analysis using OpenAI GPT-4
"""

from typing import Dict, Any, Optional
import json
from loguru import logger

try:
    from openai import OpenAI, APIError, RateLimitError, APITimeoutError
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Run: pip install openai")

import sys
import os
sys.path.insert(0, str(__file__).replace("\\", "/").rsplit("/", 4)[0])
from config.settings import settings


# System prompt for automotive expert analysis
AUTOMOTIVE_EXPERT_PROMPT = """You are CarVisor's Chief Automotive Engineer. Your goal is to analyze used car technical specifications to determine mechanical reliability, maintenance risks, and overall buyability.

INPUT DATA:
You will receive technical details: Make, Series, Model, Year, Fuel, Gear, KM, Body Type, HP, Engine Volume, Drive, and Price (if available).

YOUR TASKS:
1. IDENTIFY COMPONENTS: Determine the specific Engine Code (e.g., N47, M57, TSI, dCi) and Transmission Code (e.g., ZF 8HP, DSG, CVT) based on the year and specs provided.
2. ANALYZE RELIABILITY: assessing common chronic problems for this specific engine/transmission pairing.
3. EVALUATE MILEAGE (KM): Analyze if this specific engine/transmission structure can withstand the provided KM.
4. CALCULATE SCORE: Assign a "Mechanical Buyability Score" (0-100).
   - 100: Legendary reliability (e.g., Toyota Corolla 1.6 atm).
   - 0: Mechanical time bomb (e.g., High KM Range Rover with crank issues).

OUTPUT FORMAT:
You must write brief descriptions. Do not write long paragraphs. Get to the point.
You must output ONLY a valid JSON object with the following structure. Do not output markdown code blocks like ```json."""

class LLMMechanicalAnalyzer:
    """OpenAI-powered mechanical reliability analyzer"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.timeout = settings.OPENAI_TIMEOUT
        self.max_retries = settings.OPENAI_MAX_RETRIES
        self.client: Optional[OpenAI] = None

        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not available - LLM analysis disabled")
        elif not self.api_key:
            logger.warning("OpenAI API key not configured - LLM analysis disabled")
        else:
            try:
                # Create a custom httpx client without proxy to avoid conflicts
                # with the crawler's proxy settings
                http_client = httpx.Client(
                    timeout=httpx.Timeout(self.timeout, connect=10.0),
                    follow_redirects=True
                )
                self.client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                    http_client=http_client
                )
                logger.info(f"LLM Analyzer initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def _build_user_prompt(self, car_data: Dict[str, Any]) -> str:
        """Convert listing data to structured prompt for LLM"""
        # Extract fields with fallbacks for Turkish/English field names
        make = car_data.get('marka') or car_data.get('brand') or 'Unknown'
        series = car_data.get('seri') or car_data.get('series') or 'Unknown'
        model = car_data.get('model') or 'Unknown'
        year = car_data.get('yil') or car_data.get('year') or car_data.get('Model Yıl') or 'Unknown'
        fuel = car_data.get('yakit_tipi') or car_data.get('fuel_type') or car_data.get('yakit') or 'Unknown'
        gear = car_data.get('vites') or car_data.get('transmission') or 'Unknown'
        km = car_data.get('km') or car_data.get('mileage') or car_data.get('Km') or 'Unknown'
        body_type = car_data.get('kasa_tipi') or car_data.get('body_type') or 'Unknown'
        hp = car_data.get('motor_gucu') or car_data.get('engine_power') or car_data.get('Beygir Gucu') or 'Unknown'
        engine_volume = car_data.get('motor_hacmi') or car_data.get('engine_volume') or car_data.get('CCM') or 'Unknown'
        drive = car_data.get('cekis') or car_data.get('drive_type') or 'Unknown'
        price = car_data.get('fiyat') or car_data.get('price') or 'Not specified'

        prompt = f"""Analyze this used car for mechanical buyability:

Make: {make}
Series: {series}
Model: {model}
Year: {year}
Fuel Type: {fuel}
Transmission: {gear}
Mileage (KM): {km}
Body Type: {body_type}
Horsepower: {hp}
Engine Volume: {engine_volume}
Drive Type: {drive}
Price: {price}

Provide your expert analysis in the following JSON format:
{{
  "car_identification": {{
    "engine_code": "specific engine code (e.g., N47D20, 2ZR-FE, EA888)",
    "transmission_name": "specific transmission name (e.g., ZF 8HP, Aisin U660E, DSG DQ200)",
    "generation": "car generation if applicable (e.g., F30, W212, MK7)"
  }},
  "expert_analysis": {{
    "general_comment": "overall assessment of this specific vehicle",
    "engine_reliability": "engine-specific reliability analysis with known issues",
    "transmission_reliability": "transmission-specific reliability analysis with known issues",
    "km_endurance_check": "assessment of whether this engine/transmission can handle the current mileage"
  }},
  "recommendation": {{
    "verdict": "detailed buying recommendation",
    "buy_or_pass": "Clear verdict: High Risk / Pass, Medium Risk / Inspect, or Low Risk / Buy"
  }},
  "scores": {{
    "mechanical_score": 0-100,
    "reasoning_for_score": "explanation of score calculation"
  }}
}}"""
        return prompt

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response"""
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```'):
                # Extract content between ```json and ```
                lines = cleaned.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                cleaned = '\n'.join(json_lines)

            # Handle case where it starts with json keyword
            if cleaned.lower().startswith('json'):
                cleaned = cleaned[4:].strip()

            parsed = json.loads(cleaned)

            # Validate required structure
            required_keys = ['car_identification', 'expert_analysis', 'recommendation', 'scores']
            for key in required_keys:
                if key not in parsed:
                    raise ValueError(f"Missing required key: {key}")

            # Validate mechanical_score is 0-100
            score = parsed['scores'].get('mechanical_score')
            if score is None:
                raise ValueError("Missing mechanical_score")

            # Convert to int if it's a float or string
            if isinstance(score, str):
                score = int(float(score))
            elif isinstance(score, float):
                score = int(score)

            if not isinstance(score, int) or score < 0 or score > 100:
                raise ValueError(f"Invalid mechanical_score: {score}")

            # Ensure score is stored as int
            parsed['scores']['mechanical_score'] = score

            # Validate nested structures
            if 'engine_code' not in parsed['car_identification']:
                parsed['car_identification']['engine_code'] = 'Unknown'
            if 'transmission_name' not in parsed['car_identification']:
                parsed['car_identification']['transmission_name'] = 'Unknown'

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError("LLM returned invalid JSON")
        except Exception as e:
            logger.error(f"Error validating LLM response: {e}")
            raise

    async def analyze_mechanical_reliability(
        self,
        car_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze car mechanical reliability using OpenAI GPT-4

        Args:
            car_data: Dictionary containing car specifications

        Returns:
            Parsed LLM analysis or None if API key not configured/failed
        """
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI package not installed - skipping LLM analysis")
            return None

        if not self.client:
            logger.warning("OpenAI client not initialized - skipping LLM analysis")
            return None

        try:
            user_prompt = self._build_user_prompt(car_data)

            make = car_data.get('marka') or car_data.get('brand') or 'Unknown'
            model = car_data.get('model') or 'Unknown'
            logger.info(f"Calling OpenAI {self.model} for mechanical analysis: {make} {model}")

            # Make OpenAI API call (synchronous, but wrapped for async compatibility)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": AUTOMOTIVE_EXPERT_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_completion_tokens=1500,  # Use max_completion_tokens for newer models
                response_format={"type": "json_object"}  # Enforce JSON mode
            )

            response_text = response.choices[0].message.content
            logger.info("OpenAI response received successfully")

            # Parse and validate response
            analysis = self._parse_llm_response(response_text)

            return analysis

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return None
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            return None
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except ValueError as e:
            logger.error(f"LLM response parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in LLM analysis: {e}")
            return None


# Global instance
llm_analyzer = LLMMechanicalAnalyzer()
