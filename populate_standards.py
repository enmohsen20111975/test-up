"""
Populate reference standards for all calculations based on domain and type.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "workflows.db"

# Reference standards mapping
STANDARDS = {
    "electrical": {
        "apparent_power_3ph": "IEC 60038, IEC 60909",
        "power_ac_3ph": "IEC 60038, IEEE Std 1459",
        "power_dc": "NFPA 78 (DC systems)",
        "electrical_capacitive_reactance": "IEC 60038",
        "electrical_inductive_reactance": "IEC 60038",
        "electrical_impedance_series": "IEC 60038, NFPA 70",
        "grounding_rod": "IEEE Std 80 (Grounding)",
        "illumination_lumen_method": "CIE 8.4, IES LM-79",
        "ohms_law": "Basic Physics (Ohm's Law)",
        "power_factor": "IEC 60050-131 (Power Factor)",
        "short_circuit_mva": "IEC 60909, ANSI C37.5",
        "transformer_kva": "IEC 60076 (Transformers)",
        "voltage_drop_3ph": "IEC 60364-5-52, NFPA 70 (NEC)",
        "voltage_drop_dc": "IEEE 141 (DC Distribution)",
        "electric_power_ac_3ph": "IEEE 100-2000",
    },
    "mechanical": {
        "compressor_power": "ISO 1217 (Compressors)",
        "continuity_flow": "ISO 2941 (Fluid Power)",
        "cop": "ISO 13256 (Heat Pump COP)",
        "darcy_weisbach": "ISO 13707 (Friction loss)",
        "fan_power": "ASHRAE 90.1 (Fan Power)",
        "heat_transfer_conduction": "ISO 6946 (Thermal Insulation)",
        "heat_transfer_convection": "ISO 6946",
        "hvac_latent_load": "ASHRAE Handbook - Fundamentals",
        "hvac_sensible_load": "ASHRAE Handbook - Fundamentals",
        "ideal_gas": "ISO 6976 (Gas Properties)",
        "mechanical_bernoulli_equation": "ISO 2941 (Bernoulli)",
        "mechanical_heat_exchanger": "TEMA Standards (Heat Exchangers)",
        "mechanical_moment_of_inertia_rect": "ISO 6954 (Terminology)",
        "mechanical_thermal_expansion": "ISO 10149 (Thermal Expansion)",
        "mechanical_torsion_stress": "ASME BPVC (Torsional Stress)",
        "pump_power": "ISO 2041 (Pump Power)",
        "reynolds_number": "ISO 5167 (Reynolds Number)",
    },
    "civil": {
        "axial_stress": "EN 1992-1-1 (Concrete Design)",
        "beam_bending_stress": "EN 1992-1-1, AISC 360",
        "beam_deflection_ss_udl": "EN 1991-2-5 (Deflection)",
        "beam_shear_stress": "EN 1992-1-1 (Shear)",
        "column_buckling": "EN 1993-1-1 (Buckling)",
        "bearing_pressure": "EN 1997-1 (Bearing Capacity)",
        "retaining_wall_active_pressure": "EN 1997-1 (Earth Pressure)",
        "retaining_wall_passive_pressure": "EN 1997-1",
        "settlement_elastic": "EN 1997-2 (Settlement)",
        "terzaghi_bearing_capacity": "EN 1997-1 (Bearing Calculation)",
        "manning_flow": "ISO 1438 (Manning's Formula)",
    }
}

def populate_references():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        updated_count = 0
        
        for domain, mappings in STANDARDS.items():
            print(f"\nProcessing {domain} standards...")
            
            for calc_id, reference in mappings.items():
                # Update calculation with reference where it's NULL or empty
                cur.execute("""
                    UPDATE calculations 
                    SET reference = ?
                    WHERE calculation_id = ? AND (reference IS NULL OR reference = '')
                """, (reference, calc_id))
                
                if cur.rowcount > 0:
                    updated_count += cur.rowcount
                    print(f"  ✓ {calc_id}: {reference}")
        
        conn.commit()
        print(f"\n✓ Updated {updated_count} calculation reference(s) with standards")
        
        # Show summary
        cur.execute("""
            SELECT w.domain, COUNT(*) as with_ref, 
                   SUM(CASE WHEN c.reference IS NULL OR c.reference = '' THEN 1 ELSE 0 END) as without_ref
            FROM calculations c
            JOIN workflow_steps ws ON c.id = ws.calculation_id
            JOIN workflows w ON ws.workflow_id = w.id
            GROUP BY w.domain
            ORDER BY w.domain
        """)
        
        print("\nReference Coverage by Domain:")
        for domain, with_ref, without_ref in cur.fetchall():
            total = with_ref + (without_ref or 0)
            pct = (with_ref / total * 100) if total > 0 else 0
            print(f"  {domain}: {with_ref}/{total} ({pct:.0f}%)")
    
    finally:
        conn.close()

if __name__ == "__main__":
    populate_references()
