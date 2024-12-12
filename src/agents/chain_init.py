"""
LangChain initialization module for AI Newsletter Pipeline.
"""
import logging
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config.settings import GEMINI_API_KEY, GEMINI_MODEL, LLM_TEMPERATURE
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.callbacks import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)

def create_llm(temperature=LLM_TEMPERATURE):
    """Initialize the language model.
    
    Args:
        temperature (float, optional): Temperature for the model. Defaults to LLM_TEMPERATURE.
    """
    try:
        # Configure Gemini with explicit API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize LangChain with Gemini
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temperature,  # Use the passed temperature
            google_api_key=GEMINI_API_KEY,
            convert_system_message_to_human=True
        )
        
        logger.info(f"Initialized Gemini model: {GEMINI_MODEL}")
        return llm
    
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise

def create_summarization_chain():
    """Create a chain for article summarization."""
    try:
        llm = create_llm()  # Lower temperature for more focused summaries
        
        template = """You are an AI assistant tasked with summarizing technical articles about AI and product management.
        Please provide a concise summary of the following article, highlighting the key points and maintaining technical accuracy.
        
        Article Title: {title}
        Article Content: {content}
        
        Please provide a summary in the following format:
        - Key Points (2-3 bullet points)
        - Brief Summary (2-3 sentences)
        - Technical Details (if any)
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        return LLMChain(llm=llm, prompt=prompt)
    
    except Exception as e:
        logger.error(f"Error creating summarization chain: {str(e)}")
        raise

def create_newsletter_chain():
    """Create a chain for newsletter drafting."""
    try:
        llm = create_llm(temperature=0.7)  # Higher temperature for more creative writing
        
        template = """You are an AI assistant tasked with creating an engaging newsletter about AI and product management.
        Please create a newsletter section using the following summaries of articles.
        
        Article Summaries:
        {summaries}
        
        Please create a newsletter section that:
        1. Has an engaging title
        2. Introduces the main themes
        3. Presents the articles in a logical order
        4. Adds relevant context and connections between articles
        5. Maintains a professional but engaging tone
        6. Includes relevant emojis where appropriate
        
        The section should be formatted in Markdown.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        return LLMChain(llm=llm, prompt=prompt)
    
    except Exception as e:
        logger.error(f"Error creating newsletter chain: {str(e)}")
        raise

def create_refinement_chain():
    """Create a chain for content refinement."""
    try:
        llm = create_llm(temperature=0.4)  # Moderate temperature for refinement
        
        template = """You are an AI assistant tasked with refining and improving newsletter content.
        Please review and enhance the following newsletter section while maintaining its core message.
        
        Current Content:
        {content}
        
        Please:
        1. Improve clarity and flow
        2. Enhance technical accuracy
        3. Ensure consistent tone
        4. Add or improve transitions between topics
        5. Fix any grammatical or stylistic issues
        
        Return the refined content in Markdown format.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        return LLMChain(llm=llm, prompt=prompt)
    
    except Exception as e:
        logger.error(f"Error creating refinement chain: {str(e)}")
        raise

def get_token_usage(func):
    """Decorator to track token usage of LangChain operations."""
    def wrapper(*args, **kwargs):
        with get_openai_callback() as cb:
            result = func(*args, **kwargs)
            logger.info(f"Token usage - Total: {cb.total_tokens}, "
                       f"Prompt: {cb.prompt_tokens}, "
                       f"Completion: {cb.completion_tokens}, "
                       f"Cost: ${cb.total_cost:.4f}")
        return result
    return wrapper 

class GeminiCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.token_count = 0
        
    def on_llm_start(self, *args, **kwargs):
        self.token_count = 0
        
    def on_llm_end(self, *args, **kwargs):
        # Gemini doesn't provide direct token counts, 
        # you might need to implement your own counting logic
        pass