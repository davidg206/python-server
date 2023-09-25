from concurrent import futures
import logging
import math
import time
import os
import unreal
import subprocess

import grpc
import PalatialWeb_pb2
import PalatialWeb_pb2_grpc
import glob

from pathlib import Path
import sys


class importFunctions:
    # Define the paths
    project_path = unreal.Paths.project_dir()
    import_folder = os.path.join(project_path, 'import')
    assets_import_folder = "/Game/User/Import"

    def loadLevel(self):
        # Check if the 'import' level exists, otherwise create it
        level_path = "/Game/User/Main"
        level_system = unreal.LevelEditorSubsystem()
        if not level_system.load_level(level_path):
            level_system.new_level(level_path)



    def importFiles(self):
        # Get a list of all Datasmith files in the import folder
        ds_files = [f for f in os.listdir(self.import_folder) if f.endswith('.udatasmith')]
        eas = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
        ic_mng = unreal.InterchangeManager.get_interchange_manager_scripted()
        #pipeline = eas.load_asset("/Game/Palatial/Features/Dataprep/Recipes/DA_RevitPipeline")
        #mesh_pipeline = pipeline.get_editor_property("mesh_pipeline")
        dataprep_asset = unreal.EditorAssetLibrary.load_asset("/Game/Palatial/Features/Dataprep/Recipes/DA_RevitPipeline")
        dataprep_lib = unreal.EditorDataprepAssetLibrary()

        asset_path = self.project_path + "/Palatial/Features/Dataprep/Recipes/DA_RevitPipeline"
        if not dataprep_lib.get_producers_count(dataprep_asset): # or (isinstance(dataprep_lib.get_producer(dataprep_asset, 0), unreal.DatasmithDirProducer) and dataprep_lib.get_producer(dataprep_asset, 0).folder_path == import_folder):
            producer = dataprep_lib.add_producer_automated(dataprep_asset, unreal.DatasmithDirProducer)
            print(self.import_folder)
            producer.set_editor_property("folder_path" , self.import_folder)



        # Import the Datasmith files into the level
        dataprep_lib.execute_dataprep(dataprep_asset, unreal.DataprepReportMethod.STANDARD_LOG, unreal.DataprepReportMethod.STANDARD_LOG)

    #   for ds_file in ds_files:
    #       ds_path = os.path.join(import_folder, ds_file)

    #       # Set import options
    #       options = unreal.DatasmithImportOptions()
    #       options.base_options.scene_handling = unreal.DatasmithImportScene.CURRENT_LEVEL
    #       options.base_options.include_geometry = True
    #       options.base_options.include_material = True
    #       options.base_options.include_light = True
    #       options.base_options.include_camera = True
    #       options.base_options.include_animation = True

    #       # Create the factory and set the options
    #       factory = unreal.DatasmithImportFactory()
    #       #factory.set_editor_property('import_options', options)

    #       # Import the Datapith file
    #       task = unreal.AssetImportTask()
    #       task.set_editor_property('filename', ds_path)
    #       task.set_editor_property('destination_path', assets_import_folder)
    #       task.set_editor_property('replace_existing', True)
    #       task.set_editor_property('save', True)
    #       task.set_editor_property('automated', True)
    #       task.set_editor_property('factory', factory)

    #       unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])



            

    def deleteFiles(self):
        # Get a list of all Datasmith files in the import folder
        ds_files = [f for f in os.listdir(self.import_folder) if f.endswith('.udatasmith')]


        for ds_file in ds_files:
            # Delete the Datasmith file from the import folder
            ds_path = os.path.join(self.import_folder, ds_file)
            os.remove(ds_path)

        print("Datasmith files imported and original files deleted from the 'import' folder.")

class PalatialBuildServer:
    buildClientCommand = ""


    buildServerCommand = ""

    editActionQueue = []

    def __init__(self):
        print("build system initialized")

    def buildProject(self):
        #os.system(self.buildClientCommand)

        #os.system(self.buildServerCommand)
        print("the packaging would start now")
        unreal.ImportEditorScriptLibrary.save_level()
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        os.chdir('D:\Steven_GIGACHONK_Dev\Palatial_V01_UE51')
        print("test 1")
        
        batch_file_path = r"C:\Github\UE_511\UnrealEngine\Engine\Build\BatchFiles\RunUAT.bat"
        command = 'BuildCookRun'
        project_path = r'D:\Steven_GIGACHONK_Dev\Palatial_V01_UE51\Palatial_V01_UE51.uproject'
        output_directory = r'.'
        # Prepare the command with arguments
        arguments = [
            batch_file_path,
            'BuildCookRun',
            f'-project="{project_path}"',
            '-noP4',
            '-platform=Linux',
            '-clientconfig=Development',
            '-serverconfig=Development',
            '-cook',
            '-allmaps',
            '-build',
            '-stage',
            '-pak',
            '-archive',
            f'-archivedirectory="{output_directory}"'
        ]
        
        # Execute the command
        subprocess.call(arguments)
        print("test 2")
        #os.rename("./Saved/StagedBuilds/Linux", "./Saved/StagedBuilds/LinuxClient")

        argumentsServer = [
            batch_file_path,
            'BuildCookRun',
            f'-project="{project_path}"',
            '-noP4',
            '-platform=Linux',
            '-clientconfig=Development',
            '-serverconfig=Development',
            '-cook',
            '-server',
            '-serverplatform=Linux',
            '-noclient',
            '-build',
            '-stage',
            '-pak',
            '-archive',
            f'-archivedirectory="{output_directory}"'
        ]
        
        subprocess.call(argumentsServer)
        print("test 3")
        
        name = "test"

        os.chdir('D:\Steven_GIGACHONK_Dev\Palatial_V01_UE51')
        cwd = os.getcwd()
        # Printing the current working directory
        print("Th Current working directory is: {0}".format(cwd))
        subprocess.run('sps-app deploy ./Saved/StagedBuilds --custom-docker-build --owner test --create-link')


    def CommitEdits(self):
        valid_actions = self.process_undo_actions()
        print("Num actions after undo = " + str(len(valid_actions)) + " ," + 
              str(len(self.editActionQueue) - len(valid_actions)) + " undo actions proccessed")

        unreal.ImportEditorScriptLibrary.initialize_maps()
        
        for action in valid_actions:
            if isinstance(action, PalatialWeb_pb2.EditingAction):
                action_type = action.WhichOneof("edit_action")
                
                if action_type == "batch_delete_action":
                    mesh_ids = [delete.mesh_id for delete in action.batch_delete_action.delete_action]
                    unreal.ImportEditorScriptLibrary.batch_delete(mesh_ids)
                elif action_type == "batch_translate_action":
                    mesh_ids = []
                    mesh_locations = []

                    for translate in action.batch_translate_action.translate:
                        mesh_ids.append(translate.mesh_id)
                        mesh_locations.append(unreal.Vector(translate.location.x, translate.location.y, translate.location.z))
                        
                    unreal.ImportEditorScriptLibrary.batch_translate(mesh_ids, mesh_locations)
                elif action_type == "flip_normal_action":
                    unreal.ImportEditorScriptLibrary.flip_normal(action.flip_normal_action.mesh_id)
                elif action_type == "batch_light_setting_action":
                    for light_setting in action.batch_light_setting_action.light_setting_action:      
                        unreal.ImportEditorScriptLibrary.batch_light_settings(
                            light_setting.light_id,
                            light_setting.source_radius,
                            light_setting.soft_source_radius,
                            light_setting.source_length,
                            light_setting.inner_cone_angle,
                            light_setting.outer_cone_angle,
                            light_setting.source_width,
                            light_setting.source_weight,
                            light_setting.barn_door_angle,
                            light_setting.barn_door_length,
                            light_setting.intensity,
                            light_setting.attenuation,
                            unreal.LinearColor(light_setting.color_r, light_setting.color_g, light_setting.color_b),
                            light_setting.cast_shadows,
                            light_setting.enabled
                        )
                elif action_type == "add_light_action":
                    add_light = action.add_light_action

                    unreal.ImportEditorScriptLibrary.add_light(
                        add_light.unique_id,
                        add_light.type,
                        unreal.Vector(
                            add_light.location.x,
                            add_light.location.y,
                            add_light.location.z)
                    )
                elif action_type == "batch_replace_material_action":
                    mesh_ids = [id for id in action.batch_replace_material_action.mesh_ids]

                    unreal.ImportEditorScriptLibrary.batch_replace_material(
                        action.batch_replace_material_action.old_material_path,
                        action.batch_replace_material_action.new_material_path,
                        mesh_ids
                    )
                elif action_type == "toggle_nanite_action":
                    continue
                elif action_type == "adjust_context_action":
                    adjust_context = action.adjust_context_action

                    unreal.ImportEditorScriptLibrary.adjust_context(
                        adjust_context.long,
                        adjust_context.lat,
                        adjust_context.height,
                        adjust_context.angle
                    )
                elif action_type == "crop_context_action":
                    spline_points = [unreal.Vector(point.x, point.y, point.z) for point in action.crop_context_action.spline_point]
                    unreal.ImportEditorScriptLibrary.crop_context(spline_points)
                elif action_type == "place_context_action":
                    unreal.ImportEditorScriptLibrary.place_context(action.place_context_action.enabled)
                elif action_type == "set_saved_view_action":
                    set_saved_view = action.set_saved_view_action

                    unreal.ImportEditorScriptLibrary.set_saved_view(
                        set_saved_view.camera_id,
                        set_saved_view.enabled,
                        set_saved_view.name
                    )
                elif action_type == "add_saved_view_action":
                    add_saved_view = action.add_saved_view_action

                    unreal.ImportEditorScriptLibrary.add_saved_view(
                        add_saved_view.unique_id,
                        add_saved_view.name,
                        unreal.Vector(add_saved_view.location.x, add_saved_view.location.y, add_saved_view.location.z),
                        unreal.Vector(add_saved_view.rotation_x, add_saved_view.rotation_y, add_saved_view.rotation_z)
                    )
                elif action_type == "set_player_start_action":
                    unreal.ImportEditorScriptLibrary.set_player_start(action.set_player_start_action.camera_id)
                else:
                    print(f"Unknown action_type: {action_type}")

    def process_undo_actions(self):
        valid_actions = []
        undo_count = 0

        for edit in reversed(self.editActionQueue):
            if isinstance(edit, PalatialWeb_pb2.EditingAction):
                action_type = edit.WhichOneof("edit_action")

                if action_type == "undo_action":
                    undo_count += 1
                elif undo_count > 0:
                    undo_count -= 1
                else:
                    valid_actions.append(edit)
        return list(reversed(valid_actions))

buildServer = PalatialBuildServer()
class PalatialWebServicer(PalatialWeb_pb2_grpc.PalatialServerServicer):


    def __init__(self, server):
        self.server = server
        print("grpc server initialized")

    def SendEditingCommand(self, request, context):
        print(request.WhichOneof("edit_action"))
        buildServer.editActionQueue.append(request)

        return PalatialWeb_pb2.Ack(ack = True)

    def CommitEdits(self, request, context):
        self.server.stop(1)
        print("stopped server")
        

        return PalatialWeb_pb2.Ack(ack = True)


def serve():
    
    os.chdir('D:\Steven_GIGACHONK_Dev\Palatial_V01_UE51')
    cwd = os.getcwd()
    # Printing the current working directory
    print("Th Current working directory is: {0}".format(cwd))
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    PalatialWeb_pb2_grpc.add_PalatialServerServicer_to_server(
        PalatialWebServicer(server), server)
    server.add_insecure_port('[::]:50051')
    print("starting GRPC server")
    server.start()
    server.wait_for_termination()

    buildServer.CommitEdits()

    buildServer.buildProject()




if __name__ == '__main__':
    logging.basicConfig()

    importInstance = importFunctions()
    importInstance.loadLevel()

    importInstance.importFiles()

    #importInstance.deleteFiles()
    unreal.EditorLevelLibrary.save_all_dirty_levels()

    unreal.PalatialEditorFunctionLibrary.execute_post_import_scripts()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    buildServer.buildProject()

    while True:
        serve()

