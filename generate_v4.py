r"""
FOMO NFT Generator v4 - Uses psd_traits PNG layers + traits_config.json
All source files from C:\Users\D\Downloads\psd_traits\ only.
"""
import numpy as np
from PIL import Image
import hashlib, json, os, random
from collections import Counter

BASE = r"C:\Users\D\Downloads\psd_traits"
OUT_DIR = r"C:\Users\D\fomo-nft"
IMG_DIR = os.path.join(OUT_DIR, "images")
META_DIR = os.path.join(OUT_DIR, "metadata")
SUPPLY = 10000

os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

# Clear old
import glob
for f in glob.glob(os.path.join(IMG_DIR, "*.png")): os.remove(f)
for f in glob.glob(os.path.join(META_DIR, "*.json")): os.remove(f)

# Load bbox config
with open(os.path.join(BASE, "traits_config.json")) as f:
    config = json.load(f)

def load_trait_pngs(folder, config_key, name_map=None):
    """Load all PNGs from a trait folder, map to config bbox keys.
    name_map: {filename_without_ext: config_number_key} or None for numeric filenames.
    """
    folder_path = os.path.join(BASE, folder)
    layers = {}
    if not os.path.isdir(folder_path):
        print(f"  WARNING: {folder} not found")
        return layers
    
    bboxes = config["traits"].get(config_key, {})
    
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith('.png'):
            continue
        name_noext = os.path.splitext(fname)[0]
        
        # Determine config key
        if name_map:
            ckey = name_map.get(name_noext)
        else:
            ckey = name_noext
        
        if ckey is None or ckey not in bboxes:
            print(f"  WARNING: {folder}/{fname} -> no bbox for key '{ckey}'")
            continue
        
        img = Image.open(os.path.join(folder_path, fname)).convert('RGBA')
        bbox = bboxes[ckey]["bbox"]  # [x1,y1,x2,y2]
        layers[name_noext] = (np.array(img).astype(np.float32)/255.0, bbox)
        # print(f"  Loaded {folder}/{fname} -> key={ckey}, bbox={bbox}")
    
    return layers

# --- Ear name mapping (psd_traits filenames -> config bbox keys) ---
EAR_NAME_MAP = {
    "human": "1", "superhuman": "2", "demon": "3", "dwarf": "4", "elf": "5"
}
EAR_DISPLAY = {
    "human": "Human Ears", "superhuman": "Superhuman Ears",
    "demon": "Demon Ears", "dwarf": "Dwarf Ears", "elf": "Elf Ears"
}

# --- Eye "red eye" -> config key "10" ---
EYE_NAME_MAP = {
    "red eye": "10"
}
EYE_DISPLAY = {}
for i in range(1, 10):
    EYE_DISPLAY[str(i)] = f"Eyes {i}"
EYE_DISPLAY["red eye"] = "Red Eyes"
# Also map numeric config keys back to display
for i in range(1, 10):
    EYE_NAME_MAP[str(i)] = str(i)

# --- Trait display names ---
HAIR_DISPLAY = {str(i): f"Hair {i}" for i in range(1, 10)}
HEAD_DISPLAY = {str(i): f"Head {i}" for i in range(1, 6)}
SHOULDER_DISPLAY = {str(i): f"Shoulders {i}" for i in range(1, 6)}
NOSE_DISPLAY = {str(i): f"Nose {i}" for i in range(1, 10)}
LIPS_DISPLAY = {str(i): f"Lips {i}" for i in range(1, 10)}

print("Loading trait PNGs...")
shoulder = load_trait_pngs("5_shoulders", "5 shoulders")
head = load_trait_pngs("5_head", "5 head")
ear = load_trait_pngs("5_Ears", "5 Ears", EAR_NAME_MAP)
nose = load_trait_pngs("9_Nose", "9 Nose")
lips = load_trait_pngs("9_Lips", "9 Lips")
eye = load_trait_pngs("9_Eyes", "9 Eyes", EYE_NAME_MAP)
hair = load_trait_pngs("9_hair", "9 hair")

# Load backgrounds
bg_layers = {}
bg_folder = os.path.join(BASE, "backgrounds")
bg_bboxes = config.get("backgrounds", {})
for fname in os.listdir(bg_folder):
    if not fname.lower().endswith('.png'):
        continue
    name_noext = os.path.splitext(fname)[0]
    bb = bg_bboxes.get(name_noext)
    if bb is None:
        print(f"  WARNING: background {fname} -> no bbox for '{name_noext}'")
        continue
    img = Image.open(os.path.join(bg_folder, fname)).convert('RGBA')
    bg_layers[name_noext] = (np.array(img).astype(np.float32)/255.0, bb["bbox"])

BG_DISPLAY = {
    "moon": "Moon", "sun": "Sun", "stars": "Stars", "clouds": "Clouds",
    "trees": "Trees", "flowers": "Flowers", "grass": "Grass",
    "Butterflies": "Butterflies", "thunder": "Thunder", "house": "House",
    "cat": "Cat", "cars": "Cars"
}

print(f"  Shoulders: {len(shoulder)}  Head: {len(head)}  Ears: {len(ear)}")
print(f"  Nose: {len(nose)}  Lips: {len(lips)}  Eyes: {len(eye)}  Hair: {len(hair)}")
print(f"  Backgrounds: {len(bg_layers)}")

# --- Trait definitions with rarity weights ---
TRAITS = {
    "Background": [
        ("Plain White",20), ("moon",8), ("sun",8), ("stars",8), ("clouds",8),
        ("trees",8), ("flowers",8), ("grass",8), ("Butterflies",6), ("thunder",6),
        ("house",6), ("cat",6), ("cars",6),
    ],
    "Head": [
        ("1",25), ("2",20), ("3",20), ("4",18), ("5",17),
    ],
    "Shoulders": [
        ("1",22), ("2",20), ("3",20), ("4",20), ("5",18),
    ],
    "Ears": [
        ("human",484), ("superhuman",500), ("demon",10), ("dwarf",5), ("elf",1),
    ],
    "Hair": [
        ("1",18), ("2",14), ("3",14), ("4",3), ("5",5),
        ("6",12), ("7",14), ("8",8), ("9",12),
    ],
    "Eyes": [
        ("red eye",1),
        ("1",14), ("2",14), ("3",14), ("5",14),
        ("6",14), ("7",14), ("8",14), ("9",14),
    ],
    "Nose": [
        ("1",14), ("2",12), ("3",11), ("4",12),
        ("5",12), ("6",10), ("7",11), ("8",8), ("9",10),
    ],
    "Lips": [
        ("1",12), ("2",4), ("3",4), ("4",12),
        ("5",12), ("6",12), ("7",12), ("8",8), ("9",4),
    ],
}

DISPLAY = {
    "Background": BG_DISPLAY,
    "Head": HEAD_DISPLAY,
    "Shoulders": SHOULDER_DISPLAY,
    "Ears": EAR_DISPLAY,
    "Hair": HAIR_DISPLAY,
    "Eyes": EYE_DISPLAY,
    "Nose": NOSE_DISPLAY,
    "Lips": LIPS_DISPLAY,
}

# Layer lookup by trait
LAYER_MAP = {
    "Shoulders": shoulder,
    "Head": head,
    "Ears": ear,
    "Hair": hair,
    "Eyes": eye,
    "Nose": nose,
    "Lips": lips,
}

# --- Composite function ---
def composite_over(canvas, layer_np, bbox):
    """Alpha composite a layer onto canvas at its bbox position."""
    x1, y1, x2, y2 = bbox
    lh, lw = layer_np.shape[:2]
    bw, bh = x2 - x1, y2 - y1
    
    # Resize if layer doesn't match bbox size
    if lw != bw or lh != bh:
        pil = Image.fromarray((np.clip(layer_np, 0, 1) * 255).astype(np.uint8), 'RGBA')
        pil = pil.resize((bw, bh), Image.LANCZOS)
        layer_np = np.array(pil).astype(np.float32) / 255.0
    
    # Clip to canvas bounds
    cx1, cy1 = max(0, x1), max(0, y1)
    cx2, cy2 = min(1024, x2), min(1024, y2)
    lx1, ly1 = cx1 - x1, cy1 - y1
    lx2, ly2 = lx1 + (cx2 - cx1), ly1 + (cy2 - cy1)
    
    sa = layer_np[ly1:ly2, lx1:lx2, 3:4]
    sr = layer_np[ly1:ly2, lx1:lx2, :3]
    dr = canvas[cy1:cy2, cx1:cx2, :3]
    canvas[cy1:cy2, cx1:cx2, :3] = sr * sa + dr * (1 - sa)

def composite_nft(bg_name, shoulder_key, head_key, ear_key, hair_key, eye_key, nose_key, lips_key):
    canvas = np.ones((1024, 1024, 4), dtype=np.float32)
    
    # Background
    if bg_name != "Plain White" and bg_name in bg_layers:
        composite_over(canvas, *bg_layers[bg_name])
    
    # Layer order: shoulders -> head -> ears -> hair -> eyes -> nose -> lips
    for layer_dict, key in [
        (shoulder, shoulder_key),
        (head, head_key),
        (ear, ear_key),
        (hair, hair_key),
        (eye, eye_key),
        (nose, nose_key),
        (lips, lips_key),
    ]:
        if key in layer_dict:
            composite_over(canvas, *layer_dict[key])
    
    return np.clip(canvas, 0, 1)

# --- Generate ---
print(f"\nGenerating {SUPPLY} NFTs...", flush=True)
used = set()

for tid in range(1, SUPPLY + 1):
    seed = int(hashlib.sha256(f"fomo-v4-{tid}".encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    for retry in range(100):
        sel = {}
        for cat, variants in TRAITS.items():
            names = [v[0] for v in variants]
            wts = [v[1] for v in variants]
            if retry > 0:
                wts = [w + rng.randint(0, 2) for w in wts]
            sel[cat] = rng.choices(names, weights=wts, k=1)[0]
        
        combo = tuple(sel[c] for c in TRAITS.keys())
        if combo not in used:
            used.add(combo)
            break
    
    canvas = composite_nft(
        sel["Background"],
        sel["Shoulders"], sel["Head"], sel["Ears"],
        sel["Hair"], sel["Eyes"], sel["Nose"], sel["Lips"],
    )
    
    img = Image.fromarray((canvas * 255).astype(np.uint8), 'RGBA')
    img.save(os.path.join(IMG_DIR, f"{tid}.png"))
    
    # Build attributes with display names
    attrs = []
    for cat in ["Background", "Head", "Shoulders", "Ears", "Hair", "Eyes", "Nose", "Lips"]:
        val = sel[cat]
        display = DISPLAY[cat].get(val, val)
        attrs.append({"trait_type": cat, "value": display})
    
    meta = {
        "name": f"Fear Of Missing Outline #{tid}",
        "description": "Hand-drawn grayscale character art. Red Eyes, Elf Ears, Dwarf Ears, and Demon Ears are the rarest traits.",
        "image": f"ipfs://CID/{tid}.png",
        "attributes": attrs,
        "properties": {
            "files": [{"uri": f"{tid}.png", "type": "image/png"}],
            "category": "image",
            "creators": [{"address": "YOUR_WALLET_ADDRESS", "share": 100}]
        }
    }
    with open(os.path.join(META_DIR, f"{tid}.json"), 'w') as f:
        json.dump(meta, f, indent=2)
    
    if tid % 500 == 0:
        print(f"  {tid}/{SUPPLY} ({tid*100//SUPPLY}%)", flush=True)

print(f"\n{len(used)} unique NFTs generated.", flush=True)

# --- Rarity scoring ---
print("Calculating rarity...", flush=True)
MAX_WEIGHTS = {
    "Background": 20, "Head": 25, "Shoulders": 22, "Ears": 500,
    "Hair": 18, "Eyes": 14, "Nose": 14, "Lips": 12,
}
TRAIT_WEIGHTS = {cat: dict(variants) for cat, variants in TRAITS.items()}

scores = []
for tid in range(1, SUPPLY + 1):
    with open(os.path.join(META_DIR, f"{tid}.json")) as f:
        meta = json.load(f)
    attrs = {a["trait_type"]: a["value"] for a in meta["attributes"]}
    
    # Map display names back to internal keys for weight lookup
    rev_bg = {v: k for k, v in BG_DISPLAY.items()}
    rev_ear = {v: k for k, v in EAR_DISPLAY.items()}
    rev_eye = {v: k for k, v in EYE_DISPLAY.items()}
    rev_hair = {v: k for k, v in HAIR_DISPLAY.items()}
    rev_head = {v: k for k, v in HEAD_DISPLAY.items()}
    rev_shoulder = {v: k for k, v in SHOULDER_DISPLAY.items()}
    rev_nose = {v: k for k, v in NOSE_DISPLAY.items()}
    rev_lips = {v: k for k, v in LIPS_DISPLAY.items()}
    
    rev_map = {
        "Background": rev_bg, "Ears": rev_ear, "Eyes": rev_eye,
        "Hair": rev_hair, "Head": rev_head, "Shoulders": rev_shoulder,
        "Nose": rev_nose, "Lips": rev_lips,
    }
    
    num_cats = len(MAX_WEIGHTS)
    total_score = 0.0
    for cat, max_w in MAX_WEIGHTS.items():
        display_val = attrs.get(cat, "")
        internal_val = rev_map.get(cat, {}).get(display_val, display_val)
        weight = TRAIT_WEIGHTS.get(cat, {}).get(internal_val, max_w)
        cat_score = (1.0 - weight / max_w) * (100.0 / num_cats)
        total_score += cat_score
    
    total_score = round(total_score, 1)
    scores.append(total_score)
    meta["rarity_score"] = total_score
    with open(os.path.join(META_DIR, f"{tid}.json"), 'w') as f:
        json.dump(meta, f, indent=2)

scores_sorted = sorted(scores, reverse=True)
tier_counts = Counter()

for tid in range(1, SUPPLY + 1):
    with open(os.path.join(META_DIR, f"{tid}.json")) as f:
        meta = json.load(f)
    attrs = {a["trait_type"]: a["value"] for a in meta["attributes"]}
    eyes = attrs.get("Eyes", "")
    ears = attrs.get("Ears", "")
    score = meta["rarity_score"]
    
    if eyes == "Red Eyes" or ears in ("Elf Ears", "Dwarf Ears", "Demon Ears"):
        tier = "Legendary"
    elif score >= scores_sorted[int(SUPPLY * 0.10)]:
        tier = "Epic"
    elif score >= scores_sorted[int(SUPPLY * 0.25)]:
        tier = "Rare"
    elif score >= scores_sorted[int(SUPPLY * 0.50)]:
        tier = "Uncommon"
    else:
        tier = "Common"
    
    meta["rarity_tier"] = tier
    tier_counts[tier] += 1
    with open(os.path.join(META_DIR, f"{tid}.json"), 'w') as f:
        json.dump(meta, f, indent=2)

# Count specials
red_eyes = elf = dwarf = demon = 0
for tid in range(1, SUPPLY + 1):
    with open(os.path.join(META_DIR, f"{tid}.json")) as f:
        meta = json.load(f)
    attrs = {a["trait_type"]: a["value"] for a in meta["attributes"]}
    if attrs.get("Eyes") == "Red Eyes": red_eyes += 1
    if attrs.get("Ears") == "Elf Ears": elf += 1
    if attrs.get("Ears") == "Dwarf Ears": dwarf += 1
    if attrs.get("Ears") == "Demon Ears": demon += 1

print("\n=== RARITY DISTRIBUTION ===")
for tier in ["Legendary", "Epic", "Rare", "Uncommon", "Common"]:
    c = tier_counts.get(tier, 0)
    print(f"  {tier:12s}: {c:5d} ({c*100/SUPPLY:5.1f}%)")

print(f"\n=== SPECIAL TRAITS ===")
print(f"  Red Eyes:   {red_eyes:5d} ({red_eyes*100/SUPPLY:.2f}%)")
print(f"  Elf Ears:   {elf:5d} ({elf*100/SUPPLY:.2f}%)")
print(f"  Dwarf Ears: {dwarf:5d} ({dwarf*100/SUPPLY:.2f}%)")
print(f"  Demon Ears: {demon:5d} ({demon*100/SUPPLY:.2f}%)")

print(f"\nDone! Images: {IMG_DIR}")
print(f"Metadata: {META_DIR}")
