import os
from file_parser import parse_single_file
from results_printer import (print_file_header, print_jobiph_data, 
                           print_states_mapping, print_energy_summary,
                           print_error)

def process_file(file_path):#Przetwarza pojedynczy plik i wyświetla wyniki
    
    try:
        results = parse_single_file(file_path)
        
        print_file_header(file_path, results['distance'], results['num_states'])
        print_jobiph_data(results['jobiph_data'])
        print_states_mapping(results['states_mapping'], results['energies'])
        print_energy_summary(results['energies'])
        
    except Exception as e:
        print_error(e)

if __name__ == "__main__":
    file_path = os.path.join("dane", "O2.0.9000.rassi.output")
    process_file(file_path)