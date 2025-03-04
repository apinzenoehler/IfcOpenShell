# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifccsv
import ifcopenshell
import json
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


class SelectDiffJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_json_file"
    bl_label = "Select Diff JSON File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.DiffProperties.diff_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class VisualiseDiff(bpy.types.Operator):
    bl_idname = "bim.visualise_diff"
    bl_label = "Visualise Diff"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        with open(context.scene.DiffProperties.diff_json_file, "r") as file:
            diff = json.load(file)
        for obj in context.visible_objects:
            obj.color = (1.0, 1.0, 1.0, 0.2)
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            global_id = element.GlobalId
            if global_id in diff["deleted"]:
                obj.color = (1.0, 0.0, 0.0, 0.2)
            elif global_id in diff["added"]:
                obj.color = (0.0, 1.0, 0.0, 0.2)
            elif global_id in diff["changed"]:
                obj.color = (0.0, 0.0, 1.0, 0.2)
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SelectDiffOldFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_old_file"
    bl_label = "Select Diff Old File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.DiffProperties.diff_old_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectDiffNewFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_new_file"
    bl_label = "Select Diff New File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.DiffProperties.diff_new_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcDiff(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_diff"
    bl_label = "Execute IFC Diff"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifcdiff

        ifc_diff = ifcdiff.IfcDiff(
            context.scene.DiffProperties.diff_old_file,
            context.scene.DiffProperties.diff_new_file,
            self.filepath,
            context.scene.DiffProperties.diff_relationships.split(),
        )
        ifc_diff.diff()
        ifc_diff.export()
        context.scene.DiffProperties.diff_json_file = self.filepath
        return {"FINISHED"}
