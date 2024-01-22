import configparser

import matplotlib.pyplot as plt
import numpy as np

from src.Boat import Boat


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


if __name__ == "__main__":
    config = load_config("conf.ini")

    boat = Boat(config['Boat']['name'], config['Boat']['type'], config['Boat']['polar_file'])
    # Supponendo che `polar_grid` sia la matrice con i dati STW per ogni TWA e TWS.
    polar_grid = boat.polar.polar_grid

    v = 2
    if v == 1:
        # Converti la griglia in un array numpy per una facile manipolazione
        data = np.array(polar_grid)

        # Impostazioni per il grafico
        twa_angles = np.linspace(0, 180, data.shape[0])
        tws_speeds = np.linspace(0, 80, data.shape[1])
        TWA, TWS = np.meshgrid(twa_angles, tws_speeds)
        STW = data.T  # Trasposta per allineare gli assi correttamente

        # Creazione del grafico polare
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        contour = ax.contourf(np.radians(TWA), TWS, STW)

        # Aggiungi una barra dei colori per indicare la velocità della barca
        plt.colorbar(contour)

        # Configurazione aggiuntiva del grafico
        ax.set_theta_zero_location('N')  # Zero gradi al Nord
        ax.set_theta_direction(-1)  # Direzione degli angoli in senso orario
        ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
        ax.set_title("A line plot on a polar axis", va='bottom')
        ax.grid(True)

        # Mostra il grafico
        plt.show()

    if v == 2:
        # Prepara i dati per il plot
        twa_angles_degrees = np.linspace(0, 180, len(polar_grid))  # TWA da 0 a 180 gradi
        twa_angles_radians = np.radians(twa_angles_degrees)  # Conversione in radianti per il plot

        # Imposta il grafico
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        # Per ogni TWS crea una curva nel grafico polare
        for tws in range(0, 81, 1):  # Vai da 0 a 80 inclusi solo i multipli di 1
            stw_values = [polar_grid[twa][tws] for twa in range(len(twa_angles_degrees))]
            if any(stw > 0 for stw in stw_values):
                ax.plot(twa_angles_radians, stw_values, label=f'TWS {tws} kn')

        # Configura il grafico
        ax.set_theta_zero_location('N')  # Imposta il Nord (0 gradi) in cima al grafico
        ax.set_theta_direction(-1)  # Imposta la direzione degli angoli in senso orario
        ax.set_thetamin(0)  # Imposta l'angolo minimo
        ax.set_thetamax(180)  # Imposta l'angolo massimo
        ax.set_ylim(0, max([max(row) for row in polar_grid if max(row) > 0]))  # Imposta il limite per STW

        # Aggiungi la legenda
        ax.legend(loc='upper right')

        # Mostra il grafico
        plt.show()

    if v == 3:
        # Prepariamo i dati per il plot
        twa_angles_degrees = np.linspace(0, 180, len(polar_grid))  # TWA da 0 a 180 gradi
        twa_angles_radians = np.radians(twa_angles_degrees)  # Conversione in radianti per il plot

        # Impostiamo il grafico
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        # Per ogni TWS divisibile per 5, crea una curva nel grafico polare
        for tws in range(0, 81, 5):  # Vai da 0 a 80 inclusi solo i multipli di 5
            stw_values = [polar_grid[twa][tws] for twa in range(len(twa_angles_degrees)) if polar_grid[twa][tws] > 0]
            valid_twa_angles = [twa_angles_radians[twa] for twa in range(len(twa_angles_degrees)) if
                                polar_grid[twa][tws] > 0]

            # Solo plot i punti validi (STW > 0)
            if stw_values:
                ax.plot(valid_twa_angles, stw_values, label=f'TWS {tws} kn', linewidth=2)

        # Aggiungiamo alcune configurazioni estetiche al grafico
        ax.set_theta_zero_location('N')  # Zero gradi al Nord
        ax.set_theta_direction(-1)  # Direzione degli angoli in senso orario
        ax.set_ylim(0, max(max(row) for row in polar_grid if row))  # Imposta il limite per STW
        ax.set_theta_offset(np.pi / 2.0)  # Sposta l'inizio degli angoli a Est (90 gradi)

        # Aggiungiamo la legenda fuori dal grafico
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

        # Mostra il grafico
        plt.show()


    if v == 4:
        # Prepariamo i dati per il plot
        twa_angles_degrees = np.linspace(0, 180, len(polar_grid))  # TWA da 0 a 180 gradi
        twa_angles_radians = np.radians(twa_angles_degrees)  # Conversione in radianti per il plot

        # Impostiamo il grafico
        fig = plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)

        # Per ogni TWS divisibile per 5, crea una curva nel grafico polare
        for tws in range(0, 81, 5):  # Vai da 0 a 80 inclusi solo i multipli di 5
            # Estraiamo i valori STW per il TWS corrente
            stw_values = [polar_grid[twa][tws] for twa in range(len(twa_angles_degrees))]
            # Assicuriamo che la curva inizi e finisca con zero
            if stw_values[0] > 0:
                stw_values.insert(0, 0)
            if stw_values[-1] > 0:
                stw_values.append(0)
            # Calcola i corrispondenti angoli TWA, aggiungendo zero dove necessario
            valid_twa_angles = twa_angles_radians
            if stw_values[0] > 0:
                valid_twa_angles = np.insert(valid_twa_angles, 0, 0)
            if stw_values[-1] > 0:
                valid_twa_angles = np.append(valid_twa_angles, np.pi)

            # Plot solo se abbiamo dati validi
            if any(stw > 0 for stw in stw_values):
                ax.plot(valid_twa_angles, stw_values, label=f'TWS {tws} kn')

        # Aggiungiamo alcune configurazioni estetiche al grafico
        ax.set_theta_zero_location('N')  # Zero gradi al Nord
        ax.set_theta_direction(-1)  # Direzione degli angoli in senso orario
        ax.set_ylim(0, max(max(row) for row in polar_grid if row))  # Imposta il limite per STW
        ax.set_theta_offset(np.pi / 2.0)  # Sposta l'inizio degli angoli a Est (90 gradi)

        # Aggiungiamo la legenda fuori dal grafico
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

        # Mostra il grafico
        plt.show()
