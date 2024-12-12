"""
Fact checking agent for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any, Tuple
import logging
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from .chain_init import create_llm, get_token_usage

logger = logging.getLogger(__name__)

class FactCheckAgent:
    def __init__(self):
        try:
            # Create a more conservative LLM for fact checking
            self.llm = create_llm(temperature=0.1)
            self._create_chains()
            logger.info("Initialized fact check agent")
        except Exception as e:
            logger.error(f"Error initializing fact check agent: {str(e)}")
            raise

    def _create_chains(self):
        """Create the necessary LangChain chains."""
        # Chain for checking technical accuracy
        technical_template = """You are a technical fact checker specializing in AI and product management.
        Please analyze the following text for technical accuracy and identify any potential issues:

        Text: {text}

        Please identify:
        1. Any technical inaccuracies
        2. Outdated information
        3. Misleading statements
        4. Missing context

        Return your findings in a structured format:
        - Issues Found: (list specific issues)
        - Suggested Corrections: (provide accurate alternatives)
        - Confidence Level: (high/medium/low)
        """
        self.technical_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(technical_template)
        )

        # Chain for source verification
        source_template = """You are a source verification specialist.
        Please analyze the following article and its source:

        Title: {title}
        Source: {source}
        Content: {content}

        Please verify:
        1. Source credibility
        2. Publication date relevance
        3. Author expertise (if available)
        4. Citation quality

        Return your assessment in a structured format:
        - Source Credibility: (high/medium/low)
        - Currency: (current/outdated)
        - Verification Status: (verified/unverified/suspicious)
        """
        self.source_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(source_template)
        )

    @get_token_usage
    def check_technical_accuracy(self, text: str) -> Dict[str, Any]:
        """Check technical accuracy of content."""
        try:
            result = self.technical_chain.run(text=text)
            return self._parse_technical_check(result)
        except Exception as e:
            logger.error(f"Error checking technical accuracy: {str(e)}")
            return {"status": "error", "message": str(e)}

    @get_token_usage
    def verify_source(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Verify source credibility and relevance."""
        try:
            result = self.source_chain.run(
                title=article.get("title", ""),
                source=article.get("url", ""),
                content=article.get("content", "")
            )
            return self._parse_source_verification(result)
        except Exception as e:
            logger.error(f"Error verifying source: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _parse_technical_check(self, result: str) -> Dict[str, Any]:
        """Parse technical check results."""
        try:
            lines = result.strip().split("\n")
            parsed = {
                "issues": [],
                "corrections": [],
                "confidence": "low"
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if "Issues Found:" in line:
                    current_section = "issues"
                elif "Suggested Corrections:" in line:
                    current_section = "corrections"
                elif "Confidence Level:" in line:
                    parsed["confidence"] = line.split(":")[-1].strip().lower()
                elif line.startswith("- ") and current_section:
                    parsed[current_section].append(line[2:])
            
            return parsed
        except Exception as e:
            logger.error(f"Error parsing technical check: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _parse_source_verification(self, result: str) -> Dict[str, Any]:
        """Parse source verification results."""
        try:
            lines = result.strip().split("\n")
            parsed = {
                "credibility": "low",
                "currency": "outdated",
                "status": "unverified"
            }
            
            for line in lines:
                line = line.strip()
                if "Source Credibility:" in line:
                    parsed["credibility"] = line.split(":")[-1].strip().lower()
                elif "Currency:" in line:
                    parsed["currency"] = line.split(":")[-1].strip().lower()
                elif "Verification Status:" in line:
                    parsed["status"] = line.split(":")[-1].strip().lower()
            
            return parsed
        except Exception as e:
            logger.error(f"Error parsing source verification: {str(e)}")
            return {"status": "error", "message": str(e)}

    def validate_newsletter(self, newsletter: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Validate entire newsletter content."""
        try:
            content = newsletter.get("content", "")
            articles = newsletter.get("articles", [])
            
            # Check technical accuracy of content
            technical_issues = self.check_technical_accuracy(content)
            
            # Verify sources
            source_issues = []
            for article in articles:
                verification = self.verify_source(article)
                if verification.get("status") != "verified":
                    source_issues.append({
                        "article": article.get("title", ""),
                        "issues": verification
                    })
            
            # Combine all issues
            all_issues = []
            if technical_issues.get("issues"):
                all_issues.append({
                    "type": "technical",
                    "details": technical_issues
                })
            if source_issues:
                all_issues.append({
                    "type": "source",
                    "details": source_issues
                })
            
            # Determine if newsletter passes validation
            passes_validation = (
                technical_issues.get("confidence", "low") != "low" and
                len(source_issues) == 0
            )
            
            return passes_validation, all_issues
        
        except Exception as e:
            logger.error(f"Error validating newsletter: {str(e)}")
            return False, [{"type": "error", "message": str(e)}] 