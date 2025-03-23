import requests
import time
from typing import Set, Dict, List, Optional
import json
from string import ascii_lowercase

# Constants
BASE_URL = "http://35.200.185.69:8000"
ENDPOINTS = ["/v1/autocomplete", "/v2/autocomplete", "/v3/autocomplete"]
CHARACTERS = ascii_lowercase  # a-z
REQUEST_COUNT = {"v1": 0, "v2": 0, "v3": 0}
RESULTS = {"v1": set(), "v2": set(), "v3": set()}
OUTPUT_FILE = "api_results.json"
NAMES_FILE = "extracted_names.json"

class APIExplorer:
    """Class to explore and extract names from the autocomplete API."""
    
    def __init__(self):
        self.session = requests.Session()  # Reuse TCP connection for efficiency

    def make_request(self, endpoint: str, query: str) -> Optional[List[str]]:
        """Make a request to the API and return results."""
        global REQUEST_COUNT
        url = f"{BASE_URL}{endpoint}?query={query}"
        version = endpoint.split("/")[1]
        
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=5)
                REQUEST_COUNT[version] += 1
                response.raise_for_status()
                
                data = response.json()
                # Handle different possible response formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "results" in data:
                    return data["results"]
                else:
                    print(f"Warning: Unexpected response format for {endpoint}: {data}")
                    return []
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    print(f"Rate limit hit for {endpoint}. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                elif e.response.status_code == 404:
                    print(f"Endpoint {endpoint} not found.")
                    return None  # Indicates endpoint doesn't exist
                else:
                    print(f"HTTP Error for {endpoint}: {e}")
                    return []
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Request or JSON parsing failed for {endpoint}: {e}")
                return []
            except Exception as e:
                print(f"Unexpected error for {endpoint}: {e}")
                return []
        print(f"Failed to fetch data from {endpoint} after retries.")
        return []

    def explore_endpoint(self, endpoint: str) -> Optional[Set[str]]:
        """Explore an endpoint and extract all unique names."""
        names = set()
        print(f"Exploring {endpoint}...")

        # Test empty query first to see if it returns all results
        results = self.make_request(endpoint, "")
        if results is None:
            return None
        if results:
            names.update(results)
            print(f"Empty query returned {len(results)} results for {endpoint}")
            return names  # If empty query works, no need for further exploration

        # Single-letter queries
        for char in CHARACTERS:
            results = self.make_request(endpoint, char)
            if results is None:
                return None
            names.update(results)
            time.sleep(0.5)  # Respectful delay

        # Check if results are capped (e.g., same number for multiple queries)
        sample_sizes = [len(self.make_request(endpoint, char) or []) for char in CHARACTERS[:3]]
        if names and len(set(sample_sizes)) == 1 and sample_sizes[0] > 0:
            print(f"{endpoint} may have a result limit ({sample_sizes[0]}). Trying two-letter queries...")
            for char1 in CHARACTERS:
                for char2 in CHARACTERS:
                    results = self.make_request(endpoint, char1 + char2)
                    if results is None:
                        return None
                    names.update(results)
                    time.sleep(0.5)

        return names

    def save_results(self):
        """Save results and request counts to a file."""
        with open(OUTPUT_FILE, "w") as f:
            json.dump({
                "requests": REQUEST_COUNT,
                "results_count": {k: len(v) for k, v in RESULTS.items()},
                "total_requests": sum(REQUEST_COUNT.values()),
                "total_unique_records": len(set.union(*RESULTS.values()))
            }, f, indent=2)
        # Save extracted names separately
        with open(NAMES_FILE, "w") as f:
            json.dump({k: sorted(list(v)) for k, v in RESULTS.items()}, f, indent=2)

    def run(self):
        """Run exploration for all endpoints."""
        for endpoint in ENDPOINTS:
            version = endpoint.split("/")[1]
            result = self.explore_endpoint(endpoint)
            if result is not None:
                RESULTS[version] = result
                print(f"Found {len(result)} names in {endpoint}")
            else:
                print(f"Skipping {endpoint} as it doesn't exist or failed.")
        
        self.save_results()
        
        # Print summary
        print("\nSummary:")
        for version in REQUEST_COUNT:
            print(f"No. of searches made for {version}: {REQUEST_COUNT[version]}")
            print(f"No. of results in {version}: {len(RESULTS[version])}")
        print(f"Total requests: {sum(REQUEST_COUNT.values())}")
        print(f"Total unique records: {len(set.union(*RESULTS.values()))}")

def main():
    """Main entry point."""
    explorer = APIExplorer()
    try:
        explorer.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving current progress...")
        explorer.save_results()
    except Exception as e:
        print(f"Fatal error: {e}")
        explorer.save_results()

if __name__ == "__main__":
    main()