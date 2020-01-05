import bpy
from .. lib.utils.selection import select, deselect_all, select_all, activate
from .. lib.utils.collections import add_object_to_collection, create_collection


class MT_OT_Tile_Voxeliser(bpy.types.Operator):
    """Voxelises the visible objects in the active collection"""
    bl_idname = "scene.voxelise_tile"
    bl_label = "Voxelise tile"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.object is not None:
            return bpy.context.object.mode == 'OBJECT'
        else:
            return True

    def execute(self, context):
        deselect_all()

        tile_collection = context.collection
        tile_name = tile_collection.name

        # save list of visible objects in active tile collection
        obs = []
        for obj in tile_collection.all_objects:
            if obj.type == 'MESH':
                if obj.hide_viewport is False and obj.hide_get() is False:
                    obs.append(obj)
                    select(obj.name)

        # Apply all modifiers and create a copy of our meshes
        bpy.ops.object.convert(target='MESH', keep_original=True)

        # hide the original objects
        for obj in obs:
            obj.hide_set(True)

        # save a list of the copies
        copies = []
        for obj in tile_collection.all_objects:
            if obj.type == 'MESH':
                if obj.hide_viewport is False and obj.hide_get() is False:
                    obj.mt_tile_properties.tile_name = tile_name
                    copies.append(obj)

        # create a sub collection in our tile collection called Flattened objects
        new_collection = create_collection("Flattened Objects", tile_collection)

        # if merge is true join meshes together
        if context.scene.mt_merge_and_voxelise is True:
            ctx = bpy.context.copy()
            ctx['active_object'] = copies[0]
            ctx['object'] = copies[0]
            ctx['selected_objects'] = copies
            ctx['selected_editable_objects'] = copies

            bpy.ops.object.join(ctx)

            # Rename merged tile
            merged_obj = copies[0]
            merged_obj.name = tile_name + '.merged'
            merged_obj = voxelise_mesh(merged_obj)

            add_object_to_collection(merged_obj, new_collection.name)

        # otherwise just voxelise displacement objects
        else:
            for copy in copies:
                if 'geometry_type' in copy:
                    if copy['geometry_type'] == 'DISPLACEMENT':
                        voxelise_mesh(copy)
                        add_object_to_collection(copy, new_collection.name)

        return {'FINISHED'}

    @classmethod
    def register(cls):
        bpy.types.Scene.mt_voxel_quality = bpy.props.FloatProperty(
            name="Quality",
            description="Quality of the voxelisation. Smaller = Better",
            soft_min=0.005,
            default=0.005,
            precision=3,
        )

        bpy.types.Scene.mt_voxel_adaptivity = bpy.props.FloatProperty(
            name="Adaptivity",
            description="Amount by which to simplify mesh",
            default=0.01,
            precision=3,
        )

        bpy.types.Scene.mt_merge_and_voxelise = bpy.props.BoolProperty(
            name="Merge",
            description="Merge tile before voxelising? Creates a single mesh.",
            default=True
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.mt_merge_and_voxelise
        del bpy.types.Scene.mt_voxel_adaptivity
        del bpy.types.Scene.mt_voxel_quality


def voxelise_mesh(obj):
    """Voxelises the passed in object
    Keyword Arguments:
    obj -- MESH OBJECT
    """

    obj.data.remesh_voxel_size = bpy.context.scene.mt_voxel_quality
    obj.data.remesh_voxel_adaptivity = bpy.context.scene.mt_voxel_adaptivity

    ctx = {
        'object': obj,
        'active_object': obj}

    bpy.ops.object.voxel_remesh(ctx)
    obj.modifiers.new('Triangulate', 'TRIANGULATE')

    return obj
