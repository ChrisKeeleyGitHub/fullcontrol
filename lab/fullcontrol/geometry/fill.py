from fullcontrol import Point, polar_to_point, point_to_polar, BoundingBox, Vector, move, travel_to
from lab.fullcontrol.geometry.convex import convex_pathsXY


# necessary functions
def create_solid_layer(outline: list, extrusion_width: float, z_height: float, ref_midpoint: Point | None = None):
    ''' create a solid layer by offsetting the outline inwards by 0.25*extrusion_width, then
    using the convex function to find a streamline filling path. The solid fill is then returned
    (not including the original outline). Note that the convex function treats the outline as the
    external boundary of the solid fill, so it offsets the outline inwards by 0.5*extrusion_width.
    To get the first line of the solid fill to be extrusion_width away from the outline, the outline
    should be offset by 0.5*extrusion_width, to represent the external boundary of the solid fill
    (internal boundary of the shell). Here, the boundary is only offset by 0.25*extrusion_width to
    ensure a good connection to the shell. Optionally supply ref_midpoint to avoid recalculating the
    midpoint when generating multiple layers.
    '''
    if ref_midpoint is None:
        bounds = BoundingBox()
        bounds.calc_bounds(outline)
        mid_point = Point(x=bounds.midx, y=bounds.midy, z=z_height)
    else:
        mid_point = Point(x=ref_midpoint.x, y=ref_midpoint.y, z=z_height)
    point_count = 0
    offset_outline = []
    max_rad = 0
    for step in outline:
        if isinstance(step, Point):
            polar_data = point_to_polar(step, mid_point)
            offset_outline.append(polar_to_point(
                mid_point, polar_data.radius-0.25*extrusion_width, polar_data.angle))
            point_count += 1
            max_rad = max(max_rad, polar_data.radius-0.25*extrusion_width)
    solid_fill = convex_pathsXY(offset_outline, [mid_point]*point_count, int(max_rad/extrusion_width), travel=False, overextrusion_percent=5)
    return solid_fill


def fill_base_simple(steps: list, segments_per_layer: int, solid_layers: int, extrusion_width: float):
    ''' take a vase_mode list of steps, calculate a convex fill for the first layer, which is 
    identified based on the first (segments_per_layer+1) points. Then, for each layer, for 
    the required number of solid layers, print the first layer's solid fill (outwards-in) using the 
    convex function, then travel back to the last point of the layer. The first layer is copied because
    the convex function is computationally demanding, which is fine for parts where the first few layers
    are similar. If the outline is changing a lot over the first few layers, use fill_base_full instead, 
    which finds the outline for each solid layer and used that to create the solid fill using the convex 
    function for each new outline.
    '''
    first_layer_points = steps[:segments_per_layer+1]
    solid_layer = create_solid_layer(first_layer_points, extrusion_width, 0)
    new_steps = []
    for i in range(len(steps)):
        t_val = i/segments_per_layer  # tval = 0 to layers
        if t_val > 0 and i % segments_per_layer == 0 and t_val <= solid_layers:
            last_point = new_steps[-1]
            new_steps.extend(move(solid_layer, Vector(z=last_point.z)))
            new_steps.extend(travel_to(last_point))
        new_steps.append(steps[i])
    return new_steps


def fill_base_full(steps: list, segments_per_layer: int, solid_layers: int, extrusion_width: float, ref_midpoint: Point | None = None):
    '''see fill_base_simple for an explanation of how this work. Optionally supply
    ref_midpoint to force the same midpoint to be used for all layers, ensuring
    aligned fill patterns when multiple solid layers are added. If not supplied,
    the midpoint from the first solid layer is reused.'''
    new_steps = []
    midpoint = ref_midpoint
    for i in range(len(steps)):
        t_val = i/segments_per_layer  # tval = 0 to layers
        if t_val > 0 and i % segments_per_layer == 0 and t_val <= solid_layers:
            current_layer_outline = steps[i-segments_per_layer:i]
            if midpoint is None:
                bounds = BoundingBox()
                bounds.calc_bounds(current_layer_outline)
                midpoint = Point(x=bounds.midx, y=bounds.midy, z=0)
            solid_layer = create_solid_layer(
                current_layer_outline, extrusion_width, 0, ref_midpoint=midpoint)
            last_point = new_steps[-1]
            new_steps.extend(move(solid_layer, Vector(z=last_point.z)))
            new_steps.extend(travel_to(last_point))
        new_steps.append(steps[i])
    return new_steps
