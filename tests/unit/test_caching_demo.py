# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Cache System Demo for Warehouse Operational Assistant

Demonstrates the comprehensive Redis caching system with SQL results,
evidence packs, vector searches, and monitoring capabilities.
"""

import asyncio
import logging
import json
import pytest
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_redis_cache_service():
    """Test the Redis cache service functionality."""
    print("🧪 Testing Redis Cache Service...")

    try:
        from src.retrieval.caching.redis_cache_service import (
            RedisCacheService,
            CacheType,
            CacheConfig,
        )

        # Initialize cache service
        config = CacheConfig(
            default_ttl=60,  # 1 minute for testing
            max_memory="50mb",
            compression_enabled=True,
            monitoring_enabled=True,
        )

        cache_service = RedisCacheService(config=config)
        await cache_service.initialize()

        # Test basic caching
        test_data = {
            "query": "How many active workers we have?",
            "result": {
                "total_workers": 6,
                "shifts": {
                    "morning": {"count": 3, "active_tasks": 8},
                    "afternoon": {"count": 3, "active_tasks": 6},
                },
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Store data
        cache_key = "workforce_query_001"
        success = await cache_service.set(
            cache_key, test_data, CacheType.WORKFORCE_DATA, ttl=60
        )

        print(f"✅ Cache set success: {success}")

        # Retrieve data
        retrieved_data = await cache_service.get(cache_key, CacheType.WORKFORCE_DATA)
        print(f"✅ Cache get success: {retrieved_data is not None}")

        if retrieved_data:
            print(f"📊 Retrieved data: {json.dumps(retrieved_data, indent=2)}")

        # Test cache metrics
        metrics = await cache_service.get_metrics()
        print(f"📈 Cache metrics: {metrics}")

        # Test health check
        health = await cache_service.health_check()
        print(f"🏥 Cache health: {health}")

        return True

    except Exception as e:
        print(f"❌ Redis cache service test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_cache_manager():
    """Test the cache manager functionality."""
    print("\n🧪 Testing Cache Manager...")

    try:
        from src.retrieval.caching.cache_manager import (
            CacheManager,
            CachePolicy,
            CacheWarmingRule,
            EvictionStrategy,
        )
        from src.retrieval.caching.redis_cache_service import CacheType
        from src.retrieval.caching.redis_cache_service import get_cache_service

        # Get cache service
        cache_service = await get_cache_service()

        # Initialize cache manager
        policy = CachePolicy(
            max_size=100,
            max_memory_mb=50,
            default_ttl=60,
            eviction_strategy=EvictionStrategy.LRU,
            warming_enabled=True,
            monitoring_enabled=True,
        )

        cache_manager = CacheManager(cache_service, policy)
        await cache_manager.initialize()

        # Test cache warming rule
        async def generate_test_data():
            return {
                "test_data": "This is warmed data",
                "timestamp": datetime.now().isoformat(),
            }

        warming_rule = CacheWarmingRule(
            cache_type=CacheType.WORKFORCE_DATA,
            key_pattern="test_warming",
            data_generator=generate_test_data,
            priority=1,
            frequency_minutes=1,
        )

        cache_manager.add_warming_rule(warming_rule)

        # Test warming
        warmed_count = await cache_manager.warm_cache_rule(warming_rule)
        print(f"✅ Cache warming success: {warmed_count} entries warmed")

        # Test cache health
        health = await cache_manager.get_cache_health()
        print(f"🏥 Cache manager health: {health}")

        # Test cache optimization
        optimization_results = await cache_manager.optimize_cache()
        print(f"⚡ Cache optimization: {optimization_results}")

        return True

    except Exception as e:
        print(f"❌ Cache manager test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_cache_integration():
    """Test the cache integration functionality."""
    print("\n🧪 Testing Cache Integration...")

    try:
        from src.retrieval.caching.cache_integration import (
            CachedQueryProcessor,
            CacheIntegrationConfig,
        )

        # Mock components for testing
        class MockSQLRouter:
            async def route_query(self, query):
                return type(
                    "obj",
                    (object,),
                    {
                        "route_to": "sql",
                        "query_type": type("obj", (object,), {"value": "sql_atp"}),
                        "confidence": 0.9,
                    },
                )()

            async def execute_sql_query(self, query, query_type):
                return {
                    "success": True,
                    "data": [{"sku": "SKU123", "quantity": 100}],
                    "execution_time": 0.05,
                }

        class MockVectorRetriever:
            async def search(self, query):
                return {
                    "results": [{"content": "Sample content", "score": 0.95}],
                    "evidence_score": {
                        "overall_score": 0.85,
                        "confidence_level": "high",
                    },
                }

        class MockQueryPreprocessor:
            async def preprocess_query(self, query):
                return type(
                    "obj",
                    (object,),
                    {
                        "normalized_query": query.lower(),
                        "intent": type("obj", (object,), {"value": "workforce"}),
                        "entities": {},
                        "keywords": ["workers"],
                        "complexity_score": 0.5,
                        "suggestions": [],
                    },
                )()

        class MockEvidenceScoringEngine:
            pass

        # Initialize components
        sql_router = MockSQLRouter()
        vector_retriever = MockVectorRetriever()
        query_preprocessor = MockQueryPreprocessor()
        evidence_scoring_engine = MockEvidenceScoringEngine()

        # Configure cache integration
        config = CacheIntegrationConfig(
            enable_sql_caching=True,
            enable_vector_caching=True,
            enable_evidence_caching=True,
            enable_preprocessing_caching=True,
            sql_cache_ttl=60,
            vector_cache_ttl=30,
            evidence_cache_ttl=120,
            preprocessing_cache_ttl=180,
        )

        # Initialize cached query processor
        processor = CachedQueryProcessor(
            sql_router,
            vector_retriever,
            query_preprocessor,
            evidence_scoring_engine,
            config,
        )
        await processor.initialize()

        # Test query processing with caching
        test_queries = [
            "How many active workers we have?",
            "What are the latest tasks?",
            "Show me equipment status",
        ]

        for query in test_queries:
            print(f"\n🔍 Processing query: '{query}'")

            result = await processor.process_query_with_caching(query)

            print(f"✅ Query processed successfully")
            print(f"📊 Cache hits: {result['cache_hits']}")
            print(f"📊 Cache misses: {result['cache_misses']}")
            print(f"⏱️ Processing time: {result['processing_time']:.3f}s")
            print(f"🛣️ Route: {result['route']}")

            # Process same query again to test caching
            print(f"🔄 Processing same query again (should hit cache)...")
            result2 = await processor.process_query_with_caching(query)

            print(f"📊 Second query cache hits: {result2['cache_hits']}")
            print(f"📊 Second query cache misses: {result2['cache_misses']}")

        # Test cache statistics
        stats = await processor.get_cache_stats()
        print(f"\n📈 Cache statistics: {json.dumps(stats, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ Cache integration test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_cache_monitoring():
    """Test the cache monitoring functionality."""
    print("\n🧪 Testing Cache Monitoring...")

    try:
        from src.retrieval.caching.cache_monitoring import (
            CacheMonitoringService,
            AlertLevel,
        )
        from src.retrieval.caching.redis_cache_service import get_cache_service
        from src.retrieval.caching.cache_manager import get_cache_manager

        # Get cache services
        cache_service = await get_cache_service()
        cache_manager = await get_cache_manager()

        # Initialize monitoring service
        monitoring = CacheMonitoringService(cache_service, cache_manager)
        await monitoring.start_monitoring(
            interval_seconds=5
        )  # 5 second interval for testing

        # Add alert callback
        def alert_callback(alert):
            print(f"🚨 Alert triggered: {alert.message} (Level: {alert.level.value})")

        monitoring.add_alert_callback(alert_callback)

        # Wait a bit for monitoring to collect data
        await asyncio.sleep(10)

        # Get dashboard data
        dashboard_data = await monitoring.get_dashboard_data()
        print(f"📊 Dashboard data: {json.dumps(dashboard_data, indent=2)}")

        # Get performance report
        performance_report = await monitoring.get_performance_report(hours=1)
        print(f"📈 Performance report status: {performance_report.overall_status}")
        print(f"📈 Performance score: {performance_report.performance_score:.1f}")
        print(f"📈 Uptime: {performance_report.uptime_percentage:.1f}%")

        # Stop monitoring
        await monitoring.stop_monitoring()

        return True

    except Exception as e:
        print(f"❌ Cache monitoring test failed: {e}")
        return False


async def main():
    """Run all cache system tests."""
    print("🚀 Starting Cache System Demo for Warehouse Operational Assistant")
    print("=" * 70)

    test_results = []

    # Test Redis Cache Service
    result1 = await test_redis_cache_service()
    test_results.append(("Redis Cache Service", result1))

    # Test Cache Manager
    result2 = await test_cache_manager()
    test_results.append(("Cache Manager", result2))

    # Test Cache Integration
    result3 = await test_cache_integration()
    test_results.append(("Cache Integration", result3))

    # Test Cache Monitoring
    result4 = await test_cache_monitoring()
    test_results.append(("Cache Monitoring", result4))

    # Print summary
    print("\n" + "=" * 70)
    print("📋 Test Results Summary:")
    print("=" * 70)

    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")

    if passed == len(test_results):
        print(
            "🎉 All cache system tests passed! The caching system is working correctly."
        )
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

    print("\n💡 Key Features Demonstrated:")
    print("• Redis caching with configurable TTL")
    print("• Cache compression and optimization")
    print("• Intelligent cache warming")
    print("• Real-time monitoring and alerting")
    print("• Performance metrics and health checks")
    print("• Query processing with integrated caching")
    print("• Evidence pack caching")
    print("• SQL result caching")
    print("• Vector search result caching")


if __name__ == "__main__":
    asyncio.run(main())
