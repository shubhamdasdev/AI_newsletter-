"""
Content refinement module for AI Newsletter Pipeline.
"""
from typing import Dict, Any, List, Tuple
import logging
from language_tool_python import LanguageToolPublicAPI
from ..config.settings import LANGUAGE_TOOL_LANGUAGE

logger = logging.getLogger(__name__)

class ContentRefiner:
    def __init__(self):
        try:
            self.language_tool = LanguageToolPublicAPI(LANGUAGE_TOOL_LANGUAGE)
            logger.info(f"Initialized language tool for {LANGUAGE_TOOL_LANGUAGE}")
        except Exception as e:
            logger.error(f"Error initializing language tool: {str(e)}")
            raise

    def refine_newsletter(self, newsletter: Dict[str, Any]) -> Dict[str, Any]:
        """Refine the entire newsletter content."""
        try:
            content = newsletter.get("content", "")
            if not content:
                return newsletter
            
            # Apply refinements in sequence
            content = self.fix_grammar(content)
            content = self.enhance_formatting(content)
            content = self.add_section_links(content)
            
            refined_newsletter = newsletter.copy()
            refined_newsletter["content"] = content
            
            return refined_newsletter
        
        except Exception as e:
            logger.error(f"Error refining newsletter: {str(e)}")
            return newsletter

    def fix_grammar(self, text: str) -> str:
        """Fix grammar and style issues."""
        try:
            matches = self.language_tool.check(text)
            
            # Sort matches by position in reverse order to avoid offset issues
            matches.sort(key=lambda x: x.offset, reverse=True)
            
            # Apply corrections
            for match in matches:
                if match.replacements:
                    # Get the best replacement
                    replacement = match.replacements[0]
                    
                    # Replace the text
                    text = text[:match.offset] + replacement + text[match.offset + match.errorLength:]
            
            return text
        
        except Exception as e:
            logger.error(f"Error fixing grammar: {str(e)}")
            return text

    def enhance_formatting(self, content: str) -> str:
        """Enhance markdown formatting."""
        try:
            lines = content.split("\n")
            enhanced_lines = []
            in_code_block = False
            
            for line in lines:
                # Skip code blocks
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    enhanced_lines.append(line)
                    continue
                
                if in_code_block:
                    enhanced_lines.append(line)
                    continue
                
                # Enhance headings
                if line.strip().startswith("#"):
                    line = self._enhance_heading(line)
                
                # Enhance links
                if "[" in line and "]" in line:
                    line = self._enhance_links(line)
                
                # Enhance emphasis
                line = self._enhance_emphasis(line)
                
                enhanced_lines.append(line)
            
            return "\n".join(enhanced_lines)
        
        except Exception as e:
            logger.error(f"Error enhancing formatting: {str(e)}")
            return content

    def add_section_links(self, content: str) -> str:
        """Add table of contents and section links."""
        try:
            lines = content.split("\n")
            headings = []
            toc_lines = ["## Table of Contents\n"]
            
            # Find all headings
            for i, line in enumerate(lines):
                if line.strip().startswith("## "):
                    heading = line.strip("# ").strip()
                    anchor = self._create_anchor(heading)
                    headings.append((heading, anchor, i))
            
            # Create table of contents
            for heading, anchor, _ in headings:
                toc_lines.append(f"- [{heading}](#{anchor})")
            
            # Add anchors to headings
            for heading, anchor, i in reversed(headings):
                lines[i] = f"## {heading} <a name='{anchor}'></a>"
            
            # Insert table of contents after first heading
            if len(lines) > 0:
                content = "\n".join(lines[:1] + toc_lines + ["\n"] + lines[1:])
            
            return content
        
        except Exception as e:
            logger.error(f"Error adding section links: {str(e)}")
            return content

    def _enhance_heading(self, line: str) -> str:
        """Enhance markdown heading formatting."""
        try:
            # Add emoji based on heading content
            heading = line.strip("# ").lower()
            emoji = self._get_section_emoji(heading)
            
            if emoji and not any(e in line for e in "🤖📊📈🔍💡"):
                return f"{line.rstrip()} {emoji}"
            
            return line
        
        except Exception as e:
            logger.error(f"Error enhancing heading: {str(e)}")
            return line

    def _enhance_links(self, line: str) -> str:
        """Enhance markdown link formatting."""
        try:
            # Add link icon to external links
            if "http" in line and "[" in line and "]" in line:
                line = line.replace("](", "]( 🔗 ")
            
            return line
        
        except Exception as e:
            logger.error(f"Error enhancing links: {str(e)}")
            return line

    def _enhance_emphasis(self, line: str) -> str:
        """Enhance text emphasis."""
        try:
            # Add bold to important terms
            important_terms = ["AI", "ML", "Deep Learning", "Product Management"]
            
            for term in important_terms:
                if term in line and f"**{term}**" not in line:
                    line = line.replace(term, f"**{term}**")
            
            return line
        
        except Exception as e:
            logger.error(f"Error enhancing emphasis: {str(e)}")
            return line

    def _create_anchor(self, heading: str) -> str:
        """Create HTML anchor from heading."""
        return heading.lower().replace(" ", "-").replace(":", "").replace("?", "")

    def _get_section_emoji(self, heading: str) -> str:
        """Get appropriate emoji for section heading."""
        emoji_map = {
            "ai": "🤖",
            "machine learning": "🧠",
            "product": "📊",
            "management": "📈",
            "insight": "💡",
            "news": "📰",
            "research": "🔬",
            "development": "⚙️",
            "analysis": "📊",
            "feature": "✨",
            "update": "🔄"
        }
        
        for key, emoji in emoji_map.items():
            if key in heading:
                return emoji
        
        return ""
