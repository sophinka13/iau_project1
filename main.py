import argparse

from prostredie import Prostredie


def main():
    """Ručné skúšanie prostredia pred implementáciou agenta."""
    parser = argparse.ArgumentParser(description="Ručné ovládanie bludiska.")
    parser.add_argument("--velkost", type=int, choices=[3, 5, 10], default=3)
    parser.add_argument("--seed", type=int, default=0)
    nastavenia = parser.parse_args()
    prostredie = Prostredie(nastavenia.velkost, nastavenia.seed)
    ovladanie = {"w": "hore", "s": "dole", "a": "vlavo", "d": "vpravo"}

    print("Ovládanie: w = hore, s = dole, a = vľavo, d = vpravo.")
    print("Po písmene stlač Enter. q = ukončiť.")
    prostredie.zobraz()

    while not prostredie.je_koniec():
        try:
            prikaz = input("Pohyb: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nRučné skúšanie ukončené.")
            return
        if prikaz == "q":
            print("Ručné skúšanie ukončené.")
            return
        if prikaz not in ovladanie:
            print("Použi w, s, a, d alebo q. Neplatný vstup nespotrebuje krok.")
            continue

        vnem = prostredie.vykonaj_akciu(ovladanie[prikaz])
        if not vnem["pohyb_uspesny"]:
            print("Prekážka! Agent zostáva na mieste.")
        elif vnem["zobral_ovocie"]:
            print("Pozbierala si ovocie!")
        prostredie.zobraz()


if __name__ == "__main__":
    main()
