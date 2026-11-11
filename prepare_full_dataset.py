import os
import shutil
import zipfile
import re
from pathlib import Path

def sanitize_name(name: str) -> str:
    # Lowercase, replace spaces with underscores, remove accents/special chars if needed
    name = name.strip().lower()
    name = re.sub(r'[\s\-]+', '_', name)
    return name

def main():
    zip_path = Path("C:/Users/phu14/Downloads/archive (1).zip")
    old_dataset = Path("C:/Users/phu14/Downloads/archive/dataset")
    out_dir = Path("C:/XLA/dataset_split")

    print("[*] Chuan bi thu muc du lieu moi...")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    
    (out_dir / "train").mkdir(parents=True, exist_ok=True)
    (out_dir / "val").mkdir(parents=True, exist_ok=True)

    # 1. Trich xuat cac mon tu archive (1).zip
    if zip_path.exists():
        print("[*] Dang doc danh sach anh tu archive (1).zip...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            namelist = z.namelist()
            
            # Group files by class
            train_map = {}
            val_map = {}
            
            for f in namelist:
                parts = f.replace('\\', '/').split('/')
                if len(parts) >= 3 and parts[0] == 'Images':
                    split_type = parts[1] # Train or Validate
                    raw_class = parts[2]
                    clean_class = sanitize_name(raw_class)
                    
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        if split_type == 'Train':
                            train_map.setdefault(clean_class, []).append(f)
                        elif split_type == 'Validate':
                            val_map.setdefault(clean_class, []).append(f)

            print(f"[+] Tim thay {len(train_map)} mon an trong zip.")
            
            # Extract up to 130 train images and 30 val images per class
            for cls_name, files in train_map.items():
                train_target = out_dir / "train" / cls_name
                train_target.mkdir(parents=True, exist_ok=True)
                
                selected = files[:130]
                for f in selected:
                    filename = Path(f).name
                    with z.open(f) as source, open(train_target / filename, 'wb') as target:
                        shutil.copyfileobj(source, target)
                        
            for cls_name, files in val_map.items():
                val_target = out_dir / "val" / cls_name
                val_target.mkdir(parents=True, exist_ok=True)
                
                selected = files[:30]
                for f in selected:
                    filename = Path(f).name
                    with z.open(f) as source, open(val_target / filename, 'wb') as target:
                        shutil.copyfileobj(source, target)

    # 2. Bo sung cac mon dac biet tu dataset cu (banh_trung_thu, banh_da_lon, banh_bo, etc.)
    extra_classes = ['banh_trung_thu', 'banh_da_lon', 'banh_bo', 'banh_cong', 'banh_tieu', 'banh_tai_heo']
    if old_dataset.exists():
        for extra in extra_classes:
            src_class_dir = old_dataset / extra
            if src_class_dir.exists():
                imgs = [f for f in src_class_dir.iterdir() if f.is_file() and f.suffix.lower() in ('.jpg', '.png', '.jpeg')]
                n_train = min(130, int(len(imgs) * 0.8))
                n_val = min(30, len(imgs) - n_train)
                
                train_target = out_dir / "train" / extra
                val_target = out_dir / "val" / extra
                train_target.mkdir(parents=True, exist_ok=True)
                val_target.mkdir(parents=True, exist_ok=True)
                
                for f in imgs[:n_train]:
                    shutil.copy2(f, train_target / f.name)
                for f in imgs[n_train:n_train+n_val]:
                    shutil.copy2(f, val_target / f.name)
                print(f"[+] Da them mon tu bo cu: {extra} ({n_train} train, {n_val} val)")

    all_train_classes = sorted([d.name for d in (out_dir / "train").iterdir() if d.is_dir()])
    print(f"\n[V] Tong so mon an duoc chuan bi cho mo hinh: {len(all_train_classes)} mon!")
    for idx, c in enumerate(all_train_classes, 1):
        print(f"  {idx:2d}. {c}")

if __name__ == '__main__':
    main()
