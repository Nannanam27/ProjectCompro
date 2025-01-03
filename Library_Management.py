import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta 
import pickle
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Screen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()

class MainScreen(Screen):
    def __init__(self, parent, system, history_data_screen):
        super().__init__(parent)
        self.system = system
        self.history_data_screen = history_data_screen
        
        title_frame = ctk.CTkFrame(self, fg_color="#3B8ED0", corner_radius=0)
        title_frame.pack(pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="  Library Management System  ",
            font=ctk.CTkFont("Arial", size=24, weight="bold"),
            text_color="white"
        )  
        title_label.pack(pady=10)

        content_frame = ctk.CTkFrame(self)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        #Left
        input_frame = ctk.CTkFrame(content_frame)
        input_frame.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="n")

        labels = ["First Name", "Last Name", "ID", "Book ID", "Book Title", "Date Borrowed", "Date Return"]
        self.entries = {}
        for i, label in enumerate(labels):
            lbl = ctk.CTkLabel(input_frame, text=label + ":", font=ctk.CTkFont(size=14))
            lbl.grid(row=i, column=0, pady=5, sticky="w")
            entry = ctk.CTkEntry(input_frame, width=200, font=ctk.CTkFont(size=14))
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="w")
            self.entries[label] = entry

        #Right
        search_frame = ctk.CTkFrame(content_frame)
        search_frame.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="n")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search", width=280)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda event: self.search_books())

        self.scrollable_list_frame = ctk.CTkScrollableFrame(search_frame, width=250, height=200)
        self.scrollable_list_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.selected_item_var = ctk.StringVar()
        
        self.update_radio_buttons(self.load_data_from_file("book_data.pkl", lambda book: book.get("Book Title", "Unknown Title")))

        #Button
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        btn_add = ctk.CTkButton(button_frame, text="Add Data", width=100, height=40, font=ctk.CTkFont(size=14), command=self.add_data)
        btn_add.grid(row=0, column=0, padx=10, pady=10)

        btn_history = ctk.CTkButton(button_frame, text="History", width=100, height=40, font=ctk.CTkFont(size=14), command=self.system.show_history_screen)
        btn_history.grid(row=0, column=1, padx=10, pady=10)

        btn_book_data = ctk.CTkButton(button_frame, text="Book Data", width=100, height=40, font=ctk.CTkFont(size=14), command=self.system.show_book_data_screen)
        btn_book_data.grid(row=0, column=2, padx=10, pady=10)

        btn_exit = ctk.CTkButton(button_frame, text="Exit", width=100, height=40, font=ctk.CTkFont(size=14), command=self.system.root.quit)
        btn_exit.grid(row=0, column=3, padx=10, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

    def load_data_from_file(self, file_name, extract):
        try:
            if os.path.exists(file_name):
                with open(file_name, "rb") as file:
                    data = pickle.load(file)
                    return [extract(item) for item in data]
            return []
        except (OSError, pickle.UnpicklingError) as e:
            self.popup("Error", f"Error loading file '{file_name}': {str(e)}")
            return []

    def update_entry(self):
        try:
            selected_title = self.selected_item_var.get()
            book_info = self.get_data("book_data.pkl", "Book Title", selected_title)

            if book_info:
                self.entries["Book ID"].delete(0, "end")
                self.entries["Book Title"].delete(0, "end")
                self.entries["Book ID"].insert(0, book_info.get("Book ID", ""))
                self.entries["Book Title"].insert(0, book_info.get("Book Title", ""))

                today = datetime.today().strftime("%Y-%m-%d")
                self.entries["Date Borrowed"].delete(0, "end")
                self.entries["Date Borrowed"].insert(0, today)

                date_borrowed_obj = datetime.strptime(today, "%Y-%m-%d")
                date_return_obj = date_borrowed_obj + timedelta(days=15)

                self.entries["Date Return"].delete(0, "end")
                self.entries["Date Return"].insert(0, date_return_obj.strftime("%Y-%m-%d"))
        except Exception as e:
            self.popup("Error", f"Error updating entry fields: {str(e)}")

    def search_books(self):
        search = self.search_entry.get().lower()
        matching_titles = [title for title in self.load_data_from_file("book_data.pkl", lambda book: book.get("Book Title", "Unknown Title")) if search in title.lower()]
        self.update_radio_buttons(matching_titles)

    def update_radio_buttons(self, items):
        for widget in self.scrollable_list_frame.winfo_children():
            widget.destroy()  

        if items:
            for item in items:
                radiobutton = ctk.CTkRadioButton(
                    self.scrollable_list_frame,
                    text=item,
                    value=item,
                    variable=self.selected_item_var,
                    command=self.update_entry
                )
                radiobutton.pack(anchor="w", padx=10, pady=2)
        else:
            self.update_label("No books found")

    def update_label(self, message):
        for widget in self.scrollable_list_frame.winfo_children():
            widget.destroy()

        label = ctk.CTkLabel(self.scrollable_list_frame, text=message, font=ctk.CTkFont(size=14))
        label.pack(anchor="w", padx=10, pady=5)


    def get_data(self, file_name, field, value):
        data = self.load_data_from_file(file_name, lambda item: item)
        for item in data:
            if item.get(field) == value:
                return item
        return None

    def add_data(self):
        for field in ["First Name", "Last Name", "Book ID", "Book Title", "Date Borrowed", "Date Return"]:
            if not self.entries[field].get().strip():  
                self.popup("Error", f"Please fill in the '{field}' field.")
                return  

        book_id = self.entries["Book ID"].get()
        if not self.is_book_available(book_id):
            self.popup("Error", "This book is already borrowed.")
            return

        name = self.entries["First Name"].get() + " " + self.entries["Last Name"].get()
        history_data = {
            "Borrower Name": name,
            "Book ID": book_id,
            "Book Title": self.entries["Book Title"].get(),
            "Date Borrowed": self.entries["Date Borrowed"].get(),
            "Date Return": self.entries["Date Return"].get(),
        }

        self.save_to_file("history.pkl", history_data)
        self.update_book_status(book_id, available=False)
        
        self.popup("Confirmation", "Book borrowed successfully!")

        for entry in self.entries.values():
            entry.delete(0, "end")

        self.history_data_screen.display_history()

    def popup(self, title, message):
        popup = ctk.CTkToplevel(self)
        popup.geometry("300x150")
        popup.title(title)
        label = ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=14))
        label.pack(pady=20)
        ok_button = ctk.CTkButton(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

    def is_book_available(self, book_id):
        return self.get_data("book_data.pkl", "Book ID", book_id).get("Available", True)

    def update_book_status(self, book_id, available):
        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)

            for book in all_books:
                if book.get("Book ID") == book_id:
                    book["Available"] = available

            with open(data_file, "wb") as file:
                pickle.dump(all_books, file)

    def save_to_file(self, file_name, data):
        if os.path.exists(file_name):
            with open(file_name, "rb") as file:
                all_data = pickle.load(file)
        else:
            all_data = []

        all_data.append(data)
        with open(file_name, "wb") as file:
            pickle.dump(all_data, file)

class BookDataScreen(Screen):
    def __init__(self, parent, system, main):
        super().__init__(parent)
        self.system = system
        self.main_screen = main
        
        title_frame = ctk.CTkFrame(self, fg_color="#3B8ED0", corner_radius=0)
        title_frame.pack(fill="x")
        
        title_label = ctk.CTkLabel(
            title_frame, text="Book Data",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=5)

        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ##### display table #####
        columns = ("Book ID", "Book Title", "Author Name", "Genre", "Availability") 
        self.book_tree = ttk.Treeview(self.display_frame, columns=columns, show="headings")

        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, anchor="w", width=100)

        scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.book_tree.pack(fill="both", expand=True)

        h_scrollbar = ttk.Scrollbar(self.display_frame, orient="horizontal", command=self.book_tree.xview)
        self.book_tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side="bottom", fill="x")

        #Button
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady = 10)
        
        add_button = ctk.CTkButton(button_frame, text="Add Book", width=120, command=self.system.show_add_screen)
        add_button.pack(side="left", padx=20)

        edit_button = ctk.CTkButton(button_frame, text="Edit Book", width=120, command=self.edit_book)
        edit_button.pack(side="left", padx=20)

        delete_button = ctk.CTkButton(button_frame, text="Delete Book", width=120, command=self.delete_book)
        delete_button.pack(side="left", padx=20)

        back_button = ctk.CTkButton(button_frame, text="Back", width=120, command=self.system.show_main_screen)
        back_button.pack(side="right", padx=20)

        self.display_books()

    def display_books(self):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)
        else:
            all_books = []

        for book in all_books:
            availability = "Available" if book.get("Available", True) else "Not Available"
            book_values = (
                book.get("Book ID", ""),
                book.get("Book Title", ""),
                book.get("Author Name", ""),
                book.get("Genre", ""),
                availability  
            )
            self.book_tree.insert("", "end", values=book_values)
            
    def delete_book(self):
        selected_item = self.book_tree.selection()
        if selected_item:
            book_id = self.book_tree.item(selected_item, "values")[0] 
            self.book_tree.delete(selected_item)  
            data_file = "book_data.pkl"
            if os.path.exists(data_file):
                with open(data_file, "rb") as file:
                    all_books = pickle.load(file)

                updated_books = [book for book in all_books if book.get("Book ID", "") != book_id]
                with open(data_file, "wb") as file:
                    pickle.dump(updated_books, file)

            self.main_screen.update_radio_buttons(
                self.main_screen.load_data_from_file(
                    "book_data.pkl", lambda book: book.get("Book Title", "Unknown Title")
                )
            )
        else:
            return

    def edit_book(self):
        selected_item = self.book_tree.selection()
        if selected_item:
            book_id = self.book_tree.item(selected_item, "values")[0]

            data_file = "book_data.pkl"
            if os.path.exists(data_file):
                with open(data_file, "rb") as file:
                    all_books = pickle.load(file)

                book_to_edit = next((book for book in all_books if book.get("Book ID", "") == book_id), None)
                if book_to_edit:
                    self.system.show_edit_screen(book_to_edit)

class HistoryScreen(Screen):
    def __init__(self, parent, system):
        super().__init__(parent)
        self.system = system
        
        title_frame = ctk.CTkFrame(self, fg_color="#3B8ED0", corner_radius=0)
        title_frame.pack(fill="x")
        title_label = ctk.CTkLabel(title_frame, text="History", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        title_label.pack(pady=5)

        #####Table#####
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Borrower Name", "Book Title", "Date Borrowed", "Date Return", "Status", "Fine")
        self.book_tree = ttk.Treeview(self.display_frame, columns=columns, show="headings")

        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, anchor="w", width=150)

        scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.book_tree.pack(fill="both", expand=True)

        h_scrollbar = ttk.Scrollbar(self.display_frame, orient="horizontal", command=self.book_tree.xview)
        self.book_tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side="bottom", fill="x")

        #Button
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=10)

        return_button = ctk.CTkButton(button_frame, text="Return Book", width=120, command=self.return_book)
        return_button.pack(side="left", padx=10)

        back_button = ctk.CTkButton(button_frame, text="Back", width=120, command=self.system.show_main_screen)
        back_button.pack(side="right", padx=10)

        self.display_history()

    def display_history(self):
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        history_file = "history.pkl"
        if os.path.exists(history_file):
            with open(history_file, "rb") as file:
                all_history = pickle.load(file)
        else:
            all_history = []

        for history in all_history:
            return_status = history.get("Status", "Borrowed")
            fine = history.get("Fine", 0)

            history_values = (
                history.get("Borrower Name", ""),
                history.get("Book Title", ""),
                history.get("Date Borrowed", ""),
                history.get("Date Return", ""),
                return_status,
                f"{fine} Bath" if fine > 0 else "No Fine"
            )
            self.book_tree.insert("", "end", values=history_values)


    def is_book_returned(self, book_id):
        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)
                for book in all_books:
                    if book.get("Book ID") == book_id:
                        return book.get("Available", False)
        return False

    def return_book(self):    
        selected_item = self.book_tree.selection()
        if not selected_item:
            return  
        
        item_values = self.book_tree.item(selected_item)["values"]
        book_title = item_values[1]
        due_date = item_values[3] 
        book_id = self.get_book_id_by_title(book_title)

        if book_id:
            self.mark_book_as_available(book_id)
            return_date = datetime.now().strftime("%Y-%m-%d")

            fine = self.calculate_fine(due_date, return_date)
            self.returned(book_id, return_date, fine)

            self.display_history()

    def calculate_fine(self, due_date, return_date):
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        return_date = datetime.strptime(return_date, "%Y-%m-%d")
        
        overdue_days = (return_date - due_date).days
        if overdue_days > 0:
            return overdue_days * 5 
        return 0

    def get_book_id_by_title(self, title):
        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)
                for book in all_books:
                    if book.get("Book Title") == title:
                        return book.get("Book ID")
        return None

    def make_available(self, book_id):
        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)

            for book in all_books:
                if book.get("Book ID") == book_id:
                    book["Available"] = True

            with open(data_file, "wb") as file:
                pickle.dump(all_books, file)

    def returned(self, book_id, return_date, fine):
        history_file = "history.pkl"
        if os.path.exists(history_file):
            with open(history_file, "rb") as file:
                all_history = pickle.load(file)

            for history in all_history:
                if history.get("Book ID") == book_id:
                    history["Status"] = "Returned"
                    history["Date Return"] = return_date
                    history["Fine"] = fine 
                    break

            with open(history_file, "wb") as file:
                pickle.dump(all_history, file)

        self.make_available(book_id)

class EditBookScreen(Screen):
    def __init__(self, parent, system, book_data, main_screen, book_data_screen):
        super().__init__(parent)
        self.system = system
        self.book_data = book_data  
        self.book_data_screen = book_data_screen
        self.main_screen = main_screen
        
        title_frame = ctk.CTkFrame(self, fg_color="#3B8ED0", corner_radius=0)
        title_frame.pack(fill="x")
        
        title_label = ctk.CTkLabel(
            title_frame, text="Edit Book Details",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=5)

        center_frame = ctk.CTkFrame(self)
        center_frame.pack(expand=True)  

        form_frame = ctk.CTkFrame(center_frame) 
        form_frame.pack(padx=20, pady=20)

        book_id_label = ctk.CTkLabel(form_frame, text="Book ID")
        book_id_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        book_id_entry = ctk.CTkEntry(form_frame, width=400)
        book_id_entry.insert(0, self.book_data.get("Book ID", ""))
        book_id_entry.configure(state="disabled")
        book_id_entry.grid(row=0, column=1, padx=10, pady=5)

        title_label = ctk.CTkLabel(form_frame, text="Book Title")
        title_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.title_entry = ctk.CTkEntry(form_frame, width=400)
        self.title_entry.insert(0, self.book_data.get("Book Title", ""))
        self.title_entry.grid(row=1, column=1, padx=10, pady=5)

        author_label = ctk.CTkLabel(form_frame, text="Author Name")
        author_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.author_entry = ctk.CTkEntry(form_frame, width=400)
        self.author_entry.insert(0, self.book_data.get("Author Name", ""))
        self.author_entry.grid(row=2, column=1, padx=10, pady=5)

        genre_label = ctk.CTkLabel(form_frame, text="Genre")
        genre_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.genre_entry = ctk.CTkEntry(form_frame, width=400)
        self.genre_entry.insert(0, self.book_data.get("Genre", ""))
        self.genre_entry.grid(row=3, column=1, padx=10, pady=5)

        self.availability_var = ctk.BooleanVar(value=self.book_data.get("Available", True))
        availability_checkbox = ctk.CTkCheckBox(
            form_frame, text="Available", variable=self.availability_var
        )
        availability_checkbox.grid(row=4, columnspan=2, pady=10)
        
        #Button
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=10)
        
        save_button = ctk.CTkButton(button_frame, text="Save Changes", width=120, command=self.save_changes)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", width=120, command=self.system.show_book_data_screen)
        cancel_button.pack(side="right", padx=10)

    def save_changes(self):
        updated_book = {
            "Book ID": self.book_data.get("Book ID", ""),
            "Book Title": self.title_entry.get(),
            "Author Name": self.author_entry.get(),
            "Genre": self.genre_entry.get(),
            "Available": self.availability_var.get()
        }

        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)
            
            for i, book in enumerate(all_books):
                if book.get("Book ID", "") == updated_book["Book ID"]:
                    all_books[i] = updated_book
                    break

            with open(data_file, "wb") as file:
                pickle.dump(all_books, file)

            self.main_screen.update_radio_buttons(self.main_screen.load_data_from_file("book_data.pkl", lambda book: book.get("Book Title", "Unknown Title")))
            self.book_data_screen.display_books()
            self.system.show_book_data_screen()

class AddBookScreen(Screen):
    def __init__(self, parent, system, book_data_screen, main):
        super().__init__(parent)
        self.system = system
        self.book_data_screen = book_data_screen
        self.main_screen = main
        
        title_frame = ctk.CTkFrame(self, fg_color="#3B8ED0", corner_radius=0)
        title_frame.pack(fill="x")  
        title_label = ctk.CTkLabel(title_frame, text="Add Book", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        title_label.pack(pady=10)

        content_frame = ctk.CTkFrame(self, width=500, height=300)
        content_frame.pack(pady=30, padx=50, fill="both", expand=True) 
        content_frame.pack_propagate(False) 

        input_frame = ctk.CTkFrame(content_frame)
        input_frame.place(relx=0.5, rely=0.5, anchor="center")  

        labels = ["Book ID", "Book Title", "Author Name", "Genre"]
        self.entries = {}
        for i, label in enumerate(labels):
            lbl = ctk.CTkLabel(input_frame, text=label + ":", font=ctk.CTkFont(size=14))
            lbl.grid(row=i, column=0, pady=8, padx=10, sticky="e")  
            
            entry = ctk.CTkEntry(input_frame, width=350, font=ctk.CTkFont(size=14))  
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.entries[label] = entry

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", pady=10, padx=20)  

        add_button = ctk.CTkButton(button_frame, text="Add", width=150, command=self.save_book_data)
        add_button.pack(side="left", padx=10)

        back_button = ctk.CTkButton(button_frame, text="Back", width=150, command=self.system.show_book_data_screen)
        back_button.pack(side="right", padx=10) 

    def save_book_data(self):
        book_id = self.entries["Book ID"].get()

        data_file = "book_data.pkl"
        if os.path.exists(data_file):
            with open(data_file, "rb") as file:
                all_books = pickle.load(file)
        else:
            all_books = []

        for book in all_books:
            if book["Book ID"] == book_id:
                error_popup = ctk.CTkToplevel(self)
                error_popup.geometry("300x150")
                error_popup.title("Error")
                error_label = ctk.CTkLabel(error_popup, text="Book ID already exists.", font=ctk.CTkFont(size=14))
                error_label.pack(pady=20)
                ok_button = ctk.CTkButton(error_popup, text="OK", command=error_popup.destroy)
                ok_button.pack(pady=10)
                return

        book_data = {label: entry.get() for label, entry in self.entries.items()}
        all_books.append(book_data)

        with open(data_file, "wb") as file:
            pickle.dump(all_books, file)

        confirmation_popup = ctk.CTkToplevel(self)
        confirmation_popup.geometry("300x150")
        confirmation_popup.title("Confirmation")
        confirmation_label = ctk.CTkLabel(confirmation_popup, text="Book data saved successfully!", font=ctk.CTkFont(size=14))
        confirmation_label.pack(pady=20)
        ok_button = ctk.CTkButton(confirmation_popup, text="OK", command=confirmation_popup.destroy)
        ok_button.pack(pady=10)

        for entry in self.entries.values():
            entry.delete(0, "end")

        self.main_screen.update_radio_buttons(self.main_screen.load_data_from_file("book_data.pkl", lambda book: book.get("Book Title", "Unknown Title")))
        self.book_data_screen.display_books()

class LibraryManagementSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Library Management System")
        self.root.geometry("700x500")

        self.main_screen = MainScreen(self.root, self, None)
        self.book_data_screen = BookDataScreen(self.root, self, None)
        self.history_screen = HistoryScreen(self.root, self)
        self.addbook_screen = AddBookScreen(self.root, self, self.book_data_screen, None)

        self.edit_book_screen = None  

        self.main_screen.history_data_screen = self.history_screen
        self.book_data_screen.main_screen = self.main_screen
        self.addbook_screen.main_screen = self.main_screen

        self.show_main_screen()
        self.root.mainloop()

    def show_main_screen(self):
        self.hide_all_screens()
        self.main_screen.show()

    def show_book_data_screen(self):
        self.hide_all_screens()
        self.book_data_screen.show()

    def show_history_screen(self):
        self.hide_all_screens()
        self.history_screen.show()

    def show_add_screen(self):
        self.hide_all_screens()
        self.addbook_screen.show()
        
    def show_edit_screen(self, book_data):
        self.hide_all_screens()
        if self.edit_book_screen is not None:
            self.edit_book_screen.destroy()  
        self.edit_book_screen = EditBookScreen(self.root, self, book_data, self.main_screen, self.book_data_screen)
        self.edit_book_screen.show()

    def hide_all_screens(self):
        self.main_screen.hide()
        self.book_data_screen.hide()
        self.history_screen.hide()
        self.addbook_screen.hide()
        if self.edit_book_screen is not None:
            self.edit_book_screen.hide()

LibraryManagementSystem()
