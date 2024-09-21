import tkinter as tk
import tkinter.messagebox as messagebox
from threading import Thread
from typing import Callable, Literal, Any

import pyperclip

from constants import *
from pricing import PriceManager
from treatments import Treatment, TREATMENTS
from zipcode import Zipcode



def create_button(master: tk.Tk, text: str, command: Callable[[], Any], *, fontsize: int = 12, state: Literal['normal', 'active', 'disabled'] = 'normal') -> tk.Button:
    button = tk.Button(
        master,
        text=text,
        font=(FONT, fontsize),
        command=command,
        state=state,
        **BUTTON_COLORS
    )

    def enter(_): button['background'] = ELEMENT_HOVER_COLOR
    def leave(_): button['background'] = ELEMENT_COLOR

    button.bind('<Enter>', enter)
    button.bind('<Leave>', leave)

    return button



def submit_active() -> bool:
    valid_city = Zipcode.is_city(city_str.get())

    treatment_selected = any(treatment_checkbox.get() for _, treatment_checkbox in treatment_checkboxes)

    return valid_city and treatment_selected



def zipcode_update(*_) -> None:
    zipcode = zipcode_str.get()

    if len(zipcode) > 5 or not zipcode.isdigit() and not zipcode == '':
        zipcode_str.set(_old_zipcode_str.get())

    else:
        _old_zipcode_str.set(zipcode)

        if len(zipcode) == 5:
            _update_city.set(True)

            city_str.set(Zipcode(zipcode).city)



def city_update(*_) -> None:
    city = city_str.get()

    # only allow letters, spaces, and some punctuation in city names
    if not all(char.isalpha() or char in '\'-, ' for char in city):
        city_str.set(_old_city_str.get())

    else:
        _old_city_str.set(city)

        query_button['state'] = 'normal' if submit_active() else 'disabled'

        if not _update_city.get():
            zipcode_str.set('')

        _update_city.set(False)



def checkbox_update(*_) -> None:
    query_button['state'] = 'normal' if submit_active() else 'disabled'



def get_pricing():
    city = city_str.get()

    treatments = [treatment for treatment, checkbox_state in treatment_checkboxes if checkbox_state.get()]

    ok = messagebox.askokcancel('Warning', f'Querying for {len(treatments)} treatments can cost up to ${len(treatments) * 0.05:.2f}\nAre you sure you want to get pricing in "{city}"\n(Runs in the background)', icon='warning')

    if ok:
        # asynchronously search and query GPT for the pricing information and automatically open a window with the results
        thread = Thread(target=pricing_worker, args=(city, treatments, bool(update_state.get())))
        thread.start()



def pricing_worker(city: str, treatments: list[Treatment], update_database: bool) -> None:
    prices = price_manager.get_prices_per_minute(city, treatments, update_database)

    # display pricing self
    if prices:
        sorted_prices = sorted(prices.items(), key=lambda x: x[0])

        reply = messagebox.Message(
            icon='info',
            type='ok',
            title='Pricing Information',
            message=f'Pricing in {city}:\n\n{'\n'.join(f'{treatment}: ${price:.2f}' for treatment, price in sorted_prices)}\n\nAutomatically copied so you can paste into a spreadsheet'
        )

        # copy the output to clipboard. Able to be pasted into a spreadsheet
        pyperclip.copy(f'Treatment\tPrice\n' + '\n'.join(f'{treatment}\t${price:.2f}' for treatment, price in sorted_prices))

    else:
        reply = messagebox.Message(
            icon='error',
            type='ok',
            title='Error',
            message=f'An error occured, couldn\'t get the pricing in "{city}"'
        )

    reply.show()



window = tk.Tk()

window.title('Price Estimator')

window.protocol('WM_DELETE_WINDOW', window.destroy)

size = (475, 430)

window.geometry(f'{size[0]}x{size[1]}+{int(0.5 * (window.winfo_screenwidth() - size[0]))}+{int(0.5 * (window.winfo_screenheight() - size[1]))}')
window.resizable(False, False)

window.configure(background=BACKGROUND_COLOR)

# Add title
title_label = tk.Label(
    window,
    text='Price Estimator',
    font=(FONT, 30, 'bold'),
    **LABEL_COLORS
)
title_label.place(
    x = (size[0] - title_label.winfo_reqwidth()) * 0.5,
    y = 20
)

# Add text boxes
entry_y = 20 + title_label.winfo_reqheight() + 17

zipcode_str = tk.StringVar()
_old_zipcode_str = tk.StringVar(value=zipcode_str.get())

zipcode_label = tk.Label(
    window,
    text='Zip code:',
    font=DEFAULT_FONT,
    foreground='black',
    background='gray80'
)
zipcode_entry = tk.Entry(
    window,
    textvariable=zipcode_str,
    font=DEFAULT_FONT,
    foreground='black',
    background='gray75',
    justify='center',
    width=7,
)
zipcode_label.place(
    x = 30,
    y = entry_y
)
zipcode_entry.place(
    x = 30 + 68 + 5,
    y = entry_y + 2
)

city_str = tk.StringVar()
_old_city_str = tk.StringVar(value=city_str.get())
_update_city = tk.BooleanVar(value=False)

city_label = tk.Label(
    window,
    text='City:',
    font=DEFAULT_FONT,
    foreground='black',
    background='gray80'
)
city_entry = tk.Entry(
    window,
    textvariable=city_str,
    font=DEFAULT_FONT,
    foreground='black',
    background='gray75',
    justify='center',
    width=25,
)
city_label.place(
    x = 30 + 68 + 5 + 65 + 20,
    y = entry_y
)
city_entry.place(
    x = 30 + 68 + 5 + 65 + 20 + 39 + 5,
    y = entry_y + 2
)

# Add treatment options
checkbox_y = entry_y + city_entry.winfo_reqheight() + 27
checkboxes: list[tk.Checkbutton] = []
checkbox_states: list[tk.IntVar] = []

for i, treatment in enumerate(TREATMENTS):
    checkbox_state = tk.IntVar(value=0)
    checkbox = tk.Checkbutton(
        window,
        variable=checkbox_state,
        text=treatment.name,
        font=DEFAULT_FONT,
        **CHECKBOX_COLORS
    )

    checkbox.place(
        x = 50 + 290 * (i % 2),
        y = checkbox_y + (i // 2) * 40
    )

    checkboxes.append(checkbox)
    checkbox_states.append(checkbox_state)
    
treatment_checkboxes = tuple(zip(TREATMENTS, checkbox_states))

# Add update database option
update_y = checkbox_y + (i // 2) * 40 + 40

update_state = tk.IntVar(value=0)
update_checkbox = tk.Checkbutton(
    window,
    variable=update_state,
    text='Get new prices for treatments already in the database',
    font=DEFAULT_FONT,
    **CHECKBOX_COLORS
)
update_checkbox.place(
    x=50,
    y=update_y
)

# Add query button
query_button = create_button(
    window,
    'Get Pricing',
    get_pricing,
    state='disabled'
)
query_button.place(
    x = (size[0] - query_button.winfo_reqwidth()) * 0.5,
    y = update_y + 52
)


# create the price manager
price_manager = PriceManager()


# link everything together
zipcode_str.trace_add('write', zipcode_update)
city_str.trace_add('write', city_update)

for _, checkbox_state in treatment_checkboxes:
    checkbox_state.trace_add('write', checkbox_update)


# fix focusing issues
window.bind_all('<Button>', lambda event: event.widget.focus_set())


# run
window.mainloop()

