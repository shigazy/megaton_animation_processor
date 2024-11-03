import struct

def read_uint32(file):
    return struct.unpack('<I', file.read(4))[0]

def load_fbx_animation(fbx_file):
    with open(fbx_file, 'rb') as f:
        # Check FBX signature
        if f.read(23) != b'Kaydara FBX Binary\x20\x20\x00\x1a\x00':
            raise ValueError("Not a valid FBX file")

        # Skip version number
        f.seek(4, 1)

        # Simple animation data extraction
        start_frame = 0
        end_frame = 100  # Default to 100 frames if we can't find the actual count
        frame_rate = 30  # Default frame rate

        # Attempt to find animation length
        while True:
            record_header = f.read(4)
            if len(record_header) < 4:
                break  # End of file

            end_offset = read_uint32(f)
            num_properties = read_uint32(f)
            property_list_len = read_uint32(f)

            print(f"Record header: {record_header}, End offset: {end_offset}, Num properties: {num_properties}, Property list length: {property_list_len}")

            if record_header == b'ANIM':
                # Found animation node, try to extract length
                f.seek(property_list_len, 1)  # Skip property list
                name_len = read_uint32(f)
                name = f.read(name_len).decode('utf-8', errors='ignore')
                print(f"Found animation node: {name}")
                if 'AnimationStack' in name:
                    # Assume next two float properties are start and end time
                    f.seek(16, 1)  # Skip to float values
                    start_time = struct.unpack('<d', f.read(8))[0]
                    end_time = struct.unpack('<d', f.read(8))[0]
                    print(f"Start time: {start_time}, End time: {end_time}")
                    # Assume 30 fps
                    start_frame = int(start_time * frame_rate)
                    end_frame = int(end_time * frame_rate)
                    break
            else:
                f.seek(end_offset, 0)

    frame_count = end_frame - start_frame
    duration_seconds = frame_count / frame_rate

    print(f"Start frame: {start_frame}, End frame: {end_frame}")
    return {
        "name": fbx_file,
        "start": start_frame,
        "end": end_frame,
        "frame_count": frame_count,
        "duration_seconds": duration_seconds,
        "frame_rate": frame_rate
    }