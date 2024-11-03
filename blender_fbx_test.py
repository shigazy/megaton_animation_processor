import bpy
import sys

def load_fbx_and_get_animation_length(fbx_file_path):
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import the FBX file
    bpy.ops.import_scene.fbx(filepath=fbx_file_path)
    
    # Get the imported armature (assuming there's only one)
    armature = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    
    if not armature:
        raise Exception(f"No armature found in FBX file: {fbx_file_path}")
    
    # Get the action (animation) data
    actions = bpy.data.actions
    if not actions:
        raise Exception(f"No animations found in FBX file: {fbx_file_path}")
    
    # Assuming we're interested in the first action
    action = actions[0]
    
    # Get animation properties
    frame_count = action.frame_range[1] - action.frame_range[0]
    frame_rate = bpy.context.scene.render.fps
    duration_seconds = frame_count / frame_rate
    
    print(f"Animation Length Results:")
    print(f"  Frame Count: {frame_count}")
    print(f"  Duration (seconds): {duration_seconds:.2f}")
    print(f"  Frame Rate: {frame_rate:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: blender --background --python blender_fbx_test.py -- <fbx_file_path>")
        sys.exit(1)
    
    fbx_file_path = sys.argv[-1]
    load_fbx_and_get_animation_length(fbx_file_path)