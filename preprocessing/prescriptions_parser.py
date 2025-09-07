import all_imports
from data import sample_csv
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------
# Load Local Drug DB (CSV/SQLite)
# ---------------------------
class DrugDatabase:
    def __init__(self, db_path: str = "drug_db.csv"):
        self.drug_df = pd.read_csv(db_path)  # columns: generic_name, synonyms, rxnorm_id, drugbank_id
        self.name_list = self.drug_df["generic_name"].tolist() + \
                         sum([s.split("|") for s in self.drug_df["synonyms"].dropna()], [])

    def match(self, query: str, cutoff: float = 0.7) -> Optional[Dict[str, Any]]:
        matches = get_close_matches(query.lower(), [n.lower() for n in self.name_list], n=1, cutoff=cutoff)
        if not matches:
            return None
        match = matches[0]
        row = self.drug_df[self.drug_df["generic_name"].str.lower() == match]
        if row.empty:
            row = self.drug_df[self.drug_df["synonyms"].str.lower().str.contains(match, na=False)]
        if row.empty:
            return None
        row = row.iloc[0]
        return {
            "match_name": row["generic_name"],
            "rxnorm_id": row.get("rxnorm_id", ""),
            "drugbank_id": row.get("drugbank_id", ""),
            "confidence": 0.9  # TODO: replace with similarity score
        }

# ---------------------------
# Medication Parser
# ---------------------------
class MedicationParser:
    UNIT_CONVERSIONS = {"mg": 1, "g": 1000, "mcg": 0.001}
    FREQ_MAP = {
        "od": {"times": 1, "desc": "once daily"},
        "bid": {"times": 2, "desc": "twice daily"},
        "tid": {"times": 3, "desc": "three times daily"},
        "qid": {"times": 4, "desc": "four times daily"},
        "prn": {"times": 0, "desc": "as needed"},
    }

    def __init__(self, db: DrugDatabase):
        self.db = db

    def parse_line(self, line: str) -> Dict[str, Any]:
        logging.info(f"Parsing line: {line}")
        cleaned = line.strip()

        # Dose extraction
        dose_val, dose_unit = None, None
        match = re.search(r"(\d+\.?\d*)\s*(mg|mcg|g)", cleaned, re.I)
        if match:
            dose_val, dose_unit = float(match.group(1)), match.group(2).lower()

        # Frequency extraction
        freq_info = {"raw": None, "times": None, "desc": None}
        for key, val in self.FREQ_MAP.items():
            if re.search(rf"\b{key}\b", cleaned.lower()):
                freq_info = {"raw": key, "times": val["times"], "desc": val["desc"]}
        if re.search(r"\d-\d-\d", cleaned):
            parts = list(map(int, re.findall(r"\d", cleaned)))
            freq_info = {"raw": cleaned, "times": sum(parts), "desc": f"{parts} doses/day"}

        # Route extraction
        route = None
        if "po" in cleaned.lower() or "oral" in cleaned.lower():
            route = "oral"
        elif "iv" in cleaned.lower():
            route = "intravenous"
        elif "im" in cleaned.lower():
            route = "intramuscular"

        # Drug matching
        words = re.findall(r"[A-Za-z]+", cleaned)
        drug_mapping = None
        for w in words:
            drug_mapping = self.db.match(w)
            if drug_mapping: break

        # Normalize units
        dose_mg = None
        if dose_val and dose_unit:
            dose_mg = dose_val * self.UNIT_CONVERSIONS.get(dose_unit, 1)

        return {
            "original": line,
            "cleaned": cleaned,
            "drug_mapping": drug_mapping,
            "dose_value": dose_val,
            "dose_unit": dose_unit,
            "dose_mg": dose_mg,
            "frequency": freq_info,
            "route": route,
            "parsed_at": datetime.utcnow().isoformat()
        }

    def parse_batch(self, lines: List[str]) -> Dict[str, Any]:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "medications": [self.parse_line(l) for l in lines]
        }

# ---------------------------
# Persistence Layer
# ---------------------------
class Storage:
    @staticmethod
    def save_json(obj: Dict, path: str):
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)

    @staticmethod
    def save_sqlite(obj: Dict, db_path: str = "healthcopilot.db"):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY,
                drug_name TEXT, rxnorm_id TEXT, dose_mg REAL, frequency TEXT, route TEXT, timestamp TEXT
            )
        """)
        for med in obj["medications"]:
            cur.execute("""
                INSERT INTO prescriptions (drug_name, rxnorm_id, dose_mg, frequency, route, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                med["drug_mapping"]["match_name"] if med["drug_mapping"] else None,
                med["drug_mapping"]["rxnorm_id"] if med["drug_mapping"] else None,
                med["dose_mg"], med["frequency"]["desc"], med["route"], med["parsed_at"]
            ))
        conn.commit(); conn.close()

# ---------------------------
# Example Run
# ---------------------------
if __name__ == "__main__":
    db = DrugDatabase("drug_db_sample.csv")
    parser = MedicationParser(db)
    sample = [
        "Tab Paracetmol 500mg PO 1-0-1",
        "Inj Ceftriakson 1 g IV OD",
        "Metfornin 850 mg BID"
    ]
    parsed = parser.parse_batch(sample)
    Storage.save_json(parsed, "parsed_demo.json")
    Storage.save_sqlite(parsed)
    print(json.dumps(parsed, indent=2))