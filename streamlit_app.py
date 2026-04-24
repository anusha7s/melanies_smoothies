# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# ----------------------------------
# UI
# ----------------------------------
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# ----------------------------------
# Snowflake connection
# ----------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# ----------------------------------
# Fetch fruit data (IMPORTANT: includes SEARCH_ON)
# ----------------------------------
fruit_df = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

fruit_rows = fruit_df.collect()

# Create mapping: UI name -> API name
fruit_dict = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

fruit_list = list(fruit_dict.keys())

# ----------------------------------
# Multiselect
# ----------------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Safety check
if len(ingredients_list) > 5:
    st.warning("Please select no more than 5 ingredients.")
    st.stop()

# ----------------------------------
# Process selection
# ----------------------------------
if ingredients_list:

    ingredients_string = ', '.join(ingredients_list)

    # Show nutrition info
    for fruit_chosen in ingredients_list:

        search_value = fruit_dict.get(fruit_chosen)

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_value.lower()}"
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.error(f"Failed to fetch data for {fruit_chosen}")

        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # ----------------------------------
    # Submit Order
    # ----------------------------------
    if st.button('Submit Order'):

        if not name_on_order:
            st.warning("Please enter a name for your smoothie.")

        else:
            try:
                session.sql(
                    """
                    INSERT INTO smoothies.public.orders 
                    (ingredients, name_on_order)
                    VALUES (?, ?)
                    """,
                    params=[ingredients_string, name_on_order]
                ).collect()

                st.success(
                    f'Your Smoothie is ordered, {name_on_order}!',
                    icon="✅"
                )

            except Exception as e:
                st.error(f"Order failed: {e}")
