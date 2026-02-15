import requests
import json
import sys

# Output encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.bfmr.com/api/deals?source=dashboard&_ts=1771192879289'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC93d3cuYmZtci5jb21cL2FwaVwvbG9naW5cL2dvb2dsZVwvY2FsbGJhY2siLCJpYXQiOjE3NzExOTIyOTYsImV4cCI6MTc3Mzc4NDI5NiwibmJmIjoxNzcxMTkyMjk2LCJqdGkiOiJkMHJqRkNZakxDaHBvamxNIiwic3ViIjoxMDU0NTUsInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjciLCJlbWFpbCI6ImJvbHRzNDVAZ21haWwuY29tIiwiYWN0aXZlIjoxLCJkZWxldGVkX2F0IjpudWxsfQ.onOj-HxKblREYx1Df-iR4qJ1J3uUOKpBOc-y9g-FVsk',
    'cookie': '_gcl_au=1.1.2058440893.1771192272; _gid=GA1.2.158182710.1771192272; XSRF-TOKEN=eyJpdiI6IlI4ZHBtb1E1d3haZ1ZJQkQ2RkRtQXc9PSIsInZhbHVlIjoiZ2pGNkx5VWRvUnJLN0x1RFRUa1MxQi80bXl3b3NmTktpNFZqMEZGcFpLYWh4b2hZa29mVHRacnZIZVBQSWRNMTNNVTJ3U3ZlNjRGSzNUSmNTWktRVmRtNS9XbWxURjJGajg4TmU2RjY3em9pT1FueER4MEFDanhUQ3lrZlBiMUYiLCJtYWMiOiI5MWE2YTNkNDZhZDgzNmNlNGQxYjFjZTgyZGRjN2Q0MGE3Yzk2ZDg4NDJjMWFmYmZkZjJhOTNkNjgzOTVkODgwIn0%3D; buyformeretail_session=eyJpdiI6IkdPL3Q4YXN1UVFCNWsrWUZJdEQranc9PSIsInZhbHVlIjoicEYrZmJWamhzT0dOdVZDck5OSDR0OGszRHFVQWxDQzJwRFdtZmZNenVETzlISEJNUFNsZ29oazNLWUlOQVpScVJYTHEzWGRwTDZiS3FUTWxnNXE0ZGdZZzFiSS9lTEYxZ2M4RWc3NWdjMVhtTTE1WDk1RGlQZFBZcUN5WUlmWXQiLCJtYWMiOiI1MjQxZWFkNTg0NzJkMDFmY2M0OGMxYjMzM2E0ZDgxZTM2NjI0MWI5NTQ2MjcyMmU4YjhkZmM4N2Q4MDQwYTVmIn0%3D; _gat_gtag_UA_113091694_1=1; _ga=GA1.1.1616390355.1771192272; _ga_R97PZ0WJBC=GS2.1.s1771192271$o1$g1$t1771192878$j60$l0$h0; _ga_1Z9C9ZQ293=GS2.1.s1771192272$o1$g1$t1771192878$j60$l0$h0',
    'priority': 'u=1, i',
    'referer': 'https://www.bfmr.com/dashboard',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-csrf-token': 'PYkzQiKg8ppyqWKaOn5Njvw16Gnt02qfIUSDYMoa',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': 'eyJpdiI6IlI4ZHBtb1E1d3haZ1ZJQkQ2RkRtQXc9PSIsInZhbHVlIjoiZ2pGNkx5VWRvUnJLN0x1RFRUa1MxQi80bXl3b3NmTktpNFZqMEZGcFpLYWh4b2hZa29mVHRacnZIZVBQSWRNMTNNVTJ3U3ZlNjRGSzNUSmNTWktRVmRtNS9XbWxURjJGajg4TmU2RjY3em9pT1FueER4MEFDanhUQ3lrZlBiMUYiLCJtYWMiOiI5MWE2YTNkNDZhZDgzNmNlNGQxYjFjZTgyZGRjN2Q0MGE3Yzk2ZDg4NDJjMWFmYmZkZjJhOTNkNjgzOTVkODgwIn0='
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # Handle nested data structure
    # Handle nested data structure
    if isinstance(data, dict):
        print(f"Top level keys: {list(data.keys())}")
        inner_data = data.get('data', {})
        if isinstance(inner_data, dict):
             print(f"Nested 'data' keys: {list(inner_data.keys())}")
             # The deals are likely in 'deals' or 'deal_list_view'
             items = inner_data.get('deals', []) 
             if not items:
                 print("No items in 'deals', checking 'deal_list_view'...")
                 # Sometimes it's in a different key
                 items = inner_data.get('deal_list_view', [])
    else:
        items = data

    print(f"Total deals found: {len(items)}")
    
    # Debug: Print keys of first deal to find store info
    if items:
        print(f"Deal 0 keys: {list(items[0].keys())}")
        print(f"Deal 0 content: {items[0]}")

    # Temporary: select all items as targets since store info is missing/empty
    targets = items

    # Select top 5
    top_deals = []
    for deal in targets[:5]:
        store_name = deal.get('store', {}).get('name')
        if not store_name:
            store_name = "unknown"
            
        monitor_entry = {
            "url": deal.get('url'),
            "target_payout": float(deal.get('payout', 0) or 0),
            "site": store_name.lower().replace(" ", ""),
            "name": deal.get('title')
        }
        top_deals.append(monitor_entry)

    # Save to monitors.json
    with open('monitors.json', 'w', encoding='utf-8') as f:
        json.dump(top_deals, f, indent=2)
        
    print(f"Saved {len(top_deals)} deals to monitors.json")
    for d in top_deals:
        print(f"- {d['name']} (${d['target_payout']})")

except Exception as e:
    print(f"Error: {e}")
