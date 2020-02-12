import bpy
from bpy.app.handlers import persistent


@persistent
def update_mt_scene_props_handler(dummy):
    scene_props = bpy.context.scene.mt_scene_props
    obj = bpy.context.object

    if obj is not None and obj != scene_props.mt_last_selected and obj.mt_object_props.is_mt_object is True and obj in bpy.context.selected_objects:
        obj_props = obj.mt_object_props
        tile_name = obj_props.tile_name
        tile_props = bpy.data.collections[tile_name].mt_tile_props

        scene_props.mt_last_selected = obj

        scene_props.mt_tile_name = tile_props.tile_name
        scene_props.mt_tile_blueprint = tile_props.tile_blueprint
        scene_props.mt_main_part_blueprint = tile_props.main_part_blueprint
        scene_props.mt_tile_type = tile_props.tile_type
        scene_props.mt_base_blueprint = tile_props.base_blueprint

        scene_props.mt_tile_x = tile_props.tile_size[0]
        scene_props.mt_tile_y = tile_props.tile_size[1]
        scene_props.mt_tile_z = tile_props.tile_size[2]

        scene_props.mt_base_x = tile_props.base_size[0]
        scene_props.mt_base_y = tile_props.base_size[1]
        scene_props.mt_base_z = tile_props.base_size[2]

        scene_props.mt_angle = tile_props.angle
        scene_props.mt_leg_1_len = tile_props.leg_1_len
        scene_props.mt_leg_2_len = tile_props.leg_2_len
        scene_props.mt_base_socket_side = tile_props.base_socket_side
        scene_props.mt_base_radius = tile_props.base_radius
        scene_props.mt_wall_radius = tile_props.wall_radius
        scene_props.mt_curve_type = tile_props.curve_type
        scene_props.mt_degrees_of_arc = tile_props.degrees_of_arc
        scene_props.mt_segments = tile_props.segments


bpy.app.handlers.depsgraph_update_post.append(update_mt_scene_props_handler)