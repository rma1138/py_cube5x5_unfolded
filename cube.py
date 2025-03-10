from graphics import GraphWin, color_rgb, Rectangle, Point, Text
from random import randint
import time

# Custom types used for type hints (static type checking)
# -------------------------------------------------------
type ColRow = tuple[int, int]
type Position = tuple[int, int, int]
type Travel = tuple[str, Position, Position]

# Helper class for cube constants and class functions
# ---------------------------------------------------
class CubeHelper:
    # cube colors
    #   c : cyan
    #   g : green
    #   r : read
    #   o : orange
    #   b : black
    #   y : yellow
    cube_colors = ["c", "g", "o", "r", "b", "y"]

    # Default color to name dict
    # (black is on the up side, red is on the front side)
    default_side_names = {
        "b": "Up",
        "y": "Down",
        "r": "Front",
        "o": "Back",
        "g": "Left",
        "c": "Right",
    }

    # Side name to side index dict
    cube_sides = {"Up": 0, "Down": 1, "Front": 4, "Back": 5, "Left": 2, "Right": 3}

    # side index to rotation dict, relative to side 0 Up
    side_rotation = {0: 0, 1: 0, 2: 90, 3: 270, 4: 0, 5: 180}

    # side index to opposite side dict
    # (the 2nd side in any move cycle is allways the opposite side, direction does not matter)
    opposite_side = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4}

    # side color to opposite side dict
    # (the 2nd side in any move cycle is allways the opposite side, direction does not matter)
    opposite_color = {"b": "y", "r": "o", "g": "c", "y": "b", "o": "r", "c": "g"}

    # opposite directions
    opposite_direction = {"Up": "Down", "Right": "Left", "Down": "Up", "Left": "Right"}

    # rotated directions
    rotated_90_direction = {
        "Up": "Right",
        "Right": "Down",
        "Down": "Left",
        "Left": "Up",
    }
    rotated_270_direction = {
        "Up": "Left",
        "Right": "Up",
        "Down": "Right",
        "Left": "Down",
    }
    middle_edge_col_row = ((1, 1), (3, 1), (3, 3), (1, 3))

    # cursor, rectangle and text object references (from graphics)
    cursor_obj = [any, None, None]
    cursor_pos_obj = None
    last_move_obj = None
    cursor_pos_piece_obj = None

    def is_color_adjacient(
        self, first_color: str, second_color: str, third_color: None | str = None
    ) -> bool:
        """Check if first side color is adjacient to second and, if provided, to third side color

        Args:
            first_color (str): color first side
            second_color (str): color second side
            third_color (None | str, optional): color third side. Defaults to None.

        Returns:
            bool: are first and second and, if provided, third sides adjacient ?
        """

        def is_color_adjacient_2(first_color: str, second_color: str) -> bool:
            """Check if first side is adjacient to second side.

            Args:
                first_color (str): color first side
                second_color (str): color second side

            Returns:
                bool: are first and second sides adjacient ?
            """
            cube_colors_sequences = [
                ["c", "o", "g", "r"],
                ["c", "b", "g", "y"],
                ["b", "r", "y", "o"],
            ]
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

                if index_1 is not None and index_2 is not None:
                    if abs(index_1 - index_2) == 1 or abs(index_1 - index_2) == 3:
                        return True

            return False

        if third_color is None:
            return is_color_adjacient_2(first_color, second_color)

        if first_color != second_color != third_color:
            if (
                self.is_color_adjacient(first_color, second_color)
                and self.is_color_adjacient(second_color, third_color)
                and self.is_color_adjacient(first_color, third_color)
            ):
                return True

        return False

    def is_side_adjacient(
        self, first_side: int, second_side: int, third_side: None | int = None
    ) -> bool:
        """Check if first side is adjacient to second and, if provided, to third side

        Args:
            first_side (int): index first side
            second_side (int): index secound side
            third_side (None | int, optional): index third side. Defaults to None.

        Returns:
            bool: are first and second and, if provided, third sides adjacient ?
        """
        first_color = self.default_color(first_side)
        second_color = self.default_color(second_side)
        if third_side is None:
            return self.is_color_adjacient(first_color, second_color)
        else:
            third_color = self.default_color(third_side)
            return self.is_color_adjacient(first_color, second_color, third_color)

    def reorder(self, word: str) -> str:
        """Return sorted character string

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

        return new_word

    def border_orientation(
        self, first_side: int, second_side: int, default_color_side: int = 0
    ) -> str:
        """Returns orientation name for border piece based on the first and second side of the piece
            first_side, second_side :
                0 U : up    side
                1 D : down  side
                2 L : left  side
                3 R : right side
                4 F : front side
                5 B : back  side
            orientation names ("N", "S", "W", "E") based on the first and second side index (as concatened str)

        Args:
            first_side (int): index first side
            second_side (int): index second side

        Returns:
            orientation (str): N, S, W, E (North, South, West, East)
        """
        first_second = str(first_side) + str(second_side)
        orientation = ""
        orientation_names = {
            "05": "N",
            "04": "S",
            "03": "E",
            "02": "W",
            "14": "N",
            "15": "S",
            "13": "E",
            "12": "W",
            "20": "N",
            "21": "S",
            "24": "E",
            "25": "W",
            "30": "N",
            "31": "S",
            "35": "E",
            "34": "W",
            "40": "N",
            "41": "S",
            "43": "E",
            "42": "W",
            "50": "N",
            "51": "S",
            "52": "E",
            "53": "W",
        }
        if first_second in orientation_names.keys():
            orientation = orientation_names[first_second]
            if default_color_side != 0:
                rotation = self.side_rotation[default_color_side]
                if rotation != 0:
                    rotation = 360 - rotation
                    rotated_orientation = {
                        90: {"N": "E", "E": "S", "S": "W", "W": "N"},
                        270: {"N": "W", "W": "S", "S": "E", "E": "N"},
                        180: {"N": "S", "E": "W", "S": "N", "W": "E"},
                    }
                    orientation = rotated_orientation[rotation][orientation]

        return orientation

    def corner_orientation(
        self, first: int, second: int, third: int, default_color_side: int = 0
    ) -> str:
        """Returns orientation name for corner piece based on first, second and third side of the piece

        Args:
            first (int)             : index first side
            second (int)            : index second side
            third (int)             : index third side
            default_color_side (int): default color side. Default 0

        Returns:
            orientation (str): NW, SW, EN, ES (North West, South West, North East, South Est)
            if side is specified, the relative side roation is considered (in border_orientation)
        """
        orientation = self.border_orientation(first, second, default_color_side)
        orientation = orientation + self.border_orientation(
            first, third, default_color_side
        )
        return self.reorder(orientation)

    def default_side(self, color: str) -> int:
        """Returns default side based on the color

        Args:
            color (str): color name (b, c, r, g, y, o)

        Returns:
            side index (int): index default side
        """
        default_side_name = self.default_side_names[color]
        side = self.cube_sides[default_side_name]
        return side

    def default_color(self, side: int) -> str:
        """Returns default side color based on the side index

        Args:
            side (int): side index (0, 1, 2, 3, 4, 5)

        Returns:
            side color (str): color default side
        """
        for color in self.cube_colors:
            if self.default_side(color) == side:
                return color

        raise Exception(f"default_color(side={side}): case not handled!. Check and fix")

    def rotate_side(self, col_row: ColRow, rotation: int = 0) -> ColRow:
        """Returns rotated col and row index side coordinate in respect to the given side rotation.
            If no rotation spefice col and row index remain unchanged.

        Args:
            col_row (Position) : list (2) of col and row index
            rotation (int): relative rotation to side 0 in degree
        Returns:
            new_col_row (Position) : list (2) of rotated col and row index
        """
        if rotation == 0 or abs(rotation) % 360 == 0:  # no rotation
            return (col_row[0], col_row[1])
        elif abs(rotation) == 180:  # 180 rotation
            return (4 - col_row[0], 4 - col_row[1])
        elif rotation in (90, -270):  # 90 clockwise
            return (4 - col_row[1], col_row[0])
        elif rotation in (-90, 270):  # 90 anti-clockwise or 270 clocwie
            return (col_row[1], 4 - col_row[0])

        raise Exception(
            f"rotate_side({col_row}, {rotation}): case not handled! Check and fix."
        )

    def flip_side(self, col_row: ColRow, direction: str, to_side: int) -> ColRow:
        """Returns flipped col and row side coordinate
            in respect to the direction (which defines the flip axis)

        Args:
            col_row (Position) : list (2) of col and row index
            direction (str): move direciton (90° flip axis)
        Returns:
            new_col_row (Position) : list (2) of flipped col and row index
        """
        col, row = col_row

        if to_side in (0, 1):
            return (col, row)

        if direction in ("Up", "Down"):
            if to_side in (2, 3, 4, 5):
                return (4 - col, 4 - row)

            return (col, 4 - row)

        return (4 - col, row)

    def relative_rotation(self, from_side: int, to_side: int) -> int:
        """Returns the relative rotation (360 degrees base) between to_side and from side.

        Args:
            from_side (int): from side index
            to_side (int): to side index

        Returns:
            int: rotation in degree (0, 90, 180, 270)
        """
        rotation = self.side_rotation[from_side] - self.side_rotation[to_side]
        if rotation < 0:
            rotation = 360 + rotation

        return rotation

    def translate_col_row(
        self, from_side: int, to_side: int, from_col: int, from_row: int
    ) -> ColRow:
        """translate col row coordinates from one side to another
        keeping piece positions aligned

        Args:
            from_side (int): source side index
            to_side (int): target side index
            from_col (int): source col index
            from_row (int): source row index

        Returns:
            col_row (ColRow): translated col and row index tuple
        """
        rotation = self.relative_rotation(to_side, from_side)
        if rotation not in (90, 270):  # or this_side in (0, 1) or prev_side in (0, 1)
            return self.rotate_side((from_col, from_row), rotation)

        elif from_side == 0 or to_side == 0:
            rotation = rotation - 180
            if rotation < 0:
                rotation = 360 + rotation

            return self.rotate_side((from_col, from_row), rotation)

        elif from_side == 1 or to_side == 1:
            return self.rotate_side((from_col, from_row), rotation)

        else:
            return (from_col, from_row)

    def navigate_pos(
        self, position: Position, direction: str, side_selected: bool = False
    ) -> list[int]:
        """Navigate from current position to the given direction

        Args:
            position (Position): [side, row, col]
            direction (str): "Up", "Down", "Left", "Right"
            side_selected (bool, optional): is side selected. Defaults to False.

        Returns:
            Position: new position as side, col and row indexes
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

        # find out col and row chagnes based on the direation
        direction_to_col_row_change = {
            "Up": [0, -1],
            "Down": [0, +1],
            "Right": [+1, 0],
            "Left": [-1, 0],
        }
        col_row_change = direction_to_col_row_change[direction]
        col_change, row_change = col_row_change[0], col_row_change[1]
        next_side = position[0]

        if (
            current_col + col_change >= 0
            and current_col + col_change <= 4
            and current_row + row_change >= 0
            and current_row + row_change <= 4
            and not side_selected
        ):
            # same side but differen position
            return [current_side, current_col + col_change, current_row + row_change]

        else:
            # find out next side based on the global next_side_* dictionaries
            next_side_dict_dict = {
                "Up": next_side_up_rotation,
                "Down": next_side_down_rotation,
                "Left": next_side_left_rotation,
                "Right": next_side_right_rotation,
            }
            next_side_dict = next_side_dict_dict[direction]
            next_side = next_side_dict[current_side]
            # finally set next position (rotate position if necessary based on the relative rotation)
            next_side_col, next_side_row = self.translate_col_row(
                current_side, next_side, current_col, current_row
            )
            rotation = self.relative_rotation(current_side, next_side)
            if rotation in (0, 180):
                if col_change == 0:
                    next_side_row = 4 - next_side_row

                else:
                    next_side_col = 4 - next_side_col

            elif current_side in (0, 1):
                next_side_row = 4 - next_side_row

            else:
                next_side_col = 4 - next_side_col

            return [next_side, next_side_col, next_side_row]

    def rotate_direction(self, side: int, direction: str) -> str:
        """Return the relative direction in respect to the default side rotation

        Args:
            side (int): side index
            direction (str): Up, Down, Left, Right

        Returns:
            str: Up, Down, Left, Right
        """
        direction_to_rotation = {"Up": 0, "Right": 90, "Down": 180, "Left": 270}
        rotation_to_direction = {0: "Up", 90: "Right", 180: "Down", 270: "Left"}
        rotation = direction_to_rotation[direction]
        rotation = rotation - self.side_rotation[side]
        if rotation < 0:
            rotation = 360 + rotation

        return rotation_to_direction[rotation]

    def navigate_unfolded(
        self, position: Position, direction: str, side_selected: bool
    ) -> list[int]:
        """Return new cursor position translated from the unfolded cube direction

        Args:
            position (Position): source cursor position as side, col and row index
            direction (str): Up, Down, Left, Right
            side_selected (bool): is the whole side select (contol key)

        Returns:
            Position: new position
        """
        rotated_direction = self.rotate_direction(position[0], direction)
        return self.navigate_pos(position, rotated_direction, side_selected)

    def relative_direction(self, from_side: int, to_side: int) -> str:
        """Return the relative direction form one to another side

        Args:
            from_side (int): source side index
            to_side (int): target side index

        Returns:
            str: Up, Down, Left, Right
        """
        if to_side == 0:
            if debug or False:
                print("    from side", from_side, "to side", to_side, "direction Up")
            return "Up"
        elif to_side == 1:
            if debug or False:
                print("    from side", from_side, "to side", to_side, "direction Down")
            return "Down"
        else:
            to_from_side_dict = {
                2: {0: "Left", 1: "Left", 5: "Right", 4: "Left", 3: "Down"},
                3: {0: "Right", 1: "Right", 5: "Left", 4: "Right", 2: "Up"},
                4: {0: "Down", 1: "Up", 3: "Left", 2: "Right", 5: "Right"},
                5: {0: "Up", 1: "Down", 3: "Right", 2: "Left", 4: "Left"},
            }
            if debug or False:
                print(
                    "    from side",
                    from_side,
                    "to side",
                    to_side,
                    "direction",
                    to_from_side_dict[to_side][from_side],
                )
            return to_from_side_dict[to_side][from_side]

#
# Cube class
# ----------
class Cube(CubeHelper):

    def __init__(self, cursor_pos: Position = (0, 2, 2)):
        """Initialie cube with the default (solved) pieces

        Returns:
            None
        """

        #  the main list modelling the 5 x 5 x 5 cube elements and their positions within the cube
        #
        #   1. dimension :  (0-5) side
        #                           0 up
        #                           1 down
        #                           2 left
        #                           3 right
        #                           4 front
        #                           5 back
        #   2. dimension :  (0-4) side column
        #                           numbered from left to right
        #   3. dimension :  (0-4) side row
        #                           numbered from left to right
        #   4. dimension :  (0-5) cube element
        #                           0 face color
        #                           1 piece
        #                           2 postition changed flag (0: unchanged, 1: changed)
        #                           3 graphic_object reference rectangle
        #                           4 graphic object reference text
        element_values = [" ", " ", 0, None, None]
        self.cube = [
            [[[e for e in element_values] for r in range(5)] for c in range(5)]
            for s in range(6)
        ]

        # unique cube piece indentifiers with color(s) and positions
        #   centers : color
        #   middles : color + col + row
        #               (sorted for unique id, regardless which direction the cube is searched)
        #   borders : color first + color second side
        #               (sorted for unique id, regardless which direction the cube is searched)
        #   corners : color first + color secound + color third side
        #               (sorted for unique id, regardless which direction the cube is searched)
        self.cube_centers = list(self.cube_colors)
        self.cube_centers = self.cube_colors.copy()
        self.cube_centers.sort()

        self.cube_middles = [
            color + str(col) + str(row)
            for color in self.cube_colors
            for col in [1, 2, 3]
            for row in [1, 2, 3]
            if not (col == 2 and row == 2)
        ]
        self.cube_middles.sort()

        borders = {
            self.reorder(color_1 + color_2) + str(n)
            for color_1 in self.cube_colors
            for color_2 in self.cube_colors
            for n in range(3)
            if self.is_color_adjacient(color_1, color_2)
        }
        self.cube_borders = list(borders)
        self.cube_borders.sort()

        corners = {
            self.reorder(color_1 + color_2 + color_3)
            for color_1 in self.cube_colors
            for color_2 in self.cube_colors
            for color_3 in self.cube_colors
            if self.is_color_adjacient(color_1, color_2, color_3)
        }
        self.cube_corners = list(corners)
        self.cube_corners.sort()

        if debug or False:
            print("Cube piece names:")
            i = 0
            for cube_pieces in [
                self.cube_centers,
                self.cube_middles,
                self.cube_borders,
                self.cube_corners,
            ]:
                type = ""
                if cube_pieces == self.cube_centers:
                    type = "centers"
                if cube_pieces == self.cube_middles:
                    type = "middles"
                if cube_pieces == self.cube_borders:
                    type = "borders"
                if cube_pieces == self.cube_corners:
                    type = "corners"
                for piece in cube_pieces:
                    print(str(i).rjust(2), type, piece)
                    i = i + 1

        # set default cube for centers ("b", "c", "g", "y", "o", "r" )
        for piece in self.cube_centers:
            side = self.default_side(piece)
            # for centers color = piece (eg: "b", "c", ...)
            self.cube[side][2][2] = [piece, piece, 1, None, None]

        # set default cube for middles (eg: "b11", "b12", "b13", "b21", "b23", "b31", "b32", "b33", ...)
        for piece in self.cube_middles:
            side = self.default_side(piece[0])
            col = int(piece[1])
            row = int(piece[2])
            # for middles color = first letter from piece name (eg: "b11")
            self.cube[side][col][row] = [piece[0], piece, 1, None, None]

        # set default cube for borders (eg: "bg0", "bg1", "bg2", "rg0", "rg1", ... )
        for piece in self.cube_borders:
            # border position offset on the col or the row axis
            offset = int(piece[2])
            side_1 = self.default_side(piece[0])  # color 1
            side_2 = self.default_side(piece[1])  # color 2

            # set default cube for border piece in its 2 color sides
            # the color is the first and second letter of the piece name
            # and is passed as 3rd element of each color_side sub list
            for color_side in [[side_1, side_2, piece[0]], [side_2, side_1, piece[1]]]:
                orientation = self.border_orientation(color_side[0], color_side[1])
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
                    if (
                        color_side[1] != 4
                        and color_side[1] != 2
                        or color_side[0] == 0
                        or color_side[0] == 4
                    ):
                        row = 1 + offset
                    else:
                        row = 3 - offset

                self.cube[color_side[0]][col][row] = [
                    color_side[2],
                    piece,
                    1,
                    None,
                    None,
                ]

        # set default cube for corners ("bco", "bgo", "bcr", "bgr", "coy", "cry", "goy", "gry")
        for piece in self.cube_corners:
            side_1 = self.default_side(piece[0])
            side_2 = self.default_side(piece[1])
            side_3 = self.default_side(piece[2])

            # set default cube for corner piece in its 3 color sides
            # the color is the first, second and thirst letter of the piece name
            # and is passed as 4th element of each color_side sub list
            for color_side in [
                [side_1, side_2, side_3, piece[0]],
                [side_2, side_1, side_3, piece[1]],
                [side_3, side_2, side_1, piece[2]],
            ]:
                orientation = self.corner_orientation(
                    color_side[0], color_side[1], color_side[2]
                )
                if orientation == "NW":  # North West
                    col = 0
                    row = 0

                if orientation == "SW":  # South West
                    col = 0
                    row = 4

                if orientation == "EN":  # North East
                    col = 4
                    row = 0

                if orientation == "ES":  # South East
                    col = 4
                    row = 4

                self.cube[color_side[0]][col][row][0] = color_side[3]
                self.cube[color_side[0]][col][row][1] = piece
                self.cube[color_side[0]][col][row][2] = 1  # flagged as changed

        if debug or False:
            print("Cube piece cube positions (count, face, col, row, color, piece):")
            i = 0
            for face in self.cube:
                for col in face:
                    for color_piece in col:
                        type = ""
                        if color_piece[1] in self.cube_centers:
                            type = "centers"

                        if color_piece[1] in self.cube_middles:
                            type = "middles"

                        if color_piece[1] in self.cube_borders:
                            type = "borders"

                        if color_piece[1] in self.cube_corners:
                            type = "corners"

                        print(
                            str(i).rjust(3, " "),
                            self.cube.index(face),
                            face.index(col),
                            col.index(color_piece),
                            color_piece[0],
                            type,
                            color_piece[1],
                        )
                        i = i + 1

        # Initialize graphic window
        self.height = 1090
        self.width = 740
        self.win = GraphWin("Cube 5x5x5", self.width, self.height)
        self.win.setBackground(color_rgb(48, 48, 64))
        self.win_bottom_status_height = 80
        self.cursor_color_rgb = [255, 255, 255]

        # moves history
        self.moves = []

        # current cursor position 
        self.cursor_pos = [cursor_pos[0], cursor_pos[1], cursor_pos[2]]

    def __del__(self):
        self.win.close()

    def display_unfolded_cube(
        self,
        scope: str = "cube",
        side_selected: bool = False,
        side_sequence: list[int] = [0, 3, 4, 2, 5, 1],
    ):
        """Display cube unfolded 2D

        Args:
            scope (str, optional)           : Display cube only or cursor or all. Defaults to "cube".
            side_sequence (list, optional)  : list of sides to be display. Defaults to [0, 3, 4, 2, 5, 1].

        Returns:
            none

        """

        color_codes = {
            "c": color_rgb(0, 200, 255),
            "g": color_rgb(0, 200, 0),
            "o": color_rgb(255, 140, 0),
            "r": color_rgb(200, 0, 0),
            "b": color_rgb(0, 0, 0),
            "y": color_rgb(255, 255, 0),
        }
        background_color_codes = {
            "c": color_rgb(0, 0, 0),
            "g": color_rgb(0, 0, 0),
            "o": color_rgb(0, 0, 0),
            "r": color_rgb(155, 255, 255),
            "b": color_rgb(255, 255, 255),
            "y": color_rgb(0, 0, 255),
        }

        # Side indexes 0 Up, 1 Down, 2 Left, 3 Right, 4 Front, 5 Back
        side_grid_pos = [[1, 2], [1, 0], [0, 2], [2, 2], [1, 3], [1, 1]]
        piece_size = 45
        spacer = 2
        side_spacer = 8
        side_size = (piece_size + spacer) * 5 + side_spacer
        x_margin = (self.win.width  - 3 * side_size) // 2
        y_margin = (self.win.height - (self.win_bottom_status_height + 10) - 4 * side_size) // 2

        def get_x_y(side_index, col_index, row_index, consider_side_rotation=True):
            """Return x,y coordinates from sid, col, row and side rotation

            Args:
                side_index (int)    : 0-5 side index
                col_index (int)     : 0-4 column index
                row_index (int)     : o-4 row index
                consider_side_rotation (bool, optional): consider side rotation. Defaults to True.

            Returns:
                int, int : x, y coordinates
            """
            rotated_col_row = [col_index, row_index]
            if consider_side_rotation:
                rotation = self.side_rotation[side_index]
                rotated_col_row = self.rotate_side((col_index, row_index), rotation)

            x = (
                x_margin
                + side_grid_pos[side_index][0] * side_size
                + rotated_col_row[0] * (piece_size + spacer)
            )
            y = (
                y_margin
                + side_grid_pos[side_index][1] * side_size
                + rotated_col_row[1] * (piece_size + spacer)
            )

            return x, y

        def side_iter(side_sequence):
            """Iterate over specified cube side list

            Args:
                side_sequence (list): list of cube sides

            Yields:
                int: next side index
            """
            for index in side_sequence:
                yield self.cube[index]

        if scope == "cursor" and self.cursor_obj[0] is not None:
            self.cursor_obj[0].undraw()
            if self.cursor_obj[1] is not None:
                self.cursor_obj[1].undraw()

            if self.cursor_obj[2] is not None:
                self.cursor_obj[2].undraw()

        else:
            if scope in ("cube", "all"):
                for side in side_iter(side_sequence):
                    side_index = self.cube.index(side)
                    for col in side:
                        col_index = side.index(col)
                        for row in col:
                            row_index = col.index(row)
                            if row[2] == 1:  # piece has changed
                                # coordinate previous rectange (p1)
                                x0, y0 = 0, 0
                                x, y = get_x_y(side_index, col_index, row_index)
                                if row[3] is not None:
                                    x0, y0 = row[3].getP1().x, row[3].getP1().y
                                    row[3].move(x - x0, y - y0)

                                else:
                                    # row = [row[0], row[1], row[2], None, row[4] ]
                                    row[3] = Rectangle(  # type: ignore
                                        Point(x, y),  # type: ignore
                                        Point(x + piece_size, y + piece_size),
                                    )
                                    row[3].setFill(color_codes[str(row[0])])
                                    row[3].draw(self.win)

                                if row[4] is not None:
                                    row[4].move(x - x0, y - y0)

                                else:
                                    #                                pass
                                    if debug or False:
                                        # row = [ row[0], row[1], row[2], row[3], None ]
                                        center = row[3].getCenter()
                                        row[4] = Text(Point(center.x, center.y), row[1])  # type: ignore
                                        row[4].setTextColor(
                                            background_color_codes[str(row[0])]
                                        )
                                        row[4].draw(self.win)

                                row = [row[0], row[1], 0, row[3], row[4]]

        if scope in ("cursor", "all"):
            side_index = 0
            if self.cursor_pos is not None:
                side_index = self.cursor_pos[0]

            if side_selected:
                # if cursor_obj[0] is not None:
                self.cursor_obj[0].undraw()
                if self.cursor_obj[1] is not None:
                    self.cursor_obj[1].undraw()

                if self.cursor_obj[2] is not None:
                    self.cursor_obj[2].undraw()

                x, y = get_x_y(side_index, 0, 0, False)
                self.cursor_obj[0] = Rectangle(
                    Point(x, y),
                    Point(x + 5 * (piece_size + spacer), y + 5 * (piece_size + spacer)),
                )
                self.cursor_obj[0].setWidth(spacer * 3)
                self.cursor_obj[0].setOutline(
                    color_rgb(
                        self.cursor_color_rgb[0], self.cursor_color_rgb[1], self.cursor_color_rgb[2]
                    )
                )
                self.cursor_obj[0].draw(self.win)

            else:
                col_index, row_index = 2, 2
                if self.cursor_pos is not None:
                    col_index = self.cursor_pos[1]
                    row_index = self.cursor_pos[2]

                x, y = get_x_y(side_index, col_index, row_index)
                self.cursor_obj[0] = Rectangle(
                    Point(x, y), Point(x + piece_size, y + piece_size)
                )
                self.cursor_obj[0].setWidth(spacer * 3)
                self.cursor_obj[0].setOutline(
                    color_rgb(
                        self.cursor_color_rgb[0], self.cursor_color_rgb[1], self.cursor_color_rgb[2]
                    )
                )
                self.cursor_obj[0].draw(self.win)

                if col_index in (0, 4) or row_index in (0, 4):
                    cursor_obj_index = 0
                    for s in range(6):
                        if s != side_index:
                            for c in range(5):
                                for r in range(5):
                                    if (
                                        self.cube[side_index][col_index][row_index][1]
                                        == self.cube[s][c][r][1]
                                    ):
                                        cursor_obj_index = cursor_obj_index + 1
                                        x, y = get_x_y(s, c, r)
                                        self.cursor_obj[cursor_obj_index] = Rectangle(
                                            Point(x, y),
                                            Point(x + piece_size, y + piece_size),
                                        )
                                        self.cursor_obj[cursor_obj_index].setWidth(
                                            spacer
                                        )
                                        self.cursor_obj[cursor_obj_index].setOutline(
                                            color_rgb(
                                                self.cursor_color_rgb[0],
                                                self.cursor_color_rgb[1],
                                                self.cursor_color_rgb[2],
                                            )
                                        )
                                        self.cursor_obj[cursor_obj_index].draw(self.win)

                else:
                    self.cursor_obj[1], self.cursor_obj[2] = None, None

                if self.cursor_pos_obj is not None:
                    self.cursor_pos_obj.undraw()

                cursor_pos_obj = Text(
                    Point(self.win.width - 120, self.win.height - self.win_bottom_status_height),
                    "cursor : " + str(self.cursor_pos),
                )
                cursor_pos_obj.setTextColor(color_rgb(255, 255, 255))
                cursor_pos_obj.draw(self.win)

                if self.cursor_pos_piece_obj is not None:
                    self.cursor_pos_piece_obj.undraw()

                self.cursor_pos_piece_obj = None
                if self.cursor_pos is not None:
                    self.cursor_pos_piece_obj = Text(
                        Point(
                            self.win.width - 130, self.win.height - self.win_bottom_status_height + 20
                        ),
                        "piece : "
                        + str(
                            self.cube[self.cursor_pos[0]][self.cursor_pos[1]][self.cursor_pos[2]][1]
                        ).ljust(5, " "),
                    )
                    self.cursor_pos_piece_obj.setTextColor(color_rgb(255, 255, 255))
                    self.cursor_pos_piece_obj.draw(self.win)

                if self.last_move_obj is not None:
                    self.last_move_obj.undraw()

                if len(self.moves) > 0:
                    self.last_move_obj = Text(
                        Point(
                            self.win.width - 100, self.win.height - self.win_bottom_status_height + 40
                        ),
                        "last : " + str(self.moves[len(self.moves) - 1]),
                    )
                    self.last_move_obj.setTextColor(color_rgb(255, 255, 255))
                    self.last_move_obj.draw(self.win)

    def display_keys_usage(self):
        """Display key usage legend

        Args:
            none
        Returns:
            none
        """
        line = (
            "<n> : new cube                       <r> : revese all moves",
            "<arrow-keys> : select             <escape> : end",
            "<w, a, s, d> : rotate                 <space> : shuffle",
            "<shift> : turn left/right              <ctrl> : side selection",
        )
        t = Rectangle(
            Point(0, self.win.height - self.win_bottom_status_height - 15),
            Point(self.win.width, self.win.height),
        )
        t.setFill(color_rgb(0, 0, 0))
        t.draw(self.win)
        x = (182, 160, 165, 180)
        o = (0, 20, 40, 60)
        for i in range(4):
            y = self.win.height - self.win_bottom_status_height + o[i]
            t = Text(Point(x[i], y), line[i])
            t.setFace("helvetica")
            t.setTextColor(color_rgb(255, 255, 255))
            t.draw(self.win)

    def rotate(self, side: int, rotation: int):
        saved_side = [
            [self.cube[side][col][row].copy() for row in range(5)] for col in range(5)
        ]
        for col in range(5):
            for row in range(5):
                rotated_col_row = self.rotate_side((col, row), rotation)
                self.cube[side][rotated_col_row[0]][rotated_col_row[1]] = saved_side[
                    col
                ][row].copy()
                r = self.cube[side][rotated_col_row[0]][rotated_col_row[1]]
                self.cube[side][rotated_col_row[0]][rotated_col_row[1]] = [
                    r[0],
                    r[1],
                    1,
                    r[3],
                    r[4],
                ]

    def move(self, position: Position, direction: str):
        """move from one position, identified by side, col and row index towards direction

        Args:
            position (Position): side, col, pos indexes
            direction (str): direction. "Up", "Down", "Left", "Richt
        """

        # side move direction sequences (adjusted for relative side orientation)
        side_up_move_cycle = {
            0: [5, 1, 4, 0],
            1: [4, 0, 5, 1],
            2: [0, 3, 1, 2],
            3: [0, 2, 1, 3],
            4: [0, 5, 1, 4],
            5: [0, 4, 1, 5],
        }
        side_down_move_cycle = {
            0: [4, 1, 5, 0],
            1: [5, 0, 4, 1],
            2: [1, 3, 0, 2],
            3: [1, 2, 0, 3],
            4: [1, 5, 0, 4],
            5: [1, 4, 0, 5],
        }
        side_left_move_cycle = {
            0: [2, 1, 3, 0],
            1: [2, 0, 3, 1],
            2: [5, 3, 4, 2],
            3: [4, 2, 5, 3],
            4: [2, 5, 3, 4],
            5: [3, 4, 2, 5],
        }
        side_right_move_cycle = {
            0: [3, 1, 2, 0],
            1: [3, 0, 2, 1],
            2: [4, 3, 5, 2],
            3: [5, 2, 4, 3],
            4: [3, 5, 2, 4],
            5: [2, 4, 3, 5],
        }

        # adjacient sides (depending on the move direction, based on the above move cycle dictionaries)
        adjacient_left_side_up_down = {
            side: side_left_move_cycle[side][0] for side in range(6)
        }
        adjacient_right_side_up_down = {
            side: side_right_move_cycle[side][0] for side in range(6)
        }
        adjacient_up_side_left_right = {
            side: side_up_move_cycle[side][0] for side in range(6)
        }
        adjacient_down_side_left_right = {
            side: side_down_move_cycle[side][0] for side in range(6)
        }

        side_move_cycle = {
            "Up": side_up_move_cycle,
            "Down": side_down_move_cycle,
            "Right": side_right_move_cycle,
            "Left": side_left_move_cycle,
        }
        move_cycle = side_move_cycle[self.opposite_direction[direction]]

        this_side = position[0]
        this_col = position[1]
        this_row = position[2]
        prev_sides = move_cycle[this_side]

        this_cols = []
        this_rows = []
        for i in range(5):
            if direction in ("Up", "Down"):
                this_cols.append(this_col)
                this_rows.append(i)

            else:
                this_cols.append(i)
                this_rows.append(this_row)

        adjacient_left_direction = {
            "Up": adjacient_left_side_up_down,
            "Down": adjacient_left_side_up_down,
        }
        adjacient_right_direction = {
            "Up": adjacient_right_side_up_down,
            "Down": adjacient_right_side_up_down,
        }
        adjacient_up_direction = {
            "Left": adjacient_up_side_left_right,
            "Right": adjacient_up_side_left_right,
        }
        adjacient_down_direction = {
            "Left": adjacient_down_side_left_right,
            "Right": adjacient_down_side_left_right,
        }

        adjacient_left = {}
        adjacient_right = {}
        adjacient_up = {}
        adjacient_down = {}
        if direction in ("Up", "Down"):
            adjacient_left = adjacient_left_direction[direction]
            adjacient_right = adjacient_right_direction[direction]

        elif direction in ("Left", "Right"):
            adjacient_up = adjacient_up_direction[direction]
            adjacient_down = adjacient_down_direction[direction]

        saved_side = [
            [self.cube[this_side][col][row].copy() for row in range(5)] for col in range(5)
        ]
        self.cursor_obj[0].undraw()
        if self.cursor_obj[1] is not None:
            self.cursor_obj[1].undraw()

        if self.cursor_obj[2] is not None:
            self.cursor_obj[2].undraw()

        for side_index in range(4):
            prev_side = prev_sides[side_index]
            prev_cols = [-1 for col in range(5)]
            prev_rows = [-1 for row in range(5)]
            if side_index < 3:
                # first 3 sides
                for col_row_index in range(5):
                    this_c = this_cols[col_row_index]
                    this_r = this_rows[col_row_index]
                    prev_col, prev_row = self.translate_col_row(
                        this_side, prev_side, this_c, this_r
                    )
                    self.cube[this_side][this_c][this_r] = self.cube[prev_side][
                        prev_col
                    ][prev_row]
                    r = self.cube[this_side][this_c][this_r]
                    self.cube[this_side][this_c][this_r] = [r[0], r[1], 1, r[3], r[4]]
                    prev_cols[col_row_index] = prev_col
                    prev_rows[col_row_index] = prev_row

            else:
                # last side
                for col_row_index in range(5):
                    this_c = this_cols[col_row_index]
                    this_r = this_rows[col_row_index]
                    prev_col, prev_row = self.translate_col_row(
                        this_side, prev_side, this_c, this_r
                    )
                    self.cube[this_side][this_c][this_r] = saved_side[prev_col][
                        prev_row
                    ]
                    r = self.cube[this_side][this_c][this_r]
                    self.cube[this_side][this_c][this_r] = [r[0], r[1], 1, r[3], r[4]]
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
                    self.rotate(adjacient_left[position[0]], 270)

                else:
                    self.rotate(adjacient_right[position[0]], 90)

            elif direction == "Down":
                if position[1] == 0:
                    self.rotate(adjacient_left[position[0]], 90)

                else:
                    self.rotate(adjacient_right[position[0]], 270)

        elif position[2] in (0, 4) and direction in ("Left", "Right"):
            # rotating from position row is on the edge to another side (which has to be rotated)
            # up or down side has to be rotated
            if direction == "Left":
                if position[2] == 0:
                    self.rotate(adjacient_up[position[0]], 90)

                else:
                    self.rotate(adjacient_down[position[0]], 270)

            elif direction == "Right":
                if position[2] == 0:
                    self.rotate(adjacient_up[position[0]], 270)

                else:
                    self.rotate(adjacient_down[position[0]], 90)

        self.moves.append([position, direction])
        if debug or False:
            print("        move:", len(self.moves) - 1, self.moves[len(self.moves) - 1])

    def move_from_cursor(
        self, position: Position, direction: str, side_selected: bool = False
    ) -> list[int]:
        side = position[0]
        col = position[1]
        row = position[2]
        piece = self.cube[side][col][row][1]
        color = self.cube[side][col][row][0]
        rotated_direction = self.rotate_direction(side, direction)
        if not side_selected:
            self.move(position, rotated_direction)

        else:
            rotated_direction = self.rotate_direction(side, direction)
            for i in range(5):
                if rotated_direction in ("Up", "Down"):
                    self.move((side, i, row), rotated_direction)

                else:
                    self.move((side, col, i), rotated_direction)

        for i in range(6):
            for j in range(5):
                for k in range(5):
                    if (
                        self.cube[i][j][k][1] == piece
                        and self.cube[i][j][k][0] == color
                    ):
                        return [i, j, k]
        else:
            return list(position)

    def turn(self, position, rotation):
        rotate_from_pos_90_dict = {
            0: [[5, 0, 0], "Left"],
            5: [[0, 0, 0], "Left"],
            4: [[0, 4, 4], "Right"],
            1: [[5, 4, 4], "Right"],
            2: [[0, 0, 0], "Down"],
            3: [[0, 4, 0], "Up"],
        }
        rotate_from_pos_270_dict = {
            0: [[5, 0, 0], "Right"],
            5: [[0, 0, 0], "Right"],
            4: [[0, 4, 4], "Left"],
            1: [[5, 4, 4], "Left"],
            2: [[0, 0, 0], "Up"],
            3: [[0, 4, 0], "Down"],
        }
        rotate_from_pos_dict = {
            90: rotate_from_pos_90_dict,
            270: rotate_from_pos_270_dict,
        }
        this_side = position[0]
        if debug or False:
            print("    turn: this side", this_side, "rotation", rotation)

        if rotation == 180:
            rotate_from_pos = rotate_from_pos_dict[90]
            from_pos: Position = rotate_from_pos[this_side][0]
            direction = rotate_from_pos[this_side][1]
            for i in range(2):
                self.move(from_pos, direction)

        else:
            rotate_from_pos = rotate_from_pos_dict[rotation]
            from_pos: Position = rotate_from_pos[this_side][0]
            direction = rotate_from_pos[this_side][1]
            self.move(from_pos, direction)

    def shuffle_cube(self):
        direction = ["Up", "Down", "Left", "Right"]
        for i in range(randint(1, 32)):
            side = randint(0, 5)
            col = randint(0, 4)
            row = randint(0, 4)
            dir = direction[randint(0, 3)]
            # if dir == "Right" and col == 0 and side in (0, 4) :
            self.move((side, col, row), dir)
            self.display_unfolded_cube("cube")

        self.display_unfolded_cube("cursor")

    def reverse_moves(self):
        self.move_history = [
            self.moves[i].copy() for i in range(len(self.moves) - 1, -1, -1)
        ]
        for m in self.move_history:
            direction = self.opposite_direction[m[1]]
            self.move(m[0], direction)
            self.display_unfolded_cube("cube")

        self.moves.clear()
        self.display_unfolded_cube("cursor")

class CubeSolver(CubeHelper):

    def __init__(self, cube):
        self.my_cube = cube

    def find_piece(self, piece: str, color: str | None = None) -> Position:
        """_summary_

        Args:
            piece (str): piece
            color (str | None, optional): color. Defaults to None.

        Returns:
            None | Position: side, col and row
        """
        for side_index in range(6):
            for col_index in range(5):
                for row_index in range(5):
                    if self.my_cube.cube[side_index][col_index][row_index][1] == piece:
                        if (
                            color is None
                            or color == self.my_cube.cube[side_index][col_index][row_index][0]
                        ):
                            return (side_index, col_index, row_index)

        raise Exception(
            f"find_piece({piece}, {color}): case not handled!. Check and fix"
        )

    def is_piece_reversed(self, piece: str, side: int, side_color: str) -> bool:
        """find if a piece is reversed in respect to a side and color

        Args:
            piece (str): piece identifier
            side (int): side index
            side_color (str): side color

        Returns:
            bool: is piece reversed?
        """
        if piece in (self.my_cube.cube_borders + self.my_cube.cube_corners):
            # one part of the piece is on the specified side but
            # with the wrong color
            for col in self.my_cube.cube[side]:
                for row in col:
                    if row[1] == piece and row[0] != side_color:
                        return True
        return False

    def is_piece_on_bottom_row(self, 
        piece: str, from_pos: Position, to_side: int, side_color: str
    ) -> bool:
        """find if a piece is on the bottom row in respect to the target side and color
            Applies to corner or border pieces

        Args:
            piece (str): piece identifier
            from_pos (list): starting position as side, col and row index
            to_side (int): target side
            side_color (str): target side color

        Returns:
            bool: is piece on the bottom row?
        """
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        if not self.is_piece_reversed(piece, to_side, side_color):
            if self.is_side_adjacient(from_side, to_side):
                if self.relative_direction(from_side, to_side) in ("Up", "Down"):
                    if piece in self.my_cube.cube_corners + self.my_cube.cube_borders:
                        if from_row in (0, 4):
                            return True
                else:
                    if piece in self.my_cube.cube_corners + self.my_cube.cube_borders:
                        if from_col in (0, 4):
                            return True
        return False

    def is_piece_adjacient_aligned(self, 
        piece: str, from_pos: Position, to_pos: Position
    ) -> bool:
        """find if a piece is aligned below its target position on the relative bottom row.

        Args:
            from_pos (list): source position as side, col and row index
            to_pos (list): target position as side, cold and row index

        Returns:
            bool: is piece aligned?
        """
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        to_side = to_pos[0]
        to_col = to_pos[1]
        to_row = to_pos[2]

        if (
            True  # self.my_cube.relative_direction(from_side, to_side) in ("Up", "Down")
            and piece in self.my_cube.cube_borders
        ):
            if from_side == self.border_adjacient_side(to_pos):
                return True
            else:
                return False
        else:
            col, row = self.translate_col_row(from_side, to_side, from_col, from_row)
            if col == to_col and row == to_row:
                return True
            else:
                return False

    def is_border_lateral_aligned(self, from_pos: Position, to_pos: Position) -> bool:
        """find if a border is aligned to be moved to the target position.

        Args:
            from_pos (list): source position as side, col and row index
            to_pos (list): target position as side, cold and row index

        Returns:
            bool: is border aligned?
        """
        to_adjacient_side = self.border_adjacient_side(to_pos)
        if from_pos[0] == self.opposite_side[to_adjacient_side]:
            return True
        else:
            return False

    def border_adjacient_side(self, border_pos: Position) -> int:
        """find the adjacient side of the target position.
            For border piece positions there is only 1 adjacient side

        Args:
            border_pos (Position): target position

        Returns:
            int: adjacient side index
        """
        border_side = border_pos[0]
        border_col = border_pos[1]
        border_row = border_pos[2]
        for s in range(6):
            if s != border_side:
                for c in range(5):
                    for r in range(5):
                        if (
                            self.my_cube.cube[border_side][border_col][border_row][1]
                            == self.my_cube.cube[s][c][r][1]
                        ):
                            return s

        raise Exception(
            f"border_adjacient_side(border_pos={border_pos}): case not handled!. Check and fix"
        )

    def corner_adjacient_sides(self, corner_pos: Position) -> list[int]:
        """find the adjacient side of the target position.
            For corner piece positions there there are 2 adjacient sides

        Args:
            corner_pos (Position): target position

        Returns:
            Position: adjacient side indexes
        """
        adjacient_sides = []
        corner_side = corner_pos[0]
        corner_col = corner_pos[1]
        corner_row = corner_pos[2]
        for s in range(6):
            if s != corner_side:
                for c in range(5):
                    for r in range(5):
                        if (
                            self.my_cube.cube[corner_side][corner_col][corner_row][1]
                            == self.my_cube.cube[s][c][r][1]
                        ):
                            adjacient_sides.append(s)
        return adjacient_sides

    def fill_piece_travels(self,
        color: str, pieces: list[str], side: int, cube_row: int | None = None
    ) -> list[Travel]:
        """find misplaced piece from / to positions an keep them in piece_travels list

        Args:
            color (str): color first side
            pieces (list[str]): list of pieces to be searched for
            side (int): index first side

        Returns:
            list[str Position]: piece travel (from_pos, to_pos) list
        """
        piece_travels = []
        #
        # Corner pieces
        # -------------
        if pieces[0] in self.my_cube.cube_corners:
            # cube_corners
            col_row_dict = {"NW": [0, 0], "EN": [4, 0], "SW": [0, 4], "ES": [4, 4]}
            for corner in pieces:
                if color in corner:
                    from_pos = self.find_piece(corner, color)
                    side_0 = self.default_side(corner[0])
                    side_1 = self.default_side(corner[1])
                    side_2 = self.default_side(corner[2])
                    orientation = self.corner_orientation(
                        side_0, side_1, side_2, side
                    )
                    col, row = col_row_dict[orientation]
                    to_pos = (side, col, row)
                    if from_pos != to_pos:
                        piece_travels.append((corner, from_pos, to_pos))
                        if debug or False:
                            print(f"travel corner {corner} from {from_pos} to {to_pos}")

        #
        # Border pieces first side
        # ------------------------
        if pieces[0] in self.my_cube.cube_borders and cube_row is None:
            # cube_borders
            col_row_dict = {"N": [1, 0], "E": [4, 3], "S": [3, 4], "W": [0, 1]}
            for border in pieces:
                if color in border:
                    from_pos = self.find_piece(border, color)
                    side_0 = self.default_side(border[0])
                    side_1 = self.default_side(border[1])
                    orientation = self.border_orientation(side_0, side_1, side)
                    col, row = col_row_dict[orientation]
                    cols = []
                    rows = []
                    positions = []
                    offsets = [int(border[2]), 2 - int(border[2])]
                    n = 1 if int(border[2]) == 1 else 2
                    for i in range(n):
                        cols.append(col)
                        rows.append(row)
                        if orientation == "N":
                            cols[i] += offsets[i]
                        elif orientation == "S":
                            cols[i] -= offsets[i]
                        elif orientation == "W":
                            rows[i] += offsets[i]
                        elif orientation == "E":
                            rows[i] -= offsets[i]
                        target_pos = (side, cols[i], rows[i])
                        target_border = self.my_cube.cube[target_pos[0]][target_pos[1]][
                            target_pos[2]
                        ][1]
                        target_color = self.my_cube.cube[target_pos[0]][target_pos[1]][
                            target_pos[2]
                        ][0]
                        if target_color != color:  # color does not match
                            positions.append(target_pos)
                        else:
                            if border[0:2] == target_border[0:2]:  # same border side
                                positions.append(target_pos)

                    if from_pos not in positions:
                        for pos in positions:
                            piece_travels.append((border, from_pos, pos))
                            if debug or False:
                                print(
                                    f"travel border {border} from {from_pos} to {pos}"
                                )
        #
        # Border pieces row 1 and 2
        # -------------------------
        if pieces[0] in self.my_cube.cube_borders and cube_row is not None and cube_row in (1, 2):
            # cube_borders
            for border in pieces:
                pass

        #
        # Border pieces last side
        # -----------------------
        if pieces[0] in self.my_cube.cube_borders and cube_row is not None and cube_row == 4:
            # cube_borders
            for border in pieces:
                pass

        #
        # Middle pieces
        # -------------
        if pieces[0] in self.my_cube.cube_middles:
            # cube middles
            for middle in pieces:
                if color in middle:
                    from_pos = self.find_piece(middle, color)
                    from_side = from_pos[0]
                    from_col_row = (from_pos[1], from_pos[2])
                    #
                    # allowed target pos for middle pieces
                    # - exclude border and center pos
                    # - exclude already placed middles
                    # - corner middle pos for corner middle pieces
                    # - non corner middle pos for non corner middle pieces
                    allowed_pos = [
                        [side, c, r]
                        for c in range(1, 4)
                        for r in range(1, 4)
                        if not (
                            c == 2
                            and r == 2
                            or self.my_cube.cube[side][c][r][0] == color
                            or from_col_row in self.my_cube.middle_edge_col_row
                            and (c, r) not in self.my_cube.middle_edge_col_row
                            or from_col_row not in self.my_cube.middle_edge_col_row
                            and (c, r) in self.my_cube.middle_edge_col_row
                        )
                    ]
                    if from_pos not in allowed_pos and from_side != side:
                        for pos in allowed_pos:
                            piece_travels.append([middle, from_pos, pos])
                            if debug or False:
                                print(
                                    f"travel middle {middle} from {from_pos} to {pos}"
                                )
                        break

        return piece_travels

    def move_reversed_corner_to_bottom_row(self, from_pos: Position, to_pos: Position):
        """move reversed corner to the bottom row

        Args:
            from_pos (Position): source corner position
            to_pos (Position): target corner position
        """
        direction = self.relative_direction(from_pos[0], to_pos[0])
        direction = self.opposite_direction[direction]
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        side = self.opposite_side[to_pos[0]]
        self.my_cube.turn([side, 2, 2], 90)
        self.my_cube.display_unfolded_cube("cube")

        col, row = self.translate_col_row(from_pos[0], side, from_pos[1], from_pos[2])
        new_from_pos = (side, col, row)
        direction = self.opposite_direction[direction]
        self.my_cube.move(new_from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

    def move_target_side_corner_to_bottom_row(self, from_pos: Position, to_pos: Position):
        """move target side corner down to the bottom row

        Args:
            from_pos (Position): _description_
            to_pos (Position): _description_
        """
        self.my_cube.move(from_pos, "Down")
        self.my_cube.display_unfolded_cube("cube")
        opposite = self.opposite_side[from_pos[0]]
        self.my_cube.turn([opposite, 2, 2], 270)
        self.my_cube.display_unfolded_cube("cube")

    def move_opposite_corner_to_bottom_row(self,
        piece: str, from_pos: Position, to_side: int, first_color: str
    ):
        """move corner from the opposite side to the bottom row, in respect to the target side

        Args:
            piece (str): piece identfier
            from_pos (Position): source position as side, col and row index
            to_side (int): target side index
        """
        for color in piece:
            if color != first_color:
                from_adjacient_pos = self.find_piece(piece, color)
                from_adjacient_side = 0
                from_adjacient_col = 0
                from_adjacient_row = 0
                if from_adjacient_pos is not None:
                    from_adjacient_side = from_adjacient_pos[0]
                    from_adjacient_col = from_adjacient_pos[1]
                    from_adjacient_row = from_adjacient_pos[2]
                turn_rotation = 270
                direction = self.relative_direction(from_adjacient_side, to_side)
                if (
                    direction == "Up"
                    and from_adjacient_col == 4
                    or direction == "Left"
                    and from_adjacient_row == 0
                    or direction == "Right"
                    and from_adjacient_row == 4
                    or direction == "Down"
                    and from_adjacient_col == 0
                ):
                    turn_rotation = 90

                # 1. turn once adjacient side
                self.my_cube.turn(from_adjacient_pos, turn_rotation)
                self.my_cube.display_unfolded_cube("cube")
                # 2. turn twice the opposite side
                self.my_cube.turn(from_pos, turn_rotation)
                self.my_cube.display_unfolded_cube("cube")
                self.my_cube.turn(from_pos, turn_rotation)
                self.my_cube.display_unfolded_cube("cube")
                # 3. turn adjacient side back
                self.my_cube.turn(from_adjacient_pos, 360 - turn_rotation)
                self.my_cube.display_unfolded_cube("cube")
                break  # do not repeat fo the second adjacient side

    def move_target_side_border_to_bottom_row(self, from_pos: Position, to_pos: Position):
        """move border from the target side down to the bottom row

        Args:
            from_pos (Position): source border position
            to_pos (Position): target border position
        """
        from_side = self.border_adjacient_side(from_pos)
        direction = self.relative_direction(from_pos[0], from_side)
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        to_side = to_pos[0]
        opposite = self.my_cube.opposite_side[to_side]
        self.my_cube.turn([opposite, 2, 2], 90)
        self.my_cube.display_unfolded_cube("cube")

        direction = self.my_cube.opposite_direction[direction]
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

    def move_reversed_border_to_bottom_row(self, piece: str, from_pos: Position, to_side):
        """move reversed border piece from target side to the bottom row
        Args:
            piece (str): piece identfier
            from_pos (Position): source position as side, col and row index
        """
        # 1. move border down to to opposite side
        opposite = self.my_cube.opposite_side[to_side]
        direction = self.my_cube.relative_direction(from_pos[0], opposite)
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        # 2. turn opposite side 180
        self.my_cube.turn([opposite, 2, 2], 180)
        self.my_cube.display_unfolded_cube("cube")

        # 3. move piece up to the bottom row side
        direction = self.my_cube.relative_direction(opposite, from_pos[0])
        tr_col_row = self.my_cube.translate_col_row(
            from_pos[0], opposite, from_pos[1], from_pos[2]
        )
        rotated_col_row = self.my_cube.rotate_side(tr_col_row, 180)
        rotated_from_pos = (opposite, rotated_col_row[0], rotated_col_row[1])
        self.my_cube.move(rotated_from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

    def move_opposite_border_to_bottom_row(self, 
        piece: str, from_pos: Position, to_side: int
    ):
        """move border piece from the opposite side to the bottom row, in respect to the target side

        Args:
            piece (str): piece identfier
            from_pos (Position): source position as side, col and row index
            to_side (int): target side index
        """
        # move border away from its adjacient side
        adjacient_side = self.border_adjacient_side(from_pos)
        direction = self.my_cube.relative_direction(from_pos[0], adjacient_side)
        direction = self.my_cube.opposite_direction[direction]
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        # turn target opposite side
        self.my_cube.turn([self.my_cube.opposite_side[to_side], 2, 2], 90)
        self.my_cube.display_unfolded_cube("cube")

        # reverse first move to not destroy borders on the target side
        direction = self.my_cube.opposite_direction[direction]
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

    def move_aligned_corner(self, from_pos: Position, to_pos: Position):
        """move corner previously aligned underneath to target corner position

        Args:
            from_pos (Position): source position (side, col, row indexes)
            to_pos (Position): target position (side, col, row indexes)
        """
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        to_side = to_pos[0]

        turn_rotation = 270
        direction = self.my_cube.relative_direction(from_side, to_side)
        if (
            direction == "Up"
            and from_col == 4
            or direction == "Left"
            and from_row == 0
            or direction == "Right"
            and from_row == 4
            or direction == "Down"
            and from_col == 0
        ):
            turn_rotation = 90

        # turn adjacient side forwards
        self.my_cube.turn(from_pos, turn_rotation)
        self.my_cube.display_unfolded_cube("cube")
        opposite_side_pos = [self.my_cube.opposite_side[to_side], 2, 2]

        # turn opposite side
        self.my_cube.turn(opposite_side_pos, turn_rotation)
        self.my_cube.display_unfolded_cube("cube")

        # turn adjacient side backwards
        self.my_cube.turn(from_pos, 360 - turn_rotation)
        self.my_cube.display_unfolded_cube("cube")

    def move_aligned_border_bottom(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        to_side = to_pos[0]

        # turn side left
        turn_rotation = 270
        self.my_cube.turn(from_pos, turn_rotation)
        self.my_cube.display_unfolded_cube("cube")

        # move border left
        move_direction = self.my_cube.relative_direction(from_side, to_side)
        move_direction = self.my_cube.rotated_270_direction[move_direction]
        rotated_col, rotated_row = self.my_cube.rotate_side(
            (from_col, from_row), turn_rotation
        )
        self.my_cube.move((from_side, rotated_col, rotated_row), move_direction)
        self.my_cube.display_unfolded_cube("cube")

        # turn adjacient side backwards
        self.my_cube.turn(from_pos, 360 - turn_rotation)
        self.my_cube.display_unfolded_cube("cube")

    def move_aligned_border_lateral(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        from_adjacient = self.border_adjacient_side(from_pos)
        to_side = to_pos[0]

        # move target position down to the border adjacient side
        direction = self.my_cube.relative_direction(to_side, from_adjacient)
        self.my_cube.move(to_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        # move border towards its adjacient side
        direction = self.my_cube.relative_direction(from_side, from_adjacient)
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

        # move it then back to the target side
        col, row = self.my_cube.translate_col_row(
            from_side, from_adjacient, from_pos[1], from_pos[2]
        )
        direction = self.my_cube.relative_direction(from_adjacient, to_side)
        self.my_cube.move((from_adjacient, col, row), direction)
        self.my_cube.display_unfolded_cube("cube")

    def align_bottom_row_corner(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        to_side = to_pos[0]
        from_adjacient_sides = self.corner_adjacient_sides(from_pos)
        to_adjacient_sides = self.corner_adjacient_sides(to_pos)
        for to_adjacient_side in to_adjacient_sides:
            for from_adjacient_side in from_adjacient_sides:
                if from_adjacient_side == to_adjacient_side:
                    direction = self.my_cube.relative_direction(from_side, to_adjacient_side)
                    self.my_cube.move(from_pos, direction)
                    break
            else:
                continue
            break
        else:
            opposite = self.my_cube.opposite_side[to_side]
            self.my_cube.turn([opposite, 2, 2], 180)
        self.my_cube.display_unfolded_cube("cube")

    def align_bottom_row_border(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        to_adjacient_side = self.border_adjacient_side(to_pos)
        if self.my_cube.is_side_adjacient(from_side, to_adjacient_side):
            direction = self.my_cube.relative_direction(from_side, to_adjacient_side)
            self.my_cube.move(from_pos, direction)
        else:
            from_adjacient_side = self.border_adjacient_side(from_pos)
            self.my_cube.turn([from_adjacient_side, 2, 2], 180)
        self.my_cube.display_unfolded_cube("cube")

    def align_lateral_border(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        to_side = to_pos[0]
        to_adjacient_side = self.border_adjacient_side(to_pos)
        if from_side == to_adjacient_side:
            # move lateral border twice (180 turn)
            direction = self.my_cube.relative_direction(from_side, to_side)
            direction = self.my_cube.rotated_90_direction[direction]
            self.my_cube.move(from_pos, direction)
            self.my_cube.move(from_pos, direction)
        else:
            # move lateral border once towards its adjacient side
            from_adjacient_side = self.border_adjacient_side(from_pos)
            direction = self.my_cube.relative_direction(from_side, from_adjacient_side)
            self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")

    def align_opposite_middle(self, piece: str, from_pos: Position, to_pos: Position) -> str:
        rotated_col = from_pos[1]
        rotated_row = from_pos[2]
        to_side = to_pos[0]
        to_col = to_pos[1]
        to_row = to_pos[2]
        for from_direction in ("Up", "Left"):
            rotated_col, rotated_row = self.my_cube.flip_side(
                (rotated_col, rotated_row), from_direction, to_side
            )
            rotations = 0
            while not (rotated_col, rotated_row) == (to_col, to_row) and rotations < 3:
                self.my_cube.turn(from_pos, 90)
                rotations += 1
                self.my_cube.display_unfolded_cube("cube")
                side, rotated_col, rotated_row = self.find_piece(piece)
                rotated_col, rotated_row = self.my_cube.flip_side(
                    (rotated_col, rotated_row), from_direction, to_side
                )

            if (rotated_col, rotated_row) == (to_col, to_row):
                return from_direction

        raise Exception(
            f"align_opposite_middle({piece}, {from_pos}, {to_pos}): Case not hanlded. Check and fix."
        )

    def align_adjacient_middle(self, piece: str, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        to_side = to_pos[0]
        turns = 0
        while (
            not self.is_piece_adjacient_aligned(
                piece, (from_side, from_col, from_row), to_pos
            )
            and turns < 3
        ):
            #
            # move middel sidewards (270° rotated relative to the target side direction)
            direction = self.my_cube.relative_direction(from_side, to_side)
            move_direction = self.my_cube.rotated_270_direction[direction]
            self.my_cube.move((from_side, from_col, from_row), move_direction)
            self.my_cube.display_unfolded_cube("cube")
            turns += 1
            #
            # take new from piece position
            from_side, from_col, from_row = self.find_piece(piece)

    def move_aligned_opposite_middle(self, 
        piece: str, from_pos: Position, to_pos: Position, from_direction: str
    ):
        self.move_aligned_middle(piece, from_pos, to_pos, from_direction)

    def move_aligned_middle(self, 
        piece: str,
        from_pos: Position,
        to_pos: Position,
        from_direction: str | None = None,
    ):
        from_side = from_pos[0]
        from_col = from_pos[1]
        from_row = from_pos[2]
        to_side = to_pos[0]

        # 1. move up towards target pos
        direction = (
            self.my_cube.relative_direction(from_side, to_side)
            if from_direction is None
            else from_direction
        )
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")
        if from_direction is not None:
            self.my_cube.move(from_pos, direction)
            self.my_cube.display_unfolded_cube("cube")

        # 2. turn either 90 or 270 depending on the move direction
        #    and the source position
        rotation = 90  #   for centered middle pieces 90 or 270 does not matter
        if (from_col, from_row) in self.my_cube.middle_edge_col_row:
            if direction in ("Up", "Down"):
                if (from_col, from_row) in ((1, 1), (3, 3)):
                    rotation = 90
                else:
                    rotation = 270
            else:
                if (from_col, from_row) in ((1, 1), (3, 3)):
                    rotation = 270
                else:
                    rotation = 90

        self.my_cube.turn(to_pos, rotation)
        self.my_cube.display_unfolded_cube("cube")

        # 3. move rotated middle piece up again (relative to the source side)
        new_side, new_col, new_row = self.find_piece(piece)
        new_direction = (
            self.my_cube.opposite_direction[self.my_cube.relative_direction(to_side, from_side)]
            if from_direction is None
            else self.my_cube.opposite_direction[from_direction]
        )
        self.my_cube.move((new_side, new_col, new_row), new_direction)
        self.my_cube.display_unfolded_cube("cube")
        if from_direction is not None:
            self.my_cube.move((new_side, new_col, new_row), new_direction)
            self.my_cube.display_unfolded_cube("cube")

        # 4. turn to_side back
        new_rotation = 90 if rotation == 270 else 270
        self.my_cube.turn(to_pos, new_rotation)
        self.my_cube.display_unfolded_cube("cube")
        #
        # 5. move down from pos
        direction = self.my_cube.opposite_direction[direction]
        self.my_cube.move(from_pos, direction)
        self.my_cube.display_unfolded_cube("cube")
        if from_direction is not None:
            self.my_cube.move(from_pos, direction)
            self.my_cube.display_unfolded_cube("cube")
        #
        # 6. turn to_side back again
        new_rotation = 90 if new_rotation == 270 else 270
        self.my_cube.turn(to_pos, new_rotation)
        self.my_cube.display_unfolded_cube("cube")
        #
        # 7. down rotated to_pos down again
        new_direction = self.my_cube.opposite_direction[new_direction]
        self.my_cube.move((new_side, new_col, new_row), new_direction)
        self.my_cube.display_unfolded_cube("cube")
        if from_direction is not None:
            self.my_cube.move((new_side, new_col, new_row), new_direction)
            self.my_cube.display_unfolded_cube("cube")
        #
        # 8. turn to_side forward again
        new_rotation = 90 if new_rotation == 270 else 270
        self.my_cube.turn(to_pos, new_rotation)
        self.my_cube.display_unfolded_cube("cube")

    def move_target_side_corner(self, from_pos: Position, to_pos: Position):
        from_side = from_pos[0]
        from_adjacient_sides = self.corner_adjacient_sides(from_pos)
        to_adjacient_sides = self.corner_adjacient_sides(to_pos)
        for to_adjacient_side in to_adjacient_sides:
            for from_adjacient_side in from_adjacient_sides:
                if from_adjacient_side == to_adjacient_side:
                    direction = self.my_cube.relative_direction(
                        from_side, from_adjacient_side
                    )
                    self.my_cube.move(from_pos, direction)
                    break
            else:
                continue
            break
        else:
            self.my_cube.turn(to_pos, 180)
        self.my_cube.display_unfolded_cube("cube")

    def solve_first_centers(self, first_side: int, first_color: str):
        """solve center piece of the first side

        Args:
            first_side (int): first side index
            first_color (str): color first side
        """
        if debug or False:
            print("solve_first_centers")

        pos = self.find_piece(first_color)

        if pos is not None and len(pos) == 3:
            while first_side != pos[0]:
                self.my_cube.move(pos, self.my_cube.relative_direction(pos[0], first_side))
                self.my_cube.display_unfolded_cube("cube")
                pos = self.find_piece(first_color)
        else:
            raise Exception(
                f"solve_first_centers({first_side}, {first_color}): Casen not hanlded. Check and fix."
            )

    def solve_first_corners(self, first_side: int, first_color: str):
        """solve corner pieces of the first side

        If misplaced corners exist then place them to their target position
        starting with

        1. the corners not aligned and on the top row (reversed)
        2. the corners on the target side but on the wrong position
        3. the corners which have the target color on the opposite side
        4. the corners placed on the bottom line (row or col depending on oritentation)
            of the adjacient side (alligned)

        After one piece has been moved to its correct target place,
        skip the other and re-evaluate how many misplaced pieces are still there.

        Args:
        first_side (int): first side index
        first_color (str): color first side
        """
        if debug or False:
            print("solve_first_corners")

        misplaced_piece_travels = []

        # process until no more misplaced pieces are found
        misplaced_piece_travels = self.fill_piece_travels(
            first_color, self.my_cube.cube_corners, first_side
        )
        while len(misplaced_piece_travels) > 0:
            for travel in misplaced_piece_travels:
                travel_index = misplaced_piece_travels.index(travel) + 1
                piece = travel[0]
                from_pos = travel[1]
                from_side = from_pos[0]
                to_pos = travel[2]
                to_side = to_pos[0]
                #
                # case 1: if corner on adjacient side but not aligned and on the top row
                #          move it down, to be algined later
                if self.is_piece_reversed(piece, to_side, first_color):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 1: corner {piece} on adjecient side but on top row (reversed)"
                        )

                    self.move_reversed_corner_to_bottom_row(from_pos, to_pos)
                    break
                #
                # case 2: if corner on the top side but on the wrong position
                #          and all other corners are misplaced, then move it
                #          to the correct position
                if from_side == to_side and len(misplaced_piece_travels) == 4:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(f"case 2a: corner {piece} have have to be rotated")

                    self.move_target_side_corner(from_pos, to_pos)
                    break
                #
                # case 2b: if corner on the top side but on the wrong position
                #          and all other corners are misplaced, then turn it
                if from_side == to_side and len(misplaced_piece_travels) < 4:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 2b: corner {piece} have to be move down to the bottom row"
                        )

                    self.move_target_side_corner_to_bottom_row(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 3: check if corner is on the opposite side move it up to the bottom row
                if from_side == self.my_cube.opposite_side[to_side]:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 3: corner {piece} is on the opposite side. Has to be moved to the botton row"
                        )

                    self.move_opposite_corner_to_bottom_row(piece, from_pos, to_side, first_color)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 4: if corner on adjacient side but not reversed then
                #          align it first than place it.
                if self.my_cube.is_side_adjacient(
                    from_side, to_side
                ) and self.is_piece_on_bottom_row(piece, from_pos, to_side, first_color):
                    if not self.is_piece_adjacient_aligned(piece, from_pos, to_pos):
                        if travel_index < len(misplaced_piece_travels):
                            continue

                        if debug or False:
                            print(f"case 4: corner {piece} is not aligned")

                        self.align_bottom_row_corner(from_pos, to_pos)
                        break  # skip and re-evaluate remaining misplaced pieace

                    if debug or False:
                        print(f"case 4: corner {piece} is aligned")

                    self.move_aligned_corner(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace

            # process until no more misplaced pieces are found
            misplaced_piece_travels = self.fill_piece_travels(
                first_color, self.my_cube.cube_corners, first_side
            )

    def solve_first_borders(self, first_side: int, first_color: str):
        """If misplaced borders exist place them to their target position starting with

            1. the ones on the target side but on the wrong position
            -> move it down
            2. the ones which are on the target side but with the wrong color (reversed)
            -> move it to the bottem row (down, rotate bottom 180, up)
            3. the ones on the lateral column
            -> move it left, relative to the target side, if not lateral aligned
            -> if lateral aligneed move piece to the target pos
                (turn target adjacient side 270, move border right, turn adjacient side back 90)
            4. the ones on the opposite side
            -> move it to the bottom row
            5. the ones placed on the relative bottom row (row or col depending on oritentation)
            -> move it left, relative to the target side, if not bottom row aligned
            -> if bottom row alligned move piece to the target pos
                ()

        After one piece has been moved to its correct target place,
        skip the other and re-evaluate how many misplaced pieces are still there.

        Do not skip other misplaced borders because they can be move in other target positions.

        Args:
            first_side (int): first side index
            first_color (str): first side color
        """
        if debug or False:
            print("solve_first_borders")

        # process until no more misplaced pieces are found
        misplaced_piece_travels = self.fill_piece_travels(
            first_color, self.my_cube.cube_borders, first_side
        )
        while len(misplaced_piece_travels) > 0:
            for travel in misplaced_piece_travels:
                travel_index = misplaced_piece_travels.index(travel) + 1
                piece = travel[0]
                from_pos = travel[1]
                from_side = from_pos[0]
                to_pos = travel[2]
                to_side = to_pos[0]
                col, row = self.my_cube.translate_col_row(
                    to_side, from_side, from_pos[1], from_pos[2]
                )
                #
                # case 1 : check if border has to be moved down because already on the target side
                #          but in the wrong positiion
                if from_side == to_side:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 1: border {piece} on target side has to be moved to the bottom row"
                        )
                    self.move_target_side_border_to_bottom_row(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 2 : check if border piece is on the target side but reversed and move it
                #          down to the bottom row. Use same move as for alligned borders, just take
                #          the piece aligned on the bottom row
                if self.is_piece_reversed(piece, to_side, first_color):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 2: border {piece} is reversed. Has to be moved down to the bottom row"
                        )
                    self.move_reversed_border_to_bottom_row(piece, from_pos, to_side)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 3 : check if border piece is on the lateral column.
                #          rotate it if not lateral aligned to the target position
                if (
                    not self.is_piece_on_bottom_row(piece, from_pos, to_side, first_color)
                    and not from_side == self.my_cube.opposite_side[to_side]
                ):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 3: border {piece} is on the lateral column. Has to rotate until aligned."
                        )

                    if not self.is_border_lateral_aligned(from_pos, to_pos):
                        if travel_index < len(misplaced_piece_travels):
                            continue

                        self.align_lateral_border(from_pos, to_pos)
                        break

                    if debug or False:
                        print(
                            f"case 3: border {piece} is aligned on the lateral column"
                        )
                    self.move_aligned_border_lateral(from_pos, to_pos)
                    break
                #
                # case 4 : check if border is on the opposite side move it up to the bottom row
                if from_side == self.my_cube.opposite_side[to_side]:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 4: border {piece} is on the opposite side. Has to be moved to the botton row"
                        )
                    self.move_opposite_border_to_bottom_row(piece, from_pos, to_side)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 5: if border on adjacient side but not reversed then
                #         align it first than place it.
                if self.my_cube.is_side_adjacient(
                    from_side, to_side
                ) and self.is_piece_on_bottom_row(piece, from_pos, to_side, first_color):
                    if debug or False:
                        print(
                            f"case 5a: border {piece} in on the adjacient side and has to be aligned"
                        )
                    if not self.is_piece_adjacient_aligned(piece, from_pos, to_pos):
                        if travel_index < len(misplaced_piece_travels):
                            continue

                        self.align_bottom_row_border(from_pos, to_pos)
                        break  # skip and re-evaluate remaining misplaced pieace

                    if debug or False:
                        print(f"case 5b: border {piece} is aligned")
                    self.move_aligned_border_bottom(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace

            # process until no more misplaced pieces are found
            misplaced_piece_travels = self.fill_piece_travels(
                first_color, self.my_cube.cube_borders, first_side
            )

    def solve_first_middles(self, first_side: int, first_color: str):
        """If misplaced middles exist place them to their target position starting with

            1. the ones on the opposite side
                -> rotate the opposite side until aligned to the target middle position
            2. the ones on the adjacient side
                -> rotate the target side in order to align the target position to the source middle
            4. move the aligned middle to its target position

        After each case move skip the other misplaced piece and re-evalute the pieces to place.

        Args:
            first_side (int): first side index
            first_color (str): first side color
        """
        if debug or False:
            print("solve_first_middles")

        # process until no more misplaced pieces are found
        misplaced_piece_travels = self.fill_piece_travels(
            first_color, self.my_cube.cube_middles, first_side
        )
        while len(misplaced_piece_travels) > 0:
            for travel in misplaced_piece_travels:
                travel_index = misplaced_piece_travels.index(travel) + 1
                piece = travel[0]
                from_pos = travel[1]
                from_side = from_pos[0]
                to_pos = travel[2]
                to_side = to_pos[0]
                #
                # case 1 : check if middle is on the opposite side and align it below the target pos
                if from_side == self.my_cube.opposite_side[to_side]:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 1: middle {piece} is on the opposite side. Has to be aligned below its target"
                        )
                    from_direction = self.align_opposite_middle(piece, from_pos, to_pos)
                    new_from_pos = self.find_piece(piece)
                    self.move_aligned_opposite_middle(
                        piece, new_from_pos, to_pos, from_direction
                    )
                    break
                #
                # case 2 : check if middle is on the adjacient side and align it the target pos
                if not self.is_piece_adjacient_aligned(piece, from_pos, to_pos):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 2: middle {piece} is on the adjacient side. Has to be aligned below its target"
                        )
                    self.align_adjacient_middle(piece, from_pos, to_pos)
                    break
                #
                # case 3 : move alinged middle to its target
                if debug or False:
                    print(
                        f"case 3: middle {piece} is aligned (either opposite or adjacient side) and has to be moved to its target"
                    )
                self.move_aligned_middle(piece, from_pos, to_pos)
                break

            # process until no more misplaced pieces are found
            misplaced_piece_travels = self.fill_piece_travels(
                first_color, self.my_cube.cube_middles, first_side
            )

    def solve_lateral_centers(self, first_side: int, first_color: str):
        """solve center pieces of the lateral sides. First side has to be solved first.

        Args:
            first_side (int): first side index
            first_color (str): color first side
        """
        if debug or False:
            print("solve_lateral_centers")
        lateral_centers = [
            center
            for center in self.my_cube.cube_centers
            if center not in (first_color, self.my_cube.opposite_color[first_color])
        ]
        first_borders = [border for border in self.my_cube.cube_borders if first_color in border]
        misplaced_centers = True
        while misplaced_centers:
            for center in lateral_centers:
                from_pos = self.find_piece(center)
                from_side = from_pos[0]
                for border in first_borders:
                    if center in border:
                        first_border_pos = self.find_piece(border, first_color)
                        if from_side == self.border_adjacient_side(first_border_pos):
                            misplaced_centers = False
                            break
                        direction = self.my_cube.rotated_270_direction[
                            self.my_cube.relative_direction(from_side, first_side)
                        ]
                        self.my_cube.move(from_pos, direction)
                        self.my_cube.display_unfolded_cube("cube")
                        break

    def solve_row_1_borders(self, first_side: int, first_color: str):
        """If misplaced row 1 borders exist place them to their target position starting with

            1. the ones on the lateral column
            -> move it down to the bottom row, relative to the target side
            2. the ones on the bottom row
            -> align it under the target row 1 border 
            3. move aligned piece to the target pos

        After one piece has been moved to its correct target place,
        skip the other and re-evaluate how many misplaced pieces are still there.

        Args:
            first_side (int): first side index
            first_color (str): first side color
        """
        if debug or False:
            print("solve_row_1_borders")

        # process until no more misplaced pieces are found
        misplaced_piece_travels = self.fill_piece_travels(
            first_color, self.my_cube.cube_borders, first_side
        )
        while len(misplaced_piece_travels) > 0:
            for travel in misplaced_piece_travels:
                travel_index = misplaced_piece_travels.index(travel) + 1
                piece = travel[0]
                from_pos = travel[1]
                from_side = from_pos[0]
                to_pos = travel[2]
                to_side = to_pos[0]
                col, row = self.my_cube.translate_col_row(
                    to_side, from_side, from_pos[1], from_pos[2]
                )
                #
                # case 1 : check if border has to be moved down because already on the target side
                #          but in the wrong positiion
                if from_side == to_side:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 1: border {piece} on target side has to be moved to the bottom row"
                        )
                    self.move_target_side_border_to_bottom_row(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 2 : check if border piece is on the target side but reversed and move it
                #          down to the bottom row. Use same move as for alligned borders, just take
                #          the piece aligned on the bottom row
                if self.is_piece_reversed(piece, to_side, first_color):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 2: border {piece} is reversed. Has to be moved down to the bottom row"
                        )
                    self.move_reversed_border_to_bottom_row(piece, from_pos, to_side)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 3 : check if border piece is on the lateral column.
                #          rotate it if not lateral aligned to the target position
                if (
                    not self.is_piece_on_bottom_row(piece, from_pos, to_side, first_color)
                    and not from_side == self.my_cube.opposite_side[to_side]
                ):
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 3: border {piece} is on the lateral column. Has to rotate until aligned."
                        )

                    if not self.is_border_lateral_aligned(from_pos, to_pos):
                        if travel_index < len(misplaced_piece_travels):
                            continue

                        self.align_lateral_border(from_pos, to_pos)
                        break

                    if debug or False:
                        print(
                            f"case 3: border {piece} is aligned on the lateral column"
                        )
                    self.move_aligned_border_lateral(from_pos, to_pos)
                    break
                #
                # case 4 : check if border is on the opposite side move it up to the bottom row
                if from_side == self.my_cube.opposite_side[to_side]:
                    if travel_index < len(misplaced_piece_travels):
                        continue

                    if debug or False:
                        print(
                            f"case 4: border {piece} is on the opposite side. Has to be moved to the botton row"
                        )
                    self.move_opposite_border_to_bottom_row(piece, from_pos, to_side)
                    break  # skip and re-evaluate remaining misplaced pieace
                #
                # case 5: if border on adjacient side but not reversed then
                #         align it first than place it.
                if self.my_cube.is_side_adjacient(
                    from_side, to_side
                ) and self.is_piece_on_bottom_row(piece, from_pos, to_side, first_color):
                    if debug or False:
                        print(
                            f"case 5a: border {piece} in on the adjacient side and has to be aligned"
                        )
                    if not self.is_piece_adjacient_aligned(piece, from_pos, to_pos):
                        if travel_index < len(misplaced_piece_travels):
                            continue

                        self.align_bottom_row_border(from_pos, to_pos)
                        break  # skip and re-evaluate remaining misplaced pieace

                    if debug or False:
                        print(f"case 5b: border {piece} is aligned")
                    self.move_aligned_border_bottom(from_pos, to_pos)
                    break  # skip and re-evaluate remaining misplaced pieace

            # process until no more misplaced pieces are found
            misplaced_piece_travels = self.fill_piece_travels(
                first_color, self.my_cube.cube_borders, first_side
            )

    def solve_row_2_borders(self, first_side: int, first_color: str):
        pass

    def place_last_middle_borders(self, first_side: int, first_color: str):
        pass

    def solve_last_corners(self, fist_side: int, first_color: str):
        pass

    def solve_last_lateral_borders(self, first_side: int, first_color: str):
        pass

    def solve_last_middle_borders(self, fisrt_side: int, first_color: str):
        pass

    def solve_row_3_borders(self, first_side: int, first_color: str):
        pass

    def solve_rest_middles(self, first_side: int, first_color: str):
        pass

    def solve(self, first_color: str = "b"):
        """Solve the cube using the "human" method

        Args:
            first_color (str, optional): start side color. Defaults to 'b'.
        """
        first_side = self.my_cube.cursor_pos[0] if isinstance(self.my_cube.cursor_pos, list) else 0
        self.solve_first_centers(first_side, first_color)
        self.solve_first_corners(first_side, first_color)
        self.solve_first_borders(first_side, first_color)
        self.solve_first_middles(first_side, first_color)
        self.solve_lateral_centers(first_side, first_color)
        self.solve_row_1_borders(first_side, first_color)
        self.solve_row_2_borders(first_side, first_color)
        self.place_last_middle_borders(first_side, first_color)
        self.solve_last_corners(first_side, first_color)
        self.solve_last_lateral_borders(first_side, first_color)
        self.solve_last_middle_borders(first_side, first_color)
        self.solve_row_3_borders(first_side, first_color)
        self.solve_rest_middles(first_side, first_color)

class CubeGame():
    # keys used for the game
    navigate_keys = ("Up", "Down", "Left", "Right")
    move_keys = ("w", "a", "s", "d")
    turn_keys = ("Shift_L", "Shift_R")
    shuffle_key = "space"
    new_key = "n"
    reverse_key = "r"
    solve_key = "Return"
    side_selection_keys = ("Control_L", "Control_R")
    key_to_direction = {
        "w": "Up",
        "a": "Left",
        "s": "Down",
        "d": "Right",
        "Shift_L": 270,
        "Shift_R": 90,
    }

    def __init__(self):
        # init cube with default position
        self.cursor_pos = [0, 2, 2]
        self.cube = Cube((self.cursor_pos[0], self.cursor_pos[1], self.cursor_pos[2]))

        # display cube
        self.cube.display_keys_usage()
        self.cube.display_unfolded_cube("all")
        self.side_selected = False

        # wait 0.5 seconds to make the first win.getKey() working in play()
        time.sleep(0.5)

    def __del__(self):
        del self.cube

    def play(self):
        key = self.cube.win.getKey().replace("KP_", "")
        while key != "Escape":
            print(key)
            # do something only if a relevant key has been pressed
            if key in self.navigate_keys + self.move_keys + self.turn_keys + self.side_selection_keys or key in (
                self.shuffle_key,
                self.reverse_key,
                self.new_key,
                self.solve_key,
            ):
                if key in self.navigate_keys:  # Up, Down, Left, Right
                    self.cursor_pos = self.cube.navigate_unfolded(self.cube.cursor_pos, key, self.side_selected)
                    self.cube.cursor_pos = self.cursor_pos
                    self.cube.display_unfolded_cube("cursor", self.side_selected)

                elif key in self.move_keys:  # w, a, s, d
                    self.cursor_pos = self.cube.move_from_cursor(
                        self.cursor_pos, self.key_to_direction[key], self.side_selected
                    )
                    self.side_selected = False
                    self.cube.display_unfolded_cube("all")

                elif key == self.shuffle_key:  # space
                    self.cube.shuffle_cube()
                    self.cube.display_unfolded_cube("cursor")

                elif key == self.new_key:  # new
                    del self.cube
                    self.cube = Cube()
                    self.cube.display_unfolded_cube("all")
                    self.cube.display_keys_usage()

                elif key == self.reverse_key:  # r
                    self.cube.reverse_moves()

                elif key in self.turn_keys:  # Shift_L, Shift_R
                    self.cube.turn(self.cursor_pos, self.key_to_direction[key])
                    self.cube.display_unfolded_cube("all")

                elif key == self.solve_key:  # Return
                    solver = CubeSolver(self.cube)
                    # center = self.cube.cube[self.cursor_pos[0]][2][2][1]  TODO: first_color logic not yet implemented
                    center = "b"
                    solver.solve(center)    
                    self.cube.display_unfolded_cube("cursor", self.cursor_pos)

                elif key in self.side_selection_keys:  # Control_L, Control_R
                    if not self.side_selected:
                        self.side_selected = True
                    else:
                        self.side_selected = False

                    self.cube.display_unfolded_cube("cursor", self.side_selected)

            key = self.cube.win.getKey().replace("KP_", "")

# ----------------------------------------------------------------------------------------------------------------------------------------
# Main 
# ----------------------------------------------------------------------------------------------------------------------------------------

# write or not debug messages to the terminal and show piece identifiers on the cube
debug = True
# debug = False

game = CubeGame()
game.play()
