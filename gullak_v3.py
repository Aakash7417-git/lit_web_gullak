from datetime import datetime
import plotly.express as px
import streamlit as st
import requests

# --- 1. GODOWN (Data Storage) ---
def load_memory(user_id):
    url = f"https://gullak-80cfa-default-rtdb.firebaseio.com/{user_id}.json"
    response = requests.get(url)
    data = response.json()

    if data is None:
        return None
    if "history" not in data:
        data["history"] = []
    data["total_balance"] = sum(r["amount"] for r in data["history"])
    return data

def save_memory(data, user_id):
    url = f"https://gullak-80cfa-default-rtdb.firebaseio.com/{user_id}.json"
    requests.put(url, json=data)


# --- 2. ARTIST (Chart Generator) ---
def draw_chart(gullak_data):
    date_list = []
    amount_list = []
    running_total = 0

    # Puraani list ko process kar rahe hain
    for reciept in gullak_data["history"]:
        date_list.append(reciept["date"])
        running_total += reciept["amount"]
        amount_list.append(running_total)

    if not date_list:
        return # Agar history khali hai toh error na aaye

    # Interactive chart ban banana
    fig = px.line(
        x=date_list, 
        y=amount_list, 
        markers=True,
        labels={"x": "Date", "y": "Amount"}
    )

    # Hover aur line ka design
    fig.update_traces(
        line_color="blue", 
        marker_color="darkgreen",
        hovertemplate="Date: %{x}<br>Amount: ₹%{y}<extra></extra>"
    )

    # Background aur Dotted Lines (Spikes) ka magic
    fig.update_layout(
        xaxis=dict(
            showgrid=False, 
            showspikes=True,
            showticklabels=False,
            spikemode="across", 
            spikedash="dot", 
            spikecolor="grey",
            spikethickness=1,
            showline=True,
            zeroline=False,
            linecolor="grey"
        ),
        yaxis=dict(
            showgrid=False, 
            showticklabels=True,  
            title="Amount", 
            tickvals=[running_total],
            ticktext=[f"₹{running_total}"],
            showspikes=True, 
            spikemode="across", 
            spikedash="dot", 
            spikecolor="darkgreen",
            spikethickness=1,
            showline=True,
            linecolor="grey"
        ),
        hovermode="closest",     # Ek hi clean line mein details dikhana
        plot_bgcolor="rgba(0,0,0,0)", # Transparent background
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    # Web par render karna
    st.plotly_chart(fig, use_container_width=True)

# --- 3. MANAGER (Web Interface Flow) ---
def main():
    st.set_page_config(page_title="Gullak Tracker", page_icon="🪙")

    if "logged_in_pin" not in st.session_state:
        st.session_state.logged_in_pin = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None 
    if st.session_state.logged_in_pin is None:
        st.title("Your Gullak welcomes you.")
        st.sidebar.title("Reception")

        i_will_like_to = st.sidebar.radio("I will like to", ["Create new account", "Go to my account"])

        if i_will_like_to == "Create new account":
            st.sidebar.subheader("new account")
            new_name = st.sidebar.text_input("Name: ")
            new_pin = st.sidebar.text_input("new pin of 4 digit(password)", type="password")
            if st.sidebar.button("open account", type="primary"):
                if new_name and new_pin:
                    new_data = {"name": new_name, "total_balance": 0.00, "history": []}
                    save_memory(new_data, new_pin)
                    st.sidebar.success("Account created sucessfully, please note down your pin somewhere, and now go back and choose 'go to my account' ")
                else:
                    st.sidebar.warning("Please enter new name and pin")
        elif i_will_like_to == "Go to my account":
            st.sidebar.subheader("Login")
            login_pin = st.sidebar.text_input("Enter your pin: ", type="password")
            if st.sidebar.button("My gullak", type="primary"):
                if login_pin:
                    data = load_memory(login_pin)
                    if data is not None:
                        st.session_state.logged_in_pin = login_pin
                        st.session_state.user_name = data.get("name", "user")
                        st.rerun()
                    else:
                        st.sidebar.error("Pin didn't match to existing account")
                else:
                    st.sidebar.warning("Please enter pin")

        st.stop()

    current_user = st.session_state.logged_in_pin
    user_name = st.session_state.user_name

    st.sidebar.title(f"Hi {user_name}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_pin = None
        st.rerun()
    st.title(f"{user_name}'s gullak")

    desk_name = f"desk_{current_user}"
    if desk_name not in st.session_state:
        st.session_state[desk_name] = load_memory(current_user)

    gullak_data = st.session_state[desk_name]

    # Total Balance Card
    st.metric(label="Current Balance", value=f"₹{gullak_data['total_balance']:.2f}")

    st.write("---")

    # Amount Input Box
    saved_input = st.number_input("Aaj kitne rupay save kare?", min_value=0.0, step=10.0, format="%.2f")

    if st.button("Gullak Mein Daalo", use_container_width=True):
        if saved_input > 0:
            aaj_ki_date = datetime.now().strftime("%y-%m-%d")
            gullak_data["total_balance"] += saved_input
            gullak_data["history"].append({"date": aaj_ki_date, "amount": saved_input})
            gullak_data["history"].sort(key=lambda x: x["date"])
            save_memory(gullak_data, current_user)
            st.success(f"₹{saved_input} safaltapoorvak gullak mein jama ho gaye!")
            st.rerun()
        else:
            st.warning("Kripya 0 se zyada amount daalein.")

    #-------past amount ke liye feature-------------

    with st.expander("Apni past entries daale"):
        st.write("Agar past ki entries daalna chahate hae: ")

        col1, col2 = st.columns(2)
        with col1:
            past_amount = st.number_input("Past amount: ", min_value=0.0, step=10.0, format="%.2f", key="past_amount")
        with col2:
            past_date = st.date_input("kis din ki saving hae?: ", max_value=datetime.now(), key="past_date")

        if st.button("Purani savings update kro", use_container_width=True, type="secondary"):
            if past_amount > 0:
                formatted_past_date = past_date.strftime("%y-%m-%d")
                gullak_data["total_balance"] += past_amount
                gullak_data["history"].append({"date": formatted_past_date, "amount": past_amount}) 
                gullak_data["history"].sort(key=lambda x : x["date"])

                save_memory(gullak_data, current_user)
                st.success(f"{past_amount} past date {formatted_past_date} ke saath zud gye hae.")
                st.rerun()
            else:
                st.warning("Amount should be greater then 0.")

    # History Section (Collapsible Accordion / Icon click jaisa)
    with st.expander("History & Realtime Graph"):
        if gullak_data["history"]:
            st.subheader("Savings Growth (Cumulative)")
            draw_chart(gullak_data)
            
            st.subheader("Raw Ledger")
            for index in range(len(gullak_data["history"]) -1, -1, -1):
                item = gullak_data["history"][index]
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Date:** {item['date']}  |  **Amount:** ₹{item['amount']}")

                with col2:
                    if st.button("del", type="primary", use_container_width=True, key=f"del_{index}"):
                        gullak_data["history"].pop(index)
                        gullak_data["total_balance"] = sum(r["amount"] for r in gullak_data["history"])
                        save_memory(gullak_data, current_user)
                        st.rerun()
        else:
            st.info("Abhi tak koi transaction record nahi hui hai.")

if __name__ == "__main__":
    main()
    