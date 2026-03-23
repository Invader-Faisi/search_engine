import time
import hashlib
import json
from datetime import datetime, timedelta
from flask import current_app
import os
import pickle

class SearchCache:
    """Simple cache for search results"""
    
    def __init__(self, max_size=100, ttl=300):  # 5 minutes TTL by default
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.hits = 0
        self.misses = 0
        
        # Try to load cache from file
        self.cache_file = os.path.join(
            os.path.dirname(current_app.root_path) if current_app else '.',
            'data',
            'search_cache.pkl'
        )
        self.load_cache()
    
    def _get_cache_key(self, query):
        """Generate a cache key from search query"""
        # Normalize query: lowercase, strip, sort words?
        normalized = ' '.join(sorted(query.lower().strip().split()))
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query):
        """Get cached results for query"""
        key = self._get_cache_key(query)
        
        if key in self.cache:
            entry = self.cache[key]
            # Check if entry is expired
            if time.time() - entry['timestamp'] < self.ttl:
                self.hits += 1
                return entry['results']
            else:
                # Remove expired entry
                del self.cache[key]
                self.misses += 1
                return None
        else:
            self.misses += 1
            return None
    
    def set(self, query, results):
        """Cache search results"""
        key = self._get_cache_key(query)
        
        # If cache is full, remove oldest entries
        if len(self.cache) >= self.max_size:
            # Remove 10% of oldest entries
            to_remove = max(1, len(self.cache) // 10)
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1]['timestamp'])
            for old_key, _ in sorted_entries[:to_remove]:
                del self.cache[old_key]
        
        self.cache[key] = {
            'results': results,
            'timestamp': time.time(),
            'query': query
        }
        
        # Save cache to disk periodically (every 10 writes)
        if len(self.cache) % 10 == 0:
            self.save_cache()
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.save_cache()
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        # Count expired entries
        expired = 0
        current_time = time.time()
        for entry in self.cache.values():
            if current_time - entry['timestamp'] >= self.ttl:
                expired += 1
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'expired_entries': expired,
            'ttl_seconds': self.ttl
        }
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    'cache': self.cache,
                    'hits': self.hits,
                    'misses': self.misses
                }, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.cache = data.get('cache', {})
                    self.hits = data.get('hits', 0)
                    self.misses = data.get('misses', 0)
                    
                    # Clean expired entries on load
                    current_time = time.time()
                    expired_keys = []
                    for key, entry in self.cache.items():
                        if current_time - entry['timestamp'] >= self.ttl:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.cache[key]
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}
            self.hits = 0
            self.misses = 0

# Global cache instance
search_cache = None

def get_cache():
    """Get or create cache instance"""
    global search_cache
    if search_cache is None:
        search_cache = SearchCache(max_size=100, ttl=300)  # 5 minutes TTL
    return search_cache

def cached_search(search_function, query):
    """Decorator-like function for caching search results"""
    cache = get_cache()
    
    # Try to get from cache
    cached_results = cache.get(query)
    if cached_results is not None:
        return cached_results
    
    # Perform actual search
    results = search_function(query)
    
    # Cache the results
    if results:  # Only cache if we have results
        cache.set(query, results)
    
    return results

def clear_search_cache():
    """Clear search cache"""
    cache = get_cache()
    cache.clear()

def get_cache_stats():
    """Get cache statistics"""
    cache = get_cache()
    return cache.get_stats()