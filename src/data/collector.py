"""SEC filing data collector."""

from typing import List, Optional, Dict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import json

from ..config import settings
from ..models.document import SECDocument


class SECDataCollector:
    """Collects SEC filing data from SEC EDGAR."""
    
    def __init__(self):
        """Initialize the collector."""
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'Sample-SEC-Research-Tool/1.0 (anubhav.anandd@gmail.com)'  # Updated with email
        }
        # Respect SEC's rate limit
        self.rate_limit = 0.1  # seconds between requests
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed SEC's rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)
        self.last_request_time = time.time()

    def fetch_filings(
        self,
        ticker: str,
        filing_types: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SECDocument]:
        """
        Fetch SEC filings for a given ticker and filing types.
        
        Args:
            ticker: Company ticker symbol
            filing_types: List of filing types (e.g., ["10-K", "10-Q"])
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of SECDocument objects
        """
        try:
            # First get the CIK number for the company
            self._respect_rate_limit()
            ticker_search_url = f"https://www.sec.gov/files/company_tickers.json"
            response = requests.get(ticker_search_url, headers=self.headers)
            response.raise_for_status()
            
            companies = response.json()
            cik = None
            company_name = None
            
            # Find the matching company
            for entry in companies.values():
                if entry['ticker'].upper() == ticker.upper():
                    cik = str(entry['cik_str']).zfill(10)
                    company_name = entry['title']
                    break
            
            if not cik:
                raise ValueError(f"Could not find CIK for ticker {ticker}")
            
            # Get the company's submissions feed
            self._respect_rate_limit()
            submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(submissions_url, headers=self.headers)
            response.raise_for_status()
            
            filings_data = response.json()
            recent_filings = filings_data.get('filings', {}).get('recent', {})
            
            if not recent_filings:
                return []
            
            documents = []
            for idx, form in enumerate(recent_filings.get('form', [])):
                if form in filing_types:
                    filing_date = datetime.strptime(
                        recent_filings['filingDate'][idx],
                        '%Y-%m-%d'
                    )
                    
                    # Apply date filters if provided
                    if start_date and filing_date < start_date:
                        continue
                    if end_date and filing_date > end_date:
                        continue
                    
                    accession_number = recent_filings['accessionNumber'][idx]
                    primary_doc = recent_filings.get('primaryDocument', [''])[idx]
                    
                    # Get the filing document URL
                    self._respect_rate_limit()
                    filing_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/"
                        f"{accession_number.replace('-', '')}/{primary_doc}"
                    )
                    
                    doc = SECDocument(
                        filing_id=accession_number.replace('-', ''),
                        company_name=company_name,
                        ticker=ticker,
                        filing_type=form,
                        filing_date=filing_date,
                        document_text=self._fetch_filing_text(filing_url),
                        metadata={
                            'cik': cik,
                            'accession_number': accession_number,
                            'file_number': recent_filings.get('fileNumber', [''])[idx],
                        },
                        sections={}
                    )
                    documents.append(doc)
                    
                    # Limit to 5 most recent filings
                    if len(documents) >= 5:
                        break
            
            return documents
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error fetching SEC data: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing SEC response: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")
    
    def _fetch_filing_text(self, url: str) -> str:
        """
        Fetch the full text content of a filing.
        
        Args:
            url: The URL of the filing document
            
        Returns:
            The text content of the filing
        """
        try:
            self._respect_rate_limit()
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the document
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main document content
            text_content = ""
            
            # Look for common document containers
            for tag in ['TEXT', 'DOCUMENT', 'filing-content']:
                content = soup.find(tag)
                if content:
                    text_content = content.get_text(separator='\n', strip=True)
                    break
            
            # If no specific container found, use the whole text
            if not text_content:
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Basic cleaning
            text_content = text_content.replace('\n', ' ').replace('\r', ' ')
            text_content = ' '.join(text_content.split())  # Normalize whitespace
            
            return text_content or "No content available"
            
        except Exception as e:
            print(f"Warning: Error fetching filing text: {str(e)}")
            return "No content available"
