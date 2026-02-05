from pathlib import Path
from main import create_user_file, delete_user_files, get_real_users, send_new_user, read_user_file
from argparse import Namespace

users_folder = Path("users")

def test_delete():
    fake_args = Namespace(save=True, print=False)
    users = get_real_users([1, 2, 3, 4], False, users_folder)
    assert len(users) == 4
    for user in users:
        create_user_file(user, users_folder, fake_args)
    delete_user_files([3, 4], users_folder)
    user_files = list(users_folder.glob("*.json"))
    assert len(user_files) == 2
    for file in user_files:
        user_id = file.name.split("_")[0].lstrip("0")
        assert user_id in ["3", "4"]
        
        
# TODO: Write more tests for each function
