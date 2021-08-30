import json
from datetime import datetime
import requests


def menu(round_one=True):
    print("*"*99)
    if round_one:
        print(f"\n*** Szia, üdvözöllek a Pénzváltó alkalmazásban! ***")

    print("-" * 99)
    print("\nAz alábbi menüpontok közül választhatsz:")
    print("1. Pénzváltás")
    print("2. Korábbi pénzváltások adatai")
    print("3. Kilépés \n")

    menu_number = int(input("Kérlek add meg a kiválasztott menüpontot: "))

    if menu_number == 1:
        exchange()
    elif menu_number == 2:
        ii_submenu()
    elif menu_number == 3:
        exit()


def ii_submenu():
    print("-" * 99)
    print("\nKorábbi pénzváltások ")
    print("\nAz alábbi menüpontok közül választhatsz:")
    print("\n1. Rendezés dátum szerint (legfrissebb elöl)")
    print("2. Keresés dátum szerint (Adott napi pénzváltások felsorolása)")
    print("3. Keresés pénznem szerint")
    print("4. Főmenü")

    menu_number = int(input("\nKérlek add meg a kiválasztott menüpontot: "))

    if menu_number == 1 or menu_number == 2 or menu_number == 3:
        historic(menu_number)
    elif menu_number == 4:
        menu(False)


def historic(menu_number):
    exchange_history = opener("exchange_history.json")
    sorted_exchange_history = reversed(sorted(exchange_history))

    if menu_number == 1:
        print("\nAz összes korábbi pénzváltás:")
        print('')
        for i in sorted_exchange_history:
            print(f'{exchange_history[i]["date_time"]}, {exchange_history[i]["input_currency_value"]:f}  '
                  f'{exchange_history[i]["input_currency"]} = {exchange_history[i]["result_value"]:f} '
                  f'{exchange_history[i]["output_currency"]}, '
                  f'Árfolyam: {exchange_history[i]["result_value"] / exchange_history[i]["input_currency_value"]:f}')

    elif menu_number == 2:
        year = int(input("Év: "))
        month = int(input("Hónap: "))
        day = int(input("Nap: "))
        print(f"\nA(z) {datetime(year, month, day)} napon történt összes pénzváltás:\n")
        for i in exchange_history:
            if datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') >= datetime(year, month, day) and datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') < datetime(year, month, day+1):
                print(f'{exchange_history[i]["date_time"]}, {exchange_history[i]["input_currency_value"]:f}  '
                      f'{exchange_history[i]["input_currency"]} = {exchange_history[i]["result_value"]:f} '
                      f'{exchange_history[i]["output_currency"]}, '
                      f'Árfolyam: {exchange_history[i]["result_value"] / exchange_history[i]["input_currency_value"]:f}')

    elif menu_number == 3:
        currency = input("Add meg a pénznemet: \n").upper()
        print(f"A(z) {currency} összes rögzített átváltása:")
        for i in exchange_history:
            if exchange_history[i]["input_currency"] == currency or exchange_history[i]["output_currency"] == currency:
                print(f'{exchange_history[i]["date_time"]}, {exchange_history[i]["input_currency_value"]:f}  '
                      f'{exchange_history[i]["input_currency"]} = {exchange_history[i]["result_value"]:f} '
                      f'{exchange_history[i]["output_currency"]}, '
                      f'Árfolyam: {exchange_history[i]["result_value"] / exchange_history[i]["input_currency_value"]:f}')

    ii_submenu()


def exchange():

    print("\nA legutóbbi 5 pénzváltás: \n")
    exchange_history = opener("exchange_history.json")
    sorted_exchange_history = reversed(sorted(exchange_history))
    api_downloader("exchange_data.json")
    exchange_data = opener("exchange_data.json")
    exchange_data_sorted = sorted(exchange_data["rates"])
    turn = 0
    for i in sorted_exchange_history:
        turn += 1
        if turn > 5:
            break
        if datetime.strptime(i, '%Y-%m-%d-%H:%M:%S') <= datetime.now():
            print(f'{turn}: {exchange_history[i]["date_time"]}, {exchange_history[i]["input_currency"]} -> '
                  f'{exchange_history[i]["output_currency"]}')

    input_currency_value = float(input("\nÁtváltandó pénzösszeg: "))

    column = int(input("\nMennyi oszlopban szeretnéd látni az átváltható pénznemeket?"))
    h = 0
    for i in exchange_data_sorted:
        if h % column == 0:
            print("")
        print(i + " ", end="")
        h += 1
    print("")

    input_currency = input("Kérlek add meg melyik pénznemről szeretnél átváltani! ").upper()
    output_currency = input("Kérlek add meg melyik pénznemre szeretnél átváltani! ").upper()

    # Itt deklarálom a számoláshoz szükséges változókat és elvégzem a számolásokat
    base_currency = exchange_data["base"]
    base_currency_exchange_rate = exchange_data["rates"][base_currency]  # elvileg ez mindig 1
    input_currency_exchange_rate = exchange_data["rates"][input_currency]
    output_currency_exchange_rate = exchange_data["rates"][output_currency]
    result_value = (base_currency_exchange_rate/input_currency_exchange_rate) * \
                   output_currency_exchange_rate * input_currency_value
    date_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    print(f'\n {input_currency_value} {input_currency} = {result_value:f} {output_currency} ')

    file_write("exchange_history.json", date_time, base_currency, input_currency, output_currency, input_currency_value,
               input_currency_exchange_rate,output_currency_exchange_rate, result_value)


def opener(file_name):

    with open(file_name) as json_file:
        data = json.load(json_file)
    return data


def api_downloader(file_to_write):
    exchange_data_respons = requests.get(
        "http://api.exchangeratesapi.io/v1/latest?access_key=6913b0c2155049a324886cbf6af0eb5f")

    data = exchange_data_respons.json()
    with open(file_to_write, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def file_write(file_name, date_time, base_currency, input_currency, output_currency, input_currency_value, input_currency_exchange_rate, output_currency_exchange_rate, result_value):
    data_dict = {
        date_time: {
            "date_time": date_time,
            "base_currency": base_currency,
            "input_currency": input_currency,
            "output_currency": output_currency,
            "input_currency_value": input_currency_value,
            "input_currency_exchange_rate": input_currency_exchange_rate,
            "output_currency_exchange_rate": output_currency_exchange_rate,
            "result_value": result_value
            }
    }
    with open(file_name) as json_file:
        data = json.load(json_file)
#    result_data = data | data_dict
    data.update(data_dict)
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

    menu(False)


if __name__ == '__main__':
    menu(True)
