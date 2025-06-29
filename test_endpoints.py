#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
Tests each endpoint individually and validates response structure
"""

import asyncio
import aiohttp
import os
import json
import time
from typing import Dict, Any, List

class EndpointTester:
    def __init__(self):
        self.user = os.getenv('THESPORTS_USER')
        self.secret = os.getenv('THESPORTS_SECRET')
        self.base_url = "https://api.thesports.com/v1/football"
        self.test_results = {}
        
        if not self.user or not self.secret:
            raise ValueError("THESPORTS_USER and THESPORTS_SECRET environment variables required")
    
    async def test_endpoint(self, name: str, url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        test_params = {'user': self.user, 'secret': self.secret}
        if params:
            test_params.update(params)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=test_params) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            # Check for API errors
                            if 'err' in data:
                                return {
                                    'status': 'FAILED',
                                    'error': f"API Error: {data['err']}",
                                    'response_time': response_time,
                                    'http_status': response.status
                                }
                            
                            # Analyze response structure
                            results = data.get('results', [])
                            result_count = len(results) if isinstance(results, list) else (1 if results else 0)
                            
                            return {
                                'status': 'SUCCESS',
                                'response_time': response_time,
                                'http_status': response.status,
                                'result_count': result_count,
                                'has_results': bool(results),
                                'data_sample': str(results)[:200] if results else "No data"
                            }
                            
                        except json.JSONDecodeError as e:
                            return {
                                'status': 'FAILED',
                                'error': f"JSON decode error: {e}",
                                'response_time': response_time,
                                'http_status': response.status
                            }
                    else:
                        return {
                            'status': 'FAILED',
                            'error': f"HTTP {response.status}",
                            'response_time': response_time,
                            'http_status': response.status
                        }
                        
            except Exception as e:
                response_time = time.time() - start_time
                return {
                    'status': 'FAILED',
                    'error': str(e),
                    'response_time': response_time,
                    'http_status': None
                }
    
    async def run_all_tests(self):
        """Run tests on all endpoints"""
        print("🧪 Starting API Endpoint Tests")
        print("=" * 50)
        
        # Test 1: Live matches (no parameters needed)
        print("📡 Testing /match/detail_live...")
        self.test_results['live'] = await self.test_endpoint(
            'live',
            f"{self.base_url}/match/detail_live"
        )
        self.print_test_result('Live Matches', self.test_results['live'])
        
        # Get a sample match ID for dependent tests
        sample_match_id = None
        if self.test_results['live']['status'] == 'SUCCESS':
            try:
                # Try to extract a match ID from the sample data
                sample_data = self.test_results['live']['data_sample']
                if 'id' in sample_data and self.test_results['live']['result_count'] > 0:
                    # We'll use a known pattern or get from actual data
                    sample_match_id = "1l4rjnh967y1m7v"  # From previous successful run
            except:
                pass
        
        # Test 2: Match details (requires match ID)
        print("\n📋 Testing /match/recent/list...")
        if sample_match_id:
            self.test_results['details'] = await self.test_endpoint(
                'details',
                f"{self.base_url}/match/recent/list",
                {'uuid': sample_match_id}
            )
        else:
            self.test_results['details'] = {
                'status': 'SKIPPED',
                'error': 'No sample match ID available',
                'response_time': 0,
                'http_status': None
            }
        self.print_test_result('Match Details', self.test_results['details'])
        
        # Test 3: Odds history (requires match ID)
        print("\n📊 Testing /odds/history...")
        if sample_match_id:
            self.test_results['odds'] = await self.test_endpoint(
                'odds',
                f"{self.base_url}/odds/history",
                {'uuid': sample_match_id}
            )
        else:
            self.test_results['odds'] = {
                'status': 'SKIPPED',
                'error': 'No sample match ID available',
                'response_time': 0,
                'http_status': None
            }
        self.print_test_result('Odds History', self.test_results['odds'])
        
        # Test 4: Team info (requires team ID)
        print("\n👕 Testing /team/additional/list...")
        sample_team_id = "965mkyh3j73r1ge"  # From previous successful run
        self.test_results['team'] = await self.test_endpoint(
            'team',
            f"{self.base_url}/team/additional/list",
            {'uuid': sample_team_id}
        )
        self.print_test_result('Team Info', self.test_results['team'])
        
        # Test 5: Competition info (requires competition ID)
        print("\n🏆 Testing /competition/additional/list...")
        sample_competition_id = "gy0or5jhj9qwzv3"  # From previous successful run
        self.test_results['competition'] = await self.test_endpoint(
            'competition',
            f"{self.base_url}/competition/additional/list",
            {'uuid': sample_competition_id}
        )
        self.print_test_result('Competition Info', self.test_results['competition'])
        
        # Test 6: Countries (no parameters needed)
        print("\n🌍 Testing /country/list...")
        self.test_results['country'] = await self.test_endpoint(
            'country',
            f"{self.base_url}/country/list"
        )
        self.print_test_result('Country List', self.test_results['country'])
        
        # Print summary
        self.print_summary()
    
    def print_test_result(self, name: str, result: Dict[str, Any]):
        """Print formatted test result"""
        status = result['status']
        if status == 'SUCCESS':
            print(f"✅ {name}: {status}")
            print(f"   ⏱️  Response Time: {result['response_time']:.3f}s")
            print(f"   📊 Results Count: {result['result_count']}")
            print(f"   💾 Has Data: {result['has_results']}")
        elif status == 'SKIPPED':
            print(f"⏭️  {name}: {status}")
            print(f"   ⚠️  Reason: {result['error']}")
        else:
            print(f"❌ {name}: {status}")
            print(f"   ❗ Error: {result['error']}")
            print(f"   ⏱️  Response Time: {result['response_time']:.3f}s")
            if result['http_status']:
                print(f"   🌐 HTTP Status: {result['http_status']}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful = sum(1 for r in self.test_results.values() if r['status'] == 'SUCCESS')
        failed = sum(1 for r in self.test_results.values() if r['status'] == 'FAILED')
        skipped = sum(1 for r in self.test_results.values() if r['status'] == 'SKIPPED')
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Success Rate: {(successful/total_tests)*100:.1f}%")
        
        # List any failed tests
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for name, result in self.test_results.items():
                if result['status'] == 'FAILED':
                    print(f"   • {name}: {result['error']}")
        
        # Average response time for successful tests
        successful_times = [r['response_time'] for r in self.test_results.values() 
                          if r['status'] == 'SUCCESS']
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            print(f"\n⏱️  Average Response Time: {avg_time:.3f}s")
        
        print("\n🎉 Endpoint testing completed!")

async def main():
    """Main test runner"""
    try:
        tester = EndpointTester()
        await tester.run_all_tests()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please set THESPORTS_USER and THESPORTS_SECRET environment variables")
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())