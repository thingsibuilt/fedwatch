"""
FedWatch - Indeed Job Postings Scraper
Real-time employment indicator from job market data
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict, List, Optional
import time


class IndeedScraper:
    """Scrape Indeed for job posting trends as employment leading indicator"""
    
    BASE_URL = "https://www.indeed.com"
    SEARCH_URL = "https://www.indeed.com/jobs"
    
    # Job categories to track (representative of economy)
    JOB_CATEGORIES = {
        "tech": ["software engineer", "data scientist", "developer", "IT"],
        "retail": ["retail", "store associate", "cashier", "sales associate"],
        "manufacturing": ["manufacturing", "factory", "warehouse", "production"],
        "healthcare": ["nurse", "medical", "healthcare", "hospital"],
        "finance": ["finance", "accountant", "analyst", "banking"],
        "general": ["full time", "part time", "employment"]
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_job_count(self, keywords: str, location: str = "us") -> Optional[Dict]:
        """Get count of job postings for given keywords"""
        params = {
            'q': keywords,
            'l': location,
            'fromage': '3',  # Jobs from last 3 days
        }
        
        try:
            response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the result count
            count_elem = soup.find('div', {'id': 'searchCount'})
            if count_elem:
                count_text = count_elem.get_text(strip=True)
                # Format: "Page 1 of 123 jobs"
                import re
                match = re.search(r'of\s+([\d,]+)\s+jobs', count_text)
                if match:
                    count = int(match.group(1).replace(',', ''))
                    return {
                        'keywords': keywords,
                        'count': count,
                        'location': location,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Alternative: look for total count
            count_elem = soup.find('span', {'class': 'mat-text'})
            if count_elem:
                count_text = count_elem.get_text(strip=True)
                
        except Exception as e:
            print(f"Error fetching {keywords}: {e}")
        
        return None
    
    def get_trend(self, category: str, location: str = "us") -> Optional[Dict]:
        """Get trend for a job category"""
        keywords = " OR ".join(self.JOB_CATEGORIES.get(category, [category]))
        return self.get_job_count(keywords, location)
    
    def get_all_trends(self, location: str = "us") -> Dict[str, Dict]:
        """Get trends for all categories"""
        results = {}
        for category in self.JOB_CATEGORIES:
            print(f"Fetching {category}...")
            result = self.get_trend(category, location)
            if result:
                results[category] = result
            time.sleep(1)  # Rate limiting
        return results
    
    def calculate_health_score(self, trends: Dict) -> float:
        """Calculate job market health score (0-100)"""
        if not trends:
            return 50.0
        
        # Weight categories by economic significance
        weights = {
            'tech': 0.25,
            'manufacturing': 0.20,
            'retail': 0.20,
            'healthcare': 0.20,
            'finance': 0.10,
            'general': 0.05
        }
        
        # Normalize and score
        max_count = max(t.get('count', 0) for t in trends.values())
        if max_count == 0:
            return 50.0
        
        score = 0
        for category, weight in weights.items():
            if category in trends:
                count = trends[category].get('count', 0)
                normalized = (count / max_count) * 100
                score += normalized * weight
        
        return round(score, 1)


def main():
    """Demo: Fetch current job market data"""
    scraper = IndeedScraper()
    
    print("🏭 FedWatch - Indeed Job Trends")
    print("=" * 50)
    
    # Fetch trends for key categories
    trends = scraper.get_all_trends()
    
    print("\n📊 Job Posting Counts (Last 3 Days):")
    print("-" * 40)
    for category, data in trends.items():
        print(f"  {category:15} : {data['count']:>6,} jobs")
    
    # Calculate health score
    health = scraper.calculate_health_score(trends)
    print(f"\n💚 Job Market Health Score: {health}/100")
    
    # Save to JSON
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "trends": trends,
        "health_score": health
    }
    
    with open('/root/.openclaw/workspace/indeed_trends.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Data saved to indeed_trends.json")


if __name__ == "__main__":
    main()
