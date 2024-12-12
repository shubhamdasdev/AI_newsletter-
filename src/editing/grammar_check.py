"""
Grammar and style checking module for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any, Tuple
import logging
from language_tool_python import LanguageTool, Match
from ..config.settings import LANGUAGE_TOOL_LANGUAGE

logger = logging.getLogger(__name__)

class GrammarChecker:
    def __init__(self):
        try:
            self.tool = LanguageTool(LANGUAGE_TOOL_LANGUAGE)
            self._configure_rules()
            logger.info(f"Initialized grammar checker for {LANGUAGE_TOOL_LANGUAGE}")
        except Exception as e:
            logger.error(f"Error initializing grammar checker: {str(e)}")
            raise

    def _configure_rules(self):
        """Configure LanguageTool rules."""
        try:
            # Enable additional rules
            self.tool.enable_spellchecking()
            
            # Disable some rules that might interfere with technical writing
            rules_to_disable = [
                "UPPERCASE_SENTENCE_START",  # For technical terms that start lowercase
                "EN_QUOTES",                 # For code snippets
                "WHITESPACE_RULE",          # For code formatting
            ]
            
            for rule in rules_to_disable:
                self.tool.disable_rule(rule)
        
        except Exception as e:
            logger.error(f"Error configuring rules: {str(e)}")

    def check_text(self, text: str) -> List[Dict[str, Any]]:
        """Check text for grammar and style issues."""
        try:
            matches = self.tool.check(text)
            return [self._format_match(match) for match in matches]
        
        except Exception as e:
            logger.error(f"Error checking text: {str(e)}")
            return []

    def fix_text(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix grammar and style issues in text."""
        try:
            matches = self.tool.check(text)
            fixes_applied = []
            
            # Sort matches by position in reverse order to avoid offset issues
            matches.sort(key=lambda x: x.offset, reverse=True)
            
            # Apply fixes
            for match in matches:
                if match.replacements:
                    # Get the best replacement
                    replacement = match.replacements[0]
                    
                    # Record the fix
                    fix = self._format_match(match)
                    fix["replacement"] = replacement
                    fixes_applied.append(fix)
                    
                    # Apply the fix
                    text = text[:match.offset] + replacement + text[match.offset + match.errorLength:]
            
            return text, fixes_applied
        
        except Exception as e:
            logger.error(f"Error fixing text: {str(e)}")
            return text, []

    def check_markdown(self, markdown: str) -> List[Dict[str, Any]]:
        """Check markdown text while preserving formatting."""
        try:
            # Split into lines
            lines = markdown.split("\n")
            all_issues = []
            in_code_block = False
            
            for i, line in enumerate(lines, 1):
                # Skip code blocks
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                
                if in_code_block:
                    continue
                
                # Skip markdown headings
                if line.strip().startswith("#"):
                    continue
                
                # Remove markdown links
                line = self._remove_markdown_formatting(line)
                
                # Check the line
                issues = self.check_text(line)
                for issue in issues:
                    issue["line_number"] = i
                    all_issues.append(issue)
            
            return all_issues
        
        except Exception as e:
            logger.error(f"Error checking markdown: {str(e)}")
            return []

    def _format_match(self, match: Match) -> Dict[str, Any]:
        """Format a LanguageTool match into a standardized format."""
        return {
            "message": match.message,
            "context": match.context,
            "offset": match.offset,
            "length": match.errorLength,
            "rule_id": match.ruleId,
            "category": match.category,
            "replacements": match.replacements
        }

    def _remove_markdown_formatting(self, text: str) -> str:
        """Remove markdown formatting for grammar checking."""
        # Remove links
        while "[" in text and "](" in text and ")" in text:
            start = text.find("[")
            mid = text.find("](")
            end = text.find(")", mid)
            if start == -1 or mid == -1 or end == -1:
                break
            link_text = text[start + 1:mid]
            text = text[:start] + link_text + text[end + 1:]
        
        # Remove bold and italic
        text = text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
        
        return text

    def get_style_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """Get style improvement suggestions."""
        try:
            suggestions = []
            
            # Check sentence length
            sentences = text.split(". ")
            for i, sentence in enumerate(sentences):
                if len(sentence.split()) > 25:
                    suggestions.append({
                        "type": "style",
                        "message": "Consider breaking this long sentence into smaller ones",
                        "context": sentence,
                        "position": i
                    })
            
            # Check paragraph length
            paragraphs = text.split("\n\n")
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.split()) > 100:
                    suggestions.append({
                        "type": "style",
                        "message": "Consider breaking this long paragraph into smaller ones",
                        "context": paragraph[:100] + "...",
                        "position": i
                    })
            
            # Check for passive voice (simple check)
            passive_indicators = ["is being", "are being", "was being", "were being",
                               "has been", "have been", "had been"]
            for indicator in passive_indicators:
                if indicator in text.lower():
                    suggestions.append({
                        "type": "style",
                        "message": f"Consider using active voice instead of '{indicator}'",
                        "context": text[max(0, text.lower().find(indicator) - 20):
                                     min(len(text), text.lower().find(indicator) + 40)]
                    })
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Error getting style suggestions: {str(e)}")
            return [] 