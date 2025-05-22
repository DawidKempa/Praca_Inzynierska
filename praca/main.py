import os
from file_parser import parse_single_file
from results_printer import (print_file_header, print_jobiph_data, 
                           print_states_mapping, print_energy_summary,
                           print_error)

def process_file(file_path):
    
    try:
        results = parse_single_file(file_path)
        
        print_file_header(file_path, results['distance'], results['num_states'])
        print_jobiph_data(results['jobiph_data'])
        print_states_mapping(results['states_mapping'], results['energies'])
        print_energy_summary(results['energies'])
        
    except Exception as e:
        print_error(e)


def show_sorted_sfstate_absm(input_file, max_states=99):
    """
    Reads .out file, sorts by SF State, and displays SF State and Abs_M values.
    Stops after collecting max_states valid entries.
    
    Args:
        input_file (str): Path to the input .out file
        max_states (int): Maximum number of states to process
    """
    data = []
    data_section = False
    
    with open(input_file, 'r') as f:
        for line in f:
            if len(data) >= max_states:
                break
                
            line = line.strip()
            
            if 'SF State' in line and 'Abs_M' in line:
                data_section = True
                continue
                
            if not data_section or not line:
                continue
                
            parts = line.split()
            try:
                sf_state = int(parts[0])
                if len(parts) >= 6:
                    abs_m = float(parts[5])
                    data.append((sf_state, abs_m))
            except (ValueError, IndexError):
                continue
    
    data.sort(key=lambda x: x[0])
    
    print("SF State | Abs_M")
    print("----------------")
    for sf_state, abs_m in data[:max_states]: 
        print(f"{sf_state:7d} | {abs_m:5.1f}")
    
    print(f"\nWyświetlono {len(data)} stanów (limit: {max_states})")





if __name__ == "__main__":
    file_path = os.path.join("dane", "O2.0.9000.rassi.output")
    process_file(file_path)
    show_sorted_sfstate_absm(file_path, max_states=99)