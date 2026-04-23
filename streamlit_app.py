# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# UI
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()
# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert dataframe to list of strings
fruit_rows = my_dataframe.collect()
fruit_list = [row['FRUIT_NAME'] for row in fruit_rows]

# Multiselect (max 5 enforced manually)
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_list, max_selections=5)

if len(ingredients_list) > 5:
    st.warning("Please select no more than 5 ingredients.")
    st.stop()

# Process selection
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # st.write("Your ingredients:", ingredients_string)

    # Button to submit order
    if st.button('Submit Order'):
        if not name_on_order:
            st.warning("Please enter a name for your smoothie.")
        else:
            # Safe parameterized query (recommended)
            session.sql(
                "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
