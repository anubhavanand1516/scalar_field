"""Test script to verify SEC QA system functionality."""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from collections import defaultdict

from src.data.collector import SECDataCollector
from src.data.processor import SECDocumentProcessor
from src.storage.vector_store import VectorStore
from src.qa.query_processor import QueryProcessor


class SECAnalyzer:
    """SEC filing analyzer with enhanced analytical capabilities."""
    
    def __init__(self):
        """Initialize the analyzer components."""
        print("1. Initializing components...")
        self.collector = SECDataCollector()
        self.processor = SECDocumentProcessor()
        self.vector_store = VectorStore()
        self.tech_companies = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
        self.financial_companies = ["JPM", "BAC", "GS", "MS", "WFC"]
        print("✓ Components initialized successfully")

    def fetch_and_process_data(self, days_back: int = 365) -> None:
        """Fetch and process SEC filings for all companies."""
        all_companies = self.tech_companies + self.financial_companies
        filing_types = ["10-K", "10-Q", "8-K"]
        
        print("\n2. Fetching and processing company filings...")
        self._fetch_and_process_company_data(
            tickers=all_companies,
            filing_types=filing_types,
            days_back=days_back
        )

    def _fetch_and_process_company_data(
        self,
        tickers: List[str],
        filing_types: List[str],
        days_back: int
    ) -> None:
        """Internal method to fetch and process company data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for ticker in tickers:
            print(f"\nProcessing {ticker}...")
            try:
                filings = self.collector.fetch_filings(
                    ticker=ticker,
                    filing_types=filing_types,
                    start_date=start_date,
                    end_date=end_date
                )
                print(f"✓ Fetched {len(filings)} filings for {ticker}")
                
                for filing in filings:
                    print(f"Processing {filing.filing_type} from {filing.filing_date}")
                    chunks = self.processor.process_document(filing)
                    if chunks:
                        self.vector_store.add_documents(chunks)
                        print(f"✓ Added {len(chunks)} chunks to vector store")
                    else:
                        print(f"! No valid chunks extracted from {ticker} {filing.filing_type}")
                        
            except Exception as e:
                print(f"! Error processing {ticker}: {str(e)}")

    def analyze_topic(
        self,
        topic: str,
        companies: Optional[List[str]] = None,
        filing_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict:
        """Analyze a topic with enhanced analysis."""
        where = {}
        if companies:
            where["ticker"] = {"$in": companies}
        if filing_types:
            where["filing_type"] = {"$in": filing_types}
            
        results = self.vector_store.search(
            query=topic,
            filter_metadata=where,
            limit=limit
        )
        
        return self._organize_results(results)

    def _organize_results(self, results: Dict) -> Dict:
        """Organize search results by company and extract key information."""
        organized = defaultdict(list)
        
        if not results['documents'] or not results['documents'][0]:
            return {}
            
        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            company = metadata['ticker']
            filing_type = metadata['filing_type']
            filing_date = metadata['filing_date']
            section = metadata.get('section', 'main')
            
            # Extract metrics if available
            metrics_summary = ""
            if metadata.get('has_metrics') == 'true':
                currency_amounts = [float(x) for x in metadata.get('currency_amounts', '').split(',') if x]
                percentages = [float(x) for x in metadata.get('percentages', '').split(',') if x]
                if currency_amounts or percentages:
                    metrics_summary = f"\nMetrics found: {len(currency_amounts)} currency amounts, {len(percentages)} percentages"
            
            organized[company].append({
                'content': doc,
                'filing_type': filing_type,
                'filing_date': filing_date,
                'section': section,
                'metrics_summary': metrics_summary
            })
        
        return dict(organized)

    def run_interactive_analysis(self) -> None:
        """Run interactive analysis session."""
        while True:
            print("\nAvailable company groups:")
            print("1. Tech companies (AAPL, MSFT, GOOGL, META, AMZN)")
            print("2. Financial companies (JPM, BAC, GS, MS, WFC)")
            print("3. All companies")
            
            group_choice = input("\nSelect company group (1/2/3): ").strip()
            
            if group_choice == "1":
                companies = self.tech_companies
            elif group_choice == "2":
                companies = self.financial_companies
            else:
                companies = self.tech_companies + self.financial_companies
            
            print("\nAvailable filing types:")
            print("1. 10-K (Annual reports)")
            print("2. 10-Q (Quarterly reports)")
            print("3. 8-K (Current reports)")
            print("4. All filing types")
            
            filing_choice = input("\nSelect filing type (1/2/3/4): ").strip()
            
            if filing_choice == "1":
                filing_types = ["10-K"]
            elif filing_choice == "2":
                filing_types = ["10-Q"]
            elif filing_choice == "3":
                filing_types = ["8-K"]
            else:
                filing_types = ["10-K", "10-Q", "8-K"]
            
            question = input("\nEnter your question: ").strip()
            
            print(f"\nAnalyzing: {question}")
            print(f"Context: Analysis for {', '.join(companies)}")
            
            results = self.analyze_topic(
                topic=question,
                companies=companies,
                filing_types=filing_types
            )
            
            if results:
                print("\nKey findings by company:")
                for company, insights in results.items():
                    print(f"\n{company}:")
                    for i, insight in enumerate(insights, 1):
                        print(f"\nInsight {i} ({insight['filing_type']} - {insight['filing_date']}):")
                        print(f"Section: {insight['section']}")
                        print(f"- {insight['content'][:500]}...")
                        if insight['metrics_summary']:
                            print(insight['metrics_summary'])
            else:
                print("\n! No relevant information found")
            
            print("-" * 80)
            
            if input("\nWould you like to ask another question? (y/n): ").lower().strip() != 'y':
                break


def main():
    """Run SEC filing analysis with enhanced capabilities."""
    try:
        analyzer = SECAnalyzer()
        analyzer.fetch_and_process_data()
        analyzer.run_interactive_analysis()
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return
    
    print("\n✓ Analysis completed successfully!")


if __name__ == "__main__":
    main()