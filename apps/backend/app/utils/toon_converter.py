"""
TOON Format Converter - Token-efficient serialization for LLMs
Converts JSON ↔ TOON to save 30-50% tokens
"""
import json
from typing import Any, Dict, List
import yaml
import logging

logger = logging.getLogger(__name__)

class TOONConverter:
    """
    TOON (Token-Optimized Object Notation) converter
    Uses YAML-like format to reduce token usage
    """

    @staticmethod
    def json_to_toon(data: Dict[str, Any], compact: bool = True) -> str:
        """
        Convert JSON/dict to TOON format

        Args:
            data: Python dict or JSON-compatible object
            compact: Remove unnecessary whitespace

        Returns:
            TOON formatted string (YAML-style)
        """
        try:
            # TOON is essentially clean YAML
            toon_str = yaml.dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
                indent=2
            )

            if compact:
                # Remove trailing spaces and empty lines
                lines = toon_str.split('\n')
                toon_str = '\n'.join(
                    line.rstrip() for line in lines if line.strip()
                )

            return toon_str

        except Exception as e:
            logger.error(f"Failed to convert JSON to TOON: {e}")
            raise ValueError(f"Invalid JSON for TOON conversion: {e}")

    @staticmethod
    def toon_to_json(toon_str: str) -> Dict[str, Any]:
        """
        Convert TOON to JSON/dict

        Args:
            toon_str: TOON formatted string

        Returns:
            Python dictionary
        """
        try:
            return yaml.safe_load(toon_str)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse TOON: {e}")
            raise ValueError(f"Invalid TOON format: {e}")

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough token estimation
        1 token ≈ 4 characters (GPT-style tokenization)

        Args:
            text: Text to estimate

        Returns:
            Approximate token count
        """
        return len(text) // 4

    @staticmethod
    def should_use_toon(data: Dict[str, Any], threshold: int = 1000) -> bool:
        """
        Determine if TOON conversion is beneficial

        Args:
            data: Data to check
            threshold: Token threshold (default 1000)

        Returns:
            True if data is large enough to benefit from TOON
        """
        json_str = json.dumps(data)
        tokens = TOONConverter.estimate_tokens(json_str)
        return tokens > threshold

    @staticmethod
    def get_token_savings(data: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate token savings from using TOON

        Args:
            data: Data to analyze

        Returns:
            Dict with json_tokens, toon_tokens, savings_tokens, savings_percent
        """
        json_str = json.dumps(data)
        toon_str = TOONConverter.json_to_toon(data)

        json_tokens = TOONConverter.estimate_tokens(json_str)
        toon_tokens = TOONConverter.estimate_tokens(toon_str)
        savings = json_tokens - toon_tokens
        savings_pct = int((savings / json_tokens) * 100) if json_tokens > 0 else 0

        return {
            "json_tokens": json_tokens,
            "toon_tokens": toon_tokens,
            "savings_tokens": savings,
            "savings_percent": savings_pct
        }

# Global instance
toon_converter = TOONConverter()
