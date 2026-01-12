# ABOUTME: Core user management logic for dynamic user profiles
# ABOUTME: Handles loading, saving, and managing users independently of Flask

import json
import os

# Hardcoded superadmin - always exists, always admin
SUPERADMIN_NAME = "Razvan Matei"

# Default paths (can be overridden in function calls)
DEFAULT_USERS_JSON = "/workspace/users.json"
DEFAULT_OUTPUT_DIR = "/workspace/ComfyUI/output"


def is_admin_check(user_name, admins_list):
    """
    Check if user is an admin (case-insensitive).
    Razvan Matei is ALWAYS admin regardless of the list.
    """
    if not user_name:
        return False

    user_lower = user_name.strip().lower()

    # Razvan is always admin
    if user_lower == SUPERADMIN_NAME.lower():
        return True

    # Check against provided admins list
    return any(admin.strip().lower() == user_lower for admin in admins_list)


def ensure_razvan_exists(users):
    """
    Ensure Razvan Matei is always in the users list and marked as admin.
    Returns the modified users list.
    """
    razvan_exists = any(
        u["name"].strip().lower() == SUPERADMIN_NAME.lower() for u in users
    )

    if not razvan_exists:
        users.append({"name": SUPERADMIN_NAME, "is_admin": True})
    else:
        # Make sure Razvan is marked as admin even if someone tried to change it
        for user in users:
            if user["name"].strip().lower() == SUPERADMIN_NAME.lower():
                user["is_admin"] = True
                break

    return users


def load_users_from_file(json_path=DEFAULT_USERS_JSON):
    """
    Load users from JSON file.
    Returns empty list if file doesn't exist or is invalid.
    """
    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            return data.get("users", [])
    except (json.JSONDecodeError, IOError):
        return []


def save_users_to_file(users, json_path=DEFAULT_USERS_JSON):
    """
    Save users list to JSON file.
    Creates parent directories if needed.
    """
    # Ensure Razvan is always present and admin before saving
    users = ensure_razvan_exists(users)

    # Create parent directory if needed
    parent_dir = os.path.dirname(json_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(json_path, "w") as f:
        json.dump({"users": users}, f, indent=2)


def get_users_from_folders(output_dir=DEFAULT_OUTPUT_DIR):
    """
    Discover users from output folder structure.
    Returns list of folder names (user names).
    Only returns directories, not files.
    """
    if not os.path.exists(output_dir):
        return []

    return sorted(
        [
            name
            for name in os.listdir(output_dir)
            if os.path.isdir(os.path.join(output_dir, name))
        ]
    )


def create_user_folder(user_name, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Create a folder for a user in the output directory.
    """
    folder_path = os.path.join(output_dir, user_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def get_admins_list(users):
    """
    Extract list of admin names from users list.
    Always includes Razvan Matei.
    """
    admins = [u["name"] for u in users if u.get("is_admin", False)]

    # Ensure Razvan is always in admins
    if SUPERADMIN_NAME not in admins:
        admins.append(SUPERADMIN_NAME)

    return admins


def initialize_users(json_path=DEFAULT_USERS_JSON, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Initialize users system.
    If JSON exists, load from it.
    If not, scan folders and create initial JSON.
    Always ensures Razvan Matei exists.
    Returns tuple: (users_list, admins_list)
    """
    users = load_users_from_file(json_path)

    if not users:
        # No JSON file - scan folders for existing users
        folder_names = get_users_from_folders(output_dir)
        users = [{"name": name, "is_admin": False} for name in folder_names]

    # Always ensure Razvan exists and is admin
    users = ensure_razvan_exists(users)

    # Save to ensure JSON file exists
    save_users_to_file(users, json_path)

    admins = get_admins_list(users)
    return users, admins


def add_users_bulk(
    names_text, json_path=DEFAULT_USERS_JSON, output_dir=DEFAULT_OUTPUT_DIR
):
    """
    Add multiple users from text (one name per line).
    Creates folders and updates JSON.
    Returns the updated users list.
    """
    # Parse names from text
    new_names = [
        name.strip() for name in names_text.strip().split("\n") if name.strip()
    ]

    # Load existing users
    users = load_users_from_file(json_path)
    existing_names = {u["name"].strip().lower() for u in users}

    # Add new users
    for name in new_names:
        if name.strip().lower() not in existing_names:
            users.append({"name": name, "is_admin": False})
            existing_names.add(name.strip().lower())

        # Create folder for user
        create_user_folder(name, output_dir)

    # Also create folders for any existing users that might not have them
    for user in users:
        create_user_folder(user["name"], output_dir)

    # Save and return
    save_users_to_file(users, json_path)
    return users


def toggle_user_admin(user_name, json_path=DEFAULT_USERS_JSON):
    """
    Toggle admin status for a user.
    Razvan Matei cannot be demoted.
    Returns the updated users list.
    """
    users = load_users_from_file(json_path)

    for user in users:
        if user["name"].strip().lower() == user_name.strip().lower():
            # Don't allow demoting Razvan
            if user["name"].strip().lower() == SUPERADMIN_NAME.lower():
                user["is_admin"] = True
            else:
                user["is_admin"] = not user.get("is_admin", False)
            break

    save_users_to_file(users, json_path)
    return users


def set_user_admin(user_name, is_admin, json_path=DEFAULT_USERS_JSON):
    """
    Set admin status for a user to a specific value.
    Razvan Matei is always kept as admin.
    Returns the updated users list.
    """
    users = load_users_from_file(json_path)

    for user in users:
        if user["name"].strip().lower() == user_name.strip().lower():
            # Don't allow demoting Razvan
            if user["name"].strip().lower() == SUPERADMIN_NAME.lower():
                user["is_admin"] = True
            else:
                user["is_admin"] = is_admin
            break

    save_users_to_file(users, json_path)
    return users


def delete_user(
    user_name,
    json_path=DEFAULT_USERS_JSON,
    delete_folder=False,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    """
    Delete a user from the system.
    Razvan Matei cannot be deleted.
    Optionally deletes the user's folder.
    Returns the updated users list.
    """
    # Don't allow deleting Razvan
    if user_name.strip().lower() == SUPERADMIN_NAME.lower():
        users = load_users_from_file(json_path)
        return ensure_razvan_exists(users)

    users = load_users_from_file(json_path)
    users = [u for u in users if u["name"].strip().lower() != user_name.strip().lower()]

    # Optionally delete folder
    if delete_folder:
        import shutil

        folder_path = os.path.join(output_dir, user_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    save_users_to_file(users, json_path)
    return users


def get_all_user_names(json_path=DEFAULT_USERS_JSON):
    """
    Get sorted list of all user names.
    """
    users = load_users_from_file(json_path)
    users = ensure_razvan_exists(users)
    return sorted([u["name"] for u in users])
