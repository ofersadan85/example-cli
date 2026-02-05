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
 
def get_real_users(ids: list[int]) -> list[dict]:
    if len(ids) == 0:
        response = httpx.get("https://jsonplaceholder.typicode.com/users")
        users = response.json()
    else:
        users = []
        for user_id in ids:
            response = httpx.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
            user = response.json()
            users.append(user)
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
   
   
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("action", choices=["get", "create"], help="The action we want to execute [get or create]")
    parser.add_argument("--username", help="Your username")
    parser.add_argument("--email", help="A valid email address")
    parser.add_argument("--name", help="Your full name")
    parser.add_argument("--max", type=int, help="Maximum number of users to save")
   
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--no-print", action="store_false", dest="print")
   
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("--id", action="append", default=[], type=int)
   
    # Accept --delete flag / argument
    # If it is there, delete all the files that aren't currently saved
    # For example, python cli.py --id 2 --id 7 --save --delete
    # Will save the files for users 2 and 7 but delete all other files in that folder
    # Delete with Path("somefile.txt").unlink()
    # You can search files with Path("users").glob("*.json")
    # BE CAREFUL - don't delete files if you're not sure
   
    # Add try except blocks around each network request (httpx.get and httpx.post)
    # Also handle cases where the status is not 200-299 in the same way
    # When errors occur, skip that file / user and continue
    # Example `python cli.py get --id 4 --id 18 --id 2`
   
    # Optional: Also handle file errors (file not found and permission errors)
    # For this, let's add another command to get/create => read
    # Example 'python cli.py read --id 5 --id 8`
 
    # Create tests for every function
     
       
    args = parser.parse_args()
    print(args)
   
    users_folder = Path("users")
 
    if args.action == "get":
        if args.verbose >= 1:
            print("Getting users")
        if args.verbose >= 2:
            print(f"Up to maximum of {args.max}")
        users = get_real_users(args.id)
        for user in users[:args.max]:
            create_user_file(user, users_folder, args)
 
    if args.action == "create":
        if args.username is None or args.email is None or args.name is None:
            parser.print_usage()
            exit("when using create you must also specify --username, --email and --name")
       
        user = send_new_user({"username": args.username, "email": args.email, "name": args.name})
        create_user_file(user, users_folder, args)