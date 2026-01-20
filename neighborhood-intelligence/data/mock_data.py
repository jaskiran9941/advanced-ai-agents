"""
Mock data for testing without API keys.
"""

# Mock commute data
MOCK_COMMUTE_DATA = {
    "origin": "123 Example St, Fremont, CA 94539",
    "destination": "1600 Amphitheatre Pkwy, Mountain View, CA",
    "distance_text": "15.2 mi",
    "distance_meters": 24462,
    "duration_text": "22 mins",
    "duration_seconds": 1320,
    "duration_in_traffic_text": "38 mins",
    "duration_in_traffic_seconds": 2280,
    "mode": "driving"
}

# Mock places data (by type)
MOCK_PLACES_DATA = {
    "gym": [
        {"name": "24 Hour Fitness", "address": "456 Fitness Ave", "rating": 4.2, "place_id": "gym1"},
        {"name": "Planet Fitness", "address": "789 Workout Blvd", "rating": 4.0, "place_id": "gym2"},
    ],
    "hindu_temple": [
        {"name": "Fremont Hindu Temple", "address": "3676 Delaware Dr", "rating": 4.8, "place_id": "temple1"},
    ],
    "park": [
        {"name": "Central Park", "address": "40000 Paseo Padre Pkwy", "rating": 4.6, "place_id": "park1"},
        {"name": "Lake Elizabeth", "address": "42000 Blacow Rd", "rating": 4.5, "place_id": "park2"},
    ],
    "grocery_or_supermarket": [
        {"name": "Patel Brothers", "address": "1000 India Way", "rating": 4.4, "place_id": "grocery1"},
        {"name": "Safeway", "address": "2000 Main St", "rating": 4.0, "place_id": "grocery2"},
    ],
    "cafe": [
        {"name": "Starbucks", "address": "100 Coffee Lane", "rating": 4.1, "place_id": "cafe1"},
        {"name": "Philz Coffee", "address": "200 Brew St", "rating": 4.6, "place_id": "cafe2"},
    ]
}

# Mock news data
MOCK_NEWS_DATA = [
    {
        "title": "New Mixed-Use Development Approved in Downtown Fremont",
        "body": "The Fremont City Council approved a 200-unit mixed-use development project that will include retail space and affordable housing units.",
        "url": "https://example.com/news/1",
        "source": "Fremont Tribune",
        "date": "2025-01-15",
        "topic": "development"
    },
    {
        "title": "Fremont Schools See Improvement in State Rankings",
        "body": "Local elementary schools have shown significant improvement in the latest state education rankings, with several schools moving up in ratings.",
        "url": "https://example.com/news/2",
        "source": "Bay Area News",
        "date": "2025-01-10",
        "topic": "schools"
    },
    {
        "title": "Crime Rates Drop 15% in Warm Springs District",
        "body": "The Fremont Police Department reports a significant decrease in property crime in the Warm Springs area over the past year.",
        "url": "https://example.com/news/3",
        "source": "Local News",
        "date": "2025-01-08",
        "topic": "crime"
    }
]

# Mock web search data
MOCK_WEB_SEARCH_DATA = [
    {
        "title": "Fremont City Planning Commission - Upcoming Projects",
        "body": "View all upcoming development projects and zoning changes in the City of Fremont.",
        "url": "https://www.fremont.gov/planning"
    },
    {
        "title": "Fremont General Plan 2030",
        "body": "The comprehensive land use and development plan for the City of Fremont through 2030.",
        "url": "https://www.fremont.gov/generalplan"
    }
]

# Mock Zillow data
MOCK_ZILLOW_DATA = {
    "address": "123 Example St, Fremont, CA 94539",
    "price": "$1,250,000",
    "beds": 4,
    "baths": 2.5,
    "sqft": 2100,
    "year_built": 1985,
    "lot_size": "6,500 sqft",
    "property_type": "Single Family",
    "zestimate": "$1,280,000",
    "days_on_market": 15,
    "price_history": [
        {"date": "2020-05", "price": "$950,000", "event": "Sold"},
        {"date": "2015-03", "price": "$720,000", "event": "Sold"}
    ],
    "source": "zillow"
}

# Mock schools data
MOCK_SCHOOLS_DATA = {
    "city": "Fremont",
    "state": "CA",
    "schools": [
        {
            "name": "Mission San Jose Elementary",
            "type": "Elementary",
            "rating": 9,
            "grades": "K-5",
            "distance": "0.5 mi",
            "trend": "stable"
        },
        {
            "name": "Hopkins Junior High",
            "type": "Middle",
            "rating": 8,
            "grades": "6-8",
            "distance": "1.2 mi",
            "trend": "improving"
        },
        {
            "name": "Mission San Jose High",
            "type": "High",
            "rating": 10,
            "grades": "9-12",
            "distance": "1.8 mi",
            "trend": "stable"
        }
    ],
    "source": "greatschools"
}

# Mock city planning data
MOCK_CITY_PLANNING_DATA = {
    "city": "Fremont",
    "state": "CA",
    "projects": [
        {
            "name": "Downtown Mixed-Use Development",
            "address": "345 Main St",
            "type": "Residential/Commercial",
            "units": 120,
            "status": "Approved",
            "start_date": "2026-Q1",
            "completion": "2028-Q2"
        },
        {
            "name": "New Community Park",
            "address": "500 Park Ave",
            "type": "Recreation",
            "status": "Planning",
            "completion": "2027"
        }
    ],
    "zoning_changes": [
        {
            "area": "Warm Springs District",
            "change": "R-1 to R-2 (higher density)",
            "status": "Under Review"
        }
    ],
    "source": "city_portal"
}

# Mock crime data
MOCK_CRIME_DATA = {
    "city": "Fremont",
    "state": "CA",
    "overall_score": 7.5,
    "trend": "improving",
    "crimes_last_30_days": 45,
    "by_type": {
        "property": 30,
        "violent": 5,
        "other": 10
    },
    "by_time": {
        "daytime": {"score": 8.5, "incidents": 15},
        "evening": {"score": 7.0, "incidents": 20},
        "night": {"score": 6.5, "incidents": 10}
    },
    "hotspots": [
        {"area": "Downtown BART Station", "concern": "Car break-ins"},
        {"area": "Shopping Center", "concern": "Theft"}
    ],
    "source": "open_data_portal"
}


def run_mock_analysis():
    """Run a test analysis with mock data to verify the flow works."""
    print("=" * 60)
    print("MOCK ANALYSIS - Testing Neighborhood Intelligence Agent")
    print("=" * 60)
    
    print("\n📍 Address: 123 Example St, Fremont, CA 94539")
    print("🏢 Work: 1600 Amphitheatre Pkwy, Mountain View, CA")
    
    print("\n--- COMMUTE ANALYSIS ---")
    print(f"Rush Hour: {MOCK_COMMUTE_DATA['duration_in_traffic_text']}")
    print(f"Off-Peak: {MOCK_COMMUTE_DATA['duration_text']}")
    print(f"Distance: {MOCK_COMMUTE_DATA['distance_text']}")
    
    print("\n--- LIFESTYLE AMENITIES ---")
    for place_type, places in MOCK_PLACES_DATA.items():
        print(f"{place_type}: {len(places)} nearby")
        for p in places[:2]:
            print(f"  - {p['name']} ({p['rating']}★)")
    
    print("\n--- SCHOOLS ---")
    for school in MOCK_SCHOOLS_DATA["schools"]:
        print(f"{school['name']}: {school['rating']}/10 ({school['trend']})")
    
    print("\n--- SAFETY ---")
    print(f"Overall Score: {MOCK_CRIME_DATA['overall_score']}/10")
    print(f"Trend: {MOCK_CRIME_DATA['trend']}")
    print(f"Daytime: {MOCK_CRIME_DATA['by_time']['daytime']['score']}/10")
    print(f"Nighttime: {MOCK_CRIME_DATA['by_time']['night']['score']}/10")
    
    print("\n--- UPCOMING DEVELOPMENT ---")
    for project in MOCK_CITY_PLANNING_DATA["projects"]:
        print(f"{project['name']}: {project['status']} (Est. {project['completion']})")
    
    print("\n--- RECENT NEWS ---")
    for article in MOCK_NEWS_DATA[:3]:
        print(f"• {article['title']}")
    
    print("\n" + "=" * 60)
    print("Mock analysis complete! System is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    run_mock_analysis()
