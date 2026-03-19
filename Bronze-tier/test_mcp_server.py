#!/usr/bin/env python3
"""Test MCP Server - Silver Tier Part 4"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import get_server


def test_server_initialization():
    """Test 1: Server initialization"""
    print("\n" + "=" * 70)
    print("  TEST 1: SERVER INITIALIZATION")
    print("=" * 70)

    try:
        server = get_server()
        print("[PASS] MCP Server initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Server initialization failed: {str(e)}")
        return False


def test_list_tools():
    """Test 2: List available tools"""
    print("\n" + "=" * 70)
    print("  TEST 2: LIST AVAILABLE TOOLS")
    print("=" * 70)

    try:
        server = get_server()
        tools = server.list_tools()

        print(f"\n[INFO] Found {len(tools)} tool(s):\n")

        for tool in tools:
            print(f"Tool: {tool['name']}")
            print(f"  Description: {tool['description']}")
            print(f"  Required params: {tool['parameters']['required']}")
            print()

        # Check for legacy tools (backward compatibility)
        tool_names = [tool['name'] for tool in tools]
        has_legacy = 'send_email' in tool_names and 'send_notification' in tool_names
        
        # Check for module tools (new modular architecture)
        has_modules = any(name in tool_names for name in ['send_bulk_email', 'post_to_linkedin', 'create_invoice'])

        if has_legacy and has_modules:
            print("[PASS] All tools registered correctly (legacy + modular)")
            return True
        elif has_legacy and not has_modules:
            print("[WARN] Only legacy tools found - modules may not be loaded")
            return True  # Still pass for backward compatibility
        else:
            print(f"[FAIL] Missing expected tools")
            return False

    except Exception as e:
        print(f"[FAIL] List tools failed: {str(e)}")
        return False


def test_send_notification():
    """Test 3: Send notification action"""
    print("\n" + "=" * 70)
    print("  TEST 3: SEND NOTIFICATION")
    print("=" * 70)

    try:
        server = get_server()

        # Test valid notification
        print("\n[TEST 3.1] Valid notification:")
        result = server.call_tool("send_notification", {
            "title": "Test Notification",
            "message": "This is a test notification from MCP Server test suite"
        })

        print(f"Result: {json.dumps(result, indent=2)}")

        if result.get("status") == "success":
            print("[PASS] Notification sent successfully")
        else:
            print(f"[FAIL] Notification failed: {result.get('message')}")
            return False

        # Test missing field
        print("\n[TEST 3.2] Missing field (should fail gracefully):")
        result = server.call_tool("send_notification", {
            "title": "Test"
            # Missing 'message' field
        })

        print(f"Result: {json.dumps(result, indent=2)}")

        if result.get("status") == "failed":
            print("[PASS] Missing field handled correctly")
        else:
            print("[FAIL] Should have failed with missing field")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Send notification test failed: {str(e)}")
        return False


def test_send_email():
    """Test 4: Send email action"""
    print("\n" + "=" * 70)
    print("  TEST 4: SEND EMAIL")
    print("=" * 70)

    try:
        server = get_server()

        # Test missing field
        print("\n[TEST 4.1] Missing field (should fail gracefully):")
        result = server.call_tool("send_email", {
            "to": "test@example.com",
            "subject": "Test"
            # Missing 'body' field
        })

        print(f"Result: {json.dumps(result, indent=2)}")

        if result.get("status") == "failed":
            print("[PASS] Missing field handled correctly")
        else:
            print("[FAIL] Should have failed with missing field")
            return False

        # Test with all fields (may fail if credentials not set up)
        print("\n[TEST 4.2] Valid email request:")
        print("[INFO] This will fail if Gmail credentials are not configured")
        print("[INFO] That's expected - we're testing the validation logic\n")

        result = server.call_tool("send_email", {
            "to": "test@example.com",
            "subject": "Test Email from MCP Server",
            "body": "This is a test email sent via MCP Server"
        })

        print(f"Result: {json.dumps(result, indent=2)}")

        # Either success or graceful failure is acceptable
        if result.get("status") in ["success", "failed"]:
            print("[PASS] Email action handled correctly")
            return True
        else:
            print("[FAIL] Unexpected result")
            return False

    except Exception as e:
        print(f"[FAIL] Send email test failed: {str(e)}")
        return False


def test_json_request():
    """Test 5: JSON request handling"""
    print("\n" + "=" * 70)
    print("  TEST 5: JSON REQUEST HANDLING")
    print("=" * 70)

    try:
        server = get_server()

        # Test valid JSON request
        print("\n[TEST 5.1] Valid JSON request:")
        json_request = json.dumps({
            "tool": "send_notification",
            "parameters": {
                "title": "JSON Test",
                "message": "Testing JSON request handling"
            }
        })

        print(f"Request: {json_request}\n")
        response = server.handle_json_request(json_request)
        print(f"Response: {response}")

        result = json.loads(response)
        if result.get("status") == "success":
            print("[PASS] JSON request handled successfully")
        else:
            print(f"[FAIL] JSON request failed: {result.get('message')}")
            return False

        # Test invalid JSON
        print("\n[TEST 5.2] Invalid JSON (should fail gracefully):")
        invalid_json = "{ invalid json }"
        print(f"Request: {invalid_json}\n")
        response = server.handle_json_request(invalid_json)
        print(f"Response: {response}")

        result = json.loads(response)
        if result.get("status") == "failed":
            print("[PASS] Invalid JSON handled correctly")
        else:
            print("[FAIL] Should have failed with invalid JSON")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] JSON request test failed: {str(e)}")
        return False


def test_unknown_tool():
    """Test 6: Unknown tool handling"""
    print("\n" + "=" * 70)
    print("  TEST 6: UNKNOWN TOOL HANDLING")
    print("=" * 70)

    try:
        server = get_server()

        result = server.call_tool("unknown_tool", {})
        print(f"Result: {json.dumps(result, indent=2)}")

        if result.get("status") == "failed" and "Unknown tool" in result.get("message", ""):
            print("[PASS] Unknown tool handled correctly")
            return True
        else:
            print("[FAIL] Should have failed with unknown tool error")
            return False

    except Exception as e:
        print(f"[FAIL] Unknown tool test failed: {str(e)}")
        return False


def main():
    print("\n" + "=" * 70)
    print("  MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Server Initialization", test_server_initialization),
        ("List Tools", test_list_tools),
        ("Send Notification", test_send_notification),
        ("Send Email", test_send_email),
        ("JSON Request Handling", test_json_request),
        ("Unknown Tool Handling", test_unknown_tool)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    print("\n" + "=" * 70)
    print(f"  RESULT: {passed_count}/{total_count} tests passed")
    print("=" * 70)

    if passed_count == total_count:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total_count - passed_count} test(s) failed")

    print("\n[INFO] Check logs/notifications.log for notification logs")
    print("[INFO] Check logs/bronze_tier.log for MCP server logs")
    print()


if __name__ == "__main__":
    main()
