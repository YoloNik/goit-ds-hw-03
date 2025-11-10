import os
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from pprint import pprint
from dotenv import load_dotenv
from generate_random_cat import generate_random_cat

# === Load env var ===
load_dotenv()

# === MongoDB connection setup ===
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("Error: MONGO_URI not found in environment variables.")
    exit(1)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # test connection
    print("Connected to MongoDB successfully.")
except errors.ServerSelectionTimeoutError:
    print("Could not connect to MongoDB. Check your internet or .env file.")
    exit(1)

db = client["cats_db"]
cats_collection = db["cats"]

# === CRUD functions ===
# --- CREATE ---
def create_cat(name, age, features):
    try:
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be a positive integer.")
        if not isinstance(features, list) or not all(isinstance(f, str) for f in features):
            raise ValueError("Features must be a list of strings.")

        cat = {"name": name.strip().lower(), "age": age, "features": features}
        result = cats_collection.insert_one(cat)
        print(f"Cat inserted with _id: {result.inserted_id}")
    except ValueError as ve:
        print(f"Validation error: {ve}")
    except errors.ServerSelectionTimeoutError:
        print("Lost connection to MongoDB server.")
    except Exception as e:
        print(f"Error inserting cat: {e}")


# --- READ ---
def read_all_cats():
    try:
        cats = list(cats_collection.find())
        if not cats:
            print("⚠️ No cats found in the collection.")
            return
        for cat in cats:
            pprint(cat)
    except errors.ServerSelectionTimeoutError:
        print("Connection to MongoDB failed.")
    except Exception as e:
        print(f"Error reading cats: {e}")


def find_cat_by_name(name):
    try:
        if not name:
            raise ValueError("Cat name cannot be empty.")
        cat = cats_collection.find_one({"name": name.lower().strip()})
        if cat:
            pprint(cat)
        else:
            print(f"Cat with name '{name}' not found.")
    except ValueError as ve:
        print(f"{ve}")
    except errors.ServerSelectionTimeoutError:
        print("Lost connection to MongoDB.")
    except Exception as e:
        print(f"Error finding cat: {e}")


# --- UPDATE ---
def update_cat_age(name, new_age):
    try:
        if not name:
            raise ValueError("Name cannot be empty.")
        if not isinstance(new_age, int) or new_age < 0:
            raise ValueError("Age must be a positive integer.")

        result = cats_collection.update_one({"name": name.lower().strip()}, {"$set": {"age": new_age}})
        if result.modified_count > 0:
            print(f"Cat '{name}' age updated to {new_age}.")
        else:
            print(f"Cat '{name}' not found or age unchanged.")
    except ValueError as ve:
        print(f"{ve}")
    except errors.ServerSelectionTimeoutError:
        print("Connection to MongoDB lost.")
    except Exception as e:
        print(f"Error updating age: {e}")


def add_feature_to_cat(name, new_feature):
    try:
        if not name or not new_feature:
            raise ValueError("Name and feature must not be empty.")
        result = cats_collection.update_one({"name": name.lower().strip()}, {"$push": {"features": new_feature}})
        if result.modified_count > 0:
            print(f"Feature '{new_feature}' added to '{name}'.")
        else:
            print(f"Cat '{name}' not found.")
    except ValueError as ve:
        print(f"{ve}")
    except errors.ServerSelectionTimeoutError:
        print("Connection to MongoDB lost.")
    except Exception as e:
        print(f"Error adding feature: {e}")


# --- DELETE ---
def delete_cat_by_name(name):
    try:
        if not name:
            raise ValueError("Name cannot be empty.")
        result = cats_collection.delete_one({"name": name.lower().strip()})
        if result.deleted_count > 0:
            print(f"Cat '{name}' deleted.")
        else:
            print(f"Cat '{name}' not found.")
    except ValueError as ve:
        print(f"{ve}")
    except errors.ServerSelectionTimeoutError:
        print("Connection to MongoDB lost.")
    except Exception as e:
        print(f"Error deleting cat: {e}")


def delete_all_cats():
    try:
        count = cats_collection.count_documents({})
        if count == 0:
            print("Collection is already empty.")
            return
        result = cats_collection.delete_many({})
        print(f"Deleted {result.deleted_count} cat(s) from collection.")
    except errors.ServerSelectionTimeoutError:
        print("Connection to MongoDB lost.")
    except Exception as e:
        print(f"Error deleting all cats: {e}")


# === MENU ===
def menu():
    while True:
        print("\n=== CATS DATABASE MENU ===")
        print("1. Add a new cat")
        print("2. Show all cats")
        print("3. Find cat by name")
        print("4. Update cat age")
        print("5. Add new feature to cat")
        print("6. Delete cat by name")
        print("7. Delete all cats")
        print("8. Generate random cat")
        print("0. Exit")

        choice = input("Choose an option: ")

        try:
            if choice == "1":
                name = input("Enter cat name: ")
                age = int(input("Enter cat age: "))
                features = input("Enter features (comma separated): ").split(",")
                features = [f.strip() for f in features if f.strip()]
                create_cat(name, age, features)
            elif choice == "2":
                read_all_cats()
            elif choice == "3":
                name = input("Enter cat name: ")
                find_cat_by_name(name)
            elif choice == "4":
                name = input("Enter cat name: ")
                new_age = int(input("Enter new age: "))
                update_cat_age(name, new_age)
            elif choice == "5":
                name = input("Enter cat name: ")
                feature = input("Enter new feature: ")
                add_feature_to_cat(name, feature)
            elif choice == "6":
                name = input("Enter cat name to delete: ")
                delete_cat_by_name(name)
            elif choice == "7":
                confirm = input("Are you sure? (y/n): ").lower()
                if confirm == "y":
                    delete_all_cats()
            elif choice == "8":
                cat = generate_random_cat()
                create_cat(cat["name"], cat["age"], cat["features"])
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Try again.")
        except ValueError:
            print("Please enter valid numeric values where required.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    menu()
