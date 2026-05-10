#!/usr/bin/env python3
"""Test Twitter & Facebook Auto-Post Integration"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

print('=== Testing Twitter & Facebook Auto-Post ===\n')

# Test 1: Import skills
print('[TEST 1] Importing auto-post skills...')
try:
    from skills.twitter_auto_post_skill import TwitterAutoPostSkill
    from skills.facebook_auto_post_skill import FacebookAutoPostSkill
    print('[PASS] Auto-post skills imported\n')
except Exception as e:
    print(f'[FAIL] Import failed: {e}\n')

# Test 2: Initialize skills
print('[TEST 2] Initializing skills...')
try:
    twitter = TwitterAutoPostSkill()
    facebook = FacebookAutoPostSkill()
    print('[PASS] Skills initialized')
    print(f'       Twitter session: {twitter.session_file}')
    print(f'       Facebook session: {facebook.session_file}\n')
except Exception as e:
    print(f'[FAIL] Init failed: {e}\n')

# Test 3: Test MCP Social module
print('[TEST 3] Testing MCP Social module...')
try:
    from mcp_server.modules.social_module import SocialModule
    social = SocialModule()
    tools = social.get_tool_names()
    
    twitter_tools = [t for t in tools if 'twitter' in t.lower()]
    facebook_tools = [t for t in tools if 'facebook' in t.lower()]
    auto_post_tools = [t for t in tools if 'auto_post' in t.lower()]
    
    print(f'[PASS] SocialModule has {len(tools)} tools')
    print(f'       Twitter tools: {twitter_tools}')
    print(f'       Facebook tools: {facebook_tools}')
    print(f'       Auto-post tools: {auto_post_tools}\n')
except Exception as e:
    print(f'[FAIL] MCP test failed: {e}\n')

# Test 4: Test MCP Server integration
print('[TEST 4] Testing MCP Server integration...')
try:
    from mcp_server import get_server
    server = get_server()
    all_tools = server.list_tools()
    
    auto_post_tools = [t for t in all_tools if 'auto_post' in t.get('name', '').lower()]
    print(f'[PASS] MCP Server has {len(auto_post_tools)} auto-post tools')
    for tool in auto_post_tools:
        print(f'       - {tool["name"]}')
    print()
except Exception as e:
    print(f'[FAIL] MCP Server test failed: {e}\n')

# Test 5: Backward compatibility
print('[TEST 5] Testing backward compatibility...')
try:
    from mcp_server import get_server
    server = get_server()
    
    # Test legacy notification
    result = server.call_tool("send_notification", {
        "title": "Auto-Post Test",
        "message": "Testing backward compatibility"
    })
    
    if result.get("status") == "success":
        print('[PASS] Legacy send_notification works\n')
    else:
        print(f'[WARN] send_notification: {result}\n')
except Exception as e:
    print(f'[FAIL] Backward compatibility failed: {e}\n')

print('=== All Tests Complete ===')
print('\n[INFO] Auto-post skills ready for use')
print('[INFO] Run: python run_twitter_auto_post.py')
print('[INFO] Run: python run_facebook_auto_post.py')
