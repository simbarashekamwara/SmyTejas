import json
import csv

class Cable_sizing:
    """
    This is a class to answer the question:
    Given a load current, an installation method, and a cable length, what is the smallest 
    conductor cross-section (mm²) that is both thermally safe and within allowed voltage drop?

    K1  installation method (how/where the cable is laid, e.g. embedded, in conduit, in free air)
    K2  mutual heating from other loaded circuits nearby (drops as more circuits share the same route)
    K3  ambient temperature vs. insulation type (PVC/PR/rubber tolerate heat differently)
    Ks — the symmetry correction factor for parallel cables
    Kn — the neutral conductor loading (harmonic) correction factor
    
    """
    def __init__(self):
        with open('reference_tables\\k2_correction_factors.csv', 'r') as file:
            reader = csv.DictReader(file)
            self.k2_data = [row for row in reader ] 

        with open('reference_tables\\k3_correction_factors.csv', 'r') as file:
            reader = csv.DictReader(file)
            self.k3_data = [row for row in reader ] 
         
    def case(self, k):
        """
        Method to select case of installation
        """
        if k == 1:
            print("Cases:\n1.embedded_directly_in_thermally_insulating_material\n2.conduit_embedded_in_thermally_insulating_mater\n3.multiconductor_cables\n4.construction_void_or_trench\n5.mounted_under_ceiling\n6.other_cases\n")

            choice =  int(input("Enter the case of installation: "))
            cases = [
                "embedded_directly_in_thermally_insulating_material",
                "conduit_embedded_in_thermally_insulating_material",
                "multiconductor_cables",
                "construction_void_or_trench",
                "mounted_under_ceiling",
                "other_cases",
                ]
            return cases[choice-1]

        elif k == 2:
            print("Arrangement:\n1.embedded_or_touching_in_walls\n2.single_layer_wall_floor_or_non_perforated_tray\n3.single_layer_ceiling\n4.single_layer_perforated_or_vertical_tray\n5.single_layer_ladders_brackets")
            choice =  int(input("Enter the case of Arrangement: "))
            cases = [
                    'embedded_or_touching_in_walls',
                    'single_layer_wall_floor_or_non_perforated_tray',
                    'single_layer_ceiling',
                    'single_layer_perforated_or_vertical_tray',
                    'single_layer_ladders_brackets',
                    ]
            return cases[choice-1]
        
        elif k==3:
            print("Insulation type:\n1.pvc\n2.pr_butyl_epr\n3.elastomer_rubber")
            choice = int(input("enter the insu type: "))
            cases = [
                "pvc",
                "elastomer_rubber",
                "pr_butyl_epr"
                ]
            return cases[choice-1]
        
        else:
            print("Neutral 3rd-harmonic loading correction:\n1. third_harmonic_rate_under_15_percent\n2. third_harmonic_rate_15_to_33_percent\n3. third_harmonic_rate_over_33_percent")
            choice = int(input("Select the 3rd-harmonic loading correction: "))
            cases = [ 
                        "third_harmonic_rate_under_15_percent",
                        "third_harmonic_rate_15_to_33_percent",
                        "third_harmonic_rate_over_33_percent"
                    ]
            return cases[choice-1]
        
        
    def get_k1(self, selection_letter, special_case):
        """
        Method to calculate K using data from k1_correction_factors.json
        """

        with open('reference_tables\\k1_correction_factors.json','r') as file:
            data =  json.load(file)

        if special_case == "other_cases":
            return data[special_case]
        return data[selection_letter][special_case]
        

    def get_k2(self, selection_letter, arrangement, num_circuits):
        """
        Method to calculate k2 
        """               
        lookup = {(row["selection_letter"], row["arrangement"], row["num_circuits"]): row["K2"] for row in self.k2_data }
        return lookup.get((selection_letter, arrangement, num_circuits))
    

    def get_k3(self, ambient_temp, insulation_type):
        """
        Method to get k3
        """

        lookup = {(row["ambient_temp_c"], row["insulation_type"]): row["K3"] for row in self.k3_data }
        return lookup.get((ambient_temp, insulation_type))


    def get_kn_ks(self, third_harmonic_rate):
        with open('reference_tables\\kn_ks_correction_factors.json','r') as file:
            data =  json.load(file)
        
        print("Parallel-cable symmetry correction\n1. 2_or_4_cables_per_phase_symmetric\n2. 2_3_or_4_cables_per_phase_not_symmetric_n3. default(1)")
        choice = int(input("Select Parallel-cable symmetry correction: "))
        
        if choice == 3:
            return 1
        is_symmetric = ["2_or_4_cables_per_phase_symmetric", "2_3_or_4_cables_per_phase_not_symmetric"][choice -1]
        return data['Kn'][third_harmonic_rate] *  data['Ks'][is_symmetric]
    
    
    def k_total(self):
        """
        - Methodalculate the K_total i.e global(overall or total) correction factor
        - K_total =  k1 * k2 * k3 * ks * kn
        """
        
        selection_letter = input("Enter selection_letter (B, C , Other): ")
        num_circuits = input("Enter number of circuits: ")
        temp = input("Enter the ambient temperature in  degree celcius: ")
        
        return self.get_k1(selection_letter, self.case(1)) * float(self.get_k2(selection_letter, self.case(2), num_circuits)) * float(self.get_k3(temp, self.case(3))) * self.get_kn_ks(self.case(4))


    
    def cable_size(self):
        """
        - Method to return the exact cable/wire cross sectional area in mm² by looking up in the *** using effective current.
        
        """
        
        k_total = self.k_total()
        print(f"Debugger: k_total = {k_total}")
        normal_current = float(input("Enter the normal current: "))
        effective_current = normal_current / k_total
        print(f"Debugger: Effective current is {round(effective_current, 1)}")
        return k_total
    
