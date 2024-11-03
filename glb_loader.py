import pygltflib

def load_glb_skeleton(glb_file):
    glb = pygltflib.GLTF2().load(glb_file)
    
    # Extract skeleton data from the GLB file
    # This is a simplified version and may need to be expanded based on your specific needs
    skeleton = {
        "nodes": glb.nodes,
        "skins": glb.skins,
    }
    
    return skeleton