# 🧪 API Testing with S3 Data Pipeline
# Separate file for testing Allen and KDT APIs with real Jeju folklore data from S3

import os
import json
import boto3
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import warnings

warnings.filterwarnings('ignore')

class S3JejuDataProcessor:
    """
    🗃️ S3 Data Processor for Jeju Folklore Content
    
    Handles data retrieval from S3 buckets and prepares it for API testing
    """
    
    def __init__(self, region: str = "ap-southeast-2"):
        self.region = region
        self.source_bucket = "jeju-folklore-data"
        self.target_bucket = "elbee-oreumi"
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
            print(f"✅ S3 client initialized for region: {self.region}")
        except Exception as e:
            print(f"⚠️ S3 client initialization failed: {e}")
            self.s3_client = None
    
    def list_jeju_episodes(self, max_files: int = 10) -> List[Dict[str, Any]]:
        """
        List available Jeju episode files from S3
        """
        episodes = []
        
        if not self.s3_client:
            print("❌ S3 client not available - using mock data")
            return self._get_mock_episodes()
        
        try:
            print(f"🔍 Listing files from S3 bucket: {self.source_bucket}")
            
            # List objects in the raw data directory
            response = self.s3_client.list_objects_v2(
                Bucket=self.source_bucket,
                Prefix='team-data/jeju-stories/raw/',
                MaxKeys=max_files
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.json'):
                        episodes.append({
                            'filename': obj['Key'].split('/')[-1],
                            's3_key': obj['Key'],
                            'size_kb': round(obj['Size'] / 1024, 2),
                            'last_modified': obj['LastModified'].isoformat()
                        })
                        
            print(f"✅ Found {len(episodes)} Jeju episode files")
            return episodes
            
        except Exception as e:
            print(f"❌ Failed to list S3 files: {e}")
            return self._get_mock_episodes()
    
    def download_episode_content(self, s3_key: str) -> Dict[str, Any]:
        """
        Download and parse episode content from S3
        """
        if not self.s3_client:
            return self._get_mock_content(s3_key)
        
        try:
            print(f"📥 Downloading: {s3_key}")
            
            response = self.s3_client.get_object(
                Bucket=self.source_bucket,
                Key=s3_key
            )
            
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
            
            print(f"✅ Downloaded {len(content)} bytes")
            return data
            
        except Exception as e:
            print(f"❌ Failed to download {s3_key}: {e}")
            return self._get_mock_content(s3_key)
    
    def _get_mock_episodes(self) -> List[Dict[str, Any]]:
        """Mock episode data for testing when S3 is unavailable"""
        return [
            {
                'filename': 'ebook_C_F_001.json',
                's3_key': 'team-data/jeju-stories/raw/ebook/ebook_C_F_001.json',
                'size_kb': 45.2,
                'last_modified': '2024-12-04T09:30:00'
            },
            {
                'filename': 'ebook_C_F_002.json',
                's3_key': 'team-data/jeju-stories/raw/ebook/ebook_C_F_002.json',
                'size_kb': 52.1,
                'last_modified': '2024-12-04T09:31:00'
            },
            {
                'filename': 'ocr_traditional_001.json',
                's3_key': 'team-data/jeju-stories/raw/ocr/ocr_traditional_001.json',
                'size_kb': 38.7,
                'last_modified': '2024-12-04T09:32:00'
            }
        ]
    
    def _get_mock_content(self, s3_key: str) -> Dict[str, Any]:
        """Mock content data for testing"""
        mock_contents = {
            'ebook_C_F_001.json': {
                'title': '제주도의 옛날 이야기',
                'content': '옛날 제주도에 살던 할머니가 있었어요. 그 할머니는 매일 한라산을 바라보며 해녀들을 위해 기도했다고 해요. 돌하르방이 지켜주는 이 섬에서, 사람들은 바다와 더불어 살아왔습니다. 메서 고마우신 할머니의 수다가 그리워요.',
                'type': 'folklore',
                'dialect': 'jeju',
                'cultural_elements': ['돌하르방', '해녀', '한라산']
            },
            'ebook_C_F_002.json': {
                'title': '바다 속의 용왕 이야기',
                'content': '제주 바다 깊은 곳에 용왕님이 살고 있다고 했어요. 해녀들이 물질을 할 때마다 용왕님께 안전을 기원했습니다. 어느 날 용왕님이 꿈에 나타나서 말했어요. "이 바다를 아끼고 보살펴라." 그때부터 제주 사람들은 바다를 더욱 소중히 여겼다고 해요.',
                'type': 'legend',
                'dialect': 'standard',
                'cultural_elements': ['용왕', '해녀', '물질']
            },
            'ocr_traditional_001.json': {
                'title': '전통 민담 - 설문대할망',
                'content': '설문대할망은 제주도를 만든 거인할망이었어요. 커다란 치마폭으로 흙을 날라다가 제주도를 만들었다고 해요. 한라산도 설문대할망이 만든 것이라고 전해집니다. 할망이 죽을 때 몸이 제주도의 오름들이 되었다고 해요.',
                'type': 'myth',
                'dialect': 'jeju',
                'cultural_elements': ['설문대할망', '한라산', '오름']
            }
        }
        
        filename = s3_key.split('/')[-1]
        return mock_contents.get(filename, {
            'title': 'Mock Episode',
            'content': '제주도의 아름다운 이야기입니다.',
            'type': 'unknown',
            'dialect': 'standard',
            'cultural_elements': []
        })

class APITestOrchestrator:
    """
    🎭 API Test Orchestrator
    
    Manages testing of Allen and KDT APIs with S3 data pipeline
    """
    
    def __init__(self, allen_api, kdt_api, s3_processor):
        self.allen_api = allen_api
        self.kdt_api = kdt_api
        self.s3_processor = s3_processor
        self.test_results = []
        self.quota_history = []
        
    def run_comprehensive_test(self, max_episodes: int = 3) -> Dict[str, Any]:
        """
        Run comprehensive API testing with real S3 data
        """
        print("🚀 STARTING COMPREHENSIVE API TESTING WITH S3 DATA")
        print("=" * 60)
        
        # Initialize test session
        test_session = {
            'session_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'max_episodes': max_episodes,
            'allen_quota_start': self.allen_api.check_quota(),
            'tests_completed': 0,
            'results': []
        }
        
        # Step 1: Get S3 episode list
        print(f"\n📂 STEP 1: Retrieving episode list from S3")
        episodes = self.s3_processor.list_jeju_episodes(max_episodes)
        
        if not episodes:
            print("❌ No episodes available for testing")
            return test_session
        
        print(f"✅ Found {len(episodes)} episodes for testing")
        
        # Step 2: Process each episode
        for i, episode in enumerate(episodes, 1):
            print(f"\n🧪 STEP 2.{i}: Processing Episode {i}/{len(episodes)}")
            print(f"   📁 File: {episode['filename']}")
            
            # Download episode content
            content = self.s3_processor.download_episode_content(episode['s3_key'])
            
            if not content:
                print("   ⚠️ Skipping - no content available")
                continue
            
            # Test both APIs with this episode
            episode_test = self._test_episode_with_both_apis(episode, content)
            test_session['results'].append(episode_test)
            test_session['tests_completed'] += 1
            
            # Quota check after each test
            current_quota = self.allen_api.check_quota()
            self.quota_history.append({
                'episode': episode['filename'],
                'quota_remaining': current_quota['requests_remaining'],
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"   📊 Allen API quota remaining: {current_quota['requests_remaining']}")
            
            # Stop if quota is getting low
            if current_quota['requests_remaining'] < 5:
                print(f"   ⚠️ Stopping tests - Allen API quota getting low")
                break
        
        # Step 3: Generate final report
        test_session['end_time'] = datetime.now().isoformat()
        test_session['allen_quota_end'] = self.allen_api.check_quota()
        test_session['quota_used'] = test_session['allen_quota_start']['requests_made'] - test_session['allen_quota_end']['requests_made']
        
        print(f"\n📊 STEP 3: Generating Test Report")
        self._generate_test_report(test_session)
        
        return test_session
    
    def _test_episode_with_both_apis(self, episode: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test both APIs with a single episode
        """
        episode_test = {
            'episode_info': episode,
            'content_preview': content.get('content', '')[:100] + "...",
            'allen_api_result': {},
            'kdt_api_result': {},
            'comparison': {},
            'timestamp': datetime.now().isoformat()
        }
        
        text_content = content.get('content', '')
        
        # Test Allen API
        print(f"      🤖 Testing Allen API...")
        try:
            allen_result = self.allen_api.analyze_korean_text(text_content, "comprehensive")
            episode_test['allen_api_result'] = {
                'status': allen_result.get('status'),
                'success': allen_result.get('status') == 'success',
                'quota_remaining': allen_result.get('quota_remaining', 0),
                'processing_time': allen_result.get('processing_time_ms', 0)
            }
            
            if allen_result.get('status') == 'success':
                analysis = allen_result.get('analysis', {})
                episode_test['allen_api_result']['insights'] = {
                    'dialect': analysis.get('language_detection', {}).get('dialect'),
                    'cultural_richness': analysis.get('cultural_elements', {}).get('cultural_richness_score', 0),
                    'quality': analysis.get('quality_assessment', {}).get('overall_quality')
                }
            
            print(f"         ✅ Allen API: {episode_test['allen_api_result']['status']}")
            
        except Exception as e:
            episode_test['allen_api_result'] = {'status': 'error', 'error': str(e)}
            print(f"         ❌ Allen API failed: {e}")
        
        # Test KDT API
        print(f"      🔧 Testing KDT API...")
        try:
            kdt_result = self.kdt_api.analyze_korean_text(text_content)
            episode_test['kdt_api_result'] = {
                'status': kdt_result.get('status'),
                'success': kdt_result.get('status') == 'success',
                'endpoint_used': kdt_result.get('endpoint_used')
            }
            
            print(f"         ✅ KDT API: {episode_test['kdt_api_result']['status']}")
            
        except Exception as e:
            episode_test['kdt_api_result'] = {'status': 'error', 'error': str(e)}
            print(f"         ❌ KDT API failed: {e}")
        
        # Compare results
        episode_test['comparison'] = self._compare_api_results(
            episode_test['allen_api_result'], 
            episode_test['kdt_api_result']
        )
        
        return episode_test
    
    def _compare_api_results(self, allen_result: Dict[str, Any], kdt_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare results from both APIs
        """
        comparison = {
            'both_successful': allen_result.get('success', False) and kdt_result.get('success', False),
            'allen_only': allen_result.get('success', False) and not kdt_result.get('success', False),
            'kdt_only': kdt_result.get('success', False) and not allen_result.get('success', False),
            'both_failed': not allen_result.get('success', False) and not kdt_result.get('success', False)
        }
        
        if comparison['both_successful']:
            comparison['recommendation'] = 'Both APIs working - use Allen for primary analysis, KDT for validation'
        elif comparison['allen_only']:
            comparison['recommendation'] = 'Use Allen API as primary - KDT API unavailable'
        elif comparison['kdt_only']:
            comparison['recommendation'] = 'KDT API working but Allen API failed - investigate Allen quota'
        else:
            comparison['recommendation'] = 'Both APIs failed - check network and API status'
        
        return comparison
    
    def _generate_test_report(self, test_session: Dict[str, Any]):
        """
        Generate comprehensive test report
        """
        print(f"\n📋 COMPREHENSIVE API TEST REPORT")
        print("=" * 50)
        
        # Session summary
        start_time = datetime.fromisoformat(test_session['start_time'])
        end_time = datetime.fromisoformat(test_session['end_time'])
        duration = end_time - start_time
        
        print(f"🕒 Test Duration: {duration.total_seconds():.1f} seconds")
        print(f"📊 Episodes Tested: {test_session['tests_completed']}")
        print(f"🔋 Allen Quota Used: {test_session['quota_used']} requests")
        
        # API Performance Summary
        successful_allen = sum(1 for result in test_session['results'] 
                              if result['allen_api_result'].get('success', False))
        successful_kdt = sum(1 for result in test_session['results'] 
                            if result['kdt_api_result'].get('success', False))
        
        print(f"\n📈 API PERFORMANCE SUMMARY")
        print(f"   Allen API Success Rate: {successful_allen}/{test_session['tests_completed']} ({successful_allen/test_session['tests_completed']*100:.1f}%)")
        print(f"   KDT API Success Rate: {successful_kdt}/{test_session['tests_completed']} ({successful_kdt/test_session['tests_completed']*100:.1f}%)")
        
        # Individual episode results
        print(f"\n📄 INDIVIDUAL EPISODE RESULTS")
        for i, result in enumerate(test_session['results'], 1):
            episode_name = result['episode_info']['filename']
            allen_status = "✅" if result['allen_api_result'].get('success') else "❌"
            kdt_status = "✅" if result['kdt_api_result'].get('success') else "❌"
            
            print(f"   {i}. {episode_name}")
            print(f"      Allen: {allen_status} | KDT: {kdt_status} | {result['comparison']['recommendation']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        if successful_allen >= successful_kdt:
            print("   1. Use Allen API as primary analysis tool")
            print("   2. Implement KDT API as fallback when available")
        else:
            print("   1. Investigate Allen API issues")
            print("   2. Consider KDT API as primary if consistently available")
        
        print("   3. Implement caching to reduce API calls")
        print("   4. Monitor quota usage and implement rate limiting")
        print("   5. Set up automated health checks for both APIs")

def main():
    """
    Main function to run API testing with S3 data pipeline
    """
    print("🌊 JEJU FOLKLORE API TESTING WITH S3 DATA PIPELINE")
    print("=" * 60)
    
    # Note: This assumes Allen and KDT API clients are already initialized
    # In the notebook environment, these would be imported from the notebook variables
    
    # Initialize S3 processor
    s3_processor = S3JejuDataProcessor()
    
    # Mock API clients for standalone testing
    class MockAllenAPI:
        def __init__(self):
            self.requests_made = 2
            self.daily_limit = 100
        
        def check_quota(self):
            return {
                'requests_made': self.requests_made,
                'requests_remaining': self.daily_limit - self.requests_made,
                'percentage_used': (self.requests_made / self.daily_limit) * 100,
                'quota_exceeded': self.requests_made >= self.daily_limit
            }
        
        def analyze_korean_text(self, text, analysis_type="comprehensive"):
            self.requests_made += 1
            return {
                'status': 'success',
                'quota_remaining': self.daily_limit - self.requests_made,
                'processing_time_ms': 150,
                'analysis': {
                    'language_detection': {'dialect': 'jeju'},
                    'cultural_elements': {'cultural_richness_score': 0.8},
                    'quality_assessment': {'overall_quality': 'high'}
                }
            }
    
    class MockKDTAPI:
        def analyze_korean_text(self, text):
            return {'status': 'api_error', 'status_code': 404}
    
    # Initialize mock APIs (replace with real APIs when available)
    allen_api = MockAllenAPI()
    kdt_api = MockKDTAPI()
    
    # Initialize test orchestrator
    orchestrator = APITestOrchestrator(allen_api, kdt_api, s3_processor)
    
    # Run comprehensive test
    test_results = orchestrator.run_comprehensive_test(max_episodes=3)
    
    print(f"\n✅ API testing completed!")
    print(f"📊 Session ID: {test_results['session_id']}")
    print(f"📝 Results stored in test_results variable")
    
    return test_results

if __name__ == "__main__":
    # This allows the file to be run independently for testing
    results = main()
    
    # Save results to file
    output_file = f"api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Results saved to: {output_file}")