#!/usr/bin/env python
#
# png2kicad_mod - converts one (or two) RGBA pngs to a .kicad_mod file
#
# Copyright 2017 Jack Humbert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from PIL import Image, ImageOps
import numpy as np
import potrace
from shapely.geometry import Point, Polygon

# Text for the file header, the parameter is the name of the module, ex "LOGO".
header = """(module %(name)s (layer F.Cu)
"""

# Text for the file footer, the only parameter is the name of the module
footer = """)
"""

def bezier_to_polyline(p1, p2, p3, p4):
    delta = 0.25 # accuacy in pixels

    dd0     = ( p1[0] - 2 * p2[0] + p3[0] )**2 + ( p1[1] - 2 * p2[1] + p3[1] )**2
    dd1     = ( p2[0] - 2 * p3[0] + p4[0] )**2 + ( p2[1] - 2 * p3[1] + p4[1] )**2
    dd      = 6 * ( max( dd0, dd1 ) )**.5
    if ((8 * delta) <= dd):
        e2 = 8 * delta / dd
    else:
        e2 = 1
    epsilon = ( e2 )**.5; # necessary interval size

    points = list()
    t = epsilon
    while (t < 1):
        point = (p1[0] * ( 1 - t )**3 + \
                               3* p2[0]* ( 1 - t )**2 * t + \
                               3 * p3[0] * (1 - t) * ( t )**2 + \
                               p4[0]* ( t )**3,
                p1[1] * ( 1 - t )**3 + \
                               3* p2[1]* ( 1 - t )**2 * t + \
                               3 * p3[1] * (1 - t) * ( t )**2 + p4[1]* ( t )**3)
        points.append( point )
        t += epsilon
    return points

# def plot_curve(curve, scale_factor):


    # module += " (xy %f %f)" % (curve.start_point[0] * 25.4 / scale_factor, curve.start_point[1] * 25.4 / scale_factor)
    # for child in curve.children:
    #     module += plot_curve(child, scale_factor)
    # i += 1
    # if (i > 6):
    #     i = 0
    #     module += "\n        "
    # return module

def curve_to_points(areas, curve, fp_type, process_children):
    points = list()
    points.append((curve.start_point[0], curve.start_point[1]))
    for segment in curve.segments:  
        if segment.is_corner:
            points.append((segment.c[0], segment.c[1]))
            points.append((segment.end_point[0], segment.end_point[1]))
        # else:
            # points.extend(curve.tesselate())   
            # points.extend(bezier_to_polyline(curve.start_point, segment.c1, segment.c2, segment.end_point))
            # points.append((segment.end_point[0], segment.end_point[1]))
    points.append((curve.start_point[0], curve.start_point[1]))
    
    if not process_children:
        return points

    for child in curve.children:
        for grandchild in child.children:
            curve_to_points(areas, grandchild, fp_type, True)
        child_points = curve_to_points(areas, child, fp_type, False)
        if fp_type == "fp_poly":
            closest = 10000
            closest_point = 0
            closest_child_point = 0
            for p, point in enumerate(points):
                for cp, child_point in enumerate(child_points):
                    distance = ((point[0] - child_point[0])**2 + (point[1] - child_point[1])**2)**.5
                    if distance < closest:
                        closest = distance
                        closest_point = p
                        closest_child_point = cp
            points.insert(closest_point + 1, points[closest_point])
            points.insert(closest_point + 1, child_points[closest_child_point])
            for point in child_points[closest_child_point::-1]:
                points.insert(closest_point + 1, point)
            for point in child_points[:closest_child_point:-1]:
                points.insert(closest_point + 1, point)
            points.insert(closest_point + 1, child_points[closest_child_point])
        else:
            areas.append(child_points)

    areas.append(points)


def render_path_to_layer(path, fp_type, layer, scale_factor):
    module = ""
    areas = list()
    children = list()
    for curve in path.curves_tree:
        curve_to_points(areas, curve, fp_type, True)

    for poly in areas:
        if fp_type == "fp_poly":
            module += "\n  (%s (pts" % fp_type
            i = 0
            for point in poly:
                module += " (xy %f %f)" % (point[0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor)
                i += 1
                if (i > 6):
                    i = 0
                    module += "\n"
            module += " (xy %f %f)" % (poly[0][0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor)

            module += """)
    (layer %s)
    (width 0.0001)
  )
""" % layer
        else:
            i = 0
            poly.append(poly[len(poly)-1])
            for i, point in enumerate(poly):
                if i+2 < len(poly):
                    module += "\n  (%s" % fp_type
                    module += " (start %f %f)" % (point[0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor)
                    module += " (end %f %f)" % (poly[i+1][0] * 25.4 / scale_factor, poly[i+1][1] * 25.4 / scale_factor)
                    module += """    (layer %s)
    (width 0.0001)
  )
""" % layer      

    return module

def conv_image_to_module(name, scale_factor):

    module = header % {"name": name}

    front_image = Image.open("%s_front.png" % name)    
    print("Reading image from \"%s_front.png\"" % name)

    front_image_red, front_image_green, front_image_blue, front_image_alpha = front_image.split()

    front_image_red = front_image_red.point(lambda i: 0 if i < 127 else 1)
    red_array = np.array(front_image_red)
    bmp_red = potrace.Bitmap(red_array)
    path_red = bmp_red.trace(alphamax = 0.0, opttolerance = 50)

    # Soldermask needs to be inverted
    front_image_green = ImageOps.invert(front_image_green)
    front_image_green = Image.composite(front_image_green, front_image_alpha, front_image_alpha)
    front_image_green = front_image_green.point(lambda i: 0 if i < 127 else 1)
    green_array = np.array(front_image_green)
    bmp_green = potrace.Bitmap(green_array)
    path_green = bmp_green.trace(alphamax = 0.0, opttolerance = 50)

    front_image_blue = front_image_blue.point(lambda i: 0 if i < 127 else 1)
    blue_array = np.array(front_image_blue)
    bmp_blue = potrace.Bitmap(blue_array)
    path_blue = bmp_blue.trace(alphamax = 0.0, opttolerance = 50)

    front_image_alpha = front_image_alpha.point(lambda i: 0 if i < 127 else 1)
    front_image_alpha_array = np.array(front_image_alpha)
    bmp_alpha = potrace.Bitmap(front_image_alpha_array)
    path_alpha = bmp_alpha.trace(alphamax = 0.0, opttolerance = 50)

    w, h = front_image.size

    print("Generating Edge.Cuts layer from front alpha channel")
    module += render_path_to_layer(path_alpha, "fp_line", "Edge.Cuts", scale_factor)

    print("Generating F.Cu layer from front red channel")
    module += render_path_to_layer(path_red, "fp_poly", "F.Cu", scale_factor)
    print("Generating F.Mask layer from front green channel")
    module += render_path_to_layer(path_green, "fp_poly", "F.Mask", scale_factor)
    print("Generating F.SilkS layer from front blue channel")
    module += render_path_to_layer(path_blue, "fp_poly", "F.SilkS", scale_factor)

    try:
        back_image = Image.open("%s_back.png" % name)
        back_image = ImageOps.mirror(back_image)
        print("Reading image from \"%s_back.png\"" % name)

        back_image_red, back_image_green, back_image_blue, back_image_alpha = back_image.split()

        back_image_red = back_image_red.point(lambda i: 0 if i < 127 else 1)
        red_array = np.array(back_image_red)
        bmp_red = potrace.Bitmap(red_array)
        path_red = bmp_red.trace(alphamax = 0.0, opttolerance = 50)

        # Soldermask needs to be inverted
        back_image_green = ImageOps.invert(back_image_green)
        back_image_green = back_image_green.point(lambda i: 0 if i < 127 else 1)
        green_array = np.array(back_image_green)
        bmp_green = potrace.Bitmap(green_array)
        path_green = bmp_green.trace(alphamax = 0.0, opttolerance = 50)

        back_image_blue = back_image_blue.point(lambda i: 0 if i < 127 else 1)
        blue_array = np.array(back_image_blue)
        bmp_blue = potrace.Bitmap(blue_array)
        path_blue = bmp_blue.trace(alphamax = 0.0, opttolerance = 50)

        print("Generating B.Cu layer from back red channel")
        module += render_path_to_layer(path_red, "fp_poly", "B.Cu", scale_factor)
        print("Generating B.Mask layer from back green channel")
        module += render_path_to_layer(path_green, "fp_poly", "B.Mask", scale_factor)
        print("Generating B.SilkS layer from back blue channel")
        module += render_path_to_layer(path_blue, "fp_poly", "B.SilkS", scale_factor)
    except IOError:
        pass

    module += footer % {"name": name}
    return module, (w * 25.4 / scale_factor, h * 25.4 / scale_factor)


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: %s input_name dpi" % sys.argv[0])
        print("  input_name is added to \"_front.png\" (and \"_back.png\") ")
        print("  dpi is the dots per inch of the input file\"")
        sys.exit(1)

    input_name = sys.argv[1]
    dpi = int(sys.argv[2])

    module, size = conv_image_to_module(input_name, dpi)
    print("Output image size: %f x %f mm" % (size[0], size[1]))
    print("Writing module file to \"%s.kicad_mod\"" % input_name)
    fid = open("%s.kicad_mod" % input_name, "w")
    fid.write(module)
    fid.close()

if __name__ == "__main__":
    main()

