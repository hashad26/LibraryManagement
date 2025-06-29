# Importing all necessary modules
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Functions
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')
    if not Cid:
        mb.showerror('Missing Issuer ID', 'Issuer ID cannot be empty.')
        return None
    return Cid

def display_records():
    tree.delete(*tree.get_children())
    curr = connector.execute('SELECT * FROM Library')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)

def clear_fields():
    bk_status.set('Available')
    for i in [bk_id, bk_name, author_name, card_id]:
        i.set('')
    bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def view_record():
    if not tree.focus():
        mb.showerror('No Selection', 'Please select a record to view.')
        return

    selected = tree.focus()
    values = tree.item(selected)['values']
    if not values: return

    bk_name.set(values[0])
    bk_id.set(values[1])
    author_name.set(values[2])
    bk_status.set(values[3])
    card_id.set(values[4])

def add_record():
    if not all([bk_name.get(), bk_id.get(), author_name.get()]):
        mb.showerror("Missing Fields", "Please fill in all the fields.")
        return

    if bk_status.get() == 'Issued':
        cid = issuer_card()
        if not cid:
            return
        card_id.set(cid)
    else:
        card_id.set('N/A')

    surety = mb.askyesno('Confirm Entry',
                         'Are you sure this is the data you want to enter?\nBook ID cannot be changed later.')

    if surety:
        try:
            connector.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
            connector.commit()
            clear_and_display()
            mb.showinfo('Success', 'Record successfully added.')
        except sqlite3.IntegrityError:
            mb.showerror('Duplicate Book ID', 'This Book ID already exists. Use a unique ID.')

def update_record():
    view_record()
    bk_id_entry.config(state='disable')
    clear.config(state='disable')

    def update():
        if not all([bk_name.get(), author_name.get()]):
            mb.showerror("Missing Fields", "Book name and Author name cannot be empty.")
            return

        if bk_status.get() == 'Issued':
            cid = issuer_card()
            if not cid:
                return
            card_id.set(cid)
        else:
            card_id.set('N/A')

        cursor.execute(
            'UPDATE Library SET BK_NAME=?, BK_STATUS=?, AUTHOR_NAME=?, CARD_ID=? WHERE BK_ID=?',
            (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get()))
        connector.commit()
        clear_and_display()
        bk_id_entry.config(state='normal')
        clear.config(state='normal')
        edit.destroy()

    global edit
    edit = Button(left_frame, text='Confirm Update', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item to delete.')
        return

    current_item = tree.focus()
    values = tree.item(current_item)['values']
    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (values[1],))
    connector.commit()
    tree.delete(current_item)
    mb.showinfo('Deleted', 'Record deleted successfully.')
    clear_and_display()

def delete_inventory():
    if mb.askyesno('Are you sure?', 'Delete the entire inventory? This action cannot be undone.'):
        tree.delete(*tree.get_children())
        cursor.execute('DELETE FROM Library')
        connector.commit()

def change_availability():
    if not tree.selection():
        mb.showerror('Error!', 'Please select a book from the table.')
        return

    selected = tree.focus()
    values = tree.item(selected)['values']
    BK_id = values[1]
    BK_status = values[3]

    if BK_status == 'Issued':
        surety = mb.askyesno('Return Confirmation', 'Has the book been returned?')
        if surety:
            cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Available', 'N/A', BK_id))
            connector.commit()
        else:
            mb.showinfo('Not Returned', 'Cannot mark as available unless returned.')
    else:
        cid = issuer_card()
        if not cid:
            return
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=? WHERE BK_ID=?', ('Issued', cid, BK_id))
        connector.commit()

    clear_and_display()

# GUI Variables
lf_bg = 'LightSkyBlue'
rtf_bg = 'DeepSkyBlue'
rbf_bg = 'DodgerBlue'
btn_hlb_bg = 'SteelBlue'

lbl_font = ('Georgia', 13)
entry_font = ('Times New Roman', 12)
btn_font = ('Gill Sans MT', 13)

root = Tk()
root.title('KBP Library Management System')
root.geometry('1010x530')
root.resizable(0, 0)

Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(side=TOP, fill=X)

bk_status = StringVar(value='Available')
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame Widgets
Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font).place(x=98, y=25)
Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=45, y=55)

Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=45, y=215)

Label(left_frame, text='Status of the Book', bg=lf_bg, font=lbl_font).place(x=75, y=265)
dd = OptionMenu(left_frame, bk_status, 'Available', 'Issued')
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)

submit = Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record)
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame Buttons
Button(RT_frame, text='Delete book record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8, y=30)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
Button(RT_frame, text='Update book details', font=btn_font, bg=btn_hlb_bg, width=17, command=update_record).place(x=348, y=30)
Button(RT_frame, text='Change Book Availability', font=btn_font, bg=btn_hlb_bg, width=19, command=change_availability).place(x=518, y=30)

# Right Bottom Frame (Inventory Table)
tree = ttk.Treeview(RB_frame, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID'), show='headings')

tree.heading('Book Name', text='Book Name')
tree.heading('Book ID', text='Book ID')
tree.heading('Author', text='Author')
tree.heading('Status', text='Status')
tree.heading('Card ID', text='Card ID')

tree.column('Book Name', width=150)
tree.column('Book ID', width=80)
tree.column('Author', width=150)
tree.column('Status', width=80)
tree.column('Card ID', width=80)

tree.pack(fill=BOTH, expand=True)
tree.bind('<Double-1>', lambda e: view_record())

# Initial Load
display_records()

# Start GUI loop
root.mainloop()
