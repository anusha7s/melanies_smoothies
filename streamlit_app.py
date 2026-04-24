# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd   # ✅ NEW (required)

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
# Fetch fruit data (NOW includes SEARCH_ON)
# ----------------------------------
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark → Pandas (IMPORTANT STEP)
pd_df = my_dataframe.to_pandas()

# Optional debug (use if needed)
# st.dataframe(pd_df)
# st.stop()

# ----------------------------------
# Multiselect (uses FRUIT_NAME)
# ----------------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],   # ✅ correct source
    max_selections=5
)

# ----------------------------------
# Process selection
# ----------------------------------
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        # ✅ KEY LINE (core of this step)
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        # Show mapping
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Build ingredients string
        ingredients_string += fruit_chosen + ' '

        # ----------------------------------
        # API CALL (USE search_on, NOT fruit_chosen)
        # ----------------------------------
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.error(f"API returned error for {fruit_chosen}")

        except Exception as e:
            st.error(f"Error fetching data: {e}")

    # ----------------------------------
    # Submit Order
    # ----------------------------------
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

            st.success(
                f'Your Smoothie is ordered, {name_on_order}!',
                icon="✅"
            )
