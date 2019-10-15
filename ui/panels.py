import bpy
import os

class MT_PT_Panel(bpy.types.Panel):
    bl_idname       = "MT_PT_Panel"
    bl_label        = "Make Tiles"
    bl_category     = "Make-Tile"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "UI"

    def draw(self, context):
        scn = context.scene
        lay = self.layout
        lay.operator('scene.make_tile', text="Make Tile")
        lay.prop(scn, 'mt_tile_name')
        lay.prop(scn, 'mt_tile_system')
        lay.prop(scn, 'mt_tile_type')
        lay.prop(scn, 'mt_base_size')
        lay.prop(scn, 'mt_tile_size')