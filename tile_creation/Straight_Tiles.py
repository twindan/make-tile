import os
from math import radians
from mathutils import Vector
import bpy

from bpy.types import Operator, Panel
from .. utils.registration import get_prefs
from .. lib.utils.collections import (
    add_object_to_collection,
    create_collection,
    activate_collection)
from .. lib.turtle.scripts.primitives import draw_cuboid
from .. lib.turtle.scripts.straight_tile import draw_straight_wall_core
from .. lib.utils.utils import mode, get_all_subclasses
from .. lib.utils.selection import deselect_all, select_by_loc
from ..operators.maketile import (
    MT_Tile_Generator,
    initialise_tile_creator,
    create_common_tile_props)
from .create_tile import (
    finalise_tile,
    spawn_empty_base,
    create_displacement_core,
    spawn_prefab)
from .Rectangular_Tiles import create_plain_rect_floor_cores as create_plain_floor_cores

class MT_PT_Straight_Wall_Panel(Panel):
    """Draw a tile options panel in UI."""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Make Tile"
    bl_label = "Tile Options"
    bl_order = 2
    bl_idname = "MT_PT_Straight_Wall_Panel"
    bl_description = "Options to configure the dimensions of a tile"

    @classmethod
    def poll(cls, context):
        """Check tile_type_new."""
        if hasattr(context.scene, 'mt_scene_props'):
            return context.scene.mt_scene_props.tile_type_new in ["object.make_straight_wall", "object.make_straight_floor"]
        return False

    def draw(self, context):
        """Draw the Panel."""
        scene = context.scene
        scene_props = scene.mt_scene_props
        layout = self.layout

        layout.label(text="Blueprints")
        layout.prop(scene_props, 'base_blueprint')
        layout.prop(scene_props, 'main_part_blueprint')

        layout.label(text="Tile Size")
        row = layout.row()
        row.prop(scene_props, 'tile_x')
        row.prop(scene_props, 'tile_y')
        row.prop(scene_props, 'tile_z')

        layout.label(text="Lock Proportions")
        row = layout.row()
        row.prop(scene_props, 'x_proportionate_scale')
        row.prop(scene_props, 'y_proportionate_scale')
        row.prop(scene_props, 'z_proportionate_scale')

        layout.label(text="Base Size")
        row = layout.row()
        row.prop(scene_props, 'base_x')
        row.prop(scene_props, 'base_y')
        row.prop(scene_props, 'base_z')

        layout.operator('scene.reset_tile_defaults')


class MT_OT_Make_Openlock_Straight_Base(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an OpenLOCK straight base."""

    bl_idname = "object.make_openlock_straight_base"
    bl_label = "Straight Base"
    bl_options = {'INTERNAL'}
    mt_blueprint = "OPENLOCK"
    mt_type = "STRAIGHT_BASE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        spawn_openlock_base(tile_props)
        return{'FINISHED'}


class MT_OT_Make_Plain_Straight_Base(MT_Tile_Generator, Operator):
    """Internal Operator. Generate a plain straight base."""

    bl_idname = "object.make_plain_straight_base"
    bl_label = "Straight Base"
    bl_options = {'INTERNAL'}
    mt_blueprint = "PLAIN"
    mt_type = "STRAIGHT_BASE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        spawn_plain_base(tile_props)
        return{'FINISHED'}


class MT_OT_Make_Empty_Straight_Base(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an empty straight base."""

    bl_idname = "object.make_empty_straight_base"
    bl_label = "Straight Base"
    bl_options = {'INTERNAL'}
    mt_blueprint = "NONE"
    mt_type = "STRAIGHT_BASE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        spawn_empty_base(tile_props)
        return{'FINISHED'}


class MT_OT_Make_Plain_Straight_Wall_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate a plain straight wall core."""

    bl_idname = "object.make_plain_straight_wall_core"
    bl_label = "Straight Wall Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "PLAIN"
    mt_type = "STRAIGHT_WALL_CORE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        base = context.active_object
        create_plain_wall_cores(base, tile_props)
        return{'FINISHED'}


class MT_OT_Make_Openlock_Straight_Wall_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an openlock straight wall core."""

    bl_idname = "object.make_openlock_straight_wall_core"
    bl_label = "Straight Wall Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "OPENLOCK"
    mt_type = "STRAIGHT_WALL_CORE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        base = context.active_object
        create_openlock_wall_cores(base, tile_props)
        return{'FINISHED'}


class MT_OT_Make_Empty_Straight_Wall_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an empty straight wall core."""

    bl_idname = "object.make_empty_straight_wall_core"
    bl_label = "Straight Wall Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "NONE"
    mt_type = "STRAIGHT_WALL_CORE"

    def execute(self, context):
        """Execute the operator."""
        return {'PASS_THROUGH'}


class MT_OT_Make_Plain_Straight_Floor_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate a plain straight floor core."""

    bl_idname = "object.make_plain_straight_floor_core"
    bl_label = "Straight Floor Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "PLAIN"
    mt_type = "STRAIGHT_FLOOR_CORE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        base = context.active_object
        create_plain_floor_cores(base, tile_props)
        return{'FINISHED'}


class MT_OT_Make_Openlock_Straight_Floor_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an openlock straight floor core."""

    bl_idname = "object.make_openlock_straight_floor_core"
    bl_label = "Straight Floor Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "OPENLOCK"
    mt_type = "STRAIGHT_FLOOR_CORE"

    def execute(self, context):
        """Execute the operator."""
        tile = context.collection
        tile_props = tile.mt_tile_props
        base = context.active_object
        create_plain_floor_cores(base, tile_props)
        return{'FINISHED'}


class MT_OT_Make_Empty_Straight_Floor_Core(MT_Tile_Generator, Operator):
    """Internal Operator. Generate an empty straight wall core."""

    bl_idname = "object.make_empty_straight_floor_core"
    bl_label = "Straight Floor Core"
    bl_options = {'INTERNAL'}
    mt_blueprint = "NONE"
    mt_type = "STRAIGHT_FLOOR_CORE"

    def execute(self, context):
        """Execute the operator."""
        return {'PASS_THROUGH'}


class MT_OT_Make_Straight_Wall_Tile(MT_Tile_Generator, Operator):
    """Operator. Generates a straight wall tile with a customisable base and main part."""

    bl_idname = "object.make_straight_wall"
    bl_label = "Straight Wall"
    bl_options = {'UNDO'}
    mt_blueprint = "CUSTOM"
    mt_type = "STRAIGHT_WALL"

    def execute(self, context):
        """Execute the operator."""
        scene = context.scene
        scene_props = scene.mt_scene_props
        base_blueprint = scene_props.base_blueprint
        core_blueprint = scene_props.main_part_blueprint
        base_type = 'STRAIGHT_BASE'
        core_type = 'STRAIGHT_WALL_CORE'

        subclasses = get_all_subclasses(MT_Tile_Generator)

        original_renderer, cursor_orig_loc, cursor_orig_rot = initialise_wall_creator(context, scene_props)

        base = spawn_prefab(context, subclasses, base_blueprint, base_type)

        if core_blueprint == 'NONE':
            preview_core = None
        else:
            preview_core = spawn_prefab(context, subclasses, core_blueprint, core_type)

        finalise_tile(base, preview_core, cursor_orig_loc, cursor_orig_rot)

        scene.render.engine = original_renderer

        return {'FINISHED'}


class MT_OT_Make_Straight_Floor_Tile(MT_Tile_Generator, Operator):
    """Operator. Generates a straight wall tile with a customisable base and main part."""

    bl_idname = "object.make_straight_floor"
    bl_label = "Straight Floor"
    bl_options = {'UNDO'}
    mt_blueprint = "CUSTOM"
    mt_type = "STRAIGHT_FLOOR"

    def execute(self, context):
        """Execute the operator."""
        scene = context.scene
        scene_props = scene.mt_scene_props
        base_blueprint = scene_props.base_blueprint
        core_blueprint = scene_props.main_part_blueprint
        base_type = 'STRAIGHT_BASE'
        core_type = 'STRAIGHT_FLOOR_CORE'
        subclasses = get_all_subclasses(MT_Tile_Generator)

        original_renderer, cursor_orig_loc, cursor_orig_rot = initialise_floor_creator(context, scene_props)
        base = spawn_prefab(context, subclasses, base_blueprint, base_type)

        if core_blueprint == 'NONE':
            preview_core = None
        else:
            preview_core = spawn_prefab(context, subclasses, core_blueprint, core_type)

        finalise_tile(base, preview_core, cursor_orig_loc, cursor_orig_rot)

        scene.render.engine = original_renderer

        return {'FINISHED'}


def initialise_wall_creator(context, scene_props):
    """Initialise the wall creator and set common properties.

    Args:
        context (bpy.context): context
        scene_props (bpy.types.PropertyGroup.mt_scene_props): maketile scene properties

    Returns:
        enum: enum in {'BLENDER_EEVEE', 'CYCLES', 'WORKBENCH'}
        list[3]: cursor original location
        list[3]: cursor original rotation

    """
    original_renderer, tile_name, tiles_collection, cursor_orig_loc, cursor_orig_rot = initialise_tile_creator(context)
    # We store tile properties in the mt_tile_props property group of
    # the collection so we can access them from any object in this
    # collection.
    create_collection('Walls', tiles_collection)
    tile_collection = bpy.data.collections.new(tile_name)
    bpy.data.collections['Walls'].children.link(tile_collection)
    activate_collection(tile_collection.name)

    tile_props = tile_collection.mt_tile_props
    create_common_tile_props(scene_props, tile_props, tile_collection)

    tile_props.tile_type = 'STRAIGHT_WALL'
    tile_props.tile_size = (scene_props.tile_x, scene_props.tile_y, scene_props.tile_z)
    tile_props.base_size = (scene_props.base_x, scene_props.base_y, scene_props.base_z)

    tile_props.x_native_subdivisions = scene_props.x_native_subdivisions
    tile_props.y_native_subdivisions = scene_props.y_native_subdivisions
    tile_props.z_native_subdivisions = scene_props.z_native_subdivisions

    return original_renderer, cursor_orig_loc, cursor_orig_rot


def initialise_floor_creator(context, scene_props):
    """Initialise the floor creator and set common properties.

    Args:
        context (bpy.context): context
        scene_props (bpy.types.PropertyGroup.mt_scene_props): maketile scene properties

    Returns:
        enum: enum in {'BLENDER_EEVEE', 'CYCLES', 'WORKBENCH'}
        list[3]: cursor original location
        list[3]: cursor original rotation

    """
    original_renderer, tile_name, tiles_collection, cursor_orig_loc, cursor_orig_rot = initialise_tile_creator(context)
    # We store tile properties in the mt_tile_props property group of
    # the collection so we can access them from any object in this
    # collection.
    create_collection('Floors', tiles_collection)
    tile_collection = bpy.data.collections.new(tile_name)
    bpy.data.collections['Floors'].children.link(tile_collection)
    activate_collection(tile_collection.name)

    tile_props = tile_collection.mt_tile_props
    create_common_tile_props(scene_props, tile_props, tile_collection)

    tile_props.tile_type = 'STRAIGHT_FLOOR'
    tile_props.tile_size = (scene_props.tile_x, scene_props.tile_y, scene_props.tile_z)
    tile_props.base_size = (scene_props.base_x, scene_props.base_y, scene_props.base_z)

    tile_props.x_native_subdivisions = scene_props.x_native_subdivisions
    tile_props.y_native_subdivisions = scene_props.y_native_subdivisions
    tile_props.z_native_subdivisions = scene_props.z_native_subdivisions

    return original_renderer, cursor_orig_loc, cursor_orig_rot


def spawn_plain_base(tile_props):
    """Spawn a plain base into the scene.

    Args:
        tile_props (bpy.types.PropertyGroup.mt_tile_props): tile properties

    Returns:
        bpy.types.Object: tile base
    """
    base_size = tile_props.base_size
    tile_name = tile_props.tile_name

    # make base
    base = draw_cuboid(base_size)
    base.name = tile_name + '.base'
    add_object_to_collection(base, tile_name)

    ctx = {
        'object': base,
        'active_object': base,
        'selected_objects': [base]
    }

    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')

    obj_props = base.mt_object_props
    obj_props.is_mt_object = True
    obj_props.geometry_type = 'BASE'
    obj_props.tile_name = tile_name
    bpy.context.view_layer.objects.active = base

    return base


def spawn_openlock_base(tile_props):
    """Spawn an openlock base into the scene.

    Args:
        tile_props (bpy.types.PropertyGroup.mt_tile_props): tile properties

    Returns:
        bpy.types.Object: tile base
    """

    # make base
    base = spawn_plain_base(tile_props)

    # create the slot cutter in the bottom of the base used for stacking tiles
    slot_cutter = create_openlock_base_slot_cutter(base, tile_props, offset=0.236)
    slot_cutter.hide_viewport = True

    # create the clip cutters used for attaching walls to bases
    if base.dimensions[0] >= 1:
        clip_cutter = create_openlock_base_clip_cutter(base, tile_props)
        clip_boolean = base.modifiers.new(clip_cutter.name, 'BOOLEAN')
        clip_boolean.operation = 'DIFFERENCE'
        clip_boolean.object = clip_cutter
        clip_cutter.parent = base
        clip_cutter.display_type = 'BOUNDS'
        clip_cutter.hide_viewport = True
    bpy.context.view_layer.objects.active = base

    return base


def create_openlock_base_slot_cutter(base, tile_props, offset=0.236):
    """Makes a cutter for the openlock base slot
    based on the width of the base
    """
    # get original location of object and cursor
    base_location = base.location.copy()
    base_size = tile_props.base_size

    # work out bool size X from base size, y and z are constants.
    # Correct for negative base dimensions when making curved walls
    if base_size[0] > 0:
        bool_size = [
            base_size[0] - (0.236 * 2),
            0.197,
            0.25]
    else:
        bool_size = [
            base_size[0] + (0.236 * 2),
            0.197,
            0.25]

    cutter = draw_cuboid(bool_size)
    cutter.name = tile_props.tile_name + ".slot_cutter"

    diff = base_size[0] - bool_size[0]

    cutter.location = (
        base_location[0] + diff / 2,
        base_location[1] + offset,
        base_location[2] - 0.001)

    ctx = {
        'object': cutter,
        'active_object': cutter,
        'selected_objects': [cutter]
    }

    base.select_set(False)
    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')

    slot_boolean = base.modifiers.new(cutter.name, 'BOOLEAN')
    slot_boolean.operation = 'DIFFERENCE'
    slot_boolean.object = cutter
    cutter.parent = base
    cutter.display_type = 'BOUNDS'
    cutter.hide_viewport = True

    cutter.mt_object_props.is_mt_object = True
    cutter.mt_object_props.geometry_type = 'CUTTER'
    cutter.mt_object_props.tile_name = tile_props.tile_name

    return cutter


def create_openlock_base_clip_cutter(base, tile_props):
    """Makes a cutter for the openlock base clip based
    on the width of the base and positions it correctly
    """

    mode('OBJECT')

    # get original location of cursor
    base_location = base.location.copy()

    # Get cutter
    preferences = get_prefs()
    booleans_path = os.path.join(
        preferences.assets_path,
        "meshes",
        "booleans",
        "openlock.blend")

    # load base cutters
    with bpy.data.libraries.load(booleans_path) as (data_from, data_to):
        data_to.objects = [
            'openlock.wall.base.cutter.clip',
            'openlock.wall.base.cutter.clip.cap.start',
            'openlock.wall.base.cutter.clip.cap.end']

    for obj in data_to.objects:
        add_object_to_collection(obj, tile_props.tile_name)

    clip_cutter = data_to.objects[0]
    cutter_start_cap = data_to.objects[1]
    cutter_end_cap = data_to.objects[2]

    cutter_start_cap.hide_viewport = True
    cutter_end_cap.hide_viewport = True

    clip_cutter.location = Vector((
        base_location[0] + 0.5,
        base_location[1] + 0.25,
        base_location[2]))

    array_mod = clip_cutter.modifiers.new('Array', 'ARRAY')
    array_mod.start_cap = cutter_start_cap
    array_mod.end_cap = cutter_end_cap
    array_mod.use_merge_vertices = True

    array_mod.fit_type = 'FIT_LENGTH'
    array_mod.fit_length = tile_props.base_size[0] - 1

    obj_props = clip_cutter.mt_object_props
    obj_props.is_mt_object = True
    obj_props.tile_name = tile_props.tile_name
    obj_props.geometry_type = 'CUTTER'

    return clip_cutter


def straight_wall_to_vert_groups(obj):
    """Make a vertex group for each side of wall.

    Corrects for displacement map distortion

    """
    mode('OBJECT')
    dim = obj.dimensions / 2

    # get original location of object origin and of cursor
    obj_original_loc = obj.location.copy()
    cursor_original_loc = bpy.context.scene.cursor.location.copy()

    # set origin to center of bounds
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # make vertex groups
    obj.vertex_groups.new(name='Left')
    obj.vertex_groups.new(name='Right')
    obj.vertex_groups.new(name='Front')
    obj.vertex_groups.new(name='Back')
    obj.vertex_groups.new(name='Top')
    obj.vertex_groups.new(name='Bottom')

    mode('EDIT')

    # select X- and assign to X-
    select_by_loc(
        lbound=[-dim[0] - 0.01, -dim[1], -dim[2] + 0.001],
        ubound=[-dim[0] + 0.01, dim[1], dim[2] - 0.001],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)

    bpy.ops.object.vertex_group_set_active(group='Left')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    # select X+ and assign to X+
    select_by_loc(
        lbound=[dim[0] - 0.01, -dim[1], -dim[2] + 0.001],
        ubound=[dim[0] + 0.01, dim[1], dim[2] - 0.001],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)
    bpy.ops.object.vertex_group_set_active(group='Right')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    # select Y- and assign to Y-
    select_by_loc(
        lbound=[-dim[0] + 0.001, -dim[1], -dim[2] + 0.001],
        ubound=[dim[0] - 0.001, -dim[1], dim[2] - 0.001],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)
    bpy.ops.object.vertex_group_set_active(group='Front')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    # select Y+ and assign to Y+
    select_by_loc(
        lbound=[-dim[0] + 0.001, dim[1], -dim[2] + 0.001],
        ubound=[dim[0] - 0.001, dim[1], dim[2] - 0.001],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)
    bpy.ops.object.vertex_group_set_active(group='Back')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    # select Z- and assign to Z-
    select_by_loc(
        lbound=[-dim[0] + 0.001, -dim[1], -dim[2]],
        ubound=[dim[0] - 0.001, dim[1], -dim[2] + 0.01],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)
    bpy.ops.object.vertex_group_set_active(group='Bottom')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    # select Z+ and assign to Z+
    select_by_loc(
        lbound=[-dim[0] + 0.001, -dim[1], dim[2] - 0.012],
        ubound=[dim[0] - 0.001, dim[1], dim[2]],
        select_mode='VERT',
        coords='LOCAL',
        buffer=0.0001,
        additive=True)
    bpy.ops.object.vertex_group_set_active(group='Top')
    bpy.ops.object.vertex_group_assign()

    deselect_all()

    mode('OBJECT')

    # reset cursor and object origin
    bpy.context.scene.cursor.location = obj_original_loc
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = cursor_original_loc


def create_plain_wall_cores(base, tile_props):
    """Create preview and displacement cores.

    Args:
        base (bpy.types.Object): tile base
        tile_props (bpy.types.PropertyGroup.mt_tile_props): tile properties

    Returns:
        bpy.types.Object: preview core
    """
    preview_core = spawn_wall_core(tile_props)
    textured_vertex_groups = ['Front', 'Back']
    preview_core, displacement_core = create_displacement_core(
        base,
        preview_core,
        tile_props,
        textured_vertex_groups)
    displacement_core.hide_viewport = True
    return preview_core


def create_openlock_wall_cores(base, tile_props):
    """Create preview and displacement cores.

    Args:
        base (bpy.types.Object): tile base
        tile_props (bpy.types.PropertyGroup.mt_tile_props): tile properties

    Returns:
        bpy.types.Object: preview core
    """
    preview_core = spawn_wall_core(tile_props)
    textured_vertex_groups = ['Front', 'Back']
    preview_core, displacement_core = create_displacement_core(
        base,
        preview_core,
        tile_props,
        textured_vertex_groups)

    wall_cutters = create_openlock_wall_cutters(
        preview_core,
        tile_props)

    cores = [preview_core, displacement_core]
    tile_name = tile_props.tile_name

    for wall_cutter in wall_cutters:
        wall_cutter.parent = base
        wall_cutter.display_type = 'BOUNDS'
        wall_cutter.hide_viewport = True
        obj_props = wall_cutter.mt_object_props
        obj_props.is_mt_object = True
        obj_props.tile_name = tile_name
        obj_props.geometry_type = 'CUTTER'

        for core in cores:
            wall_cutter_bool = core.modifiers.new(wall_cutter.name + '.bool', 'BOOLEAN')
            wall_cutter_bool.operation = 'DIFFERENCE'
            wall_cutter_bool.object = wall_cutter
            wall_cutter_bool.show_render = False

            # add cutters to object's mt_cutters_collection
            # so we can activate and deactivate them when necessary
            item = core.mt_object_props.cutters_collection.add()
            item.name = wall_cutter.name
            item.value = True
            item.parent = core.name

    displacement_core.hide_viewport = True

    return preview_core


def spawn_wall_core(tile_props):
    """Returns the core (vertical) part of a straight wall tile
    """

    cursor = bpy.context.scene.cursor
    cursor_start_loc = cursor.location.copy()
    tile_size = tile_props.tile_size
    base_size = tile_props.base_size
    tile_name = tile_props.tile_name
    native_subdivisions = (
        tile_props.x_native_subdivisions,
        tile_props.y_native_subdivisions,
        tile_props.z_native_subdivisions
    )

    core = draw_straight_wall_core(
        [tile_size[0],
            tile_size[1],
            tile_size[2] - base_size[2]],
        native_subdivisions)

    core.name = tile_name + '.core'
    add_object_to_collection(core, tile_name)

    # move core so centred, move up so on top of base and set origin to world origin
    core.location = (
        core.location[0],
        core.location[1] + (base_size[1] - tile_size[1]) / 2,
        cursor_start_loc[2] + base_size[2])

    ctx = {
        'object': core,
        'active_object': core,
        'selected_objects': [core]
    }

    bpy.ops.object.origin_set(ctx, type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.uv.smart_project(ctx, island_margin=tile_props.UV_island_margin)

    straight_wall_to_vert_groups(core)

    obj_props = core.mt_object_props
    obj_props.is_mt_object = True
    obj_props.tile_name = tile_props.tile_name

    return core

def create_openlock_wall_cutters(core, tile_props):
    """Creates the cutters for the wall and positions them correctly
    """
    preferences = get_prefs()

    tile_name = tile_props.tile_name
    tile_size = tile_props.tile_size
    base_size = tile_props.base_size

    booleans_path = os.path.join(
        preferences.assets_path,
        "meshes",
        "booleans",
        "openlock.blend")

    # load side cutter
    with bpy.data.libraries.load(booleans_path) as (data_from, data_to):
        data_to.objects = ['openlock.wall.cutter.side']

    core_location = core.location.copy()

    cutters = []
    # left side cutters
    left_cutter_bottom = data_to.objects[0].copy()
    left_cutter_bottom.name = 'X Neg Bottom.' + tile_name

    add_object_to_collection(left_cutter_bottom, tile_name)
    # get location of bottom front left corner of tile
    front_left = core_location

    # move cutter to bottom front left corner then up by 0.63 inches
    left_cutter_bottom.location = [
        front_left[0],
        front_left[1] + (base_size[1] / 2),
        front_left[2] + 0.63]

    array_mod = left_cutter_bottom.modifiers.new('Array', 'ARRAY')
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace[2] = 2
    array_mod.fit_type = 'FIT_LENGTH'
    array_mod.fit_length = tile_size[2] - 1

    # make a copy of left cutter bottom
    left_cutter_top = left_cutter_bottom.copy()
    left_cutter_top.name = 'X Neg Top.' + tile_name

    add_object_to_collection(left_cutter_top, tile_name)

    # move cutter up by 0.75 inches
    left_cutter_top.location[2] = left_cutter_top.location[2] + 0.75

    array_mod = left_cutter_top.modifiers[array_mod.name]
    array_mod.fit_length = tile_size[2] - 1.8

    cutters.extend([left_cutter_bottom, left_cutter_top])

    # right side cutters

    right_cutter_bottom = data_to.objects[0].copy()
    right_cutter_bottom.name = 'X Pos Bottom.' + tile_name

    add_object_to_collection(right_cutter_bottom, tile_name)
    # get location of bottom front right corner of tile
    front_right = [
        core_location[0] + (tile_size[0]),
        core_location[1],
        core_location[2]]
    # move cutter to bottom front right corner then up by 0.63 inches
    right_cutter_bottom.location = [
        front_right[0],
        front_right[1] + (base_size[1] / 2),
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
    right_cutter_top.name = 'X Pos Top.' + tile_name

    add_object_to_collection(right_cutter_top, tile_name)
    right_cutter_top.location[2] = right_cutter_top.location[2] + 0.75

    array_mod = right_cutter_top.modifiers["Array"]
    array_mod.fit_length = tile_size[2] - 1.8

    cutters.extend([right_cutter_bottom, right_cutter_top])

    return cutters
