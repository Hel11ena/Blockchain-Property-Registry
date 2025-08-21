from blockchain import PropertyRegistry

def main():
    registry = PropertyRegistry()

    while True:
        print("\n====== Blockchain Property Registry ======")
        print("1. Register new property")
        print("2. Transfer property")
        print("3. View property history")
        print("4. Check current owner")
        print("5. Validate blockchain")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            prop_id = input("Enter Property ID: ")
            owner = input("Enter Owner Name: ")
            location = input("Enter Location: ")
            area = input("Enter Area (sqft): ")
            survey = input("Enter Survey Number: ")
            registry.register_property(prop_id, owner, location, area, survey)

        elif choice == "2":
            prop_id = input("Enter Property ID: ")
            current_owner = input("Enter Current Owner: ")
            new_owner = input("Enter New Owner: ")
            note = input("Enter Note (optional): ")
            registry.transfer_property(prop_id, current_owner, new_owner, note)

        elif choice == "3":
            prop_id = input("Enter Property ID: ")
            registry.show_property_history(prop_id)

        elif choice == "4":
            prop_id = input("Enter Property ID: ")
            owner = registry.get_current_owner(prop_id)
            if owner:
                print(f"Current owner of '{prop_id}' is '{owner}'.")
            else:
                print("Property not found.")

        elif choice == "5":
            valid = registry.blockchain.validate_chain()
            print(f"[✓] Blockchain valid: {valid}")

        elif choice == "6":
            print("Exiting... Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
