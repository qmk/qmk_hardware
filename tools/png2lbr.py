#!/usr/bin/env python
#
# png2lbr - converts one (or two) RGBA pngs to an Eagle .lbr file
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
header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="7.7.0">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.05" unitdist="inch" unit="mm" style="lines" multiple="1" display="yes" altdistance="0.025" altunitdist="inch" altunit="mm"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="yes" active="yes"/>
<layer number="2" name="Route2" color="1" fill="3" visible="yes" active="yes"/>
<layer number="3" name="Route3" color="4" fill="3" visible="yes" active="yes"/>
<layer number="4" name="Route4" color="1" fill="4" visible="yes" active="yes"/>
<layer number="5" name="Route5" color="4" fill="4" visible="yes" active="yes"/>
<layer number="6" name="Route6" color="1" fill="8" visible="yes" active="yes"/>
<layer number="7" name="Route7" color="4" fill="8" visible="yes" active="yes"/>
<layer number="8" name="Route8" color="1" fill="2" visible="yes" active="yes"/>
<layer number="9" name="Route9" color="4" fill="2" visible="yes" active="yes"/>
<layer number="10" name="Route10" color="1" fill="7" visible="yes" active="yes"/>
<layer number="11" name="Route11" color="4" fill="7" visible="yes" active="yes"/>
<layer number="12" name="Route12" color="1" fill="5" visible="yes" active="yes"/>
<layer number="13" name="Route13" color="4" fill="5" visible="yes" active="yes"/>
<layer number="14" name="Route14" color="1" fill="6" visible="yes" active="yes"/>
<layer number="15" name="Route15" color="4" fill="6" visible="yes" active="yes"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="yes" active="yes"/>
<layer number="17" name="Pads" color="2" fill="1" visible="yes" active="yes"/>
<layer number="18" name="Vias" color="2" fill="1" visible="yes" active="yes"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="yes" active="yes"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="yes" active="yes"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="yes" active="yes"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="yes" active="yes"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="yes" active="yes"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="yes" active="yes"/>
<layer number="25" name="tNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="26" name="bNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="27" name="tValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="28" name="bValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="29" name="tStop" color="7" fill="3" visible="yes" active="yes"/>
<layer number="30" name="bStop" color="7" fill="6" visible="yes" active="yes"/>
<layer number="31" name="tCream" color="7" fill="4" visible="yes" active="yes"/>
<layer number="32" name="bCream" color="7" fill="5" visible="yes" active="yes"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="yes" active="yes"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="yes" active="yes"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="yes" active="yes"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="yes" active="yes"/>
<layer number="37" name="tTest" color="7" fill="1" visible="yes" active="yes"/>
<layer number="38" name="bTest" color="7" fill="1" visible="yes" active="yes"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="yes" active="yes"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="yes" active="yes"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="yes" active="yes"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="yes" active="yes"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="yes" active="yes"/>
<layer number="44" name="Drills" color="7" fill="1" visible="yes" active="yes"/>
<layer number="45" name="Holes" color="7" fill="1" visible="yes" active="yes"/>
<layer number="46" name="Milling" color="3" fill="1" visible="yes" active="yes"/>
<layer number="47" name="Measures" color="7" fill="1" visible="yes" active="yes"/>
<layer number="48" name="Document" color="7" fill="1" visible="yes" active="yes"/>
<layer number="49" name="Reference" color="7" fill="1" visible="yes" active="yes"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="yes" active="yes"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="200" name="200bmp" color="1" fill="10" visible="yes" active="yes"/>
<layer number="201" name="201bmp" color="2" fill="10" visible="yes" active="yes"/>
</layers>
<library>
<packages>
<package name="%(name)s">"""

# Text for the file footer, the only parameter is the name of the module
footer = """
</package>
</packages>
<symbols>
<symbol name="%(name)s">
<text x="0" y="0" size="1.778" layer="94" align="center">%(name)s</text>
<wire x1="-12.7" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="-2.54" x2="-12.7" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-12.7" y1="-2.54" x2="-12.7" y2="2.54" width="0.254" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="%(name)s" prefix="%(name)s">
<gates>
<gate name="G$1" symbol="%(name)s" x="0" y="0"/>
</gates>
<devices>
<device name="" package="%(name)s">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</drawing>
</eagle>
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
        if fp_type == "poly":
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
        if fp_type == "poly":
            module += "\n  <polygon width=\"0.001\" layer=\"%s\">" % layer
            for point in poly:
                module += "\n    <vertex x=\"%f\" y=\"%f\" />" % (point[0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor)
            module += "\n    <vertex x=\"%f\" y=\"%f\" />" % (poly[0][0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor)

            module += "\n  </polygon>"
        else:
            i = 0
            poly.append(poly[len(poly)-1])
            for i, point in enumerate(poly):
                if i+2 < len(poly):
                    module += "  <wire x1=\"%f\" y1=\"%f\" x2=\"%f\" y2=\"%f\" width=\".001\" layer=\"%s\" />" % (point[0] * 25.4 / scale_factor, point[1] * 25.4 / scale_factor, poly[i+1][0] * 25.4 / scale_factor, poly[i+1][1] * 25.4 / scale_factor, layer)   

    return module

def conv_image_to_module(name, scale_factor):

    module = header % {"name": name.upper()}

    front_image = Image.open("%s_front.png" % name).transpose(Image.FLIP_TOP_BOTTOM) 
    print("Reading image from \"%s_front.png\"" % name)

    front_image_red, front_image_green, front_image_blue, front_image_alpha = front_image.split()

    # Soldermask needs to be inverted
    front_image_red = ImageOps.invert(front_image_red)
    front_image_red = Image.composite(front_image_red, front_image_alpha, front_image_alpha)
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

    # print("Generating Outline layer from front alpha channel")
    # module += render_path_to_layer(path_alpha, "line", "20", scale_factor)

    print("Generating tKeepout layer from front red channel")
    module += render_path_to_layer(path_red, "poly", "39", scale_factor)
    print("Generating tStop layer from front green channel")
    module += render_path_to_layer(path_green, "poly", "29", scale_factor)
    print("Generating tPlace layer from front blue channel")
    module += render_path_to_layer(path_blue, "poly", "21", scale_factor)

    try:
        back_image = Image.open("%s_back.png" % name).transpose(Image.FLIP_TOP_BOTTOM) 
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

        print("Generating bKeepout layer from back red channel")
        module += render_path_to_layer(path_red, "poly", "40", scale_factor)
        print("Generating bStop layer from back green channel")
        module += render_path_to_layer(path_green, "poly", "30", scale_factor)
        print("Generating bPlace layer from back blue channel")
        module += render_path_to_layer(path_blue, "poly", "22", scale_factor)
    except IOError:
        pass

    module += footer % {"name": name.upper()}
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
    print("Writing module file to \"%s.lbr\"" % input_name)
    fid = open("%s.lbr" % input_name, "w")  
    fid.write(module)
    fid.close()

if __name__ == "__main__":
    main()

