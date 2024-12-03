import sys
from pathlib import Path

def convert_wpt_to_gfp(input_file, output_file):
    """Create a flightplan from an ordered list of user waypoints.

    Parameters
    ----------
    input_file : str
        Path to the "*_user_renamed_DDM.wpt" file
    output_file : str
        New path under which the .gfp-file should be stored
        Recommendation: "{target}_fpl.gfp"
    """
    with open(input_file, 'r') as f:
        # Read lines from the input file
        lines = f.readlines()
    
    converted_lines = []
    for line in lines:
        parts = line.strip().split(',')
        # Remove dots, 'd', and 'm' characters from the coordinates and concatenate latitude and longitude
        coordinates = parts[2].replace('.', '').replace('d', '').replace('m', '') + parts[3].replace('.', '').replace('d', '').replace('m', '')
        # Append the formatted coordinates to the converted lines
        converted_lines.append(f'{coordinates}')
    
    # Concatenate the converted lines with the :F: delimiter and the 'FPN/RI' starting info.
    output_content = 'FPN/RI:F:' + ':F:'.join(converted_lines)

    # write the .gfp-file to disk
    with open(output_file, 'w') as f:
        f.write(output_content)

if __name__ == "__main__":
    user_wpt = Path(sys.argv[1])
    flp_gfp = (sys.argv[2])
    convert_wpt_to_gfp(user_wpt, flp_gfp)
