import time
from django.db import connection
from django.conf import settings


class SQLiteOptimizedConnectionMiddleware:
    """
    Middleware to optimize SQLite database connection handling.
    
    This middleware ensures that:
    1. Database connections are properly managed
    2. Expensive operations are properly logged
    3. Connection statistics are available for debugging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization
        self.is_sqlite = settings.DATABASES['default']['ENGINE'].endswith('sqlite3')
        
    def __call__(self, request):
        start_time = time.time()
        
        # Initialize query count if using SQLite
        if self.is_sqlite:
            initial_queries = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Post-processing after view is called
        if self.is_sqlite and settings.DEBUG:
            # Calculate query stats
            query_time = 0.0
            query_count = len(connection.queries) - initial_queries
            
            for query in connection.queries[initial_queries:]:
                query_time += float(query.get('time', 0))
            
            # Add query info to response headers for debugging
            response['X-Query-Count'] = str(query_count)
            response['X-Query-Time'] = str(round(query_time, 4))
            response['X-Request-Time'] = str(round(time.time() - start_time, 4))
                
        return response