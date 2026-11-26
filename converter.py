import trimesh
import os
import gmsh
import sys

# Added output_folder argument (defaults to None)
def convert_step_to_off_locally(input_path, output_folder=None):
    # check if file exists
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    # --- START OF MODIFICATION ---
    
    # Get the base filename (e.g., "part.step" -> "part")
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    if output_folder:
        # If a specific folder is requested, ensure it exists
        os.makedirs(output_folder, exist_ok=True)
        # Join the folder path with the new filename
        output_filename = os.path.join(output_folder, base_name + ".off")
    else:
        # Default behavior: Save in the same folder as input
        output_filename = os.path.splitext(input_path)[0] + ".off"

    # --- END OF MODIFICATION ---
    
    print(f"Processing {input_path}...")
    print(f"Saving to {output_filename}...")
    
    # Initialize GMSH
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0) # Hide GMSH logs
    
    try:
        # Merge the STEP file into GMSH
        gmsh.merge(input_path)
        
        # 2 is the dimension for surface meshing
        gmsh.model.mesh.generate(2) 
        
        # Create a temporary STL file (easier to bridge to Trimesh)
        temp_stl = "temp_conversion.stl"
        gmsh.write(temp_stl)
        
        # Load the STL into Trimesh
        mesh = trimesh.load(temp_stl)
        
        # Export as OFF
        mesh.export(output_filename)
        print(f"Success! File saved.")
        
        # Clean up
        if os.path.exists(temp_stl):
            os.remove(temp_stl)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        gmsh.finalize()

# Usage
file_to_convert = input("Enter the path to your .step file: ").strip('"')

# You can hardcode your output folder here:
my_output_folder = r"D:\Loacal step to off conversion\Single files"

# Run the function with the output folder
convert_step_to_off_locally(file_to_convert, my_output_folder)