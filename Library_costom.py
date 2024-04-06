import time
import os

class Users:
    def __init__(self, username, password, firstname, lastname):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.role = "normal_user"

    def save_user(self):
        user = "{},{},{},{},{}".format(self.username, self.password, self.firstname, self.lastname, self.role)
        with open("users.txt", "r+") as users:
            all_users = users.read()
            if self.username not in all_users:
                users.write(user+"\n")
                print("\n---user successfully registered---\n")
            else:
                print("\nusername already exists...\n")
            users.close()

    
class Admin(Users):
    def __init__(self, username, password, firstname, lastname):
        super().__init__(username, password, firstname, lastname)
        self.role = "Admin"


class Library:
    def __init__(self):
        self.books = {}
        self.users = {}
        self.users_change_status = None # False: if no recent changes in users file. True if some changes in users file
        self.load_data()
    
    def load_data(self):
        with open("users.txt", "r") as users:
            for line in users:
                username, password, first_name, last_name, role = line.strip().split(",")
                self.users[username] = (password, first_name, last_name)
            users.close()
        with open("books.txt", "r") as books:
            for line in books:
                book_id, title, author, publisher, price, publication_date, language = line.strip().split(",")
                self.books[book_id] = (title, author, publisher, price, publication_date, language)
            books.close()
        self.users_change_status = False


    def Register(self, username, password, firstname, lastname):
        if "admin" in username:
            newUser = Admin(username, password, firstname, lastname)
        else:
            newUser = Users(username, password, firstname, lastname)
        newUser.save_user()
        self.users_change_status = True
    
    def login(self, username, password):
        if self.users_change_status:
            self.load_data()
        if username in self.users:
            if self.users[username][0] == password:
                self.currentUser = username
                return True
            else: return False
        else: return False
    
    def Adminmenu(self):
        print("1. Add book")
        print("2. Accept reserves")
        print("3. Take back book")
        print("4. See all borrowed books")
        print("5. logout")
        choise = input("Enter your choise: ")

        if choise == "1": #Add book
            id = input("Enter book ID: ")
            title = input("Enter book title: ")
            auther = input("Enter book auther: ")
            publisher = input("Enter book publisher: ")
            price = input("Enter book price: ")
            publication_date = input("Enter publication date (YYYY-MM-DD): ")
            language = input("Enter language: ")
            book = f"{id},{title},{auther},{publisher},{price},{publication_date},{language}"
            with open("books.txt", "a") as books:
                books.write(book+"\n")
            books.close()
            print("\n---Successful add book---\n")
            self.Adminmenu()
        
        elif choise == "2": #Accept reserves
            with open("reserves.txt", "r+") as requestfile:
                requests = requestfile.readlines()
                bookIDs = self.books.keys()
                all_request = []
                for book in requests:
                    all_request.append(book.strip().split(',')) 
                
                all_requests_dict = {}
                for id in bookIDs:
                    all_requests_dict[id] = [req for req in all_request if req[0] == id]
                for item in all_requests_dict:
                    desired_book = None
                    if len(all_requests_dict[item]) == 0:
                        pass
                    elif len(all_requests_dict[item]) == 1:
                        filename = "{}.txt".format(all_requests_dict[item][0][1].strip())
                        if os.path.exists(filename):
                            with open("{}".format(filename), "a") as file:
                                file.write(f"{item}, {time.time()}\n")
                                
                        else:
                            print('///////////////')
                            # with open("{}".format(filename), "w") as file:
                            #     file.write(f"{item}, {time.time()}")
                        self.Add_to_Borrowed(item, all_requests_dict[item][0][1])

                    elif len(all_requests_dict[item]) > 1:
                        all_item = all_requests_dict[item]
                        min_time = all_item[0][-1]
                        desired_user = all_item[0][1]
                        for req in all_item[1:]:
                            if req[-1] < min_time:
                                min_time = req[-1]
                                desired_user = req[1].strip()

                        filename = f"{desired_user}.txt"
                        if os.path.exists(filename):
                            with open(filename, "a") as file:
                                file.write(f"{item}, {time.time()}\n")
                        
                        self.Add_to_Borrowed(item, desired_user)

            reservefile = open('reserves.txt', 'w')
            reservefile.close()
            print("\n***Successful Accept Reserves")
            self.Adminmenu()
        
        elif choise == "3": #Take back book
            choise = input("Enter book ID you want to take backe")
            self.Take_back(choise)
            self.Adminmenu()
        
        elif choise == "4": #See all borrowed books
            all_bookID = []
            with open("borrowed.txt", "r") as file:
                data = file.readlines()
                for line in data:
                    book, user = line.strip().split(",")
                    all_bookID.append(book)
            borrowedBooks = []
            with open("books.txt", "r") as file:
                data = file.readlines()
                for line in data:
                    id, title, auther, publisher, price, publication_date, language = line.strip().split(",")
                    if id in all_bookID:
                        borrowedBooks.append(line)
            for b in borrowedBooks:
                print(b)
            self.Adminmenu()

    def is_Admin(self, username):
        if 'admin' in username:
            return True
        return False

    def Add_to_Borrowed(self, bookID, username):
        with open("borrowed.txt", "a") as file:
            file.write(f"{bookID},{username}\n")
    
    def Take_back(self, bookID):
        with open("borrowed.txt", "r+") as file:
            data = file.readlines()
            replace = []
            for line in data:
                book, user = line.strip().split(",")
                if book != bookID:
                    replace.append(line)
            print(self.debt_calculation(bookID, user))
        with open("borrowed.txt", "w") as file:
            file.write("")
        with open("borrowed.txt", "a") as file:
            for line in replace:
                file.write(line)
        


    def Usermenu(self):
        print("1. search")
        print("2. reserve")
        print("3. borrrowed books")
        print("4. return book")
        print("5. logout")
        choise = input("Enter your choise")
        if choise == '1':
            search = self.Search(input("Enter book name or author: "))
            print(search)
            self.Usermenu()
        if choise == '2':
            chosenBook = input("Enter ID of your desired book ")
            if self.is_avalable(chosenBook):
                self.Reserve(chosenBook)
                self.Usermenu()
            else: print("the book is not avalable!")
            self.Usermenu()

        if choise == '3':
            with open("borrowed.txt", "r") as file:
                data = file.readlines()
                books = []
                for line in data:
                    book, user = line.strip().split(",")
                    if user.strip() == self.currentUser:
                        books.append(book)
                borrowed_books = [(id, self.books[id]) for id in books]
                for i in borrowed_books:
                    print(i)
            self.Usermenu()

        if choise == '4':
            bookID = input("Enter book ID you want to return: ")
            filename = f"{self.currentUser}.txt"
            if os.path.exists(filename):
                replace = []
                with open(filename, "r+") as file:
                    data = file.readlines()
                    for line in data:
                        print(line)
                        book, borrowTime = line.strip().split(",")
                        print(book)
                        if not book.strip() == bookID:
                            replace.append(line)
                with open(filename, "w") as file:
                    for line in replace:
                        file.write(line)
                
                with open("borrowed.txt", "r+") as file:
                    data = file.readlines()
                    for line in data:
                        print(line)
                        book, user = line.strip().split(",")
                        if not book.strip() == bookID:
                            replace.append(line)
                with open(filename, "w") as file:
                    for line in replace:
                        file.write(line)
                print(self.debt_calculation(bookID, self.currentUser))
            else:
                print("you have no borrowed book")


        if choise == '5':
            pass

    def Search(self, phrase):
        # print(self.books)
        self.load_data()
        results = []
        for book in self.books:
            if phrase in self.books[book][0] or phrase in self.books[book][1]:
                results.append((book, self.books[book]))
        if not results:
            return "\n---not found---\n"
        return results
    
    def Reserve(self, ID):
        with open("reserves.txt", "a") as reserves:
            reserves.write("{}, {}, {}\n".format(ID, self.currentUser, time.time()))
        reserves.close()
        print("\n---successful reservation request---\n")
    
    def is_avalable(self, bookID):
        with open("borrowed.txt", "r") as file:
            data = file.readlines()
            for line in data:
                book, user = line.strip().split(",")
                if book == bookID:
                    return False
            else: return True
    
    def create_user_file(self, username):
        filename = username.strip()
        if not os.path.exists(f"{filename}.txt"):
            with open(f"{filename}.txt", "w") as file:
                 file.write("")
        
    def debt_calculation(self, bookID, username):
        filename = f"{username}.txt"
        with open(filename, "r") as file:
            data = file.readlines()
            for line in data:
                book, debt = line.strip().split(",")
                if book == bookID:
                    debttime = debt
            now = time.time()
            delay = now - debttime
            if delay > 259200: # 3 days in seconds
                delay //= 86400 # days of delay
                price = delay * 5000
                return f"\n{price} toman for delay\n"
            else:
                return "\nNo delay\n"

library = Library()
while True:

    print("--- Library Management System---")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    choise = input("Enter your choise")

    if choise == '1':
        username = input("username ")
        password = input("password ")
        login = library.login(username,password)
        if login:
            if library.is_Admin(username):
                library.Adminmenu()
            else:
                library.Usermenu()
        else:
            print("wronge username or password")

    elif choise == '2':
        username = input("User_Name: ")
        password = input("Password: ")
        firstname = input("Firstname: ")
        lastname = input("Lastname: ")
        library.Register(username, password, firstname, lastname)
        if not library.is_Admin(username):
            library.create_user_file(username)

    elif choise == '3':
        break