import bpy
from ..materials.materials import assign_mat_to_vert_group
from ..utils.registration import get_prefs


class MT_OT_Return_To_Preview(bpy.types.Operator):
    """Return the maketile object to its preview state"""
    bl_idname = "scene.mt_return_to_preview"
    bl_label = "Return to preview mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(context.selected_editable_objects) > 0:
            if hasattr(context.object, 'mt_object_props'):
                return context.object.mode == 'OBJECT'
        return False

    def execute(self, context):
        for obj in context.selected_editable_objects:
            if obj.type == 'MESH' and hasattr(obj, 'mt_object_props'):
                if obj.mt_object_props.geometry_type == 'DISPLACEMENT':
                    set_to_preview(obj)

        return {'FINISHED'}


def set_to_preview(obj):
    """Set the active object to preview mode.

    Args:
        obj (bpy.types.Object): object
    """
    prefs = get_prefs()
    secondary_material = bpy.data.materials[prefs.secondary_material]
    props = obj.mt_object_props
    disp_mod = obj.modifiers[props.disp_mod_name]
    #disp_mod = obj.modifiers[obj['disp_mod_name']]
    disp_mod.strength = 0

    # reassign preview material to mesh. While in displacement mode we had assigned the secondary material
    # to the entire mesh so we only saw actual geometry.
    assign_mat_to_vert_group('disp_mod_vert_group', obj, secondary_material)

    preview_materials = props.preview_materials

    for mat in preview_materials:
        if mat.vertex_group != 'disp_mod_vert_group':
            if mat.material is not None:
                assign_mat_to_vert_group(mat.vertex_group, obj, mat.material)

    ctx = {
        'object': obj,
        'active_object': obj,
        'selected_objects': [obj],
        'selected_editable_objects': [obj]
    }

    new_index = len(obj.modifiers) - 1
    bpy.ops.object.modifier_move_to_index(ctx, modifier=props.subsurf_mod_name, index=new_index)
    obj.cycles.use_adaptive_subdivision = True
    obj.mt_object_props.geometry_type = 'PREVIEW'
