"""
Test script to verify the default collection preference system works correctly.
"""
import json
import os

CONFIG_FILE = "user_preferences_test.json"

def load_user_preferences():
    """Load user preferences from JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return {}
    return {}

def save_user_preferences(preferences):
    """Save user preferences to JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False

def get_default_collection():
    """Get the default collection from preferences."""
    prefs = load_user_preferences()
    return prefs.get('default_collection', None)

def set_default_collection(collection_name):
    """Set the default collection in preferences."""
    prefs = load_user_preferences()
    prefs['default_collection'] = collection_name
    return save_user_preferences(prefs)

def clear_default_collection():
    """Clear the default collection preference."""
    prefs = load_user_preferences()
    if 'default_collection' in prefs:
        del prefs['default_collection']
    return save_user_preferences(prefs)

# Clean up any existing test file
if os.path.exists(CONFIG_FILE):
    os.remove(CONFIG_FILE)

print("=" * 60)
print("TESTING DEFAULT COLLECTION PREFERENCE SYSTEM")
print("=" * 60)

# Test 1: No default set initially
print("\n📋 Test 1: Get default when none is set")
result = get_default_collection()
print(f"   Result: {result}")
assert result is None, "Expected None when no default is set"
print("   ✅ PASSED")

# Test 2: Set a default collection
print("\n📋 Test 2: Set 'books' as default")
success = set_default_collection('books')
print(f"   Save successful: {success}")
assert success, "Failed to save preference"
result = get_default_collection()
print(f"   Retrieved: {result}")
assert result == 'books', f"Expected 'books', got {result}"
print("   ✅ PASSED")

# Test 3: Change default collection
print("\n📋 Test 3: Change default to 'midbooks'")
success = set_default_collection('midbooks')
print(f"   Save successful: {success}")
assert success, "Failed to save preference"
result = get_default_collection()
print(f"   Retrieved: {result}")
assert result == 'midbooks', f"Expected 'midbooks', got {result}"
print("   ✅ PASSED")

# Test 4: Clear default collection
print("\n📋 Test 4: Clear default collection")
success = clear_default_collection()
print(f"   Clear successful: {success}")
assert success, "Failed to clear preference"
result = get_default_collection()
print(f"   Retrieved: {result}")
assert result is None, f"Expected None after clearing, got {result}"
print("   ✅ PASSED")

# Test 5: Verify persistence (file exists and contains correct data)
print("\n📋 Test 5: Verify persistence across operations")
set_default_collection('newbooks')
# Read file directly
with open(CONFIG_FILE, 'r') as f:
    file_contents = json.load(f)
print(f"   File contents: {file_contents}")
assert file_contents.get('default_collection') == 'newbooks', "File doesn't contain correct data"
print("   ✅ PASSED")

# Clean up test file
os.remove(CONFIG_FILE)
print(f"\n🧹 Cleaned up test file: {CONFIG_FILE}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✅")
print("=" * 60)
