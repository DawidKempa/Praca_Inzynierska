import os
from file_parser import parse_single_file
from database import create_database, save_to_database, update_database_with_mapping

def get_sfstate_absm_data(input_file, max_states=99):
    """Pobiera dane SF State i Abs_M z pliku."""
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
    return data

def process_all_files(data_dir="dane"):
    """Przetwarza wszystkie pliki w folderze."""
    files = [f for f in os.listdir(data_dir) if f.endswith(".rassi.output")]
    all_results = []

    for filename in sorted(files):
        file_path = os.path.join(data_dir, filename)
        try:
            print(f"Przetwarzam: {filename}")
            results = parse_single_file(file_path)
            abs_m_data = get_sfstate_absm_data(file_path)
            results['abs_m'] = {state: abs_m for state, abs_m in abs_m_data}
            all_results.append(results)
        except Exception as e:
            print(f"Błąd w {filename}: {str(e)}")
    
    return all_results

if __name__ == "__main__":
    create_database()
    results = process_all_files()
    save_to_database(results)
    
    # Dodajemy nową część:
    print("\nPrzetwarzanie mapowania stanów...")
    optimal_distance = update_database_with_mapping()
    
    print(f"\nOptymalna odległość: {optimal_distance} Å")
    print("Mapowanie stanów zakończone pomyślnie")
    print("Dane zapisane do bazy 'molcas_results.db'")