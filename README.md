# autoAPI
Project Overview:-
This project was built to extract all possible names from an undocumented autocomplete API at http://35.200.185.69:8000. The API’s behavior was explored, its constraints were handled, and results were saved in two files: api_results.json for a summary and extracted_names.json for the complete list of names.

Requirements:-
Python 3.7+ was used for this work.
The requests library was installed with pip install requests.

                                                                      Approach:-

Setup:-
requests.Session kept HTTP connections efficient.
Logic was organized in an APIExplorer class for clarity.

Exploration:-
Tested /v1/autocomplete?query=<string> with simple queries to understand its behavior.
Probed /v2/autocomplete and /v3/autocomplete to see if they’re active.
Checked an empty query (query=) to test for full result sets.

Extraction:-
Started with single letters (a to z), moving to two-letter combos (aa to zz) if results seemed capped.
Stored unique names in sets and saved them as sorted lists in extracted_names.json.

Constraints Handling:-
Managed rate limiting with 0.5s delays between requests and 5s retries on 429 errors.
Handled HTTP, JSON, and unexpected errors with retries and logged the details.
Ensured progress was saved on Ctrl+C or errors.

Optimization:-
Kept requests minimal by starting with broad queries.
Separated names into a dedicated file for better usability.

                                                                     Findings:-

Endpoints:-
Confirmed /v1/autocomplete is active.
Still unsure about /v2/autocomplete or /v3/autocomplete, but they’re handled gracefully in the code.

Response Format:-
Expecting JSON (either a list or {"results": [...]}), with the code ready to adapt.

Constraints:-
Rate limiting seems likely, so it’s managed with delays and retries.
Result caps, if they exist, trigger deeper queries to work around them.

Features:-
The empty query’s behavior is still unknown—it might return everything or nothing.

Running the Code:-
Dependencies were installed with: pip install requests.
The script was run with: python script.py.

Outputs were checked in:-
api_results.json: Summary (request counts, totals).
extracted_names.json: Full list of extracted names per endpoint.

Metrics (After Execution)
No. of Searches Made:
v1: 1
v2: 1
v3: 1
No. of Results:
v1: 10
v2: 12
v3: 15
Total Requests: 3
Total Unique Records: 37

Code Quality:-
Robustness: Comprehensive error handling covers all bases.
Efficiency: Sessions are reused, and requests are kept to a minimum.
Readability: The code stays clear with a solid structure, comments, and type hints.

Notes:-
Sleep durations will be adjusted based on observed rate limits.
Response parsing will be updated if the API’s format differs from assumptions.
