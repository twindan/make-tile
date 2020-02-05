import bpy
from .. lib.utils.utils import mode, view3d_find
from .. lib.utils.selection import select, select_all, deselect_all, activate
from .. lib.utils.collections import (
    create_collection,
    add_object_to_collection,
    get_collection,
    activate_collection)
from .. enums.enums import view_mode


class MT_OT_Create_Lighting_Setup(bpy.types.Operator):
    """Creates a lighting setup for Cycles and Eevee previews"""
    bl_idname = "scene.mt_create_lighting_setup"
    bl_label = "Create Lighting"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.object is not None:
            return bpy.context.object.mode == 'OBJECT'
        else:
            return True

    def execute(self, context):
        deselect_all()
         # Get 3d view
        region, rv3d, v3d, area = view3d_find(True)

        if context.scene.mt_view_mode == 'CYCLES':
            v3d.shading.type = 'RENDERED'
            context.scene.render.engine = 'CYCLES'
            context.space_data.shading.use_scene_world_render = False
            context.space_data.shading.studio_light = 'city.exr'
            context.scene.cycles.feature_set = 'EXPERIMENTAL'
            if context.scene.mt_use_gpu is True:
                context.scene.cycles.device = 'GPU'

        if context.scene.mt_view_mode == 'EEVEE':
            v3d.shading.type = 'RENDERED'
            context.scene.render.engine = 'BLENDER_EEVEE'
            context.space_data.shading.use_scene_world_render = False
            context.space_data.shading.studio_light = 'city.exr'

        if context.scene.mt_view_mode == 'PREVIEW':
            v3d.shading.type = 'MATERIAL'

        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered class: %s " % cls.bl_label)

        bpy.types.Scene.mt_use_gpu = bpy.props.BoolProperty(
            name="Use GPU",
            description="Use GPU for Cycles render",
            default=True,
            update=update_render_device
        )

        bpy.types.Scene.mt_cycles_subdivision_quality = bpy.props.IntProperty(
            name="Subdivision",
            description="Cycles subdivision - higher = higher quality.",
            default=1,
        )

        bpy.types.Scene.mt_view_mode = bpy.props.EnumProperty(
            items=view_mode,
            name="Render Engine",
            default="CYCLES",
            update=update_view_mode,
        )

    @classmethod
    def unregister(cls):
        print("Unregistered class: %s" % cls.bl_label)
        del bpy.types.Scene.mt_view_mode
        del bpy.types.Scene.mt_cycles_subdivision_quality
        del bpy.types.Scene.mt_use_gpu


def update_render_device(self, context):
    if bpy.context.scene.mt_use_gpu is True:
        bpy.context.scene.cycles.device = 'GPU'
    else:
        bpy.context.scene.cycles.device = 'CPU'


def update_view_mode(self, context):
    region, rv3d, v3d, area = view3d_find(True)

    if bpy.context.scene.mt_view_mode == 'CYCLES':
        v3d.shading.type = 'RENDERED'
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.space_data.shading.use_scene_world_render = False
        bpy.context.space_data.shading.studio_light = 'city.exr'
        bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'

        if bpy.context.scene.mt_use_gpu is True:
            bpy.context.scene.cycles.device = 'GPU'

    if bpy.context.scene.mt_view_mode == 'EEVEE':
        v3d.shading.type = 'RENDERED'
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.space_data.shading.use_scene_world_render = False
        bpy.context.space_data.shading.studio_light = 'city.exr'

    if bpy.context.scene.mt_view_mode == 'PREVIEW':
        v3d.shading.type = 'MATERIAL'
