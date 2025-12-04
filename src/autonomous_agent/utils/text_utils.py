"""Utility functions for the autonomous research agent."""

from typing import List, Dict, Any
import re


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only use if in latter half
                end = start + break_point + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown text.
    
    Args:
        text: Text containing code blocks
    
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    code_blocks = []
    for match in matches:
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        code_blocks.append({
            'language': language,
            'code': code
        })
    
    return code_blocks


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_prompt_with_examples(
    task: str,
    examples: List[Dict[str, str]],
    query: str
) -> str:
    """
    Format a few-shot prompt with examples.
    
    Args:
        task: Task description
        examples: List of example dicts with 'input' and 'output' keys
        query: Current query
    
    Returns:
        Formatted prompt
    """
    prompt_parts = [task, ""]
    
    for i, example in enumerate(examples, 1):
        prompt_parts.append(f"Example {i}:")
        prompt_parts.append(f"Input: {example['input']}")
        prompt_parts.append(f"Output: {example['output']}")
        prompt_parts.append("")
    
    prompt_parts.append(f"Now, for the following input:")
    prompt_parts.append(f"Input: {query}")
    prompt_parts.append("Output:")
    
    return "\n".join(prompt_parts)


def calculate_token_estimate(text: str) -> int:
    """
    Estimate token count for text.
    Simple approximation: ~4 characters per token.
    
    Args:
        text: Text to estimate
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def merge_dicts_deep(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        else:
            result[key] = value
    
    return result
