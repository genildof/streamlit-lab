import streamlit as st
import pandas as pd


tab1, tab2, tab3, tab4 = st.tabs(["Show More", "Data Editor", 'Dataframe Pagination', "Data Wizard"])

with tab1:

    def on_more_click(show_more, idx):
        show_more[idx] = True


    def on_less_click(show_more, idx):
        show_more[idx] = False


    if "show_more" not in st.session_state:
        st.session_state["show_more"] = dict.fromkeys([1, 2, 3], False)
    show_more = st.session_state["show_more"]

    cols = st.columns(2)
    fields = ["id", "content"]

    # header
    for col, field in zip(cols, fields):
        col.write("**" + field + "**")

    # rows
    for idx, row in zip([1, 2, 3], ["test1", "test2", "test3"]):

        col1, col2 = st.columns(2)
        col1.write(str(idx))
        placeholder = col2.empty()

        if show_more[idx]:
            placeholder.button(
                "less", key=str(idx) + "_", on_click=on_less_click, args=[show_more, idx]
            )

            # do stuff
            st.write("This is some more stuff with a checkbox")
            temp = st.selectbox("Select one", ["A", "B", "C"], key=idx)
            st.write("You picked ", temp)
            st.write("---")
        else:
            placeholder.button(
                "more",
                key=idx,
                on_click=on_more_click,
                args=[show_more, idx],
                type="primary",
            )

with tab2:

    df = pd.DataFrame(
        [
        {"command": "st.selectbox", "rating": 4, "is_widget": True},
        {"command": "st.balloons", "rating": 5, "is_widget": False},
        {"command": "st.time_input", "rating": 3, "is_widget": True},
    ]
    )
    edited_df = st.experimental_data_editor(df)

    favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
    st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

with tab3:

    #st.set_page_config(layout="centered")

    @st.cache_data(show_spinner=False)
    def load_data(file_path):
        dataset = pd.read_csv(file_path)
        return dataset


    @st.cache_data(show_spinner=False)
    def split_frame(input_df, rows):
        df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
        return df


    file_path = st.file_uploader("Select CSV file to upload", type=["csv"])
    if file_path:
        dataset = load_data(file_path)
        top_menu = st.columns(3)
        with top_menu[0]:
            sort = st.radio("Sort Data", options=["Yes", "No"], horizontal=1, index=1)
        if sort == "Yes":
            with top_menu[1]:
                sort_field = st.selectbox("Sort By", options=dataset.columns)
            with top_menu[2]:
                sort_direction = st.radio(
                    "Direction", options=["⬆️", "⬇️"], horizontal=True
                )
            dataset = dataset.sort_values(
                by=sort_field, ascending=sort_direction == "⬆️", ignore_index=True
            )
        pagination = st.container()

        bottom_menu = st.columns((4, 1, 1))
        with bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=[25, 50, 100])
        with bottom_menu[1]:
            total_pages = (
                int(len(dataset) / batch_size) if int(len(dataset) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1
            )
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")

        pages = split_frame(dataset, batch_size)
        pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

with tab4:

    import uuid

    if "rows" not in st.session_state:
        st.session_state["rows"] = []

    rows_collection = []

    def add_row():
        element_id = uuid.uuid4()
        st.session_state["rows"].append(str(element_id))

    def remove_row(row_id):
        st.session_state["rows"].remove(str(row_id))

    def generate_row(row_id):
        row_container = st.empty()
        row_columns = row_container.columns((3, 2, 1))
        row_name = row_columns[0].text_input("Item Name", key=f"txt_{row_id}")
        row_qty = row_columns[1].number_input("Item Quantity", step=1, key=f"nbr_{row_id}")
        row_columns[2].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])
        return {"name": row_name, "qty": row_qty}

    st.title("Item Inventory")

    for row in st.session_state["rows"]:
        row_data = generate_row(row)
        rows_collection.append(row_data)

    menu = st.columns(2)

    with menu[0]:
        st.button("Add Item", on_click=add_row)
    if len(rows_collection) > 0:
        st.subheader("Collected Data")
        display = st.columns(2)
        data = pd.DataFrame(rows_collection)
        data.rename(columns={"name": "Item Name", "qty": "Quantity"}, inplace=True)
        display[0].dataframe(data=data, use_container_width=True)
        display[1].bar_chart(data=data, x="Item Name", y="Quantity")
