# SEC Filings QA System

A question-answering system that analyzes SEC filings to answer complex financial research questions.

## Features

- Process financial documents at scale
- Synthesize information across multiple documents and time periods
- Provide source attribution for all answers
- Handle complexity and nuance of financial information

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your SEC API key:
```
SEC_API_KEY=your_api_key_here
```

## Project Structure

```
sec_qa/
├── data/
│   └── cache/  # For storing downloaded filings
├── src/
│   ├── config.py
│   ├── data/
│   │   ├── collector.py
│   │   └── processor.py
│   ├── models/
│   │   └── document.py
│   ├── storage/
│   │   └── vector_store.py
│   └── qa/
│       └── query_processor.py
└── tests/
```

## Usage

Example usage of the QA system:

```python
from src.data.collector import SECDataCollector
from src.data.processor import SECDocumentProcessor
from src.storage.vector_store import VectorStore
from src.qa.query_processor import QueryProcessor

# Initialize components
collector = SECDataCollector()
processor = SECDocumentProcessor()
vector_store = VectorStore()
query_processor = QueryProcessor()

# Fetch and process documents
filings = collector.fetch_filings(
    ticker="AAPL",
    filing_types=["10-K"],
    start_date=datetime(2022, 1, 1)
)
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
isort .
```

4. Run type checking:
```bash
mypy .
```

## License

MIT License
