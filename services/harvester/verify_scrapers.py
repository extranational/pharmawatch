"""
Test script to verify both ChiCTR and NMPA scrapers are operational.
Run from: pharmawatch_repo/services/harvester/
"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.scraper import ChiCTRScraper, ChiCTRSignal, NMPAScraper, NMPASignal


async def test_chictr():
    print("=" * 60)
    print("TEST 1: ChiCTR Harvester")
    print("=" * 60)
    scraper = ChiCTRScraper()
    results = await scraper.fetch_recent_trials()
    print(f"✓ ChiCTR returned {len(results)} signals")
    for r in results:
        assert isinstance(r.trial_id, str) and r.trial_id.startswith("ChiCTR"), f"Bad trial_id: {r.trial_id}"
        assert len(r.title) > 10, f"Title too short: {r.title}"
        print(f"  [{r.trial_id}] {r.title[:60]}...")
    print("✓ ChiCTR TEST PASSED\n")
    return results


async def test_nmpa():
    print("=" * 60)
    print("TEST 2: NMPA Harvester")
    print("=" * 60)
    scraper = NMPAScraper()
    results = await scraper.fetch_drug_announcements()
    print(f"✓ NMPA returned {len(results)} signals")
    for r in results:
        assert isinstance(r.announcement_id, str), f"Bad announcement_id: {r.announcement_id}"
        assert len(r.title) > 5, f"Title too short: {r.title}"
        print(f"  [{r.announcement_id}] ({r.category}) {r.title[:60]}...")
    print("✓ NMPA TEST PASSED\n")
    return results


async def main():
    print("\n🚀 PharmaWatch Harvester Verification")
    print("=" * 60)

    try:
        chi_results = await test_chictr()
    except Exception as e:
        print(f"✗ ChiCTR TEST FAILED: {e}")

    try:
        nmpa_results = await test_nmpa()
    except Exception as e:
        print(f"✗ NMPA TEST FAILED: {e}")

    print("=" * 60)
    print("All verification tests completed.")


if __name__ == "__main__":
    asyncio.run(main())