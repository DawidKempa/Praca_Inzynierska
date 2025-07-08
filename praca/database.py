import sqlite3
from typing import List, Dict

def create_database(db_name="molcas_results.db"):
    """Tworzy bazę danych z tabelą calculations."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        distance REAL NOT NULL,
        state_num INTEGER NOT NULL,
        energy REAL NOT NULL,
        abs_m REAL,
        jobiph TEXT,
        root INTEGER,
        irrep INTEGER,
        multiplicity INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

def save_to_database(results: List[Dict], db_name="molcas_results.db"):
    """Zapisuje wyniki do bazy danych z poprawnym mapowaniem JOBIPH."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for result in results:
        distance = result['distance']
        
        # Tworzymy mapę JOBIPH dla szybkiego dostępu
        jobiph_map = {job['file']: job for job in result['jobiph_data']}
        
        for state, mappings in result['states_mapping'].items():
            energy = result['energies'].get(state, None)
            abs_m = result['abs_m'].get(state, None)
            
            for mapping in mappings:
                jobiph_name = mapping['jobiph']
                root = mapping['root']
                
                # Pobierz dane JOBIPH z mapy
                jobiph_info = jobiph_map.get(jobiph_name)
                
                # Debugowanie
                print(f"State {state}: JOBIPH={jobiph_name}, Root={root}, "
                      f"Irrep={jobiph_info['irrep'] if jobiph_info else None}, "
                      f"Mult={jobiph_info['multiplicity'] if jobiph_info else None}")
                
                cursor.execute("""
                INSERT INTO calculations (
                    distance, state_num, energy, abs_m, 
                    jobiph, root, irrep, multiplicity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    distance,
                    state,
                    energy,
                    abs_m,
                    jobiph_name,
                    root,
                    jobiph_info['irrep'] if jobiph_info else None,
                    jobiph_info['multiplicity'] if jobiph_info else None
                ))
    
    conn.commit()
    conn.close()
