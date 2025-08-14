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
        multiplicity INTEGER,
        order_index INTEGER,
        irrep_index INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

def save_to_database(results: List[Dict], db_name="molcas_results.db"):
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

def find_optimal_distance(db_name="molcas_results.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT distance, MIN(energy) 
    FROM calculations 
    GROUP BY distance
    ORDER BY energy
    LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def create_state_mapping(db_name="molcas_results.db", optimal_distance=None):
    if optimal_distance is None:
        optimal_distance = find_optimal_distance(db_name)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT state_num, energy, irrep, multiplicity
    FROM calculations
    WHERE distance = ?
    GROUP BY state_num
    ORDER BY energy
    """, (optimal_distance,))
    
    states = cursor.fetchall()
    
    state_mapping = {}
    order_index = 1
    
    for state_num, energy, irrep, multiplicity in states:
        state_mapping[state_num] = {
            'order_index': order_index,
            'irrep': irrep,
            'multiplicity': multiplicity,
            'energy': energy
        }
        order_index += 1
    
    conn.close()
    return optimal_distance, state_mapping


def update_database_with_mapping(db_name="molcas_results.db"):
    optimal_distance, state_mapping = create_state_mapping(db_name)
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Aktualizacja order_index
    for state_num, data in state_mapping.items():
        cursor.execute("""
        UPDATE calculations
        SET order_index = ?
        WHERE state_num = ?
        """, (data['order_index'], state_num))
    
    # Aktualizacja irrep_index
    cursor.execute("""
    SELECT DISTINCT distance, irrep, multiplicity, abs_m
    FROM calculations
    WHERE irrep IS NOT NULL AND multiplicity IS NOT NULL AND abs_m IS NOT NULL
    """)
    
    symmetry_groups = cursor.fetchall()
    
    for distance, irrep, multiplicity, abs_m in symmetry_groups:
        cursor.execute("""
        SELECT state_num
        FROM calculations
        WHERE distance = ? AND irrep = ? AND multiplicity = ? AND abs_m = ?
        GROUP BY state_num
        ORDER BY energy
        """, (distance, irrep, multiplicity, abs_m))
        
        states = cursor.fetchall()
        
        for index, (state_num,) in enumerate(states, start=1):
            cursor.execute("""
            UPDATE calculations
            SET irrep_index = ?
            WHERE state_num = ? AND distance = ?
            """, (index, state_num, distance))
    
    conn.commit()
    conn.close()
    
    return optimal_distance


    
#dodaj lambde 