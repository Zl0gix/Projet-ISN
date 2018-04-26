# coding: utf-8
from Tkinter import *
from pprint import *
from random import randint
import os.path


def initGrid(liste):
    liste = [0] * 10
    temp = liste[:]
    for i in range(len(liste)):
        liste[i] = temp[:]


def nb_lignes(name):
    file = open(name, "r")
    temp = file.readline()
    count = 0
    while temp != "":
        count += 1
        temp = file.readline()
    file.close()
    return count


def txt_to_grid(name):
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


def determineTir():
    if IA_level.get() == 1:
        tirIA(ships, "Random")
    elif IA_level.get() == 2:
        if to_follow[0] == 1:
            tirIA(ships, "Following")
        else:
            tirIA(ships, "Random")
    elif IA_level.get() == 3:
        if len(possibleBoat) != 0:
            tirIA(ships, "Intelligent")
        if to_follow[0] == 1:
            tirIA(ships, "Following")
        else:
            tirIA(ships, "Random")


def tir_joueur(Grid, car, IA_boats):
    global TirPlayer
    if phase == "in-game":
        try:
            assert 2 <= len(car) <= 3
            lettre = car[0].upper()
            Nombre = car[1:]
            # Conversion du car lettre en nombre
            for i in range(10):
                if lettre == lettres[i]:
                    x = i
            y = int(Nombre) - 1
            assert 0 <= x <= 9
            assert 0 <= y <= 9
            Indic.config(text="Coordonées acceptées")
            ship_tag = ""
            TirPlayer[x][y] = 1
            if Grid[x][y] == 1:
                boat_index = 0
                for b in range(len(IA_boats)):
                    for p in range(len(IA_boats[b])):
                        if (IA_boats[b][p][0] == x + 1) and (IA_boats[b][p][1] == y + 1):
                            if IA_boats[b][p][2] == 1:
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
                    finDuJeu()
            else:
                display_case(Grilles, "IA", x + 1, y + 1, 1, nametag="fail")
                # Tour de l'IA
                determineTir()
        except AssertionError:
            Indic.config(text="Les coordonées du tir ne sont pas valides\n(elles doivent être de la forme : LXX)\n(avec L une lettre et XX un nombre entre 1 et 10)")
        if car == "annihilation":
            for l_item in lettres:
                for n_item in range(1, 11):
                    tir_joueur(IAGrid, l_item + str(n_item), IAships)
        if car == "r-annihilation":
            for l_item in reversed_Lettres:
                for n_item in range(1, 11):
                    tir_joueur(IAGrid, l_item + str(n_item), IAships)
    else:
        Indic.config(text='Vous êtes encore en phase de placement des bateaux.\nPour commencer la bataille veuillez cliquer sur le bouton :\n"Début du combat"')


def moveboat(canvas, Grid, vehicle, direction):
    if phase == "init":
        if len(vehicle) != 0:
            for i in range(len(ships_name)):
                if vehicle[0] == i:
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
                        for i in range(len(boat)):
                            x1 = boat[i][0]
                            y1 = boat[i][1]
                            Grid[x1 - 1][y1 - 1] -= 1
                            boat[i][0] += decal[0]
                            boat[i][1] += decal[1]
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


def validation(Grid, ships):
    global possibleBoat
    if phase != "init":
        return
    global phase
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
            if i == (IA_level.get() - 1):
                difficulte = diff[i]
        Indic.config(text="Bateaux verouillés\nLa partie commence !" + "\n vous avez choisis l'IA " + difficulte)
        Grilles.itemconfig(Boatlist.get(ACTIVE), fill='blue')
        Boatlist.selection_clear(0, END)
        if IA_level.get() == 3:
            possibleBoat = convert_proba_to_coord(old_Average_Pboat, 0.5)
    else:
        Indic.config(text="Il y a " + str(count) + " points\nde superpositions")


def saut_ligne(canvas, y, nb):
    for i in range(nb):
        y += 40
        canvas.create_line(0, y, 430, y, tags="core")
        canvas.create_text(15, y - 20, font=("Times", 12), text=numbers[i], tags="core")
    return y


def trace_grid(canvas):
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
        if state == values[i]:
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


def init_ships_Grids(boat_tab, grid):
    for b in range(len(boat_tab)):
        for p in range(len(boat_tab[b])):
            posx = boat_tab[b][p][0]
            posy = boat_tab[b][p][1]
            grid[posx - 1][posy - 1] = 1


def finDuJeu():
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
        EndLabel = Label(endWindow, text="La partie est finie, vous avez " + state + " !\nA bientôt pour une nouvelle partie !")
        EndLabel.pack()
        quitter = Button(endWindow, text="Quitter", command=detruire)
        quitter.pack()
        new_Average_Pshots = add_grids(TirPlayer, old_Average_Pshots)
        new_Average_Pboat = add_grids(playerGrid, old_Average_Pboat)
        overwrite_file("AveragePshots", new_Average_Pshots)
        overwrite_file("AveragePboat", new_Average_Pboat)


def detruire():
    fenetre.destroy()
    endWindow.destroy()
    debugWindow.destroy()


def initializeQueue(grid, min_proba):
    liste = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] >= min_proba:
                liste.append([x, y])
    return liste


def add_grids(grid, to_Add_Grid):
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            grid[x][y] = (grid[x][y] + to_Add_Grid[x][y]) / 2


def overwrite_file(name, grid):
    file = open(name, "w")
    file.write(grid_to_txt(grid))
    file.close()


def grid_to_txt(grid):
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


def set_IA_Boats():
    # insérer le sélectionneur de positions
    oui


def coreTir(ships, x, y):
    global TirIA
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
        for p in range(len(ships[b])):
            valid += ships[b][p][2]
        if valid == 0:
            Grilles.itemconfig(ships_name[boat], fill='red')
            full_valid = 0
            for b in range(len(ships)):
                for p in range(len(ships[b])):
                    full_valid += ships[b][p][2]
            if full_valid == 0:
                finDuJeu()
        TirIA[x - 1][y - 1] += 1
        IA_f_shots.set(pformat(TirIA))
        return "touched", valid
    else:
        # Raté
        display_case(Grilles, "Player", x, y, 1, nametag="fail")
        TirIA[x - 1][y - 1] += 1
        return "fail"


def detect_T_or_F(oldx, oldy):
    global to_follow
    if oldy == 1:
        to_follow[6] = False
    if oldy == 10:
        to_follow[5] = False
    if oldx == 1:
        to_follow[3] = False
    if oldx == 10:
        to_follow[4] = False


def tirIA(ships, mode, oldx=0, oldy=0):
    global possibleBoat
    global to_follow
    if mode == "Random":
        x = randint(1, 10)
        y = randint(1, 10)
        while TirIA[x - 1][y - 1] == 1:
            x = randint(1, 10)
            y = randint(1, 10)
        tirState, boatLiving = coreTir(ships, x, y)
        if state == "touched":
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
    elif mode == "Intelligent":
        x = possibleBoat[0][0]
        y = possibleBoat[0][1]
        possibleBoat.pop(0)
        tirState, boatLiving = coreTir(ships, x, y)
        if boatLiving > 0:
            tirIA(ships, "Following", x, y)
        elif len(possibleBoat) > 0:
            tirIA(ships, "Intelligent")
    elif mode == "Following":
        to_follow[7] += 1
        if to_follow[0] == 0:
            to_follow[1] = oldx
            to_follow[2] = oldy
            detect_T_or_F(oldx, oldy)
            direction = randint(3, 6)
            while to_follow[direction] is False:
                direction = randint(0, 3)
            x = oldx + offset[direction + 3][0]
            y = oldy + offset[direction + 3][1]
            state, boatLiving = coreTir(ships, x, y)
            if state == "fail":
                to_follow[direction] = False
                to_follow[0] = 1
                count = 0
                for i in range(4):
                    if to_follow[3 + i] is False:
                        count += 1
                if count == 3:
                    for i in range(4):
                        if to_follow[3 + i] == 0:
                            to_follow[3 + i] = True
            elif boatLiving > 0:
                for i in range(4):
                    to_follow[3 + i] = directions[direction - 3][i]
                detect_T_or_F(oldx, oldy)
                tirIA(ships, "Following", oldx, oldy)
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
        else:
            direction = -1
            for i in range(4):
                if to_follow[3 + i] is True:
                    direction = i
            if direction == -1:
                for i in range(4):
                    if to_follow[3 + i] == "Maybe":
                        direction = i
            if direction == -1:
                direction = randint(3, 6)
                while to_follow[direction] is False:
                    direction = randint(0, 3)
            x = oldx + (to_follow[7] * offset[direction + 3][0])
            y = oldy + (to_follow[7] * offset[direction + 3][1])
            state, boatLiving = coreTir(ships, x, y)
            if state == "fail":
                to_follow[3 + direction] = False
                count = 0
                for i in range(4):
                    if to_follow[i + 3] is False:
                        count += 1
                if count == 3:
                    for i in range(4):
                        if to_follow[3 + i] == 0:
                            to_follow[3 + i] = True
            elif boatLiving > 0:
                count = 0
                for i in range(4):
                    if (to_follow[3 + i] is True) or (to_follow[3 + i] == "Maybe"):
                        count = 1
                if count == 0:
                    for i in range(4):
                        to_follow[3 + i] = directions[direction - 3][i]
                    detect_T_or_F(oldx, oldy)
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


numbers = range(1, 11)
lettres = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
reversed_Lettres = ["J", "I", "H", "G", "F", "E", "D", "C", "B", "A"]

fleches = ['Left', 'Right', 'Down', 'Up', "Rotate"]
offset = [[-1, 0], [1, 0], [0, 1], [0, -1], "rotation"]
directions = [[True, "Maybe", False, False], ["Maybe", True, False, False], [False, False, True, "Maybe"], [False, False, "Maybe", True]]

phase = "init"  # les autres phases possibles sont : "in-game" / "end-game"
ships_name = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]
IAships_name = ["IACarrier", "IABattleship", "IACruiser", "IASubmarine", "IADestroyer"]

zeroGrid = []
initGrid(zeroGrid)

possibleBoat = 0
old_Average_Pboat = txt_to_grid("AveragePboat")
old_Average_Pshots = txt_to_grid("AveragePshots")

# [state, x, y, left, right, down, up, indent]
to_follow = [0] * 8
to_follow[7] = 1

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

playerGrid = []
initGrid(playerGrid)

TirPlayer = []
initGrid(TirPlayer)

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

IA_Grid = []
initGrid(IAGrid)

TirIA = []
initGrid(TirIA)

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
IA_f_shots = StringVar(master=IA_Frame, value=pformat(TirIA))

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

Indic = Label(fenetre, text="Ici s'afficherons les restrictions\nauquelles vous serez potentiellement soumis")
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

"""
Il reste :
    - IA lvl 1 : positions préenregistrées
    - IA lvl 2 : + de positions
    - IA lvl 3 : Valentin trouve une solution miracle sinon aléatoire selon algo bullshit sur les bords

    - les bateaux de l'IA

Amélioration :
    - carré en rouge quand superpos ? ou pas, ce serait un eu chiant quand meme
"""
