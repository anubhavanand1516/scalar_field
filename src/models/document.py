"""Document models for SEC filings."""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel


class SECDocument(BaseModel):
    """Represents a SEC filing document."""
    
    filing_id: str
    company_name: str
    ticker: str
    filing_type: str
    filing_date: datetime
    document_text: str
    metadata: Dict[str, Any]
    sections: Dict[str, str]  # Section name -> content mapping
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
