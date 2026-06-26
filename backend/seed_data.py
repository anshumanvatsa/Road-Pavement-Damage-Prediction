"""Seed database with sample roads matching frontend sample-data.ts."""
import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from database import async_session_maker
from models import RoadModel

ROAD_NAMES = [
    "Main Street", "Highway 101", "Oak Avenue", "Industrial Blvd", "River Road",
    "Cedar Lane", "Park Drive", "Market Street", "Bridge Road", "Elm Street",
    "Sunset Boulevard", "Canyon Road", "Harbor Drive", "Mountain Pass", "Valley Way",
    "Airport Road", "University Ave", "Central Expressway", "Bay Street", "Lake Drive",
    "Commerce Way", "Factory Road", "Orchard Lane", "Coastal Highway", "Metro Boulevard",
    "Rail Corridor", "Tech Park Drive", "Heritage Road", "Forest Avenue", "Marsh Creek Rd",
    "Summit Drive", "Pier Street", "Arena Boulevard", "Campus Drive", "Quarry Road",
    "Vineyard Lane", "Mill Street", "Dock Road", "Basin Avenue", "Ridge Way",
    "Lagoon Drive", "Prairie Road", "Bluff Street", "Creek Crossing", "Hillcrest Ave",
    "Meadow Lane", "Terrace Drive", "Canal Street", "Spring Road", "Crest Avenue",
]

LOCATIONS = [
    "Downtown Core", "North District", "South Industrial Zone", "East Waterfront", "West Suburbs",
    "Central Business", "Port Area", "University Quarter", "Tech Hub", "Residential North",
    "Old Town", "New Development", "Airport Zone", "Commercial Strip", "River District",
    "Hillside", "Coastal Zone", "Transit Corridor", "Heritage District", "Innovation Park",
]


def seeded_random(seed: int):
    """Seeded random generator - matches frontend sample-data.ts."""
    s = seed

    def next_val():
        nonlocal s
        s = (s * 16807 + 0) % 2147483647
        return s / 2147483647

    return next_val


def generate_sample_roads(count: int = 50) -> list[dict]:
    """Generate sample roads matching frontend sample-data.ts exactly."""
    rand = seeded_random(42)
    roads = []

    for i in range(count):
        days_ago = int(rand() * 90)
        d = date.today() - timedelta(days=days_ago)

        roads.append({
            "id": f"road-{str(i + 1).zfill(3)}",
            "road_name": ROAD_NAMES[i % len(ROAD_NAMES)],
            "location": LOCATIONS[int(rand() * len(LOCATIONS))],
            "latitude": round(37.3 + rand() * 0.5, 6),
            "longitude": round(-122.0 - rand() * 0.5, 6),
            "current_condition_index": round((30 + rand() * 70) * 10) / 10,
            "traffic_volume": int(1000 + rand() * 19000),
            "heavy_vehicle_percentage": round(rand() * 40 * 10) / 10,
            "rainfall": round(rand() * 300 * 10) / 10,
            "temperature": round((5 + rand() * 40) * 10) / 10,
            "humidity": round((20 + rand() * 70) * 10) / 10,
            "last_updated": d.isoformat(),
        })

    return roads


async def seed_if_empty():
    """Seed database with sample roads if empty."""
    async with async_session_maker() as session:
        result = await session.execute(select(RoadModel))
        existing = result.scalars().all()
        if existing:
            print(f"Database already has {len(existing)} roads. Skipping seed.")
            return

        roads_data = generate_sample_roads(50)
        for r in roads_data:
            road = RoadModel(**r)
            session.add(road)

        await session.commit()
        print(f"Seeded {len(roads_data)} sample roads.")


if __name__ == "__main__":
    async def run():
        from database import init_db
        await init_db()
        await seed_if_empty()

    asyncio.run(run())
