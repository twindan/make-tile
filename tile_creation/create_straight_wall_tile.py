""" Contains functions for creating wall tiles """
import os
from math import radians
import bpy
from mathutils import Vector
from .. lib.utils.collections import add_object_to_collection
from .. utils.registration import get_prefs
from .. lib.turtle.scripts.primitives import draw_cuboid
from .. lib.utils.utils import mode
from .. lib.utils.vertex_groups import cuboid_sides_to_vert_groups
from .. materials.materials import (
    assign_displacement_materials,
    assign_preview_materials)
from .. operators.trim_tile import (
    create_tile_trimmers)
from . create_displacement_mesh import create_displacement_object


def create_straight_wall(tile_name, tile_empty):
    """Returns a straight wall
    Keyword arguments:
    tile_empty -- EMPTY, empty which the tile is parented to. \
        Stores properties that relate to the entire tile
    """
    # hack to correct for parenting issues.
    # moves cursor to origin and creates objects
    # then moves base to cursor original location and resets cursor
    # TODO: get rid of hack and parent properly
    scene = bpy.context.scene
    cursor = scene.cursor
    cursor_orig_loc = cursor.location.copy()
    cursor.location = (0, 0, 0)
    tile_empty.location = (0, 0, 0)
    base_blueprint = scene.mt_base_blueprint
    main_part_blueprint = scene.mt_main_part_blueprint

    if base_blueprint == 'OPENLOCK':
        base_size = Vector((
            scene.mt_tile_x,
            0.5,
            0.2755))
        base = create_openlock_base(tile_name, base_size)

    if base_blueprint == 'PLAIN':
        base_size = Vector((
            scene.mt_base_x,
            scene.mt_base_y,
            scene.mt_base_z))

        base = create_plain_base(tile_name, base_size)

    if base_blueprint == 'NONE':
        base = bpy.data.objects.new(tile_name + '.base', None)
        base.mt_tile_properties.tile_size = (0, 0, 0)
        add_object_to_collection(base, tile_name)

    if main_part_blueprint == 'OPENLOCK':
        tile_size = Vector((
            scene.mt_tile_x,
            0.3149,
            scene.mt_tile_z))

        create_openlock_cores(base, tile_size, tile_name)

    if main_part_blueprint == 'PLAIN':
        tile_size = Vector((
            scene.mt_tile_x,
            scene.mt_tile_y,
            scene.mt_tile_z))

        preview_core, displacement_core = create_cores(base, tile_size, tile_name)
        displacement_core.hide_viewport = True

    # create tile trimmers. Used to ensure that displaced
    # textures don't extend beyond the original bounds of the tile.
    # Used by voxeliser and exporter

    # tile_properties['trimmers'] = create_tile_trimmers(tile_properties)

    base.parent = tile_empty

    tile_empty.location = cursor_orig_loc
    cursor.location = cursor_orig_loc


#####################################
#              BASE                 #
#####################################

def create_plain_base(tile_name, base_size):
    """Returns a base for a wall tile
    """
    cursor = bpy.context.scene.cursor
    cursor_orig_loc = cursor.location.copy()

    # make base
    base = draw_cuboid(base_size)
    base.name = tile_name + '.base'
    add_object_to_collection(base, tile_name)

    # reposition base and set origin
    base.location = (
        cursor_orig_loc[0] - base_size[0] / 2,
        cursor_orig_loc[1] - base_size[1] / 2,
        cursor_orig_loc[2])

    ctx = {
        'object': base,
        'active_object': base,
        'selected_objects': [base]
    }
    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')

    # Store tile properties on base
    tile_properties = base.mt_tile_properties
    tile_properties.is_mt_object = True
    tile_properties.tile_name = tile_name
    tile_properties.base_size = base_size
    tile_properties.geometry_type = 'BASE'

    return base


def create_openlock_base(tile_name, base_size):
    """takes a straight wall base and makes it into an openlock style base"""
    # make base
    base = create_plain_base(tile_name, base_size)

    slot_cutter = create_openlock_base_slot_cutter(base, offset=0.018)
    #slot_cutter.hide_viewport = True

    if base.dimensions[0] >= 1:
        clip_cutter = create_openlock_base_clip_cutter(base)
        clip_boolean = base.modifiers.new(clip_cutter.name, 'BOOLEAN')
        clip_boolean.operation = 'DIFFERENCE'
        clip_boolean.object = clip_cutter
        clip_cutter.parent = base
        clip_cutter.display_type = 'BOUNDS'
        clip_cutter.hide_viewport = True

    return base


def create_openlock_base_slot_cutter(base, offset=0.18):
    """Makes a cutter for the openlock base slot
    based on the width of the base

    Keyword arguments:
    base -- OBJ, base the cutter will be used on
    """
    cursor = bpy.context.scene.cursor
    tile_properties = base.mt_tile_properties

    # get original location of object and cursor
    base_location = base.location.copy()
    cursor_original_location = cursor.location.copy()

    # work out bool size X from base size, y and z are constants
    bool_size = [
        tile_properties.base_size[0] - (0.236 * 2),
        0.197,
        0.25]

    cutter = draw_cuboid(bool_size)
    cutter.name = tile_properties.tile_name + ".slot_cutter"

    cutter.location = (
        base_location[0] - bool_size[0] / 2,
        base_location[1] - offset,
        base_location[2] - 0.001)

    ctx = {
        'object': cutter,
        'active_object': cutter,
        'selected_objects': [cutter]
    }

    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')

    slot_boolean = base.modifiers.new(cutter.name, 'BOOLEAN')
    slot_boolean.operation = 'DIFFERENCE'
    slot_boolean.object = cutter
    cutter.parent = base
    cutter.display_type = 'BOUNDS'
    cutter.mt_tile_properties.geometry_type = 'CUTTER'

    return cutter


def create_openlock_base_clip_cutter(base):
    """Makes a cutter for the openlock base clip based
    on the width of the base and positions it correctly

    Keyword arguments:
    base -- bpy.types.Object, base the cutter will be used on
    tile_properties -- DICT
    """

    mode('OBJECT')
    tile_properties = base.mt_tile_properties

    # get original location of cursor
    cursor_original_location = bpy.context.scene.cursor.location.copy()
    base_location = base.location.copy()
    # Get cutter
    preferences = get_prefs()
    booleans_path = os.path.join(preferences.assets_path, "meshes", "booleans", "openlock.blend")

    # load base cutters
    with bpy.data.libraries.load(booleans_path) as (data_from, data_to):
        data_to.objects = ['openlock.wall.base.cutter.clip', 'openlock.wall.base.cutter.clip.cap.start', 'openlock.wall.base.cutter.clip.cap.end']

    for obj in data_to.objects:
        add_object_to_collection(obj, tile_properties.tile_name)

    clip_cutter = data_to.objects[0]
    cutter_start_cap = data_to.objects[1]
    cutter_end_cap = data_to.objects[2]

    cutter_start_cap.hide_viewport = True
    cutter_end_cap.hide_viewport = True

    clip_cutter.location = Vector((
        base_location[0] - (tile_properties.base_size[0] / 2) + 0.5,
        base_location[1] - (tile_properties.base_size[1] / 2) + 0.25,
        base_location[2]))

    array_mod = clip_cutter.modifiers.new('Array', 'ARRAY')
    array_mod.start_cap = cutter_start_cap
    array_mod.end_cap = cutter_end_cap
    array_mod.use_merge_vertices = True

    array_mod.fit_type = 'FIT_LENGTH'
    array_mod.fit_length = tile_properties.base_size[0] - 1

    return clip_cutter


#####################################
#              CORE                 #
#####################################
def create_cores(base, tile_size, tile_name):
    '''Creates the preview and displacement cores'''
    scene = bpy.context.scene

    preview_core = create_core(tile_size, base.mt_tile_properties.base_size, tile_name)
    preview_core, displacement_core = create_displacement_object(preview_core)

    preview_core.parent = base
    displacement_core.parent = base

    preferences = get_prefs()

    primary_material = bpy.data.materials[scene.mt_tile_material_1]
    secondary_material = bpy.data.materials[preferences.secondary_material]

    image_size = bpy.context.scene.mt_tile_resolution

    textured_vertex_groups = ['Front', 'Back', 'Top']
    assign_displacement_materials(displacement_core, [image_size, image_size], primary_material, secondary_material)
    assign_preview_materials(preview_core, primary_material, secondary_material, textured_vertex_groups)

    displacement_core.hide_viewport = True

    preview_core.mt_tile_properties.geometry_type = 'PREVIEW'
    displacement_core.mt_tile_properties.geometry_type = 'DISPLACEMENT'

    return preview_core, displacement_core


def create_core(tile_size, base_size, tile_name):
    '''Returns the core (vertical) part of a wall tile
    '''
    cursor = bpy.context.scene.cursor
    cursor_start_loc = cursor.location.copy()

    # make our core
    core = draw_cuboid([
        tile_size[0],
        tile_size[1],
        tile_size[2] - base_size[2]])

    core.name = tile_name + '.core'
    add_object_to_collection(core, tile_name)
    mode('OBJECT')

    # move core so centred, move up so on top of base and set origin to world origin
    core.location = (
        cursor_start_loc[0] - tile_size[0] / 2,
        cursor_start_loc[1] - tile_size[1] / 2,
        cursor_start_loc[2] + base_size[2])

    ctx = {
        'object': core,
        'active_object': core,
        'selected_objects': [core]
    }

    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.uv.smart_project(ctx)

    cuboid_sides_to_vert_groups(core)

    tile_props = core.mt_tile_properties
    tile_props.is_mt_object = True
    tile_props.tile_name = tile_name
    tile_props.tile_size = tile_size
    tile_props.base_size = base_size

    return core


def create_openlock_cores(base, tile_size, tile_name):
    '''Creates the preview and displacement cores and adds side cutters for
    openLOCK clips'''
    preview_core, displacement_core = create_cores(base, tile_size, tile_name)

    wall_cutters = create_openlock_wall_cutters(preview_core)
    cores = [preview_core, displacement_core]

    for wall_cutter in wall_cutters:
        wall_cutter.parent = base
        wall_cutter.display_type = 'BOUNDS'
        wall_cutter.hide_viewport = True

        for core in cores:
            wall_cutter_bool = core.modifiers.new(wall_cutter.name + '.bool', 'BOOLEAN')
            wall_cutter_bool.operation = 'DIFFERENCE'
            wall_cutter_bool.object = wall_cutter

            # add cutters to object's mt_cutters_collection
            # so we can activate and deactivate them when necessary
            item = core.mt_tile_properties.cutters_collection.add()
            item.name = wall_cutter.name
            item.value = True
            item.parent = core.name


def create_openlock_wall_cutters(core):
    """Creates the cutters for the wall and positions them correctly

    Keyword arguments:
    core -- OBJ, wall core object
    """
    preferences = get_prefs()
    tile_properties = core.mt_tile_properties
    tile_name = tile_properties.tile_name
    tile_size = tile_properties.tile_size

    booleans_path = os.path.join(preferences.assets_path, "meshes", "booleans", "openlock.blend")

    # load side cutter
    with bpy.data.libraries.load(booleans_path) as (data_from, data_to):
        data_to.objects = ['openlock.wall.cutter.side']

    core_location = core.location.copy()

    cutters = []
    # left side cutters
    left_cutter_bottom = data_to.objects[0].copy()
    add_object_to_collection(left_cutter_bottom, tile_name)
    # get location of bottom front left corner of tile
    front_left = [
        core_location[0] - (tile_size[0] / 2),
        core_location[1] - (tile_size[1] / 2),
        core_location[2]]
    # move cutter to bottom front left corner then up by 0.63 inches
    left_cutter_bottom.location = [
        front_left[0],
        front_left[1] + (tile_size[1] / 2),
        front_left[2] + 0.63]

    array_mod = left_cutter_bottom.modifiers.new('Array', 'ARRAY')
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace[2] = 2
    array_mod.fit_type = 'FIT_LENGTH'
    array_mod.fit_length = tile_size[2] - 1

    # make a copy of left cutter bottom
    left_cutter_top = left_cutter_bottom.copy()

    add_object_to_collection(left_cutter_top, tile_name)

    # move cutter up by 0.75 inches
    left_cutter_top.location[2] = left_cutter_top.location[2] + 0.75

    array_mod = left_cutter_top.modifiers[array_mod.name]
    array_mod.fit_length = tile_size[2] - 1.8

    cutters.extend([left_cutter_bottom, left_cutter_top])

    # right side cutters

    right_cutter_bottom = data_to.objects[0].copy()
    add_object_to_collection(right_cutter_bottom, tile_name)
    # get location of bottom front right corner of tile
    front_right = [
        core_location[0] + (tile_size[0] / 2),
        core_location[1] - (tile_size[1] / 2),
        core_location[2]]
    # move cutter to bottom front left corner then up by 0.63 inches
    right_cutter_bottom.location = [
        front_right[0],
        front_right[1] + (tile_size[1] / 2),
        front_right[2] + 0.63]
    # rotate cutter 180 degrees around Z
    right_cutter_bottom.rotation_euler[2] = radians(180)

    array_mod = right_cutter_bottom.modifiers.new('Array', 'ARRAY')
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace[2] = 2
    array_mod.fit_type = 'FIT_LENGTH'
    array_mod.fit_length = tile_size[2] - 1

    right_cutter_top = right_cutter_bottom.copy()
    add_object_to_collection(right_cutter_top, tile_name)
    right_cutter_top.location[2] = right_cutter_top.location[2] + 0.75

    array_mod = right_cutter_top.modifiers["Array"]
    array_mod.fit_length = tile_size[2] - 1.8

    cutters.extend([right_cutter_bottom, right_cutter_top])

    return cutters
