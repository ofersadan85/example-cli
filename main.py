from pathlib import Path
import json
import httpx
from argparse import ArgumentParser, Namespace
 
def get_example_users():
    users = [
        {"id": 3, "name": "Alice"},
        {"id": 1, "name": "Bob"},
        {"id": 2, "name": "Charlie"},
    ]
    return users

def delete_user_files(keep_ids: list[int], users_folder: Path):
    keep_ids_str = []
    for id in keep_ids:
        keep_ids_str.append(str(id))
    for file in users_folder.glob("*.json"):
        user_id = file.name.split("_")[0].lstrip("0")
        if user_id not in keep_ids_str:
            file.unlink(True)
 
def get_real_users(ids: list[int], delete: bool, users_folder: Path) -> list[dict]:
    if len(ids) == 0:
        response = httpx.get("https://jsonplaceholder.typicode.com/users")
        users = response.json()
    else:
        users = []
        for user_id in ids:
            try:
                response = httpx.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
                user = response.json()
                if user == {}:
                    raise ValueError("The user returned was empty")
                users.append(user)
            except (httpx.HTTPError, ValueError):
                print(f"Warning: could not download user id {user_id}")
        if delete:
            delete_user_files(ids, users_folder)
    return users
 
def create_user_file(user: dict, users_folder: Path, args: Namespace):
    if args.save:
        users_folder.mkdir(exist_ok=True)
        filename = f"{user['id']:003}_{user['username']}_{user['name'].split()[0]}.json"
        file_path = users_folder / filename
        user_json = json.dumps(user)
        file_path.write_text(user_json)
    if args.print:
        print(f"Got data for user id {user['id']}")
   
def send_new_user(new_user: dict) -> dict:
    response = httpx.post("https://jsonplaceholder.typicode.com/users", json=new_user)
    user = response.json()
    return user
   
def read_user_file(id: int, users_folder: Path):
    file_list = list(users_folder.glob(f"*{id}_*.json"))
    if len(file_list) == 0:
        print(f"No file found for id {id}")
    for file in file_list:
        print(file)
        try:
            print(file.read_text())
        except (FileNotFoundError, PermissionError) as err:
            print(f"Could not open {file}: {err}")
   
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("action", choices=["get", "create", "read"], help="The action we want to execute")
    parser.add_argument("--username", help="Your username")
    parser.add_argument("--email", help="A valid email address")
    parser.add_argument("--name", help="Your full name")
    parser.add_argument("--max", type=int, help="Maximum number of users to save")
   
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--no-print", action="store_false", dest="print")
   
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("--id", action="append", default=[], type=int)
    parser.add_argument("--delete", action="store_true")

    args = parser.parse_args()
    print(args)
   
    users_folder = Path("users")
 
    if args.action == "get":
        if args.verbose >= 1:
            print("Getting users")
        if args.verbose >= 2:
            print(f"Up to maximum of {args.max}")
        users = get_real_users(args.id, args.delete, users_folder)
        for user in users[:args.max]:
            try:
                create_user_file(user, users_folder, args)
            except PermissionError:
                print(f"Warning: could not save user {user}")
 
    if args.action == "create":
        if args.username is None or args.email is None or args.name is None:
            parser.print_usage()
            exit("when using create you must also specify --username, --email and --name")
       
        user = send_new_user({"username": args.username, "email": args.email, "name": args.name})
        try:
            create_user_file(user, users_folder, args)
        except PermissionError:
            print(f"Warning: could not save user {user}")
            
    if args.action == "read":
        for id in args.id:
            read_user_file(id, users_folder)
 