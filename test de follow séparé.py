# coding: utf-8
from random import randint


def initGrid():
    liste = [0] * 10
    temp = liste[:]
    for i in range(len(liste)):
        liste[i] = temp[:]
    return liste


def detect_dir(x, y, oldShots, border, nextHit, calcul):
    global to_follow
    if oldShots == 1:
        for i in range(4):
            if TirsIA[x - 1 + offset[i][0]][y - 1 + offset[i][1]] == 1:
                to_follow[3 + i] = False
    if border == 1:
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
        if TirsIA[x - 1][y - 1] == 1:
            to_follow[nextHit] = False
    if calcul == 1:
        count = []
        for i in range(4):
            if to_follow[3 + i] is True:  # Si on détecte une direction vraie alors on applique le patterne de directions
                for j in range(4):
                    to_follow[3 + j] = directions[3 + i][j]
                return "a verif"
            elif to_follow[3 + i] is False:
                count.append(1)
            else:
                count.append(0)
        if sum(count) == 4:
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
            elif count[2] + count[3] == 2:
                for i in range(4):
                    to_follow[3 + i] = directions[0][i]
            to_follow[0] = 2
            return
        to_follow[0] = 1
        return "Incomplet"


def tirIA(ships, mode, primX=0, primY=0):
    global to_follow
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
            for i in range(len(to_follow)):
                to_follow[i] = 0
            IA_following.set(pformat(to_follow))
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
        while to_follow[3 + direction] is False:
            direction = randint(0, 3)
        x = to_follow[1] + to_follow[7] * offset[direction][0]
        y = to_follow[2] + to_follow[7] * offset[direction][1]
        state, boatLiving = coreTir(ships, x, y)
        if state == "fail":
            to_follow[direction] = False
            scan_result = detect_dir(0, 0, 0, 0, 0, 1)
            IA_following.set(pformat(to_follow))
        elif boatLiving > 0:
            to_follow[7] += 1
            to_follow[direction] = True
            scan_result = detect_dir(0, 0, 0, 0, direction, 1)
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
        if direction == -1:
            for i in range(4):
                if to_follow[3 + i] == "Maybe":
                    direction = 3 + i
        x = to_follow[1] + to_follow[7] * offset[direction][0]
        y = to_follow[2] + to_follow[7] * offset[direction][1]
        state, boatLiving = coreTir(ships, x, y)
        if state == "fail":
            to_follow[direction] = False
            IA_following.set(pformat(to_follow))
        elif boatLiving > 0:
            to_follow[7] += 1
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

"""

        if to_follow[0] == 0: # Si c'est le début d'un tir suivi alors on execute cette partie du script :
            to_follow[1] = oldx
            to_follow[2] = oldy
            detect_T_or_F(oldx, oldy)
            direction = randint(3, 6)
            count = 0
            for i in range(4): # Si toutes les directions possibles sont fausses alors on sort de la fonction
                if to_follow[3 + i] is False:
                    count += 1
            if count == 4:
                for i in range (len(to_follow)):
                    to_follow[i] = 0
                print "j'etais bloque"
                # tirIA(ships, "Random")
                return
            while to_follow[direction] is False: # Si la direction choisie premièrement est impossible, alors on rééssaye jusqu'a ce que ça soit possible
                direction = randint(3, 6)
            x = oldx + offset[direction - 3][0]
            y = oldy + offset[direction - 3][1]
            while (TirIA[x][y] == 1) or (not(1 <= x <= 10)) or (not(1 <= y <= 10)):
                to_follow[direction] = False
                while to_follow[direction] is False:
                    direction = randint(3, 6)
                x = oldx + offset[direction - 3][0]
                y = oldy + offset[direction - 3][1]
            print "    state =", to_follow
            print "    direction choisie =", fleches[direction - 3]
            state, boatLiving = coreTir(ships, x, y)
            to_follow[9] = direction
            print "boatLiving =", boatLiving
            to_follow[7] += 1
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
                    to_follow[7] += 1
                IA_following.set(pformat(to_follow))
                print "    state =", to_follow
            elif boatLiving > 0:
                to_follow[0] = 1
                for i in range(4):
                    to_follow[3 + i] = directions[direction - 3][i]
                detect_T_or_F(oldx, oldy)
                IA_following.set(pformat(to_follow))
                print "    state =", to_follow
                tirIA(ships, "Following", oldx, oldy)
            else:
                for i in range(len(to_follow)):
                    to_follow[i] = 0
                    IA_following.set(pformat(to_follow))
                if IA_level.get() == 2:
                    tirIA(ships, "Random")
                elif IA_level.get() == 3:
                    if len(possibleBoat) > 0:
                        tirIA(ships, "Intelligent")
                    else:
                        tirIA(ships, 'Random')
        else:
            if (oldx == 0) or (oldy == 0):
                oldx = to_follow[1]
                oldy = to_follow[2]
            x = oldx + ((to_follow[7]-1) * offset[to_follow[9] - 3][0])
            y = oldy + ((to_follow[7]-1) * offset[to_follow[9] - 3][1])
            detect_T_or_F(x, y)
            count = 0
            if count == 4:
                for i in range (len(to_follow)):
                    to_follow[i] = 0
                print "j'etais bloque"
                # tirIA(ships, "Random")
                return
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
            if direction == -1:
                direction = randint(3, 6)
                while to_follow[direction] is False:
                    direction = randint(3, 6)
                    to_follow[8] = 0
            x = oldx + (to_follow[7] * offset[direction - 3][0])
            y = oldy + (to_follow[7] * offset[direction - 3][1])
            if (TirIA[x][y] == 1) or (not(1 <= x <= 10)) or (not(1 <= y <= 10)):
                to_follow[direction] = False
                return
            state, boatLiving = coreTir(ships, x, y)
            to_follow[9] = direction
            print "boatLiving =", boatLiving
            if state == "fail":
                to_follow[direction] = False
                # count = 0
                # for i in range(4):
                #     if to_follow[i + 3] is False:
                #         count += 1
                # if count == 3:
                #     for i in range(4):
                #         if to_follow[3 + i] == 0:
                #             to_follow[3 + i] = True
                IA_following.set(pformat(to_follow))
                print "    state =", to_follow
            elif boatLiving > 0:
                to_follow[7] += 1
                count = 0
                for i in range(4):
                    if (to_follow[3 + i] is True) or (to_follow[3 + i] == "Maybe"):
                        count = 1
                if count == 0:
                    for i in range(4):
                        to_follow[3 + i] = directions[direction - 3][i]
                    detect_T_or_F(oldx, oldy)
                IA_following.set(pformat(to_follow))
                print "    state =", to_follow
                tirIA(ships, "Following", oldx, oldy)
            else:
                for i in range(len(to_follow)):
                    to_follow[i] = 0
                IA_following.set(pformat(to_follow))
                if IA_level.get() == 2:
                    tirIA(ships, "Random")
                elif IA_level.get() == 3:
                    if len(possibleBoat) > 0:
                        tirIA(ships, "Intelligent")
                    else:
                        tirIA(ships, 'Random')

"""



to_follow = [0] * 10
offset = [[-1, 0], [1, 0], [0, 1], [0, -1], "rotation"]
TirsIA = initGrid()
TirsIA[0][1] = 1
directions = [[True, "Maybe", False, False], ["Maybe", True, False, False], [False, False, True, "Maybe"], [False, False, "Maybe", True]]

detect_dir(1, 1, 1, 1, 1)
print to_follow
