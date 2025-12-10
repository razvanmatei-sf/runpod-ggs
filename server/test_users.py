# ABOUTME: Test suite for user management functionality
# ABOUTME: Tests user loading, saving, admin status, and the hardcoded Razvan rule

import json
import os
import shutil
import tempfile
import unittest

from user_management import (
    create_user_folder,
    ensure_razvan_exists,
    get_users_from_folders,
    is_admin_check,
    load_users_from_file,
    save_users_to_file,
)


class TestUserManagement(unittest.TestCase):
    """Tests for the user management system"""

    def setUp(self):
        """Create a temporary directory for test data"""
        self.test_dir = tempfile.mkdtemp()
        self.users_json_path = os.path.join(self.test_dir, "users.json")
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_razvan_always_admin(self):
        """Razvan Matei should always be an admin, regardless of JSON content"""
        # Even with empty admins list, Razvan should be admin
        self.assertTrue(is_admin_check("Razvan Matei", []))
        self.assertTrue(is_admin_check("razvan matei", []))  # Case insensitive
        self.assertTrue(is_admin_check("RAZVAN MATEI", []))

    def test_razvan_always_in_users(self):
        """Razvan Matei should always be in the users list"""
        users = []
        result = ensure_razvan_exists(users)
        self.assertIn("Razvan Matei", [u["name"] for u in result])

        # Should also be marked as admin
        razvan = next(u for u in result if u["name"] == "Razvan Matei")
        self.assertTrue(razvan["is_admin"])

    def test_razvan_not_duplicated(self):
        """If Razvan already exists, don't duplicate"""
        users = [{"name": "Razvan Matei", "is_admin": True}]
        result = ensure_razvan_exists(users)
        razvan_count = sum(1 for u in result if u["name"] == "Razvan Matei")
        self.assertEqual(razvan_count, 1)

    def test_load_users_from_json(self):
        """Should load users from JSON file"""
        test_users = [
            {"name": "Alice", "is_admin": False},
            {"name": "Bob", "is_admin": True},
        ]
        with open(self.users_json_path, "w") as f:
            json.dump({"users": test_users}, f)

        result = load_users_from_file(self.users_json_path)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alice")

    def test_load_users_missing_file(self):
        """Should return empty list if JSON doesn't exist"""
        result = load_users_from_file("/nonexistent/path.json")
        self.assertEqual(result, [])

    def test_save_users_to_json(self):
        """Should save users to JSON file"""
        test_users = [
            {"name": "Alice", "is_admin": False},
            {"name": "Bob", "is_admin": True},
        ]
        save_users_to_file(test_users, self.users_json_path)

        with open(self.users_json_path) as f:
            data = json.load(f)

        # Should have 3 users (Alice, Bob, and Razvan who is auto-added)
        self.assertEqual(len(data["users"]), 3)
        names = [u["name"] for u in data["users"]]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Razvan Matei", names)

    def test_get_users_from_folders(self):
        """Should discover users from output folder structure"""
        # Create some user folders
        os.makedirs(os.path.join(self.output_dir, "Alice"))
        os.makedirs(os.path.join(self.output_dir, "Bob"))
        os.makedirs(os.path.join(self.output_dir, "Charlie"))

        result = get_users_from_folders(self.output_dir)
        self.assertEqual(sorted(result), ["Alice", "Bob", "Charlie"])

    def test_get_users_from_folders_ignores_files(self):
        """Should only return directories, not files"""
        os.makedirs(os.path.join(self.output_dir, "Alice"))
        # Create a file that should be ignored
        with open(os.path.join(self.output_dir, "some_file.txt"), "w") as f:
            f.write("test")

        result = get_users_from_folders(self.output_dir)
        self.assertEqual(result, ["Alice"])

    def test_create_user_folder(self):
        """Should create folder when adding user"""
        create_user_folder("New User", self.output_dir)
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "New User")))

    def test_regular_admin_check(self):
        """Regular users should be checked against admin list"""
        admins = ["Alice", "Bob"]
        self.assertTrue(is_admin_check("Alice", admins))
        self.assertTrue(is_admin_check("alice", admins))  # Case insensitive
        self.assertFalse(is_admin_check("Charlie", admins))

    def test_non_admin_user(self):
        """Non-admin users should return False"""
        self.assertFalse(is_admin_check("Random Person", []))
        self.assertFalse(is_admin_check("Random Person", ["Someone Else"]))


if __name__ == "__main__":
    unittest.main()
