"""SEC document processor for text processing and chunking."""

from typing import List, Dict
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import json

from ..models.document import SECDocument


class SECDocumentProcessor:
    """Processes SEC documents for analysis."""
    
    def __init__(self):
        """Initialize the processor with text splitter."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # Increased for better context
            chunk_overlap=300,
            separators=["\n\n", "\n", ".", " "]
        )
        
        # Common section headers in SEC filings
        self.section_patterns = {
            'risk_factors': r'(Item\s*1A\.?\s*)?Risk\s*Factors',
            'mda': r'(Item\s*7\.?\s*)?Management\'?s?\s*Discussion\s*and\s*Analysis',
            'business': r'(Item\s*1\.?\s*)?Business',
            'financial_statements': r'(Item\s*8\.?\s*)?Financial\s*Statements',
            'market_risk': r'(Item\s*7A\.?\s*)?Quantitative\s*and\s*Qualitative\s*Disclosures\s*[Aa]bout\s*Market\s*Risk',
        }
    
    def _identify_section(self, text: str) -> str:
        """Identify the section type based on content."""
        text_lower = text.lower()
        for section_type, pattern in self.section_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return section_type
        return 'other'

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep structure
        text = re.sub(r'[^\w\s\.,;:\-\(\)\'\"$%]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def process_document(self, document: SECDocument) -> List[Dict]:
        """Process a SEC document into chunks with enhanced context."""
        chunks = []
        
        if document.document_text:
            # Split text into major sections first
            sections = self._split_into_sections(document.document_text)
            
            for section_text, section_type in sections:
                # Clean the text while preserving important information
                cleaned_text = self._clean_text(section_text)
                
                # Split into smaller chunks
                text_chunks = self.text_splitter.split_text(cleaned_text)
                
                for i, chunk in enumerate(text_chunks):
                    # Extract key metrics if present
                    metrics = self._extract_metrics(chunk)
                    
                    chunks.append({
                        "text": chunk,
                        "metadata": {
                            "filing_id": document.filing_id,
                            "company_name": document.company_name,
                            "ticker": document.ticker,
                            "filing_type": document.filing_type,
                            "filing_date": str(document.filing_date),
                            "section": section_type,
                            "chunk_index": i,
                            "total_chunks": len(text_chunks),
                            # Store metrics as strings
                            "currency_amounts": ','.join(map(str, metrics.get('currency_amounts', []))),
                            "percentages": ','.join(map(str, metrics.get('percentages', []))),
                            "has_metrics": "true" if any(metrics.values()) else "false"
                        }
                    })
        
        return chunks
    
    def _split_into_sections(self, text: str) -> List[tuple]:
        """Split document into major sections."""
        sections = []
        current_text = ""
        current_type = "other"
        
        for line in text.split('\n'):
            section_type = self._identify_section(line)
            if section_type != 'other':
                if current_text:
                    sections.append((current_text, current_type))
                current_text = line
                current_type = section_type
            else:
                current_text += '\n' + line
        
        if current_text:
            sections.append((current_text, current_type))
        
        return sections
    
    def _extract_metrics(self, text: str) -> Dict:
        """Extract key financial metrics from text."""
        metrics = {
            'currency_amounts': [],
            'percentages': []
        }
        
        # Look for currency amounts
        currency_matches = re.finditer(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(million|billion|trillion)?', text)
        for match in currency_matches:
            amount = float(match.group(1).replace(',', ''))
            if match.group(2):
                multiplier = {'million': 1e6, 'billion': 1e9, 'trillion': 1e12}
                amount *= multiplier[match.group(2)]
            metrics['currency_amounts'].append(amount)
        
        # Look for percentages
        percentage_matches = re.finditer(r'(\d+(?:\.\d+)?)\s*%', text)
        metrics['percentages'] = [float(m.group(1)) for m in percentage_matches]
        
        return metrics
