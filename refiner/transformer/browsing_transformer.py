from typing import Dict, Any, List
from datetime import datetime
import statistics
from refiner.models.refined import Base, BrowsingAuthor, BrowsingEntry, BrowsingStats
from refiner.transformer.base_transformer import DataTransformer
from refiner.utils.date import parse_timestamp

class BrowsingTransformer(DataTransformer):
    """
    Transformer for browsing data.
    """
    
    def determine_browsing_type(self, urls: List[str]) -> str:
        """
        Determine the type of browsing based on URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            String indicating the browsing type
        """
        # Simple logic to determine browsing type
        domains = [self._extract_domain(url) for url in urls]
        
        # Check for common categories
        ecommerce_domains = ['amazon', 'ebay', 'shopify']
        social_domains = ['facebook', 'twitter', 'instagram', 'linkedin','x']
        news_domains = ['cnn', 'bbc', 'nytimes', 'reuters']
        
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Find most common domain
        if not domain_counts:
            return "Unknown"
            
        most_common_domain = max(domain_counts.items(), key=lambda x: x[1])[0]
        
        # Check if most common domain is in any category
        if any(e_domain in most_common_domain for e_domain in ecommerce_domains):
            return "Shopping"
        elif any(s_domain in most_common_domain for s_domain in social_domains):
            return "Social Media"
        elif any(n_domain in most_common_domain for n_domain in news_domains):
            return "News"
        else:
            return "General"
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            Domain string
        """
        # Simple domain extraction
        try:
            # Remove protocol
            if '://' in url:
                url = url.split('://', 1)[1]
            
            # Get domain part
            domain = url.split('/', 1)[0]
            
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # Get base domain
            parts = domain.split('.')
            if len(parts) > 1:
                return parts[-2]  # Return the base domain name
            return domain
        except Exception:
            return "unknown"
    
    def transform(self, data: Dict[str, Any]) -> List[Base]:
        """
        Transform raw browsing data into SQLAlchemy model instances.
        
        Args:
            data: Dictionary containing browsing data
            
        Returns:
            List of SQLAlchemy model instances
        """
        # Extract data
        browsing_data = data.get('data', {}).get('browsingDataArray', [])
        created_time = parse_timestamp(data.get('created_time', 0))
        author_id = data.get('author', '')
        
        # Create browsing author
        author = BrowsingAuthor(
            author_id=author_id,
            created_time=created_time
        )
        
        models = [author]
        
        # URLs and timestamps for stats calculation
        urls = []
        time_spent_values = []
        
        # Process browsing entries
        for entry in browsing_data:
            url = entry.get('url', '')
            time_spent = entry.get('timeSpent', 0)
            timestamp = parse_timestamp(entry.get('timestamp', 0))
            
            # Create browsing entry
            browsing_entry = BrowsingEntry(
                author_id=author_id,
                url=url,
                time_spent=time_spent,
                timestamp=timestamp
            )
            
            models.append(browsing_entry)
            urls.append(url)
            time_spent_values.append(time_spent)
        
        # Calculate stats
        url_count = len(urls)
        average_time_spent = 0
        if time_spent_values:
            average_time_spent = sum(time_spent_values) / len(time_spent_values)
        
        browsing_type = self.determine_browsing_type(urls)
        
        # Create stats
        stats = BrowsingStats(
            author_id=author_id,
            url_count=url_count,
            average_time_spent=average_time_spent,
            browsing_type=browsing_type
        )
        
        models.append(stats)
        
        return models
    
    def get_output_data(self):
        """
        Get the transformed output data in the desired format.
        
        Returns:
            Dictionary with the output data
        """
        session = self.Session()
        try:
            # Get stats
            stats = session.query(BrowsingStats).first()
            if not stats:
                return None
                
            # Get entries
            entries = session.query(BrowsingEntry).all()
            
            # Format the output
            output_data = {
                "stats": {
                    "urls": stats.url_count,
                    "averageTimeSpent": stats.average_time_spent,
                    "type": stats.browsing_type
                },
                "data": [
                    {
                        "url": entry.url,
                        "timeSpent": entry.time_spent,
                        "timestamp": int(entry.timestamp.timestamp() * 1000)  # Convert to milliseconds
                    }
                    for entry in entries
                ]
            }
            
            return output_data
        finally:
            session.close()
