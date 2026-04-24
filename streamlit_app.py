# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# UI
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert dataframe to list of strings
fruit_rows = my_dataframe.collect()
fruit_list = [row['FRUIT_NAME'] for row in fruit_rows]

# Multiselect (max 5)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Stop if too many selected (extra safety)
if len(ingredients_list) > 5:
    st.warning("Please select no more than 5 ingredients.")
    st.stop()

# Process selection
if ingredients_list:

    # ✅ Build ingredients string safely
    ingredients_string = ' '.join(ingredients_list)

    # Show nutrition info for each fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    # ✅ Submit button OUTSIDE loop
    if st.button('Submit Order'):
        if not name_on_order:
            st.warning("Please enter a name for your smoothie.")
        else:
            session.sql(
                """
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES (?, ?)
                """,
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
