import sys
from math import gcd

ALFABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

P_ANG = {'A': .082, 'B': .015, 'C': .028, 'D': .043, 'E': .127, 'F': .022,
         'G': .020, 'H': .061, 'I': .070, 'J': .002, 'K': .008, 'L': .040,
         'M': .024, 'N': .067, 'O': .075, 'P': .019, 'Q': .001, 'R': .060,
         'S': .063, 'T': .091, 'U': .028, 'V': .010, 'W': .023, 'X': .001,
         'Y': .020, 'Z': .001}

SZYFROGRAM = (
    "IZAFRJCFWHOJUBIEFMZUFIZURTEFBBJSSHDMPJEAJSVDCJTCLRPSJWHUBJIRMZ"
    "PVCIOUZLGZEFSABZOIDFUHTZLGFSRJUHFEEREJXHICJBMPJEAJSVJIOZEEZDBM"
    "HBIFUTCJIHTIPUFEGFIIHUSBLFIHUJFEBPBHAJSTZSBIUPTIJZSDHUHWHURVZZ"
    "ANPFEJIR"
)

def oczysc_tekst(tekst):
    tekst = tekst.upper()
    return "".join(znak for znak in tekst if znak in ALFABET)

def litera_na_liczbe(litera):
    return ord(litera) - ord('A')

def liczba_na_litere(liczba):
    return chr((liczba % 26) + ord('A'))

def odwrotnosc_modulo(a, modulo=26):
    if gcd(a, modulo) != 1:
        raise ValueError(
            f"Liczba {a} nie ma odwrotnosci modulo {modulo}"
        )

    return pow(a, -1, modulo)

def szyfruj(tekst, a, b):
    tekst = oczysc_tekst(tekst)
    wynik = []

    for znak in tekst:
        x = litera_na_liczbe(znak)
        y = (a * x + b) % 26
        wynik.append(liczba_na_litere(y))

    return "".join(wynik)

def deszyfruj(szyfrogram, a, b):
    odwrotne_a = odwrotnosc_modulo(a)
    wynik = []

    for znak in oczysc_tekst(szyfrogram):
        y = litera_na_liczbe(znak)
        x = (odwrotne_a * (y - b)) % 26
        wynik.append(liczba_na_litere(x).lower())

    return "".join(wynik)

def histogram(tekst):
    tekst = oczysc_tekst(tekst)

    return {
        litera: tekst.count(litera)
        for litera in ALFABET
    }

def wskaznik_angielski(tekst):
    tekst = oczysc_tekst(tekst)

    if not tekst:
        return 0.0

    suma = sum(P_ANG[litera] for litera in tekst)

    return suma / len(tekst)

def najczestsze_litery(szyfrogram, ile=6):
    licznik = histogram(szyfrogram)

    return sorted(
        ALFABET,
        key=lambda litera: (-licznik[litera], litera)
    )[:ile]

def najczestsze_angielskie(ile=6):
    return sorted(
        ALFABET,
        key=lambda litera: -P_ANG[litera]
    )[:ile]

def znajdz_klucze(x1, y1, x2, y2):
    roznica_x = (x1 - x2) % 26
    roznica_y = (y1 - y2) % 26

    d = gcd(roznica_x, 26)

    if roznica_y % d != 0:
        return []

    modulo = 26 // d

    if modulo == 1:
        a0 = 0
    else:
        odwrotnosc = pow(
            roznica_x // d,
            -1,
            modulo
        )

        a0 = (
            (roznica_y // d) * odwrotnosc
        ) % modulo

    mozliwe_klucze = []

    for a in range(a0, 26, modulo):
        b = (y1 - a * x1) % 26
        mozliwe_klucze.append((a, b))

    return mozliwe_klucze

def kryptoanaliza(szyfrogram, prog=0.055):
    szyfrogram = oczysc_tekst(szyfrogram)

    licznik = histogram(szyfrogram)

    print(
        "Histogram:",
        " ".join(
            f"{litera}:{licznik[litera]}"
            for litera in ALFABET
            if licznik[litera] > 0
        )
    )

    szyfrowe_litery = najczestsze_litery(szyfrogram)
    angielskie_litery = najczestsze_angielskie()

    print(
        "Najczestsze w szyfrogramie:",
        szyfrowe_litery,
        " w angielskim:",
        [litera.lower() for litera in angielskie_litery]
    )

    nieskuteczne = []

    for i in range(len(angielskie_litery)):
        for j in range(i + 1, len(angielskie_litery)):

            jawna_1 = angielskie_litery[i]
            jawna_2 = angielskie_litery[j]

            for szyfr_1 in szyfrowe_litery:
                for szyfr_2 in szyfrowe_litery:

                    if szyfr_1 == szyfr_2:
                        continue

                    x1 = litera_na_liczbe(jawna_1)
                    x2 = litera_na_liczbe(jawna_2)

                    y1 = litera_na_liczbe(szyfr_1)
                    y2 = litera_na_liczbe(szyfr_2)

                    hipoteza = (
                        f"{szyfr_1}={jawna_1.lower()}, "
                        f"{szyfr_2}={jawna_2.lower()}"
                    )

                    klucze = znajdz_klucze(
                        x1, y1,
                        x2, y2
                    )

                    if not klucze:
                        print(
                            f"{hipoteza}: uklad sprzeczny"
                        )
                        continue

                    for a, b in klucze:

                        if gcd(a, 26) != 1:
                            print(
                                f"{hipoteza}: (a, b) = ({a}, {b}) "
                                f"-> NIEDOPUSZCZALNY, "
                                f"NWD({a}, 26) = {gcd(a, 26)}"
                            )

                            nieskuteczne.append(
                                (a, b, "niedopuszczalny")
                            )

                            continue

                        tekst_jawny = deszyfruj(
                            szyfrogram,
                            a,
                            b
                        )

                        wynik = wskaznik_angielski(
                            tekst_jawny
                        )

                        print(
                            f"{hipoteza}: (a, b) = ({a}, {b}) "
                            f"-> {tekst_jawny[:40]}...  "
                            f"M = {wynik:.3f}"
                        )

                        if wynik >= prog:
                            return (
                                (a, b),
                                tekst_jawny,
                                nieskuteczne
                            )

                        nieskuteczne.append(
                            (a, b, "belkot")
                        )

    return None, None, nieskuteczne

def uruchom_szyfrowanie(argumenty):
    if len(argumenty) < 5:
        return False

    if argumenty[1] != "szyfruj":
        return False

    a = int(argumenty[2])
    b = int(argumenty[3])

    if gcd(a, 26) != 1:
        sys.exit(
            f"Klucz niedopuszczalny: NWD({a}, 26) = "
            f"{gcd(a, 26)}. Wybierz a nieparzyste i rozne od 13."
        )

    tekst = " ".join(argumenty[4:])

    print(szyfruj(tekst, a, b))

    return True

def main():
    if uruchom_szyfrowanie(sys.argv):
        return

    if len(sys.argv) > 2:
        szyfrogram = oczysc_tekst(
            " ".join(sys.argv[2:])
        )
    else:
        szyfrogram = SZYFROGRAM

    print(
        f"Szyfrogram ({len(szyfrogram)} liter): "
        f"{szyfrogram}\n"
    )

    znaleziony_klucz, tekst_jawny, nieskuteczne = (
        kryptoanaliza(szyfrogram)
    )

    if nieskuteczne:
        opis_nieskutecznych = ", ".join(
            f"({a}, {b}) {powod}"
            for a, b, powod in nieskuteczne
        )
    else:
        opis_nieskutecznych = "brak"

    print(
        "\nKlucze nieskuteczne:",
        opis_nieskutecznych
    )

    if znaleziony_klucz is None:
        print(
            "Nie znaleziono klucza - szyfrogram moze byc za krotki."
        )
        return

    a, b = znaleziony_klucz
    odwrotne_a = odwrotnosc_modulo(a)

    print(
        f"\nZNALEZIONY KLUCZ: (a, b) = ({a}, {b})"
    )

    print(
        f"Deszyfrowanie: d(y) = "
        f"{odwrotne_a}*(y - {b}) mod 26"
    )

    print(
        f"Tekst jawny: {tekst_jawny}"
    )

    print(
        "Sprawdzenie: szyfruj(jawny) == szyfrogram -> "
        f"{szyfruj(tekst_jawny, a, b) == szyfrogram}"
    )

if __name__ == "__main__":
    main()