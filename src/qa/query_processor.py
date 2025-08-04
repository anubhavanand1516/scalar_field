"""Query processor for natural language queries."""

from typing import Dict, List, Optional
import re
from datetime import datetime
from dateutil.parser import parse


class QueryProcessor:
    """Processes natural language queries into structured parameters."""
    
    def __init__(self):
        """Initialize the query processor with regex patterns."""
        # Updated pattern to match common company names and their tickers
        self.company_patterns = {
            'Apple': 'AAPL',
            'Microsoft': 'MSFT',
            'Google': 'GOOGL',
            'Amazon': 'AMZN',
            # Add more as needed
        }
        self.ticker_pattern = re.compile(r'\$?[A-Z]{1,5}(?=\s|$)')
        
    def process_query(self, query: str) -> Dict:
        """
        Process a natural language query to extract structured information.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict containing extracted parameters (tickers, dates, filing_types)
        """
        return {
            "tickers": self._extract_tickers(query),
            "dates": self._extract_dates(query),
            "filing_types": self._extract_filing_types(query)
        }
        
    def _extract_tickers(self, query: str) -> List[str]:
        """
        Extract ticker symbols from query.
        
        Args:
            query: Query string
            
        Returns:
            List of extracted ticker symbols
        """
        # First check for company names
        for company, ticker in self.company_patterns.items():
            if company in query:
                return [ticker]
        
        # Then check for explicit tickers
        matches = [match.group().replace('$', '') for match in self.ticker_pattern.finditer(query)]
        return matches if matches else []
        
    def _extract_dates(self, query: str) -> Dict[str, Optional[datetime]]:
        """
        Extract date references from query.
        
        Args:
            query: Query string
            
        Returns:
            Dictionary with start and end dates if found
        """
        # TODO: Implement date extraction
        return {
            "start_date": None,
            "end_date": None
        }
        
    def _extract_filing_types(self, query: str) -> List[str]:
        """
        Extract filing types from query.
        
        Args:
            query: Query string
            
        Returns:
            List of filing types mentioned in the query
        """
        filing_types = []
        if "10-K" in query:
            filing_types.append("10-K")
        if "10-Q" in query:
            filing_types.append("10-Q")
        if "8-K" in query:
            filing_types.append("8-K")
        if "DEF 14A" in query:
            filing_types.append("DEF 14A")
        return filing_types
