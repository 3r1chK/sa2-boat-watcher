# CRC

## Entry example:
```
## Class [collaborator]
- responsibility.
```

## Config file example (conf.ini):
```
[General]
username = 534
key = ABCDEF323WFW
period = 30
[Boat]
name = My Boat
type = 50' catamaran
polar_file = polars/cat.csv
```


---

## Main [SaWatcher]
- carica le configurazioni;
- inizializza SaWatcher.

## SaWatcher [Boat, SaApi, BoatLog]
- inizializza Boat;
- gestisce il ciclo di chiamate all'api:
 - chiama l'api ogni N secondi;
 - chiama Boat.add_log() per aggiornarne lo stato.
 
## SaApi [BoatLog]
- chiama l'API;
- costruisce il BoatLog e lo restituisce.

## Boat [BoatPolar, BoatLog]
- inizializza il proprio BoatPolar
- fornisce il metodo add_log() per:
 - aggiungere un BoatLog;
 - aggiornare il BoatPolar con il metodo update_from_log().
 
## BoatPolar
- carica il polar file dal file csv della barca, o ne crea uno se non esiste;
- fornisce il metodo update_from_log() per aggiornare il polar file con un nuovo log:
 - nello specifico, deve conservare l'entry con il valore TWS più alto.
 
## BoatLog
- struttura che conserva i dati ottenuti in risposta dall'api.

## Utils
- fornisce un metodo statico per calcolare il TWA a partire dai dati disponibili.
