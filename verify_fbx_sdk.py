import logging
from pyfbx import Manager, Scene, Node, Mesh

logger = logging.getLogger('root')

def verify_fbx_sdk(fbx_file_path):
    try:
        # Initialize the manager and scene
        manager = Manager()
        scene = Scene(manager)
        
        # Load the FBX file
        scene.load(fbx_file_path)
        print(f"Loaded FBX file: {fbx_file_path}")

        # Extract animation data
        animations = scene.animations
        if not animations:
            raise Exception(f"No animations found in FBX file: {fbx_file_path}")

        # Assuming we're interested in the first animation
        anim = animations[0]

        # Get animation properties
        frame_count = anim.frame_count
        frame_rate = anim.frame_rate
        duration_seconds = frame_count / frame_rate

        print(f"Animation Length Results:")
        print(f"  Frame Count: {frame_count}")
        print(f"  Duration (seconds): {duration_seconds:.2f}")
        print(f"  Frame Rate: {frame_rate:.2f}")

    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    fbx_file_path = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\processed\Zombie Walking.fbx"
    verify_fbx_sdk(fbx_file_path)