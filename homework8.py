
from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


# ---------- Fields ----------

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")
            if birthday.strftime("%d.%m.%Y") != value:
                raise ValueError
        except ValueError:
            raise ValueError("Birthday must use DD.MM.YYYY format.")
        super().__init__(value)


# ---------- Record ----------

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        found = self.find_phone(phone)
        if found is None:
            raise ValueError("Phone not found.")
        self.phones.remove(found)

    def edit_phone(self, old_phone, new_phone):
        found = self.find_phone(old_phone)
        if found is None:
            raise ValueError("Phone not found.")
        new_phone_obj = Phone(new_phone)
        found.value = new_phone_obj.value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "No phones"
        result = f"Contact: {self.name.value}, phones: {phones}"
        if self.birthday:
            result += f", birthday: {self.birthday}"
        return result


# ---------- Address Book ----------

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise ValueError("Contact not found.")
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            try:
                next_birthday = birthday.replace(year=today.year)
            except ValueError:
                next_birthday = date(today.year, 2, 28)

            if next_birthday < today:
                try:
                    next_birthday = next_birthday.replace(
                        year=today.year + 1
                    )
                except ValueError:
                    next_birthday = date(today.year + 1, 2, 28)

            days_until = (next_birthday - today).days

            if 0 <= days_until <= 7:
                congratulation_date = next_birthday

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime(
                        "%d.%m.%Y"
                    )
                })

        return upcoming

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


# ---------- Serialization ----------

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()


# ---------- Error Handling ----------

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Please provide all required arguments."
        except KeyError:
            return "Contact not found."
        except ValueError as error:
            return f"Error: {error}"
        except TypeError:
            return "Invalid command arguments."

    return wrapper


# ---------- Command Handlers ----------

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Contact {name} added."

    record.add_phone(phone)
    return f"Phone added to contact {name}."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for {name}."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)

    if record is None:
        return "Contact not found."

    phones = "; ".join(p.value for p in record.phones)
    return phones or "No phones saved."


def show_all_contacts(book):
    return str(book)


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)

    if record is None:
        return "Contact not found."

    record.add_birthday(birthday)
    return f"Birthday added for {name}: {record.birthday}"


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)

    if record is None:
        return "Contact not found."

    if record.birthday is None:
        return f"No birthday saved for {name}."

    return f"{name}'s birthday: {record.birthday}"


def birthdays(book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    return "\n".join(
        f"{item['name']}: {item['congratulation_date']}"
        for item in upcoming
    )


# ---------- Input Parsing ----------

def parse_input(user_input):
    parts = user_input.strip().split()

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]
    return command, args


# ---------- Main ----------

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        try:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)

            if command in ("close", "exit"):
                save_data(book)
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_contact(args, book))

            elif command == "phone":
                print(show_phone(args, book))

            elif command == "all":
                print(show_all_contacts(book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                if args:
                    print("The birthdays command does not need arguments.")
                else:
                    print(birthdays(book))

            elif command == "":
                continue

            else:
                print("Invalid command. Try again.")

        except (EOFError, KeyboardInterrupt):
            save_data(book)
            print("\nGood bye!")
            break


if __name__ == "__main__":
    main()
