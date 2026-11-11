import os
import shutil
from pathlib import Path
from ultralytics import YOLO

def main():
    data_dir = 'C:/XLA/dataset_split'
    model_path = 'C:/XLA/yolov8s-cls.pt'
    
    print("[*] Khoi tao mo hinh YOLOv8s-cls (Chinh xac cao, 5.1M params)...")
    model = YOLO(model_path)

    print("[*] Bat dau huan luyen nang cao do chinh xac (36 mon, imgsz=192, AdamW + RandAugment)...")
    results = model.train(
        data=data_dir,
        epochs=12,
        imgsz=192,
        batch=64,
        workers=2,
        optimizer='AdamW',
        lr0=0.001,
        cos_lr=True,
        auto_augment='randaugment',
        fliplr=0.5,
        erasing=0.2,
        project='C:/XLA/runs/classify',
        name='vn_foods_high_acc',
        exist_ok=True,
        verbose=True
    )

    best_pt_source = Path(model.trainer.save_dir) / 'weights' / 'best.pt'
    dest_pt = Path('C:/XLA/best.pt')

    if best_pt_source.exists():
        shutil.copy2(best_pt_source, dest_pt)
        print(f"[+] Huan luyen thanh cong! Da cap nhat trong so do chinh xac cao vao: {dest_pt}")
    else:
        print("[-] Khong tim thay best.pt tai:", best_pt_source)

if __name__ == '__main__':
    main()
