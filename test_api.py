#!/usr/bin/env python3
"""
Test script for ReviewLab API Server.

This script tests the FastAPI endpoints to ensure the agentic system is working.
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health and status endpoints."""
    print("🏥 Testing Health Endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['status']}")
            print(f"   Components: {data['components']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data['status']}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test status endpoint
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status endpoint: {data['system']} - {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Endpoints: {list(data['endpoints'].keys())}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    print()

def test_bug_injection_endpoints():
    """Test bug injection endpoints."""
    print("🐛 Testing Bug Injection Endpoints...")
    
    # Test bug injection
    injection_data = {
        "template_ids": ["python_negative_index"],
        "project_path": ".",
        "language": "python",
        "max_bugs": 1,
        "dry_run": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/inject/bugs", json=injection_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bug injection: {data['total_bugs']} bugs injected")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Status: {data['status']}")
            
            # Test getting the session
            session_id = data['session_id']
            session_response = requests.get(f"{BASE_URL}/api/v1/inject/sessions/{session_id}")
            if session_response.status_code == 200:
                print(f"✅ Session retrieval: Success")
            else:
                print(f"❌ Session retrieval failed: {session_response.status_code}")
                
        else:
            print(f"❌ Bug injection failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Bug injection error: {e}")
    
    print()

def test_github_endpoints():
    """Test GitHub integration endpoints."""
    print("🔗 Testing GitHub Integration Endpoints...")
    
    # Test PR comments extraction (using your real PR)
    owner = "bfalkowski"
    repo = "BadRep"
    pr_number = 1
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/github/prs/{owner}/{repo}/{pr_number}/comments")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Comment extraction: {data['total_comments']} comments")
            print(f"   Categories: {data['categories']}")
            print(f"   Findings: {len(data['findings'])}")
        else:
            print(f"❌ Comment extraction failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Comment extraction error: {e}")
    
    print()

def test_evaluation_endpoints():
    """Test evaluation endpoints."""
    print("📊 Testing Evaluation Endpoints...")
    
    # Test evaluation with our existing files
    evaluation_data = {
        "findings_file": "github_findings.json",
        "ground_truth_file": "ground_truth_clean.jsonl",
        "output_dir": "reports/evaluation_results",
        "strategies": ["exact_overlap", "line_range_overlap", "semantic_similarity"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/evaluate/findings", json=evaluation_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Evaluation: {data['precision']:.3f} precision, {data['recall']:.3f} recall")
            print(f"   F1 Score: {data['f1_score']:.3f}")
            print(f"   Session ID: {data['session_id']}")
            
            # Test getting the evaluation report
            session_id = data['session_id']
            report_response = requests.get(f"{BASE_URL}/api/v1/evaluate/reports/{session_id}")
            if report_response.status_code == 200:
                print(f"✅ Report retrieval: Success")
            else:
                print(f"❌ Report retrieval failed: {report_response.status_code}")
                
        else:
            print(f"❌ Evaluation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
    
    print()

def test_cleanup_endpoints():
    """Test cleanup endpoints."""
    print("🧹 Testing Cleanup Endpoints...")
    
    # Test repository cleanup (dry run)
    cleanup_data = {
        "retention_days": 7,
        "dry_run": True
    }
    
    owner = "bfalkowski"
    repo = "BadRep"
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/cleanup/repository/{owner}/{repo}", json=cleanup_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Repository cleanup: {data['total_deleted']} branches")
            print(f"   Retention: {data['retention_days']} days")
            print(f"   Status: {data['status']}")
        else:
            print(f"❌ Repository cleanup failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Repository cleanup error: {e}")
    
    print()

def test_learning_endpoints():
    """Test learning endpoints."""
    print("🧠 Testing Learning Endpoints...")
    
    # Test learning analysis
    session_id = "test_session_123"
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/learning/analyze-session/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Learning analysis: {data['status']}")
            print(f"   Message: {data['message']}")
        else:
            print(f"❌ Learning analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Learning analysis error: {e}")
    
    print()

def main():
    """Run all API tests."""
    print("🚀 ReviewLab API Server Test Suite")
    print("=" * 50)
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running and responding")
            print()
        else:
            print("❌ API server responded with error")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running with: python core/api_server.py")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    # Run all tests
    test_health_endpoints()
    test_bug_injection_endpoints()
    test_github_endpoints()
    test_evaluation_endpoints()
    test_cleanup_endpoints()
    test_learning_endpoints()
    
    print("🎉 API test suite completed!")
    print()
    print("📖 API Documentation available at:")
    print(f"   {BASE_URL}/docs")
    print(f"   {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
