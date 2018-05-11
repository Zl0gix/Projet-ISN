# coding: utf-8
from Tkinter import *
from pprint import *
from random import randint
import os.path

phase = "init"  # les autres phases possibles sont : "in-game" / "end-game"


def initGrid(): # Retourne une liste de liste de 10*10
    liste = [0] * 10
    temp = liste[:]
    for i in range(len(liste)):
        liste[i] = temp[:]
    return liste


def nb_lignes(name): # retourne le nombre de lignes d'un fichier
    file = open(name, "r")
    temp = file.readline()
    count = 0
    while temp != "":
        count += 1
        temp = file.readline()
    file.close()
    return count


def txt_to_grid(name): # Retourne chaque caractère d'un fichier formaté (d'une manière particulière) dans une liste de liste
    if (os.path.exists(name)) and (os.path.getsize(name) > 0):
        n_lignes = nb_lignes(name)
        liste = [[0]]
        for i in range(n_lignes - 1):
            liste.append([0])
        file = open(name, "r")
        for i in range(n_lignes):
            temp = file.readline()
            stock = ""
            for car in temp:
                if car == " ":
                    if stock == "0":
                        liste[i].append(0)
                    else:
                        liste[i].append(float(stock))
                    stock = ""
                elif (car != "") and (car != "\n"):
                    stock += car
        file.close()
        return liste
    else:
        file = open(name, "w")
        file.write(grid_to_txt(zeroGrid))
        file.close()
        return zeroGrid


def determineTir(): # Determine en fonction du niveau de l'ia et de l'avancement du jeu quel mode de tir utiliser
    if IA_level.get() == 1:
        tirIA(ships, "Random")
    elif IA_level.get() == 2:
        if to_follow[0] != 0:
            tirIA(ships, "Following")
        else:
            tirIA(ships, "Random")
    elif IA_level.get() == 3:
        if len(possibleBoat) != 0:
            tirIA(ships, "Intelligent")
        if to_follow[0] != 0:
            tirIA(ships, "Following")
        else:
            tirIA(ships, "Random")


def tir_joueur(Grid, car, IA_boats): # Fonction de tir du joueur
    global TirPlayer
    if phase == "in-game":
        try:
            assert 2 <= len(car) <= 3
            lettre = car[0].upper()
            Nombre = car[1:]
            # Conversion du caractère lettre dans ex:"A10" en nombre
            for i in range(10):
                if lettre == lettres[i]:
                    x = i
            Nombre_valid = 0
            for i in range(10):
                if Nombre == str(i):
                    Nombre_valid = 1
            assert Nombre_valid == 1
            y = int(Nombre) - 1
            assert 0 <= x <= 9
            assert 0 <= y <= 9
            Indic.config(text="Coordonées acceptées")
            ship_tag = ""
            TirPlayer[x][y] = 1
            if Grid[x][y] == 1: # Si un bateau de l'ia est présent aux coordonnées du tir:
                boat_index = 0
                for b in range(len(IA_boats)):
                    for p in range(len(IA_boats[b])):
                        if (IA_boats[b][p][0] == x + 1) and (IA_boats[b][p][1] == y + 1): # Test de la présence d'un bateau
                            if IA_boats[b][p][2] == 1: # Si le bateau n'a pas déjà été touché
                                boat_index = b
                                ship_tag = IAships_name[b]
                                IA_boats[b][p][2] = 0
                                display_case(Grilles, "IA", x + 1, y + 1, 3, ship_tag)
                                IA_f_ships.set(pformat(IA_boats))
                            else:
                                Indic.config(text="Vous avez déjà tiré ici et vous aviez touché !\nDommage, vous perdez un tour")
                                # Tour de l'IA
                                determineTir()
                                return
                pts_coule = 0
                for p in range(len(IA_boats[boat_index])):
                    pts_coule += IA_boats[boat_index][p][2]
                if pts_coule == 0:
                    Grilles.itemconfig(ship_tag, fill="red")
                    Indic.config(text="Vous avez coulé le " + str(ship_tag)[2:] + " de votre adversaire !")
                    # Bateau coulé
                    finDuJeu()
            else:
                display_case(Grilles, "IA", x + 1, y + 1, 1, nametag="fail")
                # Tour de l'IA
                determineTir()
        except AssertionError:
            Indic.config(text="Les coordonées du tir ne sont pas valides\n(elles doivent être de la forme : LXX)\n(avec L une lettre et XX un nombre entre 1 et 10)")
        if car == "annihilation": # Variable de destruction totale
            for l_item in lettres:
                for n_item in range(1, 11):
                    tir_joueur(IAGrid, l_item + str(n_item), IAships)
        if car == "r-annihilation":
            for l_item in reversed_Lettres:
                for n_item in range(1, 11):
                    tir_joueur(IAGrid, l_item + str(n_item), IAships)
    else:
        Indic.config(text='Vous êtes encore en phase de placement des bateaux.\nPour commencer la bataille veuillez cliquer sur le bouton :\n"Début du combat"')


def moveboat(canvas, Grid, vehicle, direction): # Fonction de déplacement de bateau
    if phase == "init": # Test de la phase de jeu
        if len(vehicle) != 0:
            for i in range(len(ships_name)):
                if vehicle[0] == i: # Détermination du bateau choisi pour être bougé
                    boat = ships[i]
            decal = []
            for i in range(5):
                if direction == fleches[i]:
                    decal = offset[i]
            if decal != "rotation":
                testx = boat[0][0] + decal[0]
                testy = boat[0][1] + decal[1]
                if (1 <= testx <= 10) and (1 <= testy <= 10):
                    if (1 <= boat[len(boat) - 1][0] + decal[0] <= 10) and (1 <= boat[len(boat) - 1][1] + decal[1] <= 10):
                        # Test de position en bordure de map
                        for i in range(len(boat)):
                            x1 = boat[i][0]
                            y1 = boat[i][1]
                            Grid[x1 - 1][y1 - 1] -= 1
                            boat[i][0] += decal[0]
                            boat[i][1] += decal[1]
                            # Déplacement du bateau pour chaque point de ce dernier
                            x2 = boat[i][0]
                            y2 = boat[i][1]
                            Grid[x2 - 1][y2 - 1] += 1
                        Indic.config(text="Déplacement autorisé")
                        canvas.delete(ships_name[vehicle[0]])
                        for p in range(len(boat)):
                            display_case(canvas, "Player", boat[p][0], boat[p][1], 2, ships_name[vehicle[0]])
                        boat_color("rien")
                    else:
                        Indic.config(text="Vous ne pouvez pas déplacer le bateau plus loin")
                        return
                else:
                    Indic.config(text="Vous ne pouvez pas déplacer le bateau plus loin")
                    return
            else:
                if boat[0][0] == boat[1][0]:
                    # POUR SENS VERTICAL VERS HORIZONTAL
                    newlastx = boat[len(boat) - 1][0] + len(boat) - 1
                    if (1 <= newlastx <= 10):
                        for p in range(len(boat)):
                            x1 = boat[p][0]
                            y1 = boat[p][1]
                            Grid[x1 - 1][y1 - 1] -= 1
                            if p != 0:
                                boat[p][0] = boat[p - 1][0] + 1
                            boat[p][1] = boat[0][1]
                            x2 = boat[p][0]
                            y2 = boat[p][1]
                            Grid[x2 - 1][y2 - 1] += 1
                        Indic.config(text="Déplacement autorisé")
                    else:
                        Indic.config(text="Impossible de tourner le bateau")
                        return
                else:
                    # POUR SENS HORIZONTAL VERS VERTICAL
                    newlasty = boat[len(boat) - 1][1] + len(boat) - 1
                    if (1 <= newlasty <= 10):
                        for p in range(len(boat)):
                            x1 = boat[p][0]
                            y1 = boat[p][1]
                            Grid[x1 - 1][y1 - 1] -= 1
                            if p != 0:
                                boat[p][1] = boat[p - 1][1] + 1
                            boat[p][0] = boat[0][0]
                            x2 = boat[p][0]
                            y2 = boat[p][1]
                            Grid[x2 - 1][y2 - 1] += 1
                        Indic.config(text="Déplacement autorisé")
                    else:
                        Indic.config(text="Impossible de tourner le bateau")
                        return
                canvas.delete(ships_name[vehicle[0]])
                for p in range(len(boat)):
                    display_case(canvas, "Player", boat[p][0], boat[p][1], 2, ships_name[vehicle[0]])
                boat_color("rien")
            P_f_ships.set(pformat(ships))
            P_f_Grid.set(pformat(playerGrid))


def validation(Grid, ships): # Test de validation de la phase d'initialisation
    global possibleBoat, possibleSafe, IAGrid, phase, IAships
    if phase != "init":
        return
    count = 0
    if IA_level.get() == 0:
        Indic.config(text="Vous devez choisir une difficulté d'IA\nAvant de jouer")
        return
    for x in range(len(Grid)):
        for y in range(len(Grid[x])):
            if Grid[x][y] > 1:
                count += 1
    if count == 0:
        phase = "in-game"
        diff = ["facile", "intermédiaire", "difficile"]
        for i in range(len(diff)):
            if i == (IA_level.get() - 1): # Choix de la difficulté de l'IA
                difficulte = diff[i]
        Indic.config(text="Bateaux verouillés\nLa partie commence !" + "\n vous avez choisi l'IA " + difficulte)
        Grilles.itemconfig(Boatlist.get(ACTIVE), fill='blue')
        Boatlist.selection_clear(0, END)
        IAGrid = initGrid() # Positionnement des bateaux en fonction de la difficulté de l'IA
        if IA_level.get() == 1:
            set_IA_Boats(IAships)
            init_ships_Grids(IAships, IAGrid)
        elif IA_level.get() == 2:
            for i in range(len(IAships)):
                randomAssign(IAGrid, IAships[i])
            init_ships_Grids(IAships, IAGrid)
        elif IA_level.get() == 3:
            possibleBoat = initializeQueue(old_Average_Pboat, 0.3, 1)
            IA_3_Queue.set(pformat(possibleBoat))
            # possibleSafe = initializeQueue(old_Average_Pshots, 0.3, 2)
            possibleSafe = []
            for i in range(len(IAships)):
                randomAssign(IAGrid, IAships[i], possibleSafe)
            init_ships_Grids(IAships, IAGrid)
        IA_f_Grid.set(pformat(IAGrid))
        IA_f_ships.set(pformat(IAships))
    else:
        Indic.config(text="Il y a " + str(count) + " points\nde superpositions")


def saut_ligne(canvas, y, nb): # Définition de l'interligne
    for i in range(nb):
        y += 40
        canvas.create_line(0, y, 430, y, tags="core")
        canvas.create_text(15, y - 20, font=("Times", 12), text=numbers[i], tags="core")
    return y


def trace_grid(canvas): # Création de la grille
    canvas.create_rectangle(2, 0, 30, 830, fill='lightskyblue', tags="core")
    canvas.create_rectangle(2, 400, 430, 430, fill='lightskyblue', tags="core")
    # Colonnes :
    x = 30
    for i in range(10):
        x += 40
        canvas.create_line(x, 0, x, 830, tags="core")
        canvas.create_text(x - 20, 415, text=lettres[i], font=("Times", 12), tags="core")
    # Lignes :
    y = 0
    y += 70 + saut_ligne(canvas, y, 9)    # 70 <=> le décalage dû à la marge
    canvas.create_text(15, 400 - 20, font=("Times", 12), text="10", tags="core")
    saut_ligne(canvas, y, 10)


def display_case(canvas, board, x, y, state, nametag=""):
    # index des valeurs : [rien, tir raté, bateau de base, touché, coulé]
    color = ""
    values = [0, 1, 2, 3, 4]
    colors = ['white', 'grey', 'blue', 'orange', 'red']
    for i in range(5):
        if state == values[i]: # Changement de la couleur du bateau en fonction de son état
            color = colors[i]
    x1, x2 = ((x - 1) * 40) + 1 + 30, (x * 40) - 1 + 30
    if board == "Player":
        y1, y2 = ((y - 1) * 40) + 1, (y * 40) - 1
        if nametag != "":
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=("case", nametag))
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="case")
    elif board == "IA":
        y1, y2 = 430 + ((y - 1) * 40) + 1, 430 + (y * 40) - 1
        if nametag != "":
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=("case", nametag))
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="case")


def boat_color(event):          # Permet de mettre en vert le bateau séléctioné
    if phase != "init":
        return
    ship = Boatlist.get(ACTIVE)
    for item in ships_name:
        if item == ship:
            Grilles.itemconfig(ship, fill='green')
        else:
            Grilles.itemconfig(item, fill='blue')


def init_ships_Grids(boat_tab, grid): # Initialisation des grilles de position des bateaux
    for b in range(len(boat_tab)):
        for p in range(len(boat_tab[b])):
            posx = boat_tab[b][p][0]
            posy = boat_tab[b][p][1]
            grid[posx - 1][posy - 1] = 1


def finDuJeu(): # Création de la phase de fin de jeu
    global phase
    global endWindow
    joueur = 0
    IA = 0
    for b in range(len(ships)):
        for p in range(len(ships[b])):
            joueur += ships[b][p][2]
            IA += IAships[b][p][2]
    if (IA == 0) or (joueur == 0):
        phase = "end-game"
        endWindow = Tk()
        endWindow.geometry("300x75")
        endWindow.title("Fin du jeu")
        if IA == 0:
            state = "gagné"
        else:
            state = "perdu"
        if old_Average_Pboat == zeroGrid:
            overwrite_file("AveragePshots.txt", TirPlayer)
        else:
            add_grids(TirPlayer, old_Average_Pshots)
            overwrite_file("AveragePshots.txt", TirPlayer)
        if old_Average_Pshots == zeroGrid:
            overwrite_file("AveragePboat.txt", playerGrid) # Sauvegarde des résultats dans un fichier à l'aide de la commande « overwrite »
        else:
            add_grids(playerGrid, old_Average_Pboat)
            overwrite_file("AveragePboat.txt", playerGrid)
        EndLabel = Label(endWindow, text="La partie est finie, vous avez " + state + " !\nA bientôt pour une nouvelle partie !")
        EndLabel.pack()
        quitter = Button(endWindow, text="Quitter", command=detruire)
        quitter.pack()


def detruire(): # Fonction de débug de l'interface
    fenetre.destroy()
    endWindow.destroy()
    debugWindow.destroy()


def initializeQueue(grid, proba, mode): # Initialisation de la fonction de sauvegarde de probas
    liste = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if mode == 1:
                if grid[x][y] >= proba:
                    liste.append([x, y])
            elif mode == 2:
                if grid[x][y] <= proba:
                    liste.append([x, y])
    return liste


def add_grids(grid, to_Add_Grid):
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            grid[x][y] = (grid[x][y] + to_Add_Grid[x][y]) / 2.0


def overwrite_file(name, grid): # Fonction d'édition de fichier
    file = open(name, "w")
    file.write(grid_to_txt(grid))
    file.close()


def grid_to_txt(grid): # Transfert les entiers de la grille en caratères
    to_insert = ""
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if y != (len(grid[x]) - 1):
                to_insert += str(grid[x][y]) + " "
            else:
                if x == (len(grid) - 1):
                    to_insert += str(grid[x][y])
                else:
                    to_insert += str(grid[x][y]) + "\n"
    return to_insert


def set_IA_Boats(IAships): # Mise en place du positionnement de l'IA (position de 1 à 10)
    position = randint(1, 10)
    file = open("Placements.txt", "r")
    for i in range(position):
        ligne = file.readline()
    file.close()
    liste = [0, 0, 0, 0, 0]
    liste[0] = ligne[:10]
    liste[1] = ligne[10:18]
    liste[2] = ligne[18:24]
    liste[3] = ligne[24:30]
    liste[4] = ligne[30:]
    for b in range(len(IAships)):
        a = 0
        for p in range(len(IAships[b])):
            IAships[b][p][0] = int(liste[b][a]) + 1
            a += 1
            IAships[b][p][1] = int(liste[b][a]) + 1
            a += 1


def coreTir(ships, x, y): # Fonction de tir de l'IA
    global TirsIA
    print "Tir déclaré en x=", x, "et y=", y
    if playerGrid[x - 1][y - 1] == 1:
        # touché
        for b in range(len(ships)):
            for p in range(len(ships[b])):
                if (ships[b][p][0] == x) and (ships[b][p][1] == y):
                    ships[b][p][2] = 0
                    P_f_ships.set(pformat(ships))
                    boat = b
        display_case(Grilles, "Player", x, y, 3, nametag=ships_name[boat])
        valid = 0
        for p in range(len(ships[boat])):
            valid += ships[boat][p][2]
        if valid == 0:
            Grilles.itemconfig(ships_name[boat], fill='red')
            full_valid = 0
            for b in range(len(ships)):
                for p in range(len(ships[b])):
                    full_valid += ships[b][p][2]
            if full_valid == 0:
                finDuJeu()
        TirsIA[x - 1][y - 1] += 1
        IA_f_shots.set(pformat(TirsIA))
        return "touched", valid
    else:
        # Raté
        display_case(Grilles, "Player", x, y, 1, nametag="fail")
        TirsIA[x - 1][y - 1] += 1
        IA_f_shots.set(pformat(TirsIA))
        return "fail", 0


def detect_dir(x, y, oldShots, border, nextHit, calcul): # Calcul de la validité d'un tir suivi
    global to_follow
    if oldShots == 1:
        for i in range(4):
            testX = x - 1 + offset[i][0]
            testY = y - 1 + offset[i][1]
            if not(0 <= testX <= 9) or not(0 <= testY <= 9) or TirsIA[testX][testY] == 1:
                to_follow[3 + i] = False
    if border == 1: # Détection du bord
        if y == 1:
            to_follow[6] = False
        if y == 10:
            to_follow[5] = False
        if x == 1:
            to_follow[3] = False
        if x == 10:
            to_follow[4] = False
    if nextHit != 0:
        x = to_follow[1] + to_follow[7] * offset[nextHit][0]
        y = to_follow[1] + to_follow[7] * offset[nextHit][1]
        if TirsIA[x - 1][y - 1] == 1 or not(1 <= x <= 10) or not(1 <= y <= 10):
            to_follow[nextHit + 3] = False
    if calcul == 1:
        count = []
        for i in range(4):
            if to_follow[3 + i] is True:  # Si on détecte une direction vraie alors on applique le patterne de directions
                for j in range(4):
                    to_follow[3 + j] = directions[i][j]
                return "a verif"
            elif to_follow[3 + i] is False:
                count.append(1)
            else:
                count.append(0)
        if sum(count) == 4:
            for i in range(len(to_follow)):
                to_follow[i] = 0
            IA_following.set(pformat(to_follow))
            return "Impossible"
        if sum(count) == 3:
            for i in range(4):
                if not to_follow[3 + i] is False:
                    to_follow[3 + i] = True
                    to_follow[0] = 2
                    return 3 + i
        if sum(count) == 2:
            if count[0] + count[1] == 2:
                for i in range(4):
                    to_follow[3 + i] = directions[2][i]
                to_follow[0] = 2
            elif count[2] + count[3] == 2:
                for i in range(4):
                    to_follow[3 + i] = directions[0][i]
                to_follow[0] = 2
        to_follow[0] = 1
        return "Incomplet"


def tirIA(ships, mode, primX=0, primY=0):
    global possibleBoat
    global to_follow
    if mode == "Random":  # On effectue un tir aléatoire
        x = randint(1, 10)
        y = randint(1, 10)
        while TirsIA[x - 1][y - 1] == 1:
            x = randint(1, 10)
            y = randint(1, 10)
        state, boatLiving = coreTir(ships, x, y)
        if state == "touched":  # En fonction du niveau de l'ia et si le bateau est vivant on détermine si l'ia rejoue et de quelle manière
            if IA_level.get() == 1:
                tirIA(ships, "Random")
            elif boatLiving > 0:
                tirIA(ships, 'Following', x, y)
            elif IA_level.get() == 2:
                tirIA(ships, 'Random')
            elif len(possibleBoat) > 0:
                tirIA(ships, "Intelligent")
            else:
                tirIA(ships, "random")
    elif mode == "Intelligent":  # Ce mode de tir extrait des parties précédentes les positions les plus probables pour les bateaux d'un joueur
        x = -1
        while (x == -1) or (TirsIA[x - 1][y - 1] == 1):  # Ici on l'empêche d'extraire des coordonnées déjà utilisées
            x = possibleBoat[0][0] + 1
            y = possibleBoat[0][1] + 1
            possibleBoat.pop(0)
        IA_3_Queue.set(pformat(possibleBoat))
        state, boatLiving = coreTir(ships, x, y)
        if boatLiving > 0:
            tirIA(ships, "Following", x, y)
        elif state == "fail":
            return
        elif len(possibleBoat) > 0:
            tirIA(ships, "Intelligent")
        else:
            tirIA(ships, "Random")
    elif mode == "Following":
        if to_follow[0] == 0:
            scan_result = detect_dir(primX, primY, 1, 1, 0, 1)
            if scan_result != "Impossible":
                to_follow[1] = primX
                to_follow[2] = primY
                to_follow[7] = 1
                if scan_result == "Incomplet":
                    to_follow[0] = 1
                else:
                    to_follow[0] = 2
                IA_following.set(pformat(to_follow))
            else:  # Si le scan est impossible
                if IA_level.get() == 2:
                    tirIA(ships, "Random")
                elif IA_level.get() == 3:
                    if len(possibleBoat) > 0:
                        tirIA(ships, "Intelligent")
                    else:
                        tirIA(ships, 'Random')
                return
        if to_follow[0] == 1:
            direction = randint(0, 3)
            while to_follow[direction + 3] is False:
                direction = randint(0, 3)
            x = to_follow[1] + to_follow[7] * offset[direction][0]
            y = to_follow[2] + to_follow[7] * offset[direction][1]
            state, boatLiving = coreTir(ships, x, y)
            if state == "fail":
                to_follow[direction + 3] = False
                scan_result = detect_dir(0, 0, 0, 0, 0, 1)
                IA_following.set(pformat(to_follow))
            elif boatLiving > 0:
                to_follow[7] += 1
                to_follow[direction + 3] = True
                scan_result = detect_dir(x, y, 0, 1, direction, 1)
                to_follow[0] = 2
                IA_following.set(pformat(to_follow))
                tirIA(ships, "Following")
            else:
                for i in range(len(to_follow)):
                    to_follow[i] = 0
                if IA_level.get() == 2:
                    tirIA(ships, "Random")
                elif IA_level.get() == 3:
                    if len(possibleBoat) > 0:
                        tirIA(ships, "Intelligent")
                    else:
                        tirIA(ships, 'Random')
        elif to_follow[0] == 2:
            direction = -1
            for i in range(4):
                if to_follow[3 + i] is True:
                    direction = 3 + i
                    to_follow[8] = True
            if direction == -1:
                for i in range(4):
                    if to_follow[3 + i] == "Maybe":
                        direction = 3 + i
                        if to_follow[8] is True:
                            to_follow[7] = 1
                        to_follow[8] = "Maybe"
            x = to_follow[1] + to_follow[7] * offset[direction - 3][0]
            y = to_follow[2] + to_follow[7] * offset[direction - 3][1]
            state, boatLiving = coreTir(ships, x, y)
            if state == "fail":
                to_follow[direction] = False
                IA_following.set(pformat(to_follow))
            elif boatLiving > 0:
                to_follow[7] += 1
                scan_result = detect_dir(x, y, 0, 1, 1, 0)
                IA_following.set(pformat(to_follow))
                tirIA(ships, "Following")
            else:
                for i in range(len(to_follow)):
                    to_follow[i] = 0
                if IA_level.get() == 2:
                    tirIA(ships, "Random")
                elif IA_level.get() == 3:
                    if len(possibleBoat) > 0:
                        tirIA(ships, "Intelligent")
                    else:
                        tirIA(ships, 'Random')


def randomAssign(boats, preciseBoat, liste=[]):
    final_dir = ""
    possible_dir = [0, 0, 0, 0]  # left/right/down/up
    mainx = randint(0, 9)
    mainy = randint(0, 9)
    while boats[mainx][mainy] == 1:
        mainx = randint(0, 9)
        mainy = randint(0, 9)
    if liste != []:
        mainx = liste[0][0]
        mainy = liste[0][1]
        liste.pop(0)
        while boats[mainx][mainy] == 1:
            mainx = liste[0][0]
            mainy = liste[0][1]
            liste.pop(0)
    if (0 <= mainx + len(preciseBoat) <= 9):
        possible_dir[0] = 1
    if (0 <= mainx - len(preciseBoat) <= 9):
        possible_dir[1] = -1
    if (0 <= mainy + len(preciseBoat) <= 9):
        possible_dir[2] = 1
    if (0 <= mainy - len(preciseBoat) <= 9):
        possible_dir[3] = -1
    for indent in range(len(preciseBoat)):
        for direct in range(4):
            if possible_dir[direct] != 0:
                if boats[mainx + (indent * r_offset[direct][0])][mainy + (indent * r_offset[direct][1])] == 1:
                    possible_dir[direct] = 0
    count = 0
    stock = []
    for i in range(4):
        if possible_dir[i] != 0:
            stock.append(i)
        else:
            count += 1
        if (i == 3) and (count == 3):
            final_dir = i
    if count == 4:
        randomAssign(boats, preciseBoat, liste)
    else:
        if count != 3:
            final_dir = stock[randint(0, (len(stock) - 1))]
        for i in range(len(preciseBoat)):
            preciseBoat[i][0] = mainx + (i * r_offset[final_dir][0]) + 1
            preciseBoat[i][1] = mainy + (i * r_offset[final_dir][1]) + 1
    for p in range(len(preciseBoat)):
            posx = preciseBoat[p][0]
            posy = preciseBoat[p][1]
            boats[posx - 1][posy - 1] = 1


numbers = range(1, 11)
lettres = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
reversed_Lettres = ["J", "I", "H", "G", "F", "E", "D", "C", "B", "A"]

fleches = ['Left', 'Right', 'Down', 'Up', "Rotate"]
offset = [[-1, 0], [1, 0], [0, 1], [0, -1], "rotation"]
r_offset = [[1, 0], [-1, 0], [0, 1], [0, -1]]
directions = [[True, "Maybe", False, False], ["Maybe", True, False, False], [False, False, True, "Maybe"], [False, False, "Maybe", True]]

ships_name = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]
IAships_name = ["IACarrier", "IABattleship", "IACruiser", "IASubmarine", "IADestroyer"]

zeroGrid = initGrid()

possibleSafe = 0
possibleBoat = 0
old_Average_Pboat = txt_to_grid("AveragePboat.txt")
old_Average_Pshots = txt_to_grid("AveragePshots.txt")

# [state, x, y, left, right, down, up, indent, lastdir]
to_follow = [0] * 9

"""
Début de def des données du joueur

Bateaux construits sous la forme Bateau = [Point 1, Point 2, ..., Point n],
Avec Point = [x, y, verif] | Si un bateau est touché alors "verif" = 0
"""

Carrier = [[1, 1, 1], [2, 1, 1], [3, 1, 1], [4, 1, 1], [5, 1, 1]]
Battleship = [[1, 3, 1], [2, 3, 1], [3, 3, 1], [4, 3, 1]]
Cruiser = [[1, 5, 1], [2, 5, 1], [3, 5, 1]]
Submarine = [[1, 7, 1], [2, 7, 1], [3, 7, 1]]
Destroyer = [[1, 9, 1], [2, 9, 1]]
ships = [Carrier, Battleship, Cruiser, Submarine, Destroyer]

playerGrid = initGrid()

TirPlayer = initGrid()

"""
Fin de def des données du joueur
Début de def des données de l'IA
"""

IACarrier = [[1, 1, 1], [2, 1, 1], [3, 1, 1], [4, 1, 1], [5, 1, 1]]
IABattleship = [[1, 3, 1], [2, 3, 1], [3, 3, 1], [4, 3, 1]]
IACruiser = [[1, 5, 1], [2, 5, 1], [3, 5, 1]]
IASubmarine = [[1, 7, 1], [2, 7, 1], [3, 7, 1]]
IADestroyer = [[1, 9, 1], [2, 9, 1]]
IAships = [IACarrier, IABattleship, IACruiser, IASubmarine, IADestroyer]

IAGrid = initGrid()

TirsIA = initGrid()

# Fin de def des données de l'IA

init_ships_Grids(ships, playerGrid)
init_ships_Grids(IAships, IAGrid)

# DEBUT DE CREATION INTERFACE

endWindow = 0

debugWindow = Tk()
debugWindow.title("Debug window")
P_Frame = LabelFrame(debugWindow, text="Infos du Joueur", padx=5, pady=5)
P_Frame.grid(column=1, row=1)

P_f_Grid = StringVar(master=P_Frame, value=pformat(playerGrid))
P_f_ships = StringVar(master=P_Frame, value=pformat(ships))

P_Grid = Label(P_Frame, textvariable=P_f_Grid)
P_Grid.grid(column=1, row=1)
P_ships = Label(P_Frame, textvariable=P_f_ships, justify="left")
P_ships.grid(column=2, row=1)
IA_Frame = LabelFrame(debugWindow, text="Infos de l'IA", padx=5, pady=5)
IA_Frame.grid(column=1, row=2)

IA_f_Grid = StringVar(master=IA_Frame, value=pformat(IAGrid))
IA_f_ships = StringVar(master=IA_Frame, value=pformat(IAships))
IA_f_shots = StringVar(master=IA_Frame, value=pformat(TirsIA))

IA_Grid = Label(IA_Frame, textvariable=IA_f_Grid)
IA_Grid.grid(column=1, row=1)
IA_ships = Label(IA_Frame, textvariable=IA_f_ships, justify="left")
IA_ships.grid(column=2, row=1)
IA_shots = Label(IA_Frame, textvariable=IA_f_shots)
IA_shots.grid(column=1, columnspan=2, row=2)

IA_3_Queue = StringVar(master=IA_Frame, value=pformat(possibleBoat))
IA_3_disp_Queue = Label(master=IA_Frame, textvariable=IA_3_Queue)
IA_3_disp_Queue.grid(column=1, columnspan=2, row=3)

IA_following = StringVar(master=IA_Frame, value=pformat(to_follow))
IA_disp_following = Label(master=IA_Frame, textvariable=IA_following)
IA_disp_following.grid(column=1, columnspan=2, row=4)

debugWindow.withdraw()

fenetre = Tk()
fenetre.geometry("1200x850")
fenetre.title("Bataille Navale")

Grilles = Canvas(fenetre, width=430, height=830)  # debut creation grille
Grilles.place(x=400, y=10)

trace_grid(Grilles)

Grilles.create_line(1, 0, 1, 830, tags="core")
Grilles.create_line(30, 0, 30, 830, width=2, tags="core")
Grilles.create_line(0, 400, 430, 400, width=2, tags="core")
Grilles.create_line(0, 430, 430, 430, width=2, tags="core")
Grilles.create_rectangle(0, 400, 30, 430, fill='black', tags="core")  # fin creation grille

Boat_title = LabelFrame(fenetre, text="Choisissez le bateau à déplacer\n(Double-cliquez sur son nom)", pady=5)
Boat_title.place(x=100, y=100)

Boatlist = Listbox(Boat_title, height=5)
Boatlist.pack()
Boatlist.bind("<Button-1>", boat_color)

Button_title = LabelFrame(fenetre, text="Déplacez votre bateau\nà l'aide de ces touches :", padx=5, pady=5)
Button_title.place(x=100, y=500)

B_up = Button(Button_title, text="Up", height=2, width=5, command=lambda: moveboat(Grilles, playerGrid, Boatlist.curselection(), "Up"))
B_up.grid(row=1, column=2)

B_down = Button(Button_title, text="Down", height=2, width=5, command=lambda: moveboat(Grilles, playerGrid, Boatlist.curselection(), "Down"))
B_down.grid(row=3, column=2)

B_left = Button(Button_title, text="Left", height=2, width=5, command=lambda: moveboat(Grilles, playerGrid, Boatlist.curselection(), "Left"))
B_left.grid(row=2, column=1)

B_right = Button(Button_title, text="Right", height=2, width=5, command=lambda: moveboat(Grilles, playerGrid, Boatlist.curselection(), "Right"))
B_right.grid(row=2, column=3)

B_rotate = Button(Button_title, text="Rotate", height=2, width=5, command=lambda: moveboat(Grilles, playerGrid, Boatlist.curselection(), "Rotate"))
B_rotate.grid(row=2, column=2)

Indic = Label(fenetre, text="Ici s'afficherons les restrictions\nauquelles vous serez potentiellement soumis.\nLe code couleur est :\nbleu = votre bateau\nvert = votre bateau séléctionné\norange = touché\nrouge = coulé")
Indic.place(x=50, y=300)

B_tir = Button(fenetre, text="TIRER", command=lambda: tir_joueur(IAGrid, FireCoord.get(), IAships))
B_tir.place(x=1000, y=400)

B_verif = Button(fenetre, text="Début du combat", command=lambda: validation(playerGrid, ships))
B_verif.place(x=100, y=700)

FireCoord = Entry(fenetre)
FireCoord.place(x=950, y=350)

IA_selector = LabelFrame(fenetre, text="Choisissez votre niveau d'IA", padx=5, pady=5)
IA_selector.place(x=1000, y=600)

IA_level = IntVar(master=fenetre)
infos_radioB = [["Facile", 1], ["Intermédiaire", 2], ["Difficile", 3]]
for text, level in infos_radioB:
    radioB = Radiobutton(IA_selector, text=text, variable=IA_level, value=level)
    radioB.pack(anchor=N)

# FIN DE CREATION INTERFACE

for item in ships_name:
    Boatlist.insert(END, item)

for b in range(len(ships)):
    for p in range(len(ships[b])):
        display_case(Grilles, "Player", ships[b][p][0], ships[b][p][1], 2, ships_name[b])

fenetre.bind('<Return>', lambda event: tir_joueur(IAGrid, FireCoord.get(), IAships))
fenetre.bind('<Control_L>', lambda event: debugWindow.deiconify())

fenetre.mainloop()

