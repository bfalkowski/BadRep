#!/usr/bin/env python3
"""
Test script for GitHub comment extraction.
"""

import os
import sys
from core.github_comments import extract_and_convert_comments, GitHubCommentExtractor, GitHubRepositoryManager

def main():
    """Test GitHub comment extraction."""
    
    # Check for GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ Please set GITHUB_TOKEN environment variable")
        print("   export GITHUB_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Repository details
    owner = "bfalkowski"
    repo = "BadRep"
    
    print(f"🔍 Testing GitHub comment extraction for {owner}/{repo}")
    print(f"🔑 Using GitHub token: {github_token[:8]}...")
    print()
    
    # Test branch status
    print("📋 Testing branch management...")
    repo_manager = GitHubRepositoryManager(github_token)
    
    try:
        # Check main branch
        main_status = repo_manager.get_branch_status(owner, repo, "main")
        print(f"✅ Main branch: {main_status.name} (exists: {main_status.exists}, protected: {main_status.protection_enabled})")
        
        # Check bug injection branch
        bug_branch_status = repo_manager.get_branch_status(owner, repo, "bug-injection-demo")
        print(f"✅ Bug injection branch: {bug_branch_status.name} (exists: {bug_branch_status.exists})")
        
        if bug_branch_status.exists:
            print(f"   Last commit: {bug_branch_status.last_commit[:8] if bug_branch_status.last_commit else 'Unknown'}")
        
    except Exception as e:
        print(f"❌ Error checking branch status: {e}")
    
    print()
    
    # Test comment extraction (we'll need to find the PR number)
    print("🔍 Testing comment extraction...")
    print("   Note: We need to find the PR number for the bug-injection-demo branch")
    
    try:
        # For now, let's test with a simple extraction
        extractor = GitHubCommentExtractor(github_token)
        
        # Get repository info
        github = extractor.github
        repo_obj = github.get_repo(f"{owner}/{repo}")
        
        print(f"✅ Repository: {repo_obj.name}")
        print(f"✅ Description: {repo_obj.description or 'No description'}")
        print(f"✅ Language: {repo_obj.language or 'Unknown'}")
        print(f"✅ Stars: {repo_obj.stargazers_count}")
        print(f"✅ Forks: {repo_obj.forks_count}")
        
        # Look for PRs
        print("\n🔍 Looking for pull requests...")
        prs = repo_obj.get_pulls(state='all')
        pr_count = 0
        
        for pr in prs:
            pr_count += 1
            print(f"   PR #{pr.number}: {pr.title} ({pr.state})")
            print(f"      Branch: {pr.head.ref} → {pr.base.ref}")
            print(f"      Created: {pr.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Comments: {pr.comments}")
            print(f"      Review comments: {pr.review_comments}")
            
            # If this is our bug injection PR, test comment extraction
            if "bug-injection" in pr.head.ref:
                print(f"\n🎯 Found our bug injection PR! Testing comment extraction...")
                
                try:
                    comments = extractor.extract_pr_comments(owner, repo, pr.number)
                    print(f"✅ Extracted {len(comments)} comments")
                    
                    if comments:
                        print("\n📝 Comment details:")
                        for i, comment in enumerate(comments[:5]):  # Show first 5
                            print(f"   {i+1}. [{comment.comment_type}] {comment.author}: {comment.body[:100]}...")
                        
                        # Convert to findings
                        findings = extractor.map_comment_to_findings(comments)
                        print(f"\n🔍 Converted to {len(findings)} findings:")
                        
                        for finding in findings:
                            print(f"   - {finding.category} ({finding.severity}): {finding.message[:80]}...")
                    
                except Exception as e:
                    print(f"❌ Error extracting comments: {e}")
                
                break
        
        if pr_count == 0:
            print("   No pull requests found")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
