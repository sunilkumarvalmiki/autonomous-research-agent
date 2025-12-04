"""Unit tests for utility functions."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent.utils.text_utils import (
    chunk_text,
    extract_code_blocks,
    truncate_text,
    format_prompt_with_examples,
    calculate_token_estimate,
    merge_dicts_deep
)


class TestTextUtils(unittest.TestCase):
    """Test text utility functions."""
    
    def test_chunk_text_simple(self):
        """Test basic text chunking."""
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=200, overlap=20)
        
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 200)
    
    def test_chunk_text_small(self):
        """Test chunking text smaller than chunk size."""
        text = "Short text"
        chunks = chunk_text(text, chunk_size=200)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)
    
    def test_chunk_text_sentence_break(self):
        """Test that chunking respects sentence boundaries."""
        text = "First sentence. " * 50
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        
        # Most chunks should end with a period
        period_endings = sum(1 for chunk in chunks if chunk.endswith('.'))
        self.assertGreater(period_endings, 0)
    
    def test_extract_code_blocks(self):
        """Test extracting code blocks from markdown."""
        text = """
Some text here.

```python
def hello():
    print("world")
```

More text.

```javascript
console.log("hello");
```
        """
        
        blocks = extract_code_blocks(text)
        
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]['language'], 'python')
        self.assertIn('def hello', blocks[0]['code'])
        self.assertEqual(blocks[1]['language'], 'javascript')
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "a" * 1000
        truncated = truncate_text(text, max_length=100)
        
        self.assertLessEqual(len(truncated), 100)
        self.assertTrue(truncated.endswith("..."))
    
    def test_truncate_short_text(self):
        """Test that short text is not truncated."""
        text = "Short"
        truncated = truncate_text(text, max_length=100)
        
        self.assertEqual(text, truncated)
    
    def test_format_prompt_with_examples(self):
        """Test few-shot prompt formatting."""
        task = "Classify sentiment"
        examples = [
            {"input": "I love this!", "output": "positive"},
            {"input": "This is terrible", "output": "negative"}
        ]
        query = "It's okay"
        
        prompt = format_prompt_with_examples(task, examples, query)
        
        self.assertIn(task, prompt)
        self.assertIn("I love this!", prompt)
        self.assertIn("positive", prompt)
        self.assertIn("It's okay", prompt)
    
    def test_calculate_token_estimate(self):
        """Test token count estimation."""
        text = "word " * 100  # 100 words
        tokens = calculate_token_estimate(text)
        
        # Should be roughly 100-150 tokens
        self.assertGreater(tokens, 50)
        self.assertLess(tokens, 200)
    
    def test_merge_dicts_deep(self):
        """Test deep dictionary merging."""
        dict1 = {
            "a": 1,
            "b": {"c": 2, "d": 3}
        }
        dict2 = {
            "b": {"c": 5},
            "e": 4
        }
        
        merged = merge_dicts_deep(dict1, dict2)
        
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["c"], 5)  # Overridden
        self.assertEqual(merged["b"]["d"], 3)  # Preserved
        self.assertEqual(merged["e"], 4)  # Added


if __name__ == '__main__':
    unittest.main()
