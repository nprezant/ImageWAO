"""
Python program to implement Cohen Sutherland algorithm 
for line clipping.
"""

# Defining region codes
INSIDE = 0  # 0000
LEFT = 1  # 0001
RIGHT = 2  # 0010
BOTTOM = 4  # 0100
TOP = 8  # 1000


def computeCode(x, y, xmax, ymax, xmin, ymin):
    """
    Compute region code for a point(x,y)
    """

    code = INSIDE
    if x < xmin:  # to the left of rectangle
        code |= LEFT
    elif x > xmax:  # to the right of rectangle
        code |= RIGHT
    if y < ymin:  # below the rectangle
        code |= BOTTOM
    elif y > ymax:  # above the rectangle
        code |= TOP

    return code


def cohenSutherlandClip(x1, y1, x2, y2, xmax, ymax, xmin, ymin):
    """
    Implementing Cohen-Sutherland algorithm 
    Clipping a line from P1 = (x1, y1) to P2 = (x2, y2)
    """

    bounds = (xmax, ymax, xmin, ymin)

    # Compute region codes for P1, P2
    code1 = computeCode(x1, y1, *bounds)
    code2 = computeCode(x2, y2, *bounds)
    accept = False

    while True:

        # If both endpoints lie within rectangle
        if code1 == 0 and code2 == 0:
            accept = True
            break

        # If both endpoints are outside rectangle
        elif (code1 & code2) != 0:
            break

        # Some segment lies within the rectangle
        else:

            # Line Needs clipping
            # At least one of the points is outside,
            # select it
            x = 1.0
            y = 1.0
            if code1 != 0:
                code_out = code1
            else:
                code_out = code2

            # Find intersection point
            # using formulas y = y1 + slope * (x - x1),
            # x = x1 + (1 / slope) * (y - y1)
            if code_out & TOP:

                # point is above the clip rectangle
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax

            elif code_out & BOTTOM:

                # point is below the clip rectangle
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin

            elif code_out & RIGHT:

                # point is to the right of the clip rectangle
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax

            elif code_out & LEFT:

                # point is to the left of the clip rectangle
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            # Now intersection point x,y is found
            # We replace point outside clipping rectangle
            # by intersection point
            if code_out == code1:
                x1 = x
                y1 = y
                code1 = computeCode(x1, y1, *bounds)

            else:
                x2 = x
                y2 = y
                code2 = computeCode(x2, y2, *bounds)

    if accept:
        return x1, y1, x2, y2

    else:
        return None


if __name__ == "__main__":

    # Define x_max,y_max and x_min,y_min for rectangle
    # Since diagonal points are enough to define a rectangle
    bounds = (10.0, 8.0, 4.0, 4.0)

    # First Line segment
    # P11 = (5, 5), P12 = (7, 7)
    acceptedCoords = cohenSutherlandClip(5, 5, 7, 7, *bounds)

    # Second Line segment
    # P21 = (7, 9), P22 = (11, 4)
    acceptedCoords = cohenSutherlandClip(7, 9, 11, 4, *bounds)

    # Third Line segment
    # P31 = (1, 5), P32 = (4, 1)
    acceptedCoords = cohenSutherlandClip(1, 5, 4, 1, *bounds)  # Rejected
