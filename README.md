# SEC Filing Analysis System

A powerful system for analyzing SEC filings using natural language queries. This system fetches, processes, and analyzes SEC filings from multiple companies, allowing users to extract insights through semantic search.

## System Overview

### Architecture
```
sec_qa/
├── src/
│   ├── data/
│   │   ├── collector.py      # SEC filing data collection
│   │   └── processor.py      # Document processing and chunking
│   ├── models/
│   │   └── document.py       # Data models
│   ├── qa/
│   │   └── query_processor.py # Query understanding
│   ├── storage/
│   │   └── vector_store.py   # Vector storage and search
│   └── config.py             # System configuration
├── test_system.py            # Main interactive system
└── requirements.txt          # Dependencies
```

### Key Components

1. **Data Collection (collector.py)**
   - Fetches SEC filings from EDGAR database
   - Supports 10-K, 10-Q, and 8-K filings
   - Handles rate limiting and error recovery
   - Processes multiple companies in parallel

2. **Document Processing (processor.py)**
   - Chunks documents into manageable pieces
   - Identifies document sections (MD&A, Risk Factors, etc.)
   - Extracts financial metrics
   - Cleans and normalizes text

3. **Vector Storage (vector_store.py)**
   - Uses ChromaDB for vector storage
   - Implements semantic search
   - Handles metadata filtering
   - Deduplicates results

4. **Query Processing (query_processor.py)**
   - Analyzes natural language queries
   - Extracts company names and filing types
   - Identifies relevant search parameters

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sec_qa
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the System

```bash
python test_system.py
```

### Interactive Analysis

The system provides an interactive interface with:
1. Company selection (Tech/Financial/All)
2. Filing type selection (10-K/10-Q/8-K/All)
3. Natural language query input
4. Organized results by company

### Example Queries

1. Revenue Analysis:
```
"What are the primary revenue drivers for major technology companies?"
```

2. Risk Assessment:
```
"What are the most commonly cited risk factors across industries?"
```

3. Strategic Initiatives:
```
"How are companies positioning regarding AI and automation?"
```

4. Financial Performance:
```
"Compare R&D spending trends across companies"
```

5. Environmental Impact:
```
"How do companies describe climate-related risks?"
```

## Data Processing Flow

1. **Data Collection**
   ```python
   collector = SECDataCollector()
   filings = collector.fetch_filings(
       ticker="AAPL",
       filing_types=["10-K"],
       start_date=start_date,
       end_date=end_date
   )
   ```

2. **Document Processing**
   ```python
   processor = SECDocumentProcessor()
   chunks = processor.process_document(filing)
   ```

3. **Vector Storage**
   ```python
   vector_store = VectorStore()
   vector_store.add_documents(chunks)
   ```

4. **Query Analysis**
   ```python
   results = vector_store.search(
       query="What are the primary revenue drivers?",
       filter_metadata={"ticker": "AAPL"}
   )
   ```

## Features

1. **Intelligent Search**
   - Semantic understanding of queries
   - Section-aware search
   - Metric extraction and analysis
   - Result deduplication

2. **Comprehensive Coverage**
   - Multiple filing types (10-K, 10-Q, 8-K)
   - Tech and Financial sectors
   - Historical data analysis

3. **Rich Analysis**
   - Financial metric extraction
   - Section identification
   - Cross-company comparison
   - Trend analysis

4. **User Experience**
   - Interactive query interface
   - Organized results by company
   - Metric summaries
   - Section context

## Configuration

Key settings in `config.py`:
```python
CACHE_DIR: str = "data/cache"
VECTOR_STORE_PATH: str = "data/vector_store"
```

## Data Structure

1. **Document Model**
```python
SECDocument(
    filing_id: str
    company_name: str
    ticker: str
    filing_type: str
    filing_date: datetime
    document_text: str
    metadata: Dict
    sections: Dict[str, str]
)
```

2. **Search Results**
```python
{
    "documents": List[str],
    "metadatas": List[Dict],
    "section": str,
    "metrics_summary": str
}
```

## Best Practices

1. **Query Formation**
   - Be specific in questions
   - Include relevant context
   - Focus on single aspects

2. **Analysis Strategy**
   - Start with broad queries
   - Narrow down based on results
   - Compare across companies
   - Look for trends over time

3. **Result Interpretation**
   - Check filing dates
   - Consider section context
   - Review metrics when available
   - Compare across companies

## Limitations

1. Data availability depends on SEC EDGAR system
2. Historical data limited to available filings
3. Processing time increases with data volume
4. Rate limits on SEC API access

## Future Enhancements

1. Additional filing types support
2. More sophisticated metric extraction
3. Advanced trend analysis
4. Custom section identification
5. Enhanced visualization capabilities

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Submit pull request

## License

[Your License Here]

## Contact

[Your Contact Information]
