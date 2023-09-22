from graphics import GraphWin, color_rgb, Rectangle, Point, Text
from random   import randint

# ------------------------------------------------
# Gobal variables and initializations
# ------------------------------------------------
cube = [[[[None for i in range(5)] for j in range(5)]
         for k in range(5)] for l in range(6)]
# 1. dimension : side (0-5)
#                   0 up
#                   1 down
#                   2 left
#                   3 right
#                   4 front
#                   5 back
# 2. dimension : column (0-4)
# 3. dimension : row (0-4)
# 4. dimension :    0 face_color,
#                   1 piece,
#                   2 changed flag 0: no chage 1: changed position,
#                   4 graphic_object reference rectangle
#                   5 graphic object reference text
# side rotation relative to side 0 Up
side_rotation = {0: 0, 1: 0, 2: 90, 3: 270, 4: 0, 5: 180}

# side move direction sequences (adjusted for relative side orientation)
side_up_move_cycle = {0: [5, 1, 4, 0],
                      1: [4, 0, 5, 1],
                      2: [0, 3, 1, 2],
                      3: [0, 2, 1, 3],
                      4: [0, 5, 1, 4],
                      5: [0, 4, 1, 5]}
side_down_move_cycle = {0: [4, 1, 5, 0],
                        1: [5, 0, 4, 1],
                        2: [1, 3, 0, 2],
                        3: [1, 2, 0, 3],
                        4: [1, 5, 0, 4],
                        5: [1, 4, 0, 5]}
side_left_move_cycle = {0: [2, 1, 3, 0],
                        1: [2, 0, 3, 1],
                        2: [5, 3, 4, 2],
                        3: [4, 2, 5, 3],
                        4: [2, 5, 3, 4],
                        5: [3, 4, 2, 5]}
side_right_move_cycle = {0: [3, 1, 2, 0],
                         1: [3, 0, 2, 1],
                         2: [4, 3, 5, 2],
                         3: [5, 2, 4, 3],
                         4: [3, 5, 2, 4],
                         5: [2, 4, 3, 5]}

# adjacient sides (depending on the move direction, based on the above move cycle dictionaries)
adjacient_left_side_up_down = {
    side: side_left_move_cycle[side][0] for side in range(6)}
adjacient_right_side_up_down = {
    side: side_right_move_cycle[side][0] for side in range(6)}
adjacient_up_side_left_right = {
    side: side_up_move_cycle[side][0] for side in range(6)}
adjacient_down_side_left_right = {
    side: side_down_move_cycle[side][0] for side in range(6)}

# opposite sides
# (the 2nd side in any move cycle is allways the opposite side, direction does not matter)
opposite_side = {side: side_left_move_cycle[side][1] for side in range(6)}

# opposite move directions
opposite_direction = {"Up": "Down",
                      "Right": "Left", "Down": "Up", "Left": "Right"}

# Initialize graphic window
height = 1180
width = 850
win = GraphWin("Cube 5x5x5", width, height)
win.setBackground(color_rgb(50, 50, 50))
win_bottom_status_height = 80
cursor_color_rgb = [255, 255, 255]

# Side indexes 0 Up, 1 Down, 2 Left, 3 Right, 4 Front, 5 Back
side_grid_pos = [[1, 2], [1, 0], [0, 2], [2, 2], [1, 3], [1, 1]]
piece_size = 50
spacer = 3
side_spacer = 0
side_size = (piece_size + spacer) * 5 + side_spacer
x_margin = (win.width - 3 * side_size) // 2
y_margin = (win.height - (win_bottom_status_height + 15) - 4 * side_size) // 2

# cursor, rectangle and text object references (from graphics)
cursor_obj = [None, None, None]
cursor_pos_obj = None
last_move_obj = None
cursor_pos_piece_obj = None
rectangle_obj = Rectangle(Point(0, 0), Point(1, 1))
text_obj = Text(Point(0, 0), "")

# moves history
moves = []

# terminal output 
term_out = 0

def is_color_adjacient(first_color, second_color, third_color=None):
    """ Check if first side color is adjacient to second and, if provided, to third side color

    Args:
        first_color : color first side
        second_color: color second side
        third_color : color third side. Defaults to None.
    Returns:
        boolean: are first and second and, if provided, third sides adjacient ?
    """             
    def is_color_adjacient_2(first_color, second_color):
        """ Check if first side is adjacient to second side.

        Args:
            first_color (int): index first side
            second_color (int): index second side

        Returns:
            boolean: are first and second sides adjacient ?
        """        
        cube_colors_sequences = [["c", "o", "g", "r"]  # cyan, orange, green, red on a first rotation axis
                                 # cyan, black, green, yellow on a second rotation axis
                                 , ["c", "b", "g", "y"], ["b", "r", "y", "o"]]  # black, red, yellow, orange on the last rotation axis

        if first_color == second_color:
            return False

        for seq in cube_colors_sequences:
            index_1 = None
            index_2 = None

            for i in range(len(seq)):

                if seq[i] == first_color:
                    index_1 = i

                if seq[i] == second_color:
                    index_2 = i

            if index_1 != None and index_2 != None:

                if abs(index_1-index_2) == 1 or abs(index_1-index_2) == 3:
                    return True

        return False

    if third_color == None:
        return is_color_adjacient_2(first_color, second_color)
    if first_color != second_color != third_color :
        if is_color_adjacient(first_color, second_color)   \
        and is_color_adjacient(second_color, third_color)  \
        and is_color_adjacient(first_color, third_color):
            return True
    return False


def reorder(word):
    """ Return sorted character string

    Args:
        word (str): string to be sorted

    Returns:
        str: sorted string
    """    
    chars = []
    chars.extend(word)
    chars.sort()
    new_word = ""
    for char in chars:
        new_word = new_word + char
    return (new_word)


# cube colors and pieces
cube_colors = ["c", "g", "o", "r", "b", "y"]
# c : cyan
# g : green
# r : read
# o : orange
# b : black
# y : yellow

cube_centers = list(cube_colors)
cube_centers.sort()
cube_middles = [color+str(col)+str(row)
                for color in cube_colors
                for col in [1, 2, 3]
                for row in [1, 2, 3]
                if not (col == 2 and row == 2)]
cube_middles.sort()

borders = {reorder(color_1 + color_2) + str(n)
            for color_1 in cube_colors
            for color_2 in cube_colors
            for n in range(3)
            if is_color_adjacient(color_1, color_2)}
cube_borders = list(borders)
cube_borders.sort()

corners = {reorder(color_1 + color_2 + color_3)
            for color_1 in cube_colors
            for color_2 in cube_colors
            for color_3 in cube_colors
            if is_color_adjacient(color_1, color_2, color_3)}
cube_corners = list(corners)
cube_corners.sort()

if term_out :
    print("Cube piece names:")
    i = 0
    for cube_pieces in [cube_centers, cube_middles, cube_borders, cube_corners]:
        type = ""
        if cube_pieces == cube_centers:
            type = "centers"
        if cube_pieces == cube_middles:
            type = "middles"
        if cube_pieces == cube_borders:
            type = "borders"
        if cube_pieces == cube_corners:
            type = "corners"
        for piece in cube_pieces:
            print(str(i).rjust(2), type, piece)
            i = i + 1

def border_orientation(first_side, second_side, default_color_side=0):
    """ Returns orientation name for border piece based on the first and second side of the piece

    Args:
        first_side (int): index first side
        second_side (int): index second side

    Returns:
        orientation: N, S, W, E (North, South, West, East)
    """        
    # first_side, second_side :
    #   0 U : up    side
    #   1 D : down  side
    #   2 L : left  side
    #   3 R : right side
    #   4 F : front side
    #   5 B : back  side

    # orientation names ("U", "D", "L", "R") based on the first and second side index (as concatened str)
    first_second = str(first_side) + str(second_side)
    orientation = ""
    orientation_names ={"05": "N", "04": "S", "03": "E", "02": "W", 
                        "14": "N", "15": "S", "13": "E", "12": "W", 
                        "20": "N", "21": "S", "24": "E", "25": "W", 
                        "30": "N", "31": "S", "35": "E", "34": "W", 
                        "40": "N", "41": "S", "43": "E", "42": "W", 
                        "50": "N", "51": "S", "52": "E", "53": "W"}
    if first_second in orientation_names.keys():
        orientation = orientation_names[first_second]
        if default_color_side != 0 :
            rotation = side_rotation[default_color_side]
            if rotation != 0 :
                rotation = 360 - rotation 
                rotated_orientation = {   90: {"N": "E", "E": "S", "S": "W", "W": "N"} 
                                        ,270: {"N": "W", "W": "S", "S": "E", "E": "N"} 
                                        ,180: {"N": "S", "E": "W", "S": "N", "W": "E"} }
                orientation = rotated_orientation[rotation][orientation]

    return orientation


def corner_orientation(first, second, third, default_color_side=0):
    """ Returns orientation name for corner piece based on first, second and third side of the pieac

    Args:
        first (int): index first side
        second (int): index second side
        third (int): index third side
        default_color_side (int) : default color side. Default 0 

    Returns:
        orientation: NW, SW, EN, ES (North West, South West, North East, South Est)
        if side is specified, the relative side roation is considered (in border_orientation)
    """        
    orientation = border_orientation(first, second, default_color_side)
    orientation = orientation + border_orientation(first, third, default_color_side)
    return reorder(orientation)


def default_side(color):
    """ Returns default side based on the color

    Args:
        color (str): color name (b, c, r, g, y, o)

    Returns:
        int: index default side
    """        
    cube_sides = {"U": 0, "D": 1, "F": 4, "B": 5, "L": 2, "R": 3}
    # black is on the up side
    # red is on the front side
    default_side_names = {"b": "U", "y": "D",
                            "r": "F", "o": "B", "g": "L", "c": "R"}
    default_side_name = default_side_names[color]
    side = cube_sides[default_side_name]
    return side


def is_side_adjacient(first_side, second_side, third_side=None):
    """ Check if first side is adjacient to second and, if provided, to third side
        The sides are identified by their side indicies. See cube definition further above

    Args:
        first_side : index first side
        second_side: index second side
        third_side : index third side. Defaults to None.
    Returns:
        boolean: are first and second and, if provided, third sides adjacient ?
    """             
    sides  = [ first_side, second_side, third_side ]
    colors = [ None, None, None ]
    for i in range(3) :
        for color in cube_colors :
            if sides[i] == default_side(color) : 
                colors[i] = color
    return is_color_adjacient(colors[0], colors[1], colors[2])


def init_cube():
    """ Initialie cube

    Returns:
        None
    """    

    global cube

    cube = [[[[None for i in range(5)] for j in range(5)]
             for k in range(5)] for l in range(6)]
    side = None

    # set default cube for centers ("b", "c", "g", "y", "o", "r" )
    for piece in cube_centers:
        side = default_side(piece)
        # for centers color = piece (eg: "b", "c", ...)
        cube[side][2][2][0] = piece
        cube[side][2][2][1] = piece
        cube[side][2][2][2] = 1             # flagged as changed

    # set default cube for middles (eg: "b11", "b12", "b13", "b21", "b23", "b31", "b32", "b33", ...)
    for piece in cube_middles:
        side = default_side(piece[0])
        col = int(piece[1])
        row = int(piece[2])
        # for middles color = first letter from piece name (eg: "b11")
        cube[side][col][row][0] = piece[0]
        cube[side][col][row][1] = piece
        cube[side][col][row][2] = 1         # flagged as changed

    # set default cube for borders (eg: "bg0", "bg1", "bg2", "rg0", "rg1", ... )
    for piece in cube_borders:
        # border position offset on the col or the row axis
        offset = int(piece[2])
        side_1 = default_side(piece[0])     # color 1
        side_2 = default_side(piece[1])     # color 2

        # set default cube for border piece in its 2 color sides
        # the color is the first and second letter of the piece name
        # and is passed as 3rd element of each color_side sub list
        for color_side in [[side_1, side_2, piece[0]], [side_2, side_1, piece[1]]]:
            orientation = border_orientation(color_side[0], color_side[1])
            if orientation == "N":  # North
                if color_side[1] != 5 and color_side[1] != 2:
                    col = 1 + offset
                else:
                    col = 3 - offset
                row = 0
            if orientation == "S":  # South
                if color_side[1] != 5:
                    col = 1 + offset
                else:
                    col = 3 - offset
                row = 4
            if orientation == "E":  # East
                col = 4
                if color_side[1] != 3:
                    row = 1 + offset
                elif color_side[0] != 1:
                    row = 3 - offset
                else:
                    row = 1 + offset
            if orientation == "W":  # West 
                col = 0
                if color_side[1] != 4 and color_side[1] != 2 or color_side[0] == 0 or color_side[0] == 4:
                    row = 1 + offset
                else:
                    row = 3 - offset

            cube[color_side[0]][col][row][0] = color_side[2]
            cube[color_side[0]][col][row][1] = piece
            cube[color_side[0]][col][row][2] = 1        # flagged as changed

    # set default cube for corners ("bco", "bgo", "bcr", "bgr", "coy", "cry", "goy", "gry")
    for piece in cube_corners:
        side_1 = default_side(piece[0])
        side_2 = default_side(piece[1])
        side_3 = default_side(piece[2])

        # set default cube for corner piece in its 3 color sides
        # the color is the first, second and thirst letter of the piece name
        # and is passed as 4th element of each color_side sub list
        for color_side in [[side_1, side_2, side_3, piece[0]], [side_2, side_1, side_3, piece[1]], [side_3, side_2, side_1, piece[2]]]:
            orientation = corner_orientation(
                color_side[0], color_side[1], color_side[2])
            if orientation == "NW":     # North West 
                col = 0
                row = 0
            if orientation == "SW":     # South West
                col = 0
                row = 4
            if orientation == "EN":     # North East
                col = 4
                row = 0
            if orientation == "ES":     # South East
                col = 4
                row = 4
            cube[color_side[0]][col][row][0] = color_side[3]
            cube[color_side[0]][col][row][1] = piece
            cube[color_side[0]][col][row][2] = 1        # flagged as changed

    if term_out :
        print("Cube piece cube positions (count, face, col, row, color, piece):")
        i = 0
        for face in cube:
            for col in face:
                for color_piece in col:
                    type = ""
                    if color_piece[1] in cube_centers:
                        type = "centers"
                    if color_piece[1] in cube_middles:
                        type = "middles"
                    if color_piece[1] in cube_borders:
                        type = "borders"
                    if color_piece[1] in cube_corners:
                        type = "corners"
                    print(str(i).rjust(3, " "), cube.index(face), face.index(col),
                        col.index(color_piece), color_piece[0], type, color_piece[1])
                    i = i + 1


def display_unfolded_cube(scope="cube"
                        , cursor_pos=None
                        , side_selected=False
                        , side_sequence=[0, 3, 4, 2, 5, 1]):
    """ Display cube unfolded 2D

    Args:
        scope (str, optional): Display cube only or cursor or all. Defaults to "cube".
        cursor_pos (list, optional): cursor position as list of side, col and row index. Defaults to None.
        side_sequence (list, optional): list of sides to be display. Defaults to [0, 3, 4, 2, 5, 1].

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """    
    global cursor_obj
    global cursor_pos_obj
    global cursor_pos_piece_obj
    global last_move_obj
    global cube

    color_codes = {"c": color_rgb(0, 200, 255), "g": color_rgb(0, 200, 0), "o": color_rgb(
        255, 140, 0), "r": color_rgb(200, 0, 0), "b": color_rgb(0, 0, 0), "y": color_rgb(255, 255, 0)}
    background_color_codes = {"c": color_rgb(0, 0, 0), "g": color_rgb(0, 0, 0), "o": color_rgb(
        0, 0, 0), "r": color_rgb(155, 255, 255), "b": color_rgb(255, 255, 255), "y": color_rgb(0, 0, 255)}

    def get_x_y(side_index, col_index, row_index, consider_side_rotation=True):
        rotated_col_row = [col_index, row_index]
        if consider_side_rotation:
            rotation = side_rotation[side_index]
            rotated_col_row = rotate_side([col_index, row_index], rotation)
        x = x_margin + side_grid_pos[side_index][0] * \
            side_size + rotated_col_row[0] * (piece_size + spacer)
        y = y_margin + side_grid_pos[side_index][1] * \
            side_size + rotated_col_row[1] * (piece_size + spacer)
        return x, y

    def side_iter(side_sequence):
        for index in side_sequence:
            yield cube[index]

    if scope == "cursor" and cursor_obj[0] != None:
        cursor_obj[0].undraw()
        if cursor_obj[1] != None:
            cursor_obj[1].undraw()
        if cursor_obj[2] != None:
            cursor_obj[2].undraw()
    else:
        if scope in ("cube", "all"):
            for side in side_iter(side_sequence):
                side_index = cube.index(side)
                for col in side:
                    col_index = side.index(col)
                    for row in col:
                        row_index = col.index(row)
                        if row[2] == 1:                        # piece has changed
                            color = row[0]
                            # coordinate previous rectange (p1)
                            x0, y0 = 0, 0
                            x, y = get_x_y(side_index, col_index, row_index)
                            if row[3] != None:
                                x0, y0 = row[3].getP1().x, row[3].getP1().y
                                row[3].move(x-x0, y-y0)
                            else:
                                row[3] = Rectangle(Point(x, y), Point(
                                    x + piece_size, y + piece_size))
                                row[3].setFill(color_codes[color])
                                row[3].draw(win)
                            if row[4] != None:
                                row[4].move(x-x0, y-y0)
                            else:
                                #pass
                                center = row[3].getCenter()
                                #row[4] = Text(Point(center.x, center.y), str(col_index) + str(row_index))
                                row[4] = Text(Point(center.x, center.y), row[1])
                                row[4].setTextColor(background_color_codes[color])
                                row[4].draw(win)
                            row[2] = 0
                # sleep(2)

    if scope in ("cursor", "all"):
        side_index = cursor_pos[0]

        if side_selected:
            cursor_obj[0].undraw()
            if cursor_obj[1] != None:
                cursor_obj[1].undraw()
            if cursor_obj[2] != None:
                cursor_obj[2].undraw()
            x, y = get_x_y(side_index, 0, 0, False) 
            cursor_obj[0] = Rectangle(Point(x, y), Point(
                x + 5 * (piece_size + spacer), y + 5 * (piece_size + spacer)))
            cursor_obj[0].setWidth(spacer * 3)
            cursor_obj[0].setOutline(
                color_rgb(cursor_color_rgb[0], cursor_color_rgb[1], cursor_color_rgb[2]))
            cursor_obj[0].draw(win)

        else:
            col_index = cursor_pos[1]
            row_index = cursor_pos[2]
            x, y = get_x_y(side_index, col_index, row_index)
            cursor_obj[0] = Rectangle(Point(x, y), Point(
                x + piece_size, y + piece_size))
            cursor_obj[0].setWidth(spacer * 3)
            cursor_obj[0].setOutline(
                color_rgb(cursor_color_rgb[0], cursor_color_rgb[1], cursor_color_rgb[2]))
            cursor_obj[0].draw(win)

            if col_index in (0, 4) or row_index in (0, 4):
                cursor_obj_index = 0
                for s in range(6):
                    if s != side_index:
                        for c in range(5):
                            for r in range(5):
                                if cube[side_index][col_index][row_index][1] == cube[s][c][r][1]:
                                    cursor_obj_index = cursor_obj_index + 1
                                    x, y = get_x_y(s, c, r)
                                    cursor_obj[cursor_obj_index] = Rectangle(
                                        Point(x, y), Point(x + piece_size, y + piece_size))
                                    cursor_obj[cursor_obj_index].setWidth(spacer)
                                    cursor_obj[cursor_obj_index].setOutline(
                                        color_rgb(cursor_color_rgb[0], cursor_color_rgb[1], cursor_color_rgb[2]))
                                    cursor_obj[cursor_obj_index].draw(win)
            else:
                cursor_obj[1], cursor_obj[2] = None, None

            if cursor_pos_obj != None:
                cursor_pos_obj.undraw()
            cursor_pos_obj = Text(Point(win.width - 120, win.height -
                                win_bottom_status_height), "cursor : " + str(cursor_pos))
            cursor_pos_obj.setTextColor(color_rgb(255, 255, 255))
            cursor_pos_obj.draw(win)

            if cursor_pos_piece_obj != None:
                cursor_pos_piece_obj.undraw()
            cursor_pos_piece_obj = Text(Point(win.width - 130, win.height - win_bottom_status_height + 20), "piece : "
                                        + str(cube[cursor_pos[0]][cursor_pos[1]][cursor_pos[2]][1]).rjust(5, " "))
            cursor_pos_piece_obj.setTextColor(color_rgb(255, 255, 255))
            cursor_pos_piece_obj.draw(win)

            if last_move_obj != None:
                last_move_obj.undraw()
            if len(moves) > 0 :
                last_move_obj = Text(Point(win.width - 100, win.height -
                                    win_bottom_status_height + 40), "last : " + str(moves[len(moves)-1]))
                last_move_obj.setTextColor(color_rgb(255, 255, 255))
                last_move_obj.draw(win)


def display_keys_usage():
    """ Display key usage legend 

    Args:
        none
    Returns:
        none
    """             
    line_0 = "< n > : new cube                      < r > : revese all moves"
    line_1 = "< arrow-keys > : select          < escape > : end"
    line_2 = "< w, a, s, d > : rotate               < space > : shuffle"
    line_3 = "< shift L/R > : turn left/right     < Ctrl > : side selection"
    t0 = Rectangle(Point(0, win.height - win_bottom_status_height - 15),
                   Point(win.width, win.height))
    t0.setFill(color_rgb(0, 0, 0))
    t1 = Text(Point(190, win.height -
              win_bottom_status_height + 0), line_0)
    t2 = Text(Point(165, win.height -
              win_bottom_status_height + 20), line_1)
    t3 = Text(Point(170, win.height -
              win_bottom_status_height + 40), line_2)
    t4 = Text(Point(188, win.height -
              win_bottom_status_height + 60), line_3)
    t1.setFace("arial")
    t2.setFace("arial")
    t3.setFace("arial")
    t4.setFace("arial")
    t1.setTextColor(color_rgb(255, 255, 255))
    t2.setTextColor(color_rgb(255, 255, 255))
    t3.setTextColor(color_rgb(255, 255, 255))
    t4.setTextColor(color_rgb(255, 255, 255))
    t0.draw(win)
    t1.draw(win)
    t2.draw(win)
    t3.draw(win)
    t4.draw(win)


def rotate_side(col_row, rotation=0):
    """ Returns rotated col and row index side coordinate in respect to the given side rotation.
        If no rotation spefice col and row index remain unchanged.

    Args:
        col_row : list (2) of col and row index
        rotation : relative rotation to side 0 in degree 
    Returns:
        new_col_row : list (2) of rotated col and row index
    """             

    new_col_row = [0, 0]
    if rotation == 0 or abs(rotation) % 360 == 0:      # no rotation
        new_col_row[0] = col_row[0]
        new_col_row[1] = col_row[1]
    elif abs(rotation) == 180:                         # 180 rotation
        new_col_row[0] = 4 - col_row[0]
        new_col_row[1] = 4 - col_row[1]
    elif rotation in (90, -270):                       # 90 clockwise
        new_col_row[0] = 4 - col_row[1]
        new_col_row[1] = col_row[0]
    elif rotation in (-90, 270):                       # 90 anti-clockwise or 270 clocwie
        new_col_row[0] = col_row[1]
        new_col_row[1] = 4 - col_row[0]
    return new_col_row


def relative_rotation(from_side, to_side) :
    """ Returns the relative rotation (360 degrees base) between to_side and from side.

    Args:
        from_side : from side index
        to_side : to side index 
    Returns:
        rotation : relative rotation between to and from side
    """  
    rotation = side_rotation[from_side] - side_rotation[to_side]

    if rotation < 0 :
        rotation = 360 + rotation
    return rotation


def translate_col_row(from_side, to_side, from_col, from_row):
    rotated_col_row = [from_col, from_row]
    rotation = relative_rotation(to_side, from_side)
    if not rotation in (90, 270):  # or this_side in (0, 1) or prev_side in (0, 1)
        rotated_col_row = rotate_side([from_col, from_row], rotation)
    elif from_side == 0 or to_side == 0:
        rotation = rotation - 180
        if rotation < 0:
            rotation = 360 + rotation
        rotated_col_row = rotate_side([from_col, from_row], rotation)
    elif from_side == 1 or to_side == 1:
        rotated_col_row = rotate_side([from_col, from_row], rotation)
    return rotated_col_row


def navigate_pos(position, direction, side_selected=False):
    """ Navigate cursor from current position to the given direction

    Args:
        position (list): [side, row, col]
        direction (string): "Up", "Down", "Left", "Right"
        side_selected (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    # next side (direction relative to side orientation)
    next_side_up_rotation = {0: 5, 5: 0, 1: 4, 4: 0, 2: 0, 3: 0}
    next_side_down_rotation = {0: 4, 4: 1, 1: 5, 5: 1, 2: 1, 3: 1}
    next_side_right_rotation = {0: 3, 3: 5, 5: 2, 2: 4, 4: 3, 1: 3}
    next_side_left_rotation = {0: 2, 2: 5, 5: 3, 3: 4, 4: 2, 1: 2}
    rotation = 0
    current_side = position[0]
    current_col = position[1]
    current_row = position[2]
    pos = [0, 2, 2]

    # find out col and row chagnes based on the direation
    direction_to_col_row_change = {
        "Up": [0, -1], "Down": [0, +1], "Right": [+1, 0], "Left": [-1, 0]}
    col_row_change = direction_to_col_row_change[direction]
    col_change, row_change = col_row_change[0], col_row_change[1]
    next_side = position[0]

    if current_col + col_change >= 0 and current_col + col_change <= 4 \
            and current_row + row_change >= 0 and current_row + row_change <= 4 \
        and not side_selected:
        # same side but differen position
        pos[0] = current_side
        pos[1] = current_col + col_change
        pos[2] = current_row + row_change

    else:
        # find out next side based on the global next_side_* dictionaries
        next_side_dict_dict = {"Up": next_side_up_rotation,
                               "Down": next_side_down_rotation,
                               "Left": next_side_left_rotation,
                               "Right": next_side_right_rotation}
        next_side_dict = next_side_dict_dict[direction]
        next_side = next_side_dict[current_side]
        
        # finally set next position (rotate position if necessary based on the relative rotation)
        next_side_col_row = translate_col_row(current_side, next_side, current_col, current_row)
        rotation = relative_rotation(current_side, next_side)
        if rotation in (0, 180) :
            if col_change == 0 :
                next_side_col_row[1] = 4 - next_side_col_row[1]
            else :
                next_side_col_row[0] = 4 - next_side_col_row[0]
        elif current_side in (0,1) :
            next_side_col_row[1] = 4 - next_side_col_row[1]
        else :
            next_side_col_row[0] = 4 - next_side_col_row[0]

        pos[0] = next_side
        pos[1] = next_side_col_row[0]
        pos[2] = next_side_col_row[1]

    if term_out :
        print("navigate: from", position, "to", pos, "rotating", rotation)
    return pos


def rotate_direction(side, direction):
    direction_to_rotation = {"Up": 0, "Right": 90, "Down": 180, "Left": 270}
    rotation_to_direction = {0: "Up", 90: "Right", 180: "Down", 270: "Left"}
    rotation = direction_to_rotation[direction]
    rotation = rotation - side_rotation[side]
    if rotation < 0:
        rotation = 360 + rotation
    return rotation_to_direction[rotation]


def navigate_unfolded(position, direction, side_selected):
    rotated_direction = rotate_direction(position[0], direction)
    return navigate_pos(position,  rotated_direction, side_selected)


def rotate(side, rotation):
    saved_side = [[cube[side][col][row].copy() for row in range(5)]
                  for col in range(5)]
    for col in range(5):
        for row in range(5):
            rotated_col_row = rotate_side([col, row], rotation)
            cube[side][rotated_col_row[0]][rotated_col_row[1]
                                           ] = saved_side[col][row].copy()
            cube[side][rotated_col_row[0]][rotated_col_row[1]][2] = 1


def move(position, direction):
    global cursor_obj
    global cube

    side_move_cycle = {"Up": side_up_move_cycle,
                       "Down": side_down_move_cycle,
                       "Right": side_right_move_cycle,
                       "Left": side_left_move_cycle}
    move_cycle = side_move_cycle[opposite_direction[direction]]

    this_side = position[0]
    this_col = position[1]
    this_row = position[2]
    prev_sides = move_cycle[this_side]

    this_cols = [None for i in range(5)]
    this_rows = [None for i in range(5)]
    for i in range(5):
        if direction in ("Up", "Down"):
            this_cols[i] = this_col
            this_rows[i] = i
        else:
            this_cols[i] = i
            this_rows[i] = this_row

    adjacient_left_direction = {
        "Up": adjacient_left_side_up_down, "Down": adjacient_left_side_up_down}
    adjacient_right_direction = {
        "Up": adjacient_right_side_up_down, "Down": adjacient_right_side_up_down}
    adjacient_up_direction = {
        "Left": adjacient_up_side_left_right, "Right": adjacient_up_side_left_right}
    adjacient_down_direction = {
        "Left": adjacient_down_side_left_right, "Right": adjacient_down_side_left_right}

    adjacient_left = None
    adjacient_right = None
    adjacient_up = None
    adjacient_down = None
    if direction in ("Up", "Down"):
        adjacient_left = adjacient_left_direction[direction]
        adjacient_right = adjacient_right_direction[direction]
    elif direction in ("Left", "Right"):
        adjacient_up = adjacient_up_direction[direction]
        adjacient_down = adjacient_down_direction[direction]

    saved_side = [[cube[this_side][col][row].copy() for row in range(5)]
                  for col in range(5)]
    cursor_obj[0].undraw()
    if cursor_obj[1] != None:
        cursor_obj[1].undraw()
    if cursor_obj[2] != None:
        cursor_obj[2].undraw()

    for side_index in range(4):
        prev_side = prev_sides[side_index]
        prev_cols = [None for col in range(5)]
        prev_rows = [None for row in range(5)]
        if side_index < 3:
            # first 3 sides
            for col_row_index in range(5):
                this_col = this_cols[col_row_index]
                this_row = this_rows[col_row_index]
                [prev_col, prev_row] = translate_col_row(this_side, prev_side, this_col, this_row)
                cube[this_side][this_col][this_row] = cube[prev_side][prev_col][prev_row]
                cube[this_side][this_col][this_row][2] = 1
                prev_cols[col_row_index] = prev_col
                prev_rows[col_row_index] = prev_row
        else:
            # last side
            for col_row_index in range(5):
                this_col = this_cols[col_row_index]
                this_row = this_rows[col_row_index]
                [prev_col, prev_row] = translate_col_row(this_side, prev_side, this_col, this_row)
                cube[this_side][this_col][this_row] = saved_side[prev_col][prev_row]
                cube[this_side][this_col][this_row][2] = 1
                prev_cols[col_row_index] = prev_col
                prev_rows[col_row_index] = prev_row

        this_side = prev_side
        this_cols = prev_cols.copy()
        this_rows = prev_rows.copy()

    # check for lateral side rotations
    if position[1] in (0, 4) and direction in ("Up", "Down"):
        # rotating from position column is on the edge to another side (which has to be rotated)
        # left or right side has to be rotated
        if direction == "Up":
            if position[1] == 0:
                rotate(adjacient_left[position[0]], 270)
            else:
                rotate(adjacient_right[position[0]], 90)
        elif direction == "Down":
            if position[1] == 0:
                rotate(adjacient_left[position[0]], 90)
            else:
                rotate(adjacient_right[position[0]], 270)
    elif position[2] in (0, 4) and direction in ("Left", "Right"):
        # rotating from position row is on the edge to another side (which has to be rotated)
        # up or down side has to be rotated
        if direction == "Left":
            if position[2] == 0:
                rotate(adjacient_up[position[0]], 90)
            else:
                rotate(adjacient_down[position[0]], 270)
        elif direction == "Right":
            if position[2] == 0:
                rotate(adjacient_up[position[0]], 270)
            else:
                rotate(adjacient_down[position[0]], 90)
    moves.append([position, direction])
    if term_out :
        print("        move:", len(moves)-1, moves[len(moves)-1])
    #win.getKey()


def move_from_cursor(position, direction, side_selected=False):
    side = position[0]
    col  = position[1]
    row  = position[2]
    piece = cube[side][col][row][1]
    color = cube[side][col][row][0]
    rotated_direction = rotate_direction(side, direction) 
    if not side_selected : 
        move(position, rotated_direction)
    else:
        rotated_direction = rotate_direction(side, direction)
        for i in range(5):
            if rotated_direction in ("Up", "Down"): 
                move([side, i, row], rotated_direction)
            else:
                move([side, col, i], rotated_direction)
    new_position = position
    for i in range(6) :
        for j in range(5) :
            for k in range(5) :
                if   cube[i][j][k][1] == piece \
                and  cube[i][j][k][0] == color :  
                    new_position = [i, j, k]
    return position


def turn(position, rotation):
    rotate_from_pos_90_dict = { 0: [[5, 0, 0], "Left"], 
                                5: [[0, 0, 0], "Left"],
                                4: [[0, 4, 4], "Right"],
                                1: [[5, 4, 4], "Right"], 
                                2: [[0, 0, 0], "Down"], 
                                3: [[0, 4, 0], "Up"] }
    rotate_from_pos_270_dict = { 0: [[5, 0, 0], "Right"], 
                                 5: [[0, 0, 0], "Right"],
                                 4: [[0, 4, 4], "Left"], 
                                 1: [[5, 4, 4], "Left"], 
                                 2: [[0, 0, 0], "Up"], 
                                 3: [[0, 4, 0], "Down"] }
    rotate_from_pos_dict = { 90: rotate_from_pos_90_dict, 270: rotate_from_pos_270_dict }
    this_side = position[0]
    if term_out :
        print("    turn: this side", this_side, "rotation", rotation)
    if rotation == 180 :
        rotate_from_pos = rotate_from_pos_dict[90]
        from_pos  = rotate_from_pos[this_side][0]
        direction = rotate_from_pos[this_side][1]
        for i in range(2) :
            move(from_pos, direction)
    else :
        rotate_from_pos = rotate_from_pos_dict[rotation]
        from_pos  = rotate_from_pos[this_side][0]
        direction = rotate_from_pos[this_side][1]
        move(from_pos, direction)
    

def shuffle_cube():
    direction = ["Up", "Down", "Left", "Right"]
    for i in range(randint(1, 32)):
        side = randint(0, 5)
        col = randint(0, 4)
        row = randint(0, 4)
        dir = direction[randint(0, 3)]
        # if dir == "Right" and col == 0 and side in (0, 4) :
        move([side, col, row], dir)
        display_unfolded_cube("cube")
    display_unfolded_cube("cursor", cursor_pos)


def new_cube():
    global win
    global cursor_pos
    win.close()
    win = GraphWin("Cube 5x5x5", width, height)
    win.setBackground(color_rgb(40, 40, 40))
    init_cube()
    moves.clear()
    display_unfolded_cube("all", cursor_pos)
    display_keys_usage()


def reverse_moves():
    move_history = [moves[i].copy() for i in range(len(moves)-1, -1, -1)]
    for m in move_history:
        direction = opposite_direction[m[1]]
        move(m[0], direction)
        display_unfolded_cube("cube")
    moves.clear()
    display_unfolded_cube("cursor", cursor_pos)

def solve_cube(cursor_pos, first_color='b'):

    def find_piece(piece, color=None): 
        for side_index in range(6):
            for col_index in range(5):
                for row_index in range(5):
                    if cube[side_index][col_index][row_index][1] == piece:
                        if color == None \
                        or color == cube [side_index][col_index][row_index][0] :
                            return [side_index, col_index, row_index]


    def relative_direction(from_side, to_side):
        direction = None
        if   to_side == 0 : direction = "Up"
        elif to_side == 1 : direction = "Down"
        else : 
            to_from_side_dict = {2 : {0: "Left",  1: "Left",  5: "Right", 4: "Left",  3: "Down"} 
                                ,3 : {0: "Right", 1: "Right", 5: "Left",  4: "Right", 2: "Up"}
                                ,4 : {0: "Down",  1: "Up",    3: "Left",  2: "Right", 5: "Right"}
                                ,5 : {0: "Up",    1:"Down",   3: "Right", 2: "Left",  4: "Left"} }
            direction = to_from_side_dict[to_side][from_side]
        if term_out :
            print("    from side", from_side, "to side", to_side, "direction", direction)
        return direction 


    def is_piece_reversed(piece, side, side_color): 
        reversed = False
        if piece in (cube_borders + cube_corners) :
            # one part of the piece is on the specified side but 
            # with the wrong color
            for col in cube[side] :
                for row in col : 
                    if row[1] == piece and row[0] != side_color :
                        reversed = True
        return reversed
    

    def is_border_on_bottom_row(piece, from_pos, to_side, side_color): 
        on_bottom_row = False
        from_side = from_pos[0]
        from_col  = from_pos[1]
        from_row  = from_pos[2]
        if not is_piece_reversed(piece, to_side, side_color) :
            if is_side_adjacient(from_side, to_side) : 
                if relative_direction(from_side, to_side) in ("Up", "Down") :
                    if from_row in (0, 4) :
                        on_bottom_row = True
                else :
                    if from_col in (0, 4) :
                        on_bottom_row = True
        return on_bottom_row


    def is_piece_aligned(from_pos, to_pos) :
        aligned       = False
        from_side     = from_pos[0]
        to_side       = to_pos[0]
        translated_col_row = translate_col_row(from_side, to_side, from_pos[1], from_pos[2])
        if translated_col_row[0] == to_pos[1] and translated_col_row[1] == to_pos[2] :
            aligned = True
        return aligned


    def move_oppositie_corner_to_bottom_row(piece, from_pos, to_side) :
        # take the first the adjacient side of the corner
        for color in piece :
            if color != first_color :
                from_adjacient_pos  = find_piece(piece, color)
                from_adjacient_side = from_adjacient_pos[0]
                from_adjacient_col  = from_adjacient_pos[1]
                from_adjacient_row  = from_adjacient_pos[2]

                turn_rotation = 270
                direction = relative_direction(from_adjacient_side, to_side)
                if direction == "Up" and from_adjacient_col == 4 or \
                    direction == "Left"  and from_adjacient_row == 0 or \
                    direction == "Right" and from_adjacient_row == 4 or \
                    direction == "Down"  and from_adjacient_col == 0 :
                    turn_rotation = 90

                # 1. turn once adjacient side
                turn(from_adjacient_pos, turn_rotation)
                display_unfolded_cube("cube")
                # 2. turn twice the opposite side
                turn(from_pos, turn_rotation)
                display_unfolded_cube("cube")
                turn(from_pos, turn_rotation)
                display_unfolded_cube("cube")
                # 3. turn adjacient side back
                turn(from_adjacient_pos, 360 - turn_rotation)
                display_unfolded_cube("cube")
                break # do not repeat fo the second adjacient side


    def move_aligned_corner(from_pos, to_pos) :
        from_side = from_pos[0]
        from_col  = from_pos[1]
        from_row  = from_pos[2]
        to_side   = to_pos[0]

        turn_rotation = 270
        direction = relative_direction(from_side, to_side)
        if direction == "Up" and from_col == 4 or \
            direction == "Left"  and from_row == 0 or \
            direction == "Right" and from_row == 4 or \
            direction == "Down"  and from_col == 0 :
            turn_rotation = 90
        
        # turn adjacient side forwards
        turn(from_pos, turn_rotation)
        display_unfolded_cube("cube")
        opposite_side_pos = [opposite_side[to_side], 2, 2]

        # turn opposite side 
        turn(opposite_side_pos, turn_rotation)
        display_unfolded_cube("cube")

        # turn adjacient side backwards
        turn(from_pos, 360 - turn_rotation)
        display_unfolded_cube("cube")

    def move_aligned_border(from_pos, to_pos) :
        from_side = from_pos[0]
        from_col  = from_pos[1]
        from_row  = from_pos[2]
        to_side   = to_pos[0]

        turn_rotation = 270
        move_direction = "Left"
        direction = relative_direction(from_side, to_side)
        if direction == "Up" and from_col == 4 or \
            direction == "Left"  and from_row == 0 or \
            direction == "Right" and from_row == 4 or \
            direction == "Down"  and from_col == 0 :
            turn_rotation = 90
            move_direction = "Right"
        
        # turn adjacient side forwards
        turn(from_pos, turn_rotation)
        display_unfolded_cube("cube")
   
        # move border to the left or right to place it 
        rotated_col_row = rotate_side([from_col, from_row], turn_rotation)
        move([from_side, rotated_col_row[0], rotated_col_row[1]], move_direction)
        display_unfolded_cube("cube")

        # turn adjacient side backwards
        turn(from_pos, 360 - turn_rotation)
        display_unfolded_cube("cube")


    def move_lateral_aligned_border(from_pos, to_pos) :
        from_side = from_pos[0]
        from_col  = from_pos[1]
        from_row  = from_pos[2]
        to_side   = to_pos[0]

        turn_rotation = 270
        move_direction = "Left"
        direction = relative_direction(from_side, to_side)
        if direction == "Up" and from_col == 0 or \
            direction == "Left"  and from_row == 0 or \
            direction == "Right" and from_row == 4 or \
            direction == "Down"  and from_col == 0 :
            turn_rotation = 90
            move_direction = "Right"
        
        # turn adjacient side forwards
        turn(from_pos, turn_rotation)
        display_unfolded_cube("cube")
   
        # move border to the left or right to place it 
        rotated_col_row = rotate_side([from_col, from_row], turn_rotation)
        move([from_side, rotated_col_row[0], rotated_col_row[1]], move_direction)
        display_unfolded_cube("cube")

        # turn adjacient side backwards
        turn(from_pos, 360 - turn_rotation)
        display_unfolded_cube("cube")


    def fill_piece_travels(color, pieces, side) :
        # find misplaced piece from / to positions an keep them in piece_travels list
        piece_travels = []

        if pieces[0] in cube_corners : 
            # cube_corners 
            col_row_dict = {"NW": [0, 0], "EN": [4, 0], "SW": [0, 4], "ES": [4, 4]}
            for corner in pieces :
                if color in corner :
                    from_pos = find_piece(corner, color)
                    side_0 = default_side(corner[0])
                    side_1 = default_side(corner[1])
                    side_2 = default_side(corner[2])
                    orientation = corner_orientation(side_0, side_1, side_2, side)
                    col_row = col_row_dict[orientation]
                    to_pos = [side, col_row[0], col_row[1]]
                    if from_pos != to_pos :
                        piece_travels.append([corner, from_pos, to_pos])
                        if term_out : 
                            print("    travel corner", corner, "from", from_pos, "to", to_pos)

        if pieces[0] in cube_borders : 
            # cube_corners 
            border_col_row_dict = {"N": [1, 0], "E": [4, 3], "S": [3, 4], "W": [0, 1]}
            for border in pieces :
                if color in border :
                    from_pos = find_piece(border, color)
                    side_0 = default_side(border[0])
                    side_1 = default_side(border[1])
                    orientation = border_orientation(side_0, side_1, side)
                    col_row = border_col_row_dict[orientation].copy()
                    border_offset = int(border[2])
                    if orientation == "N" :
                        col_row[0] = col_row[0] + border_offset
                    elif orientation == "S" :
                        col_row[0] = col_row[0] - border_offset
                    elif orientation == "W" :
                        col_row[1] = col_row[1] + border_offset  
                    elif orientation == "E" :
                        col_row[1] = col_row[1] - border_offset 
                    to_pos = [side, col_row[0], col_row[1]]
                    if from_pos != to_pos :
                        piece_travels.append([border, from_pos, to_pos])
                        if term_out :
                            print("    travel border", border, "from", from_pos, "to", to_pos)

        return piece_travels


    def solve_first_center(first_side, first_color):
        if term_out :
            print("solve_first_side_center")
        pos = find_piece(first_color)
        while first_side != pos[0] :
            move(pos, relative_direction(pos[0], first_side))
            display_unfolded_cube("cube")
            pos = find_piece(first_color)


    def solve_first_corners(first_side, first_color):
        if term_out : 
            print("solve_first_corners")
        misplaced_piece_travels = []
        # If misplaced corners exist place them to their target position starting with
        #
        #    1. the ones on the target side but on the wrong position
        #    2. the ones which are on the target side but with the wrong color (reversed)
        #    3. the ones which have the target color on the opposite side
        #    4. the ones placed on the bottom line (row or col depending on oritentation) 
        #       of the adjacient side (alligned)
        #
        #  After one piece has been moved to its correct target place, 
        #  skip the other and re-evaluate how many misplaced pieces are still there.  

        # process until no more misplaced pieces are found
        misplaced_piece_travels = fill_piece_travels(first_color, cube_corners, first_side)
        while len(misplaced_piece_travels) > 0 :
            for travel in misplaced_piece_travels :
                piece     = travel[0]
                from_pos  = travel[1]
                from_side = from_pos[0]
                from_col  = from_pos[1]
                from_row  = from_pos[2]
                to_pos    = travel[2]
                to_side   = to_pos[0]
                to_col    = to_pos[1]
                to_row    = to_pos[2] 

                # case 1 : check if target side has to be rotated to place the corner
                #          only when all corners are misplaced
                if from_side == to_side and len(misplaced_piece_travels) == 4 :
                    if from_col != to_col and from_row != to_row :
                        turn(from_pos, 180)
                    elif from_col == to_col == 4 :
                        turn(from_pos, 270)
                    else :
                        turn(from_pos, 90)
                    display_unfolded_cube("cube")
                    break   # skip and re-evaluate remaining misplaced pieace
                
                # case 2 : check if corner piece is on the target side but reversed and move it  
                #          down to the bottom row. Use same move as for alligned corners, just take 
                #          the piece aligned on the bottom row 
                if is_piece_reversed(piece, to_side, first_color) :
                    if term_out :
                        print("    corner", piece, "is reversed. Has to be moved down")
                    direction = relative_direction(from_side, to_side)
                    if direction  == "Up" :
                        from_row = 4
                    elif direction == "Down" :
                        from_row = 0
                    elif direction == "Left" :
                        from_col = 4
                    else :
                        from_col = 0
                    translated_col_row = translate_col_row(from_side, to_side, from_col, from_row)
                    from_aligned_pos = [from_side, from_col, from_row]
                    to_aligned_pos   = [to_side, translated_col_row[0], translated_col_row[1]]
                    move_aligned_corner(from_aligned_pos, to_aligned_pos)
                    break   # skip and re-evaluate remaining misplaced pieace

                # case 3 : check if corner is on the opposite side move it up to the bottom row
                if from_side == opposite_side[to_side] :
                    if term_out :
                        print("    corner", piece, "is on the opposite side. Has to be moved to the botton row")

                    move_oppositie_corner_to_bottom_row(piece, from_pos, to_side)
                    break   # skip and re-evaluate remaining misplaced pieace
                    
                # case 4 : if corner on adjacient side but not reversed then 
                #          align it first than place it.
                if is_side_adjacient(from_side, to_side) :
                    if not is_piece_aligned(from_pos, to_pos) :
                        opposite_side_pos = [opposite_side[to_side], 2, 2]
                        turn(opposite_side_pos, 270)         # TODO : avoid blind turning
                        display_unfolded_cube("cube")
                        break # skip and re-evaluate remaining misplaced pieace
                    else :
                        if term_out : 
                            print("    corner", piece, "is aligned")
                        move_aligned_corner(from_pos, to_pos)

                    break   # skip and re-evaluate remaining misplaced pieace

            # process until no more misplaced pieces are found
            misplaced_piece_travels = fill_piece_travels(first_color, cube_corners, first_side)


    def sovle_first_borders(first_side, first_color):
        print("solve_first_borders")
        misplaced_piece_travels = []
        # If misplaced borders exist place them to their target position starting with
        #
        #    1. the ones on the target side but on the wrong position
        #    2. the ones which are on the target side but with the wrong color (reversed)
        #    3. the ones which have the target color on the opposite side
        #    4. the ones placed on the bottom line (row or col depending on oritentation) 
        #       of the adjacient side (alligned)
        #
        #  After one piece has been moved to its correct target place, 
        #  skip the other and re-evaluate how many misplaced pieces are still there.  

        # process until no more misplaced pieces are found
        misplaced_piece_travels = fill_piece_travels(first_color, cube_borders, first_side)
        while len(misplaced_piece_travels) > 0 :
            for travel in misplaced_piece_travels :
                piece     = travel[0]
                from_pos  = travel[1]
                from_side = from_pos[0]
                from_col  = from_pos[1]
                from_row  = from_pos[2]
                to_pos    = travel[2]
                to_side   = to_pos[0]
                to_col    = to_pos[1]
                to_row    = to_pos[2] 

                # case 1 : check if target side has to be rotated to place the corner
                #          only when all corners are misplaced
                if from_side == to_side and len(misplaced_piece_travels) == 12 :
                    if from_col != to_col and from_row != to_row :
                        turn(from_pos, 180)
                    elif from_col == to_col == 4 :
                        turn(from_pos, 270)
                    else :
                        turn(from_pos, 90)
                    display_unfolded_cube("cube")
                    break   # skip and re-evaluate remaining misplaced pieace
                
                # case 2 : check if border piece is on the target side but reversed and move it  
                #          down to the bottom row. Use same move as for alligned borders, just take 
                #          the piece aligned on the bottom row 
                if is_piece_reversed(piece, to_side, first_color) :
                    if term_out :
                        print("    border", piece, "is reversed. Has to be moved down")
                    direction = relative_direction(from_side, to_side)
                    if direction  == "Up" :
                        from_row = 4
                    elif direction == "Down" :
                        from_row = 0
                    elif direction == "Left" :
                        from_col = 4
                    else :
                        from_col = 0
                    translated_col_row = translate_col_row(from_side, to_side, from_col, from_row)
                    from_aligned_pos = [from_side, from_col, from_row]
                    to_aligned_pos   = [to_side, translated_col_row[0], translated_col_row[1]]
                    move_aligned_border(from_aligned_pos, to_aligned_pos)
                    break   # skip and re-evaluate remaining misplaced pieace

                if not is_border_on_bottom_row(piece, from_pos, to_side, first_color) and \
                    not from_side == opposite_side[to_side] :
                    if term_out :
                        print("   border", piece, "is on the lateral column. Has to rotate until aligned.")
                    if not is_piece_aligned(from_pos, to_pos) : 
                        move_direction = "Left"
                        direction = relative_direction(from_side, to_side)
                        rotated_270_direction = { "Right": "Up", "Down": "Right", "Left": "Down"}
                        if direction in rotated_270_direction.keys() :
                            move_direction = rotated_270_direction[direction]
                        move(from_pos, move_direction)
                        display_unfolded_cube("cube")
                        break   # skip and re-evaluate remaining misplaced pieace
                    if term_out :
                        print("    border", piece, "is aligned on the lateral column")
                    move_lateral_aligned_border(from_pos, to_pos)

                # case 4 : check if corner is on the opposite side move it up to the bottom row
                if from_side == opposite_side[to_side] :
                    if term_out :
                        print("    border", piece, "is on the opposite side. Has to be moved to the botton row")

                    move_oppositie_corner_to_bottom_row(piece, from_pos, to_side)
                    break   # skip and re-evaluate remaining misplaced pieace
                    
                # case 5 : if corner on adjacient side but not reversed then 
                #          align it first than place it.
                if is_side_adjacient(from_side, to_side) :
                    if not is_piece_aligned(from_pos, to_pos) :
                        opposite_side_pos = [opposite_side[to_side], 2, 2]
                        turn(opposite_side_pos, 270)         # TODO : avoid blind turning
                        display_unfolded_cube("cube")
                        break # skip and re-evaluate remaining misplaced pieace
                    if term_out : 
                        print("    border", piece, "is aligned")
                    move_aligned_border(from_pos, to_pos)
                    break   # skip and re-evaluate remaining misplaced pieace

            # process until no more misplaced pieces are found
            misplaced_piece_travels = fill_piece_travels(first_color, cube_borders, first_side)

    def solve_middles(first_side):
        pass

    def solve_row_1_borders(first_side):
        pass

    def solve_row_2_borders(first_side):
        pass

    def place_last_middle_borders(first_side):
        pass

    def solve_last_corners(fist_side):
        pass

    def solve_last_lateral_borders(first_side):
        pass

    def solve_last_middle_borders(fisrt_side):
        pass

    def solve_row_3_borders(first_side):
        pass

    def solve_rest_middles(first_side):
        pass

    global cube
    
    first_side = cursor_pos[0]

    solve_first_center(first_side, first_color)
    #win.getKey()

    solve_first_corners(first_side, first_color)
    #win.getKey()

    #sovle_first_borders(first_side, first_color)
    #win.getKey()

    solve_middles(first_side)
    #win.getKey()

    solve_row_1_borders(first_side)
    #win.getKey()

    solve_row_2_borders(first_side)
    #win.getKey()

    place_last_middle_borders(first_side)
    #win.getKey()

    solve_last_corners(first_side)
    #win.getKey()

    solve_last_lateral_borders(first_side)
    #win.getKey()

    solve_last_middle_borders(first_side)
    #win.getKey()

    solve_row_3_borders(first_side)
    #win.getKey()

    solve_rest_middles(first_side)
    #win.getKey()

# ------------------------------------------------
# M A I N L I N E
# ------------------------------------------------

# set cursor on the home postion
cursor_pos = [0, 2, 2]

# init cube with default position
init_cube()

# display cube the key used for the game
interval_sec = 0
display_unfolded_cube("all", cursor_pos)
display_keys_usage()
interval_sec = 1

navigate_keys = ("Up", "Down", "Left", "Right")
move_keys = ("w", "a", "s", "d")
turn_keys = ("Shift_L", "Shift_R")
shuffle_key = "space"
new_key = "n"
reverse_key = "r"
solve_key = "Return"
side_selection_keys = ("Control_L", "Control_R")
key_to_direction = {"w": "Up", "a": "Left", "s": "Down",
                    "d": "Right", "Shift_L": 270, "Shift_R": 90}
key = "unknown"
side_selected = False

# main game loop
while key != "Escape":

    # do something only if a relevant key has been pressed
    if key in navigate_keys + move_keys + turn_keys + side_selection_keys \
            or key in (shuffle_key, reverse_key, new_key, solve_key):
        
        if key in navigate_keys:
            cursor_pos = navigate_unfolded(cursor_pos, key, side_selected)
            display_unfolded_cube("cursor", cursor_pos, side_selected)

        elif key in move_keys:
            cursor_pos = move_from_cursor(cursor_pos, key_to_direction[key], side_selected)
            side_selected = False
            display_unfolded_cube("all", cursor_pos)

        elif key == shuffle_key:
            shuffle_cube()
            display_unfolded_cube("cursor", cursor_pos)

        elif key == new_key:
            new_cube()

        elif key == reverse_key:
            reverse_moves()

        elif key in turn_keys:
            turn(cursor_pos, key_to_direction[key])
            display_unfolded_cube("all", cursor_pos)

        elif key == solve_key:
            solve_cube(cursor_pos)
            display_unfolded_cube("cursor", cursor_pos)

        elif key in side_selection_keys:
            if not side_selected:
                side_selected = True
            else: 
                side_selected = False
            display_unfolded_cube("cursor", cursor_pos, side_selected)

    # wait for next key-press
    key = win.getKey()

win.close()