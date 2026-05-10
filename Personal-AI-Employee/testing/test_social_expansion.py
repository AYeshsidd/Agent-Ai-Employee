#!/usr/bin/env python3
"""Test Twitter/Facebook Integration"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

print('=== Testing Twitter/Facebook Integration ===\n')

# Test 1: Import watcher skills
print('[TEST 1] Importing watcher skills...')
try:
    from skills.watcher_skills.twitter_watcher_skill import TwitterWatcherSkill
    from skills.watcher_skills.facebook_watcher_skill import FacebookWatcherSkill
    print('[PASS] Watcher skills imported')
except Exception as e:
    print(f'[FAIL] Watcher skills import failed: {e}')

# Test 2: Import agent skills
print('\n[TEST 2] Importing agent skills...')
try:
    from skills.twitter_agent_skill import TwitterAgentSkill
    from skills.facebook_agent_skill import FacebookAgentSkill
    print('[PASS] Agent skills imported')
except Exception as e:
    print(f'[FAIL] Agent skills import failed: {e}')

# Test 3: Import and test SocialModule
print('\n[TEST 3] Testing SocialModule...')
try:
    from mcp_server.modules.social_module import SocialModule
    social = SocialModule()
    tools = social.get_tool_names()
    print(f'[PASS] SocialModule loaded with {len(tools)} tools')
    for tool in tools:
        print(f'       - {tool}')
except Exception as e:
    print(f'[FAIL] SocialModule test failed: {e}')

# Test 4: Test MCP Server integration
print('\n[TEST 4] Testing MCP Server integration...')
try:
    from mcp_server import get_server
    server = get_server()
    all_tools = server.list_tools()
    twitter_tools = [t for t in all_tools if 'twitter' in t.get('name', '').lower()]
    facebook_tools = [t for t in all_tools if 'facebook' in t.get('name', '').lower()]
    print(f'[PASS] MCP Server has {len(twitter_tools)} Twitter tools, {len(facebook_tools)} Facebook tools')
except Exception as e:
    print(f'[FAIL] MCP Server test failed: {e}')

# Test 5: Test backward compatibility
print('\n[TEST 5] Testing backward compatibility...')
try:
    from mcp_server import get_server
    server = get_server()
    # Test legacy tools still work
    result = server.call_tool("send_notification", {
        "title": "Backward Compatibility Test",
        "message": "Testing that existing functionality still works"
    })
    if result.get("status") == "success":
        print('[PASS] Legacy send_notification still works')
    else:
        print(f'[WARN] send_notification returned: {result}')
except Exception as e:
    print(f'[FAIL] Backward compatibility test failed: {e}')

print('\n=== All Tests Complete ===')
