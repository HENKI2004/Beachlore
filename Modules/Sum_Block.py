# Modules/Sum_Block.py
from .Block_Interface import Block_Interface
from .Faults import FAULTS
from collections import defaultdict

class Sum_Block(Block_Interface):

    def __init__(self, name: str, sub_blocks: list[Block_Interface]):
        self.name = name
        self.sub_blocks = sub_blocks

    def compute_fit(self, spfm_rates: dict, lfm_rates: dict) -> tuple[dict, dict]:
        # ... (Berechnungslogik bleibt identisch) ...
        total_spfm = spfm_rates.copy()
        total_lfm = lfm_rates.copy()
        for block in self.sub_blocks:
            res_spfm, res_lfm = block.compute_fit(spfm_rates, lfm_rates)
            for fault in set(res_spfm.keys()) | set(spfm_rates.keys()):
                delta = res_spfm.get(fault, 0.0) - spfm_rates.get(fault, 0.0)
                if delta != 0: total_spfm[fault] = total_spfm.get(fault, 0.0) + delta
            for fault in set(res_lfm.keys()) | set(lfm_rates.keys()):
                delta = res_lfm.get(fault, 0.0) - lfm_rates.get(fault, 0.0)
                if delta != 0: total_lfm[fault] = total_lfm.get(fault, 0.0) + delta
        return total_spfm, total_lfm

    def to_dot(self, dot, input_ports: dict) -> dict:
        # Sammler für neue Knoten-IDs, getrennt nach Pfadtyp
        rf_sources = defaultdict(list)
        lat_sources = defaultdict(list)

        with dot.subgraph(name=f"cluster_sum_{id(self)}") as c:
            c.attr(label=self.name, style="dotted", color="gray80", fontcolor="gray50")
            
            # 1. Alle Unterblöcke ausführen
            for block in self.sub_blocks:
                res_ports = block.to_dot(c, input_ports)
                
                for fault, ports in res_ports.items():
                    in_p = input_ports.get(fault, {})
                    
                    # Wir sammeln eine ID NUR, wenn sie sich vom Eingang unterscheidet
                    # (d.h. der Block hat hier etwas Neues erzeugt/geändert)
                    rf_p = ports.get('rf')
                    if rf_p and rf_p != in_p.get('rf'):
                        rf_sources[fault].append(rf_p)
                    
                    lat_p = ports.get('latent')
                    if lat_p and lat_p != in_p.get('latent'):
                        lat_sources[fault].append(lat_p)
            
            # 2. Finale Ausgänge bestimmen
            final_ports = {}
            # Wir betrachten alle Fehler aus dem Input und alle, die modifiziert wurden
            all_faults = set(input_ports.keys()) | set(rf_sources.keys()) | set(lat_sources.keys())
            
            for fault in all_faults:
                in_p = input_ports.get(fault, {'rf': None, 'latent': None})
                
                # --- RESIDUAL (RF) LOGIK ---
                srcs_rf = list(set(rf_sources[fault])) # Eindeutige neue IDs
                res_rf = None
                
                if len(srcs_rf) > 1:
                    # Mehrere neue Quellen -> Plus-Symbol (Summe)
                    j_id = f"junc_{fault.name}_rf_{id(self)}"
                    c.node(j_id, label="+", shape="circle", width="0.3", fixedsize="true", 
                           color="red", fontcolor="red", fontsize="10")
                    for s in srcs_rf:
                        c.edge(s, j_id, color="red")
                    res_rf = j_id
                elif len(srcs_rf) == 1:
                    # Nur eine neue Quelle -> Direkt weiterleiten
                    res_rf = srcs_rf[0]
                else:
                    # Keine Änderung durch Unterblöcke -> Original-Eingang beibehalten (Bypass)
                    res_rf = in_p.get('rf')

                # --- LATENT (L) LOGIK ---
                srcs_lat = list(set(lat_sources[fault]))
                res_lat = None
                
                if len(srcs_lat) > 1:
                    j_id = f"junc_{fault.name}_lat_{id(self)}"
                    c.node(j_id, label="+", shape="circle", width="0.3", fixedsize="true", 
                           color="blue", fontcolor="blue", fontsize="10")
                    for s in srcs_lat:
                        c.edge(s, j_id, color="blue", style="dashed")
                    res_lat = j_id
                elif len(srcs_lat) == 1:
                    res_lat = srcs_lat[0]
                else:
                    res_lat = in_p.get('latent')
                
                # Port-Dictionary für diesen Fehler aktualisieren
                final_ports[fault] = {'rf': res_rf, 'latent': res_lat}
                    
        return final_ports