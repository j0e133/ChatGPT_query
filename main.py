import threading
import tkinter as tk
import pyperclip

from tkinter import messagebox
from queue import Queue
from pricing import PriceManager
from zipcode import Zipcode



# Create the main window
window = tk.Tk()
window.title('Price Estimator')
window.protocol('WM_DELETE_WINDOW', window.destroy)
window.resizable(False, False)
window.geometry(f'{600}x{300}+{int(0.5 * (window.winfo_screenwidth() - 600))}+{int(0.5 * (window.winfo_screenheight() - 300))}')
window.configure(background='gray80')


# Add title
title_label = tk.Label(
    window,
    text='Price Estimator',
    font=('Sylfaen', 50, 'bold'),
    foreground='black',
    background='gray80'
)
title_label.place(
    x = (600 - title_label.winfo_reqwidth()) * 0.5,
    y = 20
)

# Add text boxes
old_zipcode = tk.StringVar()
zipcode = tk.StringVar()
zipcode_label = tk.Label(
    window,
    text='Zip code:',
    font=('Sylfaen', 15),
    foreground='black',
    background='gray80'
)
zipcode_label.place(x=48, y=150)
zipcode_entry = tk.Entry(
    window,
    textvariable=zipcode,
    font=('Sylfaen', 15),
    foreground='black',
    background='gray75',
    justify='center',
    width=7,
)
zipcode_entry.place(
    x = 48 + zipcode_label.winfo_reqwidth() + 5,
    y = 150 + 2
)

old_city = tk.StringVar()
city = tk.StringVar()
city_label = tk.Label(
    window,
    text='City:',
    font=('Sylfaen', 15),
    foreground='black',
    background='gray80'
)
city_label.place(x=241, y=150)
city_entry = tk.Entry(
    window,
    textvariable=city,
    font=('Sylfaen', 15),
    foreground='black',
    background='gray75',
    justify='center',
    width=25,
)
city_entry.place(
    x = 241 + city_label.winfo_reqwidth() + 5,
    y = 150 + 2
)

# function to get pricing
price_manager = PriceManager()

def get_pricing():
    location = city.get()

    response = messagebox.askokcancel('Warning', f'Querying can cost up to $0.75\nAre you sure you want to get pricing in "{location}"\n(Runs in the background)', icon='warning')

    if response:
        # asynchronously search and query GPT for the pricing information
        queue: Queue[dict[str, float]] = Queue()

        thread = threading.Thread(target=price_manager.get_prices_per_minute, args=(location, queue))
        thread.start()

        def check_queue():
            try:
                # get prices
                prices = queue.get_nowait()

                # display pricing window
                if prices is None:
                    reply = messagebox.Message(
                        window,
                        icon='error',
                        type='ok',
                        title='Error',
                        message=f'An error occured, couldn\'t get the pricing in "{location}"'
                    )

                else:
                    reply = messagebox.Message(
                        window,
                        icon='info',
                        type='ok',
                        title='Pricing Information',
                        message=f'Pricing in {location}:\n\n{'\n'.join(f'{treatment}: {f'${price:.2f}' if price > 0 else 'N/A'}' for treatment, price in prices.items())}\n\nAutomatically copied so you can paste into a spreadsheet'
                    )

                    # copy the output to clipboard. Able to be pasted into a spreadsheet
                    pyperclip.copy('\n'.join(f'{treatment}\t{price}' for treatment, price in prices.items()))

                reply.show()

            except:
                window.after(100, check_queue)

        check_queue()


# Add buttons
query_button = tk.Button(
    window,
    text='Get Pricing',
    font=('Sylfaen', 15),
    foreground='black',
    activeforeground='black',
    background='gray75',
    activebackground='gray65',
    command=get_pricing,
    state='disabled'
)
query_button.place(x=242, y=215)

def _enter(_): query_button['background']='gray70'
def _leave(_): query_button['background']='gray75'

query_button.bind('<Enter>', _enter)
query_button.bind('<Leave>', _leave)


# zipcode and city authentification functions
update_city = False

def zipcode_update(*_) -> None:
    global update_city

    zipcode_str = zipcode.get()

    if len(zipcode_str) > 5 or not zipcode_str.isdigit() and not zipcode_str == '':
        zipcode.set(old_zipcode.get())

    else:
        old_zipcode.set(zipcode_str)

        if len(zipcode_str) == 5:
            update_city = True

            city.set(Zipcode(zipcode_str).location)


def city_update(*_) -> None:
    global update_city

    city_str = city.get()

    if not all(char.isalpha() or char in ', ' for char in city_str):
        city.set(old_city.get())

    else:
        old_city.set(city_str)

        query_button['state'] = 'normal' if city_str else 'disabled'

        if not update_city:
            zipcode.set('')

        update_city = False


# link the zipcode and city
zipcode.trace_add('write', zipcode_update)
city.trace_add('write', city_update)


# fix focusing issues
window.bind_all('<Button>', lambda event: event.widget.focus_set())


# Start the GUI event loop
window.mainloop()

