from tkinter import *
from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import zillow_data as zlw
import apartment_scraper as apt
import recommendation_system as rs
import data_viz as dz
import warnings
warnings.filterwarnings("ignore")

def raise_frame(frame):
    frame.tkraise()

# Create a custom font for old-fashioned style
custom_font = ("Courier", 24, "bold")
f = ("Courier", 16)

root = Tk()
root.geometry('800x600')
root.title('Move In')
#root['bg']='#000000'

main_page = Frame(root)
basic_info = Frame(root)
choose_area = Frame(root)
visualization = Frame(root)
housing = Frame(root)

# Configure row and column weights to make frames expand
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

for frame in (main_page, basic_info, choose_area, visualization, housing):
    frame.grid(row=0, column=0, sticky='news')

############################################
# PAGE ONE
############################################

def typewriter_effect(text, index = 0):
    if index < len(text):
        label.config(text=label.cget("text") + text[index])
        index += 1
        #ws.after(100, typewrite, text, index)
        main_page.after(100, lambda: typewriter_effect(text_to_type, index))


# Text to be displayed
text_to_type = """
Hello There
We Heard You Are Moving To Pittsburgh
Exciting!!
Except If You Are Going To CMU ;(
Need A New Home?
Let Us Help!
"""

# Create a label for displaying text with the custom font and center alignment
label = Label(main_page, text="", font=custom_font, justify="center")
label.pack(expand=True, fill="both")

typewriter_effect(text_to_type)

Button(
    main_page, 
    text="Get Started", 
    font=f, 
    command=lambda:raise_frame(choose_area),
    width=15,
    height=5).pack(side='bottom')


############################################
# PAGE TWO
############################################

Label(
    basic_info,
    text="TELL US ABOUT YOURSELF",
    font=custom_font,
    pady=80,
).pack(anchor="center")

household_size_label = Label(basic_info, text="Number of People in Household:", font = f)
household_size_label.pack()

# Create and pack an entry widget for the household size
household_size_entry = Entry(basic_info, font = f)
household_size_entry.pack()

# Create and pack a label for the housing choice
housing_choice_label = Label(basic_info, text="Housing Choice:", font = f)
housing_choice_label.pack()

# Create a variable to store the housing choice
housing_choice_var = StringVar()
housing_choice_var.set("Apartment")  # Default choice

# Create and pack radio buttons for housing choice
apartment_radio = Radiobutton(basic_info, text="Apartment", variable=housing_choice_var, value="Apartment", font = f)
apartment_radio.pack()
house_radio = Radiobutton(basic_info, text="House", variable=housing_choice_var, value="House", font = f)
house_radio.pack()
both_radio = Radiobutton(basic_info, text="Both", variable=housing_choice_var, value="Both", font = f)
both_radio.pack()

# Create and pack a label for the rent budget
rent_budget_label = Label(basic_info, text="Rent Budget:", font = f)
rent_budget_label.pack()

# Create and pack an entry widget for the rent budget
rent_budget_entry = Entry(basic_info, font = f)
rent_budget_entry.pack()

############################################
# PAGE THREE
############################################
# Create and display the image
image_1 = PhotoImage(file="map copy.png")  # Replace with your image file path

# Calculate the desired width and height based on a percentage of the original dimensions
desired_width_percentage = 100  # Adjust as needed
desired_height_percentage = 80  # Adjust as needed

original_width = image_1.width()
original_height = image_1.height()

desired_width = (desired_width_percentage / 100) * original_width
desired_height = (desired_height_percentage / 100) * original_height

# Resize the image to the desired dimensions
image_1 = image_1.subsample(int(original_width / desired_width), int(original_height / desired_height))

image_label = Label(choose_area, image=image_1)
image_label.pack()

# Create a frame to hold the area_label and area_dropdown
area_frame = Frame(choose_area)
area_frame.pack()

# Area Label
area_label = Label(area_frame, text="Area You Are Going To Live In:", font=f)
area_label.pack(side=LEFT)

# List of areas
areas = ["Squirrel Hill", "Brookline", "Lawrenceville", "Point Breeze", "Shadyside"]
area_var = StringVar()
area_dropdown = ttk.Combobox(area_frame, textvariable=area_var, values=areas, font=("Helvetica", 12))
area_dropdown.pack(side=LEFT)

Button(
    choose_area, 
    text="Previous", 
    font=f, 
    command=lambda:raise_frame(main_page),
    width=15,
    height=5).pack(side='left', anchor='sw')

# Function to get the selected area
def get_selected_area():
    selected_area = area_var.get()
    dz.create_image(selected_area)
    return selected_area

#dz.create_image(area)

Button(
    choose_area, 
    text="Forward", 
    font=f, 
    command=lambda:(get_selected_area(), choose_area.after(2000, lambda: raise_frame(visualization))),
    width=15,
    height=5).pack(side='right', anchor='se')


############################################
# PAGE FOUR
############################################
# Load the image
image = Image.open('combined_charts.png')

# Define the maximum dimensions for the image
max_width = 800
max_height = 500

# Calculate the new size while preserving the aspect ratio
width, height = image.size
if width > max_width or height > max_height:
    if width / max_width > height / max_height:
        width = max_width
        height = int(max_width / image.width * image.height)
    else:
        height = max_height
        width = int(max_height / image.height * image.width)

# Resize the image
image = image.resize((width, height))

photo = ImageTk.PhotoImage(image)

# Create a frame for the centered image
image_frame = Frame(visualization, bg="white", width=800, height=500)
image_frame.pack_propagate(False)
image_frame.pack(expand=True)

# Create a label to display the image inside the frame
image_label = Label(image_frame, image=photo, bg="white")
image_label.photo = photo  # Prevent the image from being garbage collected
image_label.pack(expand=True)

Button(
    visualization, 
    text="Next", 
    font=f, 
    command=lambda:(clear_housing_frame(), raise_frame(housing), load_apart()),
    width=15,
    height=5).pack(side='right', anchor='sw')


Button(
    visualization, 
    text="Previous", 
    font=f, 
    command=lambda:(clear_housing_frame(),raise_frame(choose_area)),
    width=15,
    height=5).pack(side='left', anchor='sw')


############################################
# PAGE FIVE
############################################
class ApartmentInfoWidget(ttk.Frame):
    def __init__(self, master, apartment_info):
        super().__init__(master)
        # Create a border frame with a black border
        self.border_frame = ttk.Frame(self, borderwidth=2, relief="solid")
        self.border_frame.pack()
        
        # Fetch and display an image from the URL
        image_url = apartment_info.get('imgSrc', '')  # Replace with the image URL key in your data
        if image_url:
            image = self.fetch_and_display_image(image_url)
        else:
            # If no image URL is provided, create a placeholder image
            image = Image.new('RGB', (100, 100), color='gray')
        
        # Display the image
        image_label = ttk.Label(self.border_frame, image=image)
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, columnspan=2)
        
        # Other apartment information labels
        ttk.Label(self.border_frame, text=f"Apartment Name: {apartment_info['buildingName']}").grid(row=1, column=0, sticky='w')
        ttk.Label(self.border_frame, text=f"Address: {apartment_info['address']}").grid(row=2, column=0, sticky='w')
        ttk.Label(self.border_frame, text=f"Price: {apartment_info['price']}").grid(row=3, column=0, sticky='w')
        ttk.Label(self.border_frame, text=f"Rating Category: {apartment_info['rating_category']}").grid(row=4, column=0, sticky='w')
        ttk.Label(self.border_frame, text=f"Safety: {apartment_info['safety']}").grid(row=5, column=0, sticky='w')
        #ttk.Label(self.border_frame, text=f"Unique Features: {apartment_info['unique_features']}").grid(row=5, column=0, sticky='w')
        #ttk.Label(self.border_frame, text=f"Apartment Features: {apartment_info['apartment_features']}").grid(row=5, column=0, sticky='w')


    def fetch_and_display_image(self, url, size=(100, 100)):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = Image.open(BytesIO(response.content))
                # Resize the image to the specified size
                image_data = image_data.resize(size)
                image = ImageTk.PhotoImage(image_data)
                return image
            else:
                # If there's an issue with fetching the image, return a placeholder image
                return ImageTk.PhotoImage(Image.new('RGB', size, color='gray'))
        except Exception as e:
            # Handle any exceptions that may occur during image fetching
            print(f"Error fetching image: {e}")
            return ImageTk.PhotoImage(Image.new('RGB', size, color='gray'))

def select_price(x):
    if len(x.split(";")) == 1:
        return x
    else:
        return x.split(";")[0] + ";" + x.split(";")[1]

def load_apart():
    try:
        area = get_selected_area()
        selected = rs.find_apartments(area)
        selected = selected[['imgSrc', 'address', 'buildingName', 'price', 'rating_category', 'unique_features', 'apartment_features', 'safety']]
        selected['price'] = selected['price'].apply(lambda x: select_price(x))
        apartment_data = selected.to_dict(orient='records')

        # Create a parent frame to contain the apartment widgets
        apartment_widgets_frame = ttk.Frame(housing)
        apartment_widgets_frame.pack(side='top', fill='both', expand=True)

        # Create and display ApartmentInfoWidget for each apartment using grid
        for i, apartment_info in enumerate(apartment_data):
            apartment_widget = ApartmentInfoWidget(apartment_widgets_frame, apartment_info)
            
            # Use grid to place two widgets in the first row and two more in the second row
            apartment_widget.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky='nsew')

        # Configure the columns and rows to have equal weight (evenly distribute width and height)
        for i in range(2):  # Two columns
            apartment_widgets_frame.grid_columnconfigure(i, weight=1)

        for i in range((len(apartment_data) + 1) // 2):  # Number of rows
            apartment_widgets_frame.grid_rowconfigure(i, weight=1)
    except: # this is for emergency use when tkinter breaks
        selected = pd.read_csv("sample_result.csv")
        selected = selected[['imgSrc', 'address', 'buildingName', 'price', 'rating_category', 'unique_features', 'apartment_features', 'safety']]
        selected['price'] = selected['price'].apply(lambda x: select_price(x))
        apartment_data = selected.to_dict(orient='records')

        # Create a parent frame to contain the apartment widgets
        apartment_widgets_frame = ttk.Frame(housing)
        apartment_widgets_frame.pack(side='top', fill='both', expand=True)

        # Create and display ApartmentInfoWidget for each apartment using grid
        for i, apartment_info in enumerate(apartment_data):
            apartment_widget = ApartmentInfoWidget(apartment_widgets_frame, apartment_info)
            
            # Use grid to place two widgets in the first row and two more in the second row
            apartment_widget.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky='nsew')

        # Configure the columns and rows to have equal weight (evenly distribute width and height)
        for i in range(2):  # Two columns
            apartment_widgets_frame.grid_columnconfigure(i, weight=1)

        for i in range((len(apartment_data) + 1) // 2):  # Number of rows
            apartment_widgets_frame.grid_rowconfigure(i, weight=1)

def clear_housing_frame():
    for widget in housing.winfo_children():
        if type(widget) == ttk.Frame:
            widget.destroy()

Button(
    housing, 
    text="Previous", 
    font=f, 
    command=lambda:(clear_housing_frame(), raise_frame(choose_area)),
    width=15,
    height=5).pack(side='left', anchor='se')

raise_frame(main_page)
root.mainloop()