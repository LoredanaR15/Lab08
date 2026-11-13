from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultati = []

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()

            prezzi_mese = []

            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro)

            if len(prezzi_mese) > 0:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultati.append((distributore.nome, media))

        return risultati

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # CONDIZIONE TERMINALE: abbiamo completato tutti i 7 giorni
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        # Provo tutti i distributori per il giorno corrente
        for id_distributore in prezzi_settimana:

            prezzo_litro = prezzi_settimana[id_distributore][giorno - 1]

            if prezzo_litro is None:
                continue

            # Costo del rifornimento di 100 litri
            costo_giorno = prezzo_litro * 100

            # Aggiungo 5 euro se cambio distributore
            if ultimo_distributore is not None and ultimo_distributore != id_distributore:
                costo_giorno += 5

            nuovo_costo = costo_corrente + costo_giorno

            # Evito di continuare se il costo è già troppo alto
            if self.__costo_ottimo != -1 and nuovo_costo >= self.__costo_ottimo:
                continue

            # Aggiungo il distributore alla sequenza
            sequenza_parziale.append(id_distributore)

            # CHIAMATA RICORSIVA
            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                nuovo_costo,
                prezzi_settimana
            )

            # BACKTRACKING
            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()

            prezzi_primi_7_giorni = [None] * 7

            for prezzo in prezzi:
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7:
                    indice = prezzo.data.day - 1
                    prezzi_primi_7_giorni[indice] = prezzo.prezzo_litro

            prezzi_settimana[distributore.id] = prezzi_primi_7_giorni

        return prezzi_settimana