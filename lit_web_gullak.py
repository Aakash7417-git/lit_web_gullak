from datetime import datetime
import json
import matplotlib.pyplot as plt
import streamlit as st

file_name = "main.json"

# --- 1. GODOWN (Data Storage) ---
def load_memory():
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"total_balance": 0.0, "history": []}

def save_memory(data):
    with open(file_name, "w") as file:
        json.dump(data, file)

# --- 2. ARTIST (Chart Generator) ---
def draw_chart(gullak_data):
    date_list = ["start"]
    amount_list = [0]
    running_total = 0

    for reciept in gullak_data["history"]:
        date_list.append(reciept["date"])
        running_total += reciept["amount"]
        amount_list.append(running_total)

    # Web par graph dikhane ke liye figure object banate hain
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(date_list, amount_list, marker="o", color="green")
    
    for i in range(len(date_list)):
        ax.text(date_list[i], amount_list[i], str(amount_list[i]))
        
    plt.xticks(rotation=45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    # Web page par graph deliver karna
    st.pyplot(fig)

# --- 3. MANAGER (Web Interface Flow) ---
def main():
    st.set_page_config(page_title="Gullak Tracker", page_icon="🪙")
    st.title("🪙 Piggy Bank Tracker")

    gullak_data = load_memory()

    # Total Balance Card
    st.metric(label="Current Balance", value=f"₹{gullak_data['total_balance']:.2f}")

    st.write("---")

    # Amount Input Box
    saved_input = st.number_input("Aaj kitne rupay save kare?", min_value=0.0, step=10.0, format="%.2f")

    if st.button("Gullak Mein Daalo", use_container_width=True):
        if saved_input > 0:
            aaj_ki_date = datetime.now().strftime("%Y-%m-%d")
            gullak_data["total_balance"] += saved_input
            gullak_data["history"].append({"date": aaj_ki_date, "amount": saved_input})
            save_memory(gullak_data)
            st.success(f"₹{saved_input} safaltapoorvak gullak mein jama ho gaye!")
            st.rerun()
        else:
            st.warning("Kripya 0 se zyada amount daalein.")

    # History Section (Collapsible Accordion / Icon click jaisa)
    with st.expander("📜 History & Realtime Graph"):
        if gullak_data["history"]:
            st.subheader("Savings Growth (Cumulative)")
            draw_chart(gullak_data)
            
            st.subheader("Raw Ledger")
            # Ulti list dikhayenge taaki nayi transaction sabse upar dikhe
            for item in reversed(gullak_data["history"]):
                st.write(f"📅 **{item['date']}**: ₹{item['amount']}")
        else:
            st.info("Abhi tak koi transaction record nahi hui hai.")

if __name__ == "__main__":
    main()