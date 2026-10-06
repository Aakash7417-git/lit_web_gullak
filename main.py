from datetime import datetime
import json
import matplotlib.pyplot as plt

file_name = "main.json"
def load_memory():
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"total_balance": 0, "history": []}

def save_memory(data):
    with open(file_name, "w") as file:
        json.dump(data, file)

def main():
    gullak_data = load_memory()
    while True:
        print(f"current balance: {gullak_data["total_balance"]}")
        money_saved = input("Aaz kitne rupay save kre?: ")
        if money_saved.lower() == "q":
            break
        else:
            try:
                amount = float(money_saved)
                gullak_data["total_balance"] = gullak_data["total_balance"] + amount
            except ValueError:
                print("please enter numbers only")
                
        aaj_ki_date = datetime.now().strftime("%Y-%m-%d")
        gullak_data['history'].append({"date": aaj_ki_date, "amount": amount})
        save_memory(gullak_data)
        draw_chart(gullak_data)

def draw_chart(gullak_data):
    date_list = ["start"]
    amount_list = [0]
    running_total = 0

    for reciept in gullak_data["history"]:
        date_list.append(reciept["date"])
        running_total += reciept["amount"]
        amount_list.append(running_total)

    plt.plot(date_list, amount_list, marker = "o", color="green")
    for i in range(len(date_list)):
        plt.text(date_list[i], amount_list[i], str(amount_list[i]))
    plt.xticks(rotation=45)
    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.show()

if __name__ == "__main__":
    main()


