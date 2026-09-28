import random


class Prostredie:
    """Uchováva svet; agent z neho dostáva iba vnemy cez senzor."""

    # Riadok rastie smerom dole, stĺpec smerom doprava.
    SMERY = {
        "hore": (-1, 0),
        "dole": (1, 0),
        "vlavo": (0, -1),
        "vpravo": (0, 1),
    }

    # Veľkosť: (počet stien, počet ovocia, limit krokov)
    NASTAVENIA = {
        3: (1, 1, 30),
        5: (5, 3, 100),
        10: (25, 8, 400),
    }

    def __init__(self, velkost=3, seed=0):
        if velkost not in self.NASTAVENIA:
            raise ValueError("Veľkosť mapy musí byť 3, 5 alebo 10.")

        self.velkost = velkost
        self.seed = seed
        self._nahoda = random.Random(seed)
        self._pocet_stien, self._pocet_ovocia, self.limit_krokov = (
            self.NASTAVENIA[velkost]
        )
        self._start = (0, 0)
        self._ciel = (velkost - 1, velkost - 1)
        self._poloha_agenta = self._start
        self._vygeneruj_mapu()
        self._pocet_krokov = 0
        self._nazbierane_ovocie = 0
        self._posledny_pohyb_uspesny = None
        self._prave_zobral_ovocie = False

    def je_koniec(self):
        """Beh končí v cieli alebo vyčerpaním limitu krokov."""
        return (self._poloha_agenta == self._ciel
                or self._pocet_krokov >= self.limit_krokov)

    def vykonaj_akciu(self, smer):
        """Vykoná pohyb a vráti aktuálny vnem agenta."""
        if smer not in self.SMERY:
            raise ValueError("Smer musí byť hore, dole, vlavo alebo vpravo.")
        if self.je_koniec():
            raise RuntimeError("Beh sa už skončil. Vytvor nové prostredie.")

        # Aj náraz do steny alebo okraja spotrebuje jeden krok.
        self._pocet_krokov += 1
        self._posledny_pohyb_uspesny = False
        self._prave_zobral_ovocie = False
        r, s = self._poloha_agenta
        dr, ds = self.SMERY[smer]
        nr, ns = r + dr, s + ds

        if (0 <= nr < self.velkost and 0 <= ns < self.velkost
                and self._mapa[nr][ns] != "#"):
            self._poloha_agenta = (nr, ns)
            self._posledny_pohyb_uspesny = True
            if self._mapa[nr][ns] == "~":
                self._nazbierane_ovocie += 1
                self._prave_zobral_ovocie = True
                # Ovocie zmizne, takže ho nemožno zbierať opakovane.
                self._mapa[nr][ns] = "."

        return self.vnimaj()

    def vysledok(self):
        """Priebežné alebo konečné údaje na vyhodnotenie experimentu."""
        return {
            "uspech": self._poloha_agenta == self._ciel,
            "pocet_krokov": self._pocet_krokov,
            "nazbierane_ovocie": self._nazbierane_ovocie,
            "koniec": self.je_koniec(),
        }

    def zobraz(self):
        """Vypíše celú mapu pre človeka; nejde o senzor agenta."""
        print(f"\nMapa {self.velkost} × {self.velkost}, SEED: {self.seed}")
        for r, riadok in enumerate(self._mapa):
            zobrazeny_riadok = []
            for s, policko in enumerate(riadok):
                if (r, s) == self._poloha_agenta:
                    zobrazeny_riadok.append("A")
                elif (r, s) == self._start:
                    zobrazeny_riadok.append("S")
                else:
                    zobrazeny_riadok.append(policko)
            # Znaky A a S pridávame iba do výpisu, mapu nemeníme.
            print(" ".join(zobrazeny_riadok))
        print("A = agent, S = štart, C = cieľ, # = stena, ~ = ovocie, . = voľno")
        print(f"Kroky: {self._pocet_krokov}/{self.limit_krokov} | "
              f"Ovocie: {self._nazbierane_ovocie}/{self._pocet_ovocia}")
        if self._poloha_agenta == self._ciel:
            print("Cieľ dosiahnutý!")
        elif self.je_koniec():
            print("Limit krokov vyčerpaný.")

    def _vygeneruj_mapu(self):
        # # = stena, . = voľné políčko, ~ = ovocie, C = cieľ rozmiestnenie stien a ovocia
        policka = [
            (r, s)
            for r in range(self.velkost) ##riadok
            for s in range(self.velkost) ##stlpec
            if (r, s) not in (self._start, self._ciel)
        ]

        for _ in range(100): ##pokusy aby sa našla mapa s cestou k cieľu a dostatkom voľných políčok
            steny = self._nahoda.sample(policka, self._pocet_stien)
            self._vytvor_mapu(steny)
            dostupne = self._dostupne_policka()
            if (self._ciel in dostupne
                    and len(dostupne) >= self._pocet_ovocia + 2):
                break
        else:
            # Záložný postup: vyhradíme cestu doprava a dole.
            kroky = [(0, 1)] * (self.velkost - 1)
            kroky += [(1, 0)] * (self.velkost - 1)
            self._nahoda.shuffle(kroky)
            r, s = self._start ##suradnice startu
            cesta = {self._start}
            for dr, ds in kroky: ## posun v smere kroku
                r, s = r + dr, s + ds
                cesta.add((r, s))
            mimo_cesty = [p for p in policka if p not in cesta]
            steny = self._nahoda.sample(mimo_cesty, self._pocet_stien)
            self._vytvor_mapu(steny)
            dostupne = self._dostupne_policka()

        # Zoradenie zabezpečí stabilné poradie pred náhodným výberom.
        miesta_pre_ovocie = sorted(dostupne - {self._start, self._ciel})
        for r, s in self._nahoda.sample(miesta_pre_ovocie, self._pocet_ovocia):
            self._mapa[r][s] = "~"

    def _vytvor_mapu(self, steny):
        ## zostavi mapu s danými stenami a cieľom
        self._mapa = [["."] * self.velkost for _ in range(self.velkost)] ##zatial len prazdne bludisko
        for r, s in steny:
            self._mapa[r][s] = "#" ##nastavenie stien
        r, s = self._ciel
        self._mapa[r][s] = "C" ##nastavenie cieľa

    def _dostupne_policka(self):
        """Kontrola mapy pre generátor; agent tento výsledok nedostáva."""
        dostupne = {self._start}
        na_preskumanie = [self._start]
        while na_preskumanie: ##dokym nie je prázdny zoznam na preskúmanie
            r, s = na_preskumanie.pop() ##vyberie sa posledný prvok zo zoznamu
            for dr, ds in self.SMERY.values():
                nr, ns = r + dr, s + ds
                if (0 <= nr < self.velkost and 0 <= ns < self.velkost ##kontrola ci sa nachádza v mape
                        and self._mapa[nr][ns] != "#" ## kontrola ci nie je stena
                        and (nr, ns) not in dostupne): ##kontrola ci sme už nepreskúmali
                    dostupne.add((nr, ns))
                    na_preskumanie.append((nr, ns))
        return dostupne

    def vnimaj(self): ##senzor agenta
        riadok, stlpec = self._poloha_agenta
        susedia = {} ##ziskame aktualnu polohu agenta a vytvorime prazdny slovnik pre informacie o susedoch

        for smer, (posun_riadku, posun_stlpca) in self.SMERY.items(): ##prechadzame vsetky smery a ziskavame posun v riadku a stlpci
            novy_riadok = riadok + posun_riadku
            novy_stlpec = stlpec + posun_stlpca

            # Priestor mimo mapy považujeme za stenu.
            policko = "#"
            if (0 <= novy_riadok < len(self._mapa)
                    and 0 <= novy_stlpec < len(self._mapa[0])):
                policko = self._mapa[novy_riadok][novy_stlpec]

            susedia[smer] = {
                "priechodne": policko != "#",
                "ovocie": policko == "~",
            }

        return {
            "susedia": susedia,
            "v_cieli": self._mapa[riadok][stlpec] == "C",
            "pohyb_uspesny": self._posledny_pohyb_uspesny,
            "zobral_ovocie": self._prave_zobral_ovocie,
            "zostavajuce_kroky": max(0, self.limit_krokov - self._pocet_krokov),
            "koniec": self.je_koniec(),
        }
