import yaml
import struct
import os, time
import open3d as o3d
import numpy as np
from scipy.io import savemat

def parse_entry(entry):
    # Parse the YAML entry
    parsed_data = yaml.safe_load(entry)
    # Extract relevant information
    header = parsed_data.get('header', {})
    stamp = header.get('stamp', {})
    sec = stamp.get('sec', 0)
    nano = stamp.get('nanosec', 0)
    frame_id = header.get('frame_id', '')
    height = parsed_data.get('height', 0)
    width = parsed_data.get('width', 0)
    fields = parsed_data.get('fields', [])
    is_bigendian = parsed_data.get('is_bigendian', False)
    point_step = parsed_data.get('point_step', 0)
    row_step = parsed_data.get('row_step', 0)
    data = parsed_data.get('data', [])
    is_dense = parsed_data.get('is_dense', False)

    # Remove strange endline "- '...'"
    data = data[:-1]

    timestep = sec + nano / 1000000000

    # Extract x, y, z coordinates
    points = np.empty((0,3))
    for i in range(0, len(data) - point_step, point_step):  # Assuming fixed size of 12 bytes per point (x, y, z)

        x_bytes = data[i:i+4]
        y_bytes = data[i+4:i+8]
        z_bytes = data[i+8:i+12]

        x = struct.unpack('<f', bytes(x_bytes))[0]
        y = struct.unpack('<f', bytes(y_bytes))[0]
        z = struct.unpack('<f', bytes(z_bytes))[0]
        points = np.append(points, np.array([[x, y, z]]), axis=0)
        
    return points, timestep

def parse_fifo(fifo_path, output_path):
    all_points = []
    all_timesteps = []

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Point Cloud Viewer", width=800, height=600)

    # opt = vis.get_render_option()
    # opt.background_color = np.asarray([0, 0, 0])

    with open(fifo_path, 'r') as fifo:
        entry = ''
        all_points_array = np.empty((0,), dtype=object)
        all_timesteps_array = np.empty((0,), dtype=object)
        start_parsing = False
        output_num = 0

        while True:
            line = fifo.readline()
            
            if line == '' and not start_parsing:                # Continue if no data is read (EOF)
                continue  

            elif line.strip() == '---' and not start_parsing :  # Start of data
                start_parsing = True

            elif line.strip() == '---' and start_parsing :      # End of an entry
                points, timestep = parse_entry(entry)

                all_points.append(points)
                all_timesteps.append(timestep)

                entry = ''  # Reset entry

                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(points)

                normalized_y = (points[:, 1] - np.min(points[:, 1])) / (np.max(points[:, 1]) - np.min(points[:, 1]))
                colors = np.zeros_like(points)
                colors[:, 1] = normalized_y  # RGB values for bright green (0-255 scale)

                # Assign colors to the point cloud
                pcd.colors = o3d.utility.Vector3dVector( colors)

                # Visualize Point Cloud
                vis.clear_geometries()
                vis.add_geometry(pcd)
                vis.poll_events()
                vis.update_renderer()

                print("update")


            elif not line and start_parsing:    
                output_num += 1
                
                all_points_array = np.array(all_points,dtype=object)
                all_timesteps_array = np.array(all_timesteps,dtype=object)
                struct_array = [{'data': matrix, 'time': timesteps} for matrix, timesteps in zip(all_points_array, all_timesteps_array)]

                output_path = str(output_num) + output_path
                savemat(output_path, {'points': struct_array})

                print("Done")

                start_parsing = False
                entry = ''

            elif start_parsing == True:
                entry += line


# Path to your FIFO file

fifo_path = "C:\\Users\\amark\\OneDrive\\Desktop\\doodlelabs.txt"

# Path to save the MATLAB file
output_path = 'output.mat'

# Ensure FIFO file exists
# if not os.path.exists(fifo_path):
#     os.mkfifo(fifo_path)

# Parse the FIFO file and save to MATLAB file
parse_fifo(fifo_path, output_path)