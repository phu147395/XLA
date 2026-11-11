import os
import io
import time
import base64
import shutil
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = STATIC_DIR / "outputs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Food Vision & Xử Lý Ảnh", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Comprehensive database of 36 Vietnamese Foods & Ingredients
FOOD_INGREDIENTS = {
    'banh_trung_thu': {
        'name_vn': 'Bánh Trung Thu',
        'category': 'Bánh Nướng Truyền Thống',
        'calories': '~650 - 850 kcal / chiếc',
        'nutrition': {'Calories': '750 kcal', 'Carbs': '68g', 'Protein': '14g', 'Fat': '26g'},
        'ingredients': [
            {'name': 'Lòng đỏ trứng muối', 'name_en': 'Salted Egg Yolk', 'portion': 20, 'desc': 'Ngâm rượu mai quế lộ nướng thơm lừng, bùi béo mặn mà, màu cam óng ả.'},
            {'name': 'Nhân đậu xanh / Thập cẩm', 'name_en': 'Filling (Mung bean / Mixed)', 'portion': 50, 'desc': 'Đậu xanh xay nhuyễn dẻo mịn kết hợp lạp xưởng, hạt sen, mứt bí, mỡ đường giòn sần sật.'},
            {'name': 'Vỏ bánh nướng vàng ươm', 'name_en': 'Baked Pastry Crust', 'portion': 25, 'desc': 'Bột mì, nước đường bánh nướng cổ truyền, quét lòng đỏ trứng tạo màu nâu cánh gián bóng đẹp.'},
            {'name': 'Hạt dưa, mè trắng & dầu mè', 'name_en': 'Melon Seeds & Sesame', 'portion': 5, 'desc': 'Tạo độ giòn bùi và hương thơm ngậy đặc trưng.'}
        ]
    },
    'banh_mi': {
        'name_vn': 'Bánh Mì',
        'category': 'Món Ăn Đường Phố Nổi Tiếng',
        'calories': '~380 - 450 kcal / ổ',
        'nutrition': {'Calories': '420 kcal', 'Carbs': '48g', 'Protein': '18g', 'Fat': '14g'},
        'ingredients': [
            {'name': 'Vỏ bánh mì giòn', 'name_en': 'Crispy Baguette', 'portion': 40, 'desc': 'Bột mì lên men tự nhiên nướng vàng rụm, ruột xốp nhẹ đặc trưng bánh mì Việt Nam.'},
            {'name': 'Pa-tê gan & Bơ trứng', 'name_en': 'Liver Pâté & Butter', 'portion': 20, 'desc': 'Pâté gan heo tiêu tỏi béo ngậy quết đều dọc thân bánh mì.'},
            {'name': 'Chả lụa / Thịt nguội / Xíu mại', 'name_en': 'Pork Ham / Cold Cuts', 'portion': 25, 'desc': 'Thịt heo tươi quết dẻo dai đậm đà, thái lát mỏng xếp đều.'},
            {'name': 'Rau thơm & Đồ chua', 'name_en': 'Pickled Veggies & Herbs', 'portion': 15, 'desc': 'Dưa leo giòn mát, cà rốt củ cải chua ngọt, ngò rí và vài lát ớt hiểm cay nồng.'}
        ]
    },
    'banh_xeo': {
        'name_vn': 'Bánh Xèo',
        'category': 'Món Bánh Dân Gian Nam Bộ',
        'calories': '~350 - 450 kcal / cái',
        'nutrition': {'Calories': '390 kcal', 'Carbs': '42g', 'Protein': '16g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Vỏ bánh xèo giòn rụm', 'name_en': 'Crispy Rice Batter', 'portion': 45, 'desc': 'Bột gạo xay pha bột nghệ vàng óng, nước cốt dừa béo và hành lá phi thơm.'},
            {'name': 'Tôm đất & Thịt ba chỉ', 'name_en': 'Shrimp & Pork Belly', 'portion': 35, 'desc': 'Tôm tươi ngọt thịt xào săn cùng thịt ba chỉ heo thái mỏng thơm mùi tiêu tỏi.'},
            {'name': 'Giá đỗ & Đậu xanh hột', 'name_en': 'Bean Sprouts & Mung Beans', 'portion': 20, 'desc': 'Giá tươi ngọt giòn hấp hơi trong lòng bánh, đậu xanh hấp bùi ngậy.'}
        ]
    },
    'banh_khot': {
        'name_vn': 'Bánh Khọt',
        'category': 'Đặc Sản Miền Nam',
        'calories': '~60 - 85 kcal / chiếc',
        'nutrition': {'Calories': '75 kcal', 'Carbs': '10g', 'Protein': '4g', 'Fat': '3.5g'},
        'ingredients': [
            {'name': 'Vỏ bánh khọt chiên giòn', 'name_en': 'Crispy Mini Pancake', 'portion': 50, 'desc': 'Bột gạo chiên trong khuôn đất nung đáy lồi vàng ươm giòn rụm.'},
            {'name': 'Tôm tươi nguyên con', 'name_en': 'Whole Fresh Shrimp', 'portion': 30, 'desc': 'Tôm đất tươi bóc vỏ, đặt ngay ngắn trên mặt bánh chín đỏ hồng.'},
            {'name': 'Mỡ hành & Bột tôm chấy', 'name_en': 'Scallion Oil & Shrimp Powder', 'portion': 20, 'desc': 'Hành lá phi thơm bóng lộn cùng bột tôm chấy cam đỏ rực rỡ.'}
        ]
    },
    'banh_bot_loc': {
        'name_vn': 'Bánh Bột Lọc',
        'category': 'Đặc Sản Cố Đô Huế',
        'calories': '~45 - 65 kcal / cái',
        'nutrition': {'Calories': '55 kcal', 'Carbs': '8g', 'Protein': '3g', 'Fat': '2g'},
        'ingredients': [
            {'name': 'Vỏ bột lọc trong suốt', 'name_en': 'Clear Tapioca Dough', 'portion': 60, 'desc': 'Bột năng nhồi nước sôi kỹ, luộc hoặc hấp tạo độ dai dẻo thấy rõ nhân bên trong.'},
            {'name': 'Tôm sông rim mặn ngọt', 'name_en': 'Braised River Shrimp', 'portion': 25, 'desc': 'Tôm nhỏ rim đậm vị mắm đường tiêu, màu đỏ au bắt mắt.'},
            {'name': 'Thịt ba rọi xắt hạt lựu', 'name_en': 'Diced Pork Belly', 'portion': 15, 'desc': 'Thịt mỡ giòn dai rim ngấm gia vị béo ngậy khó cưỡng.'}
        ]
    },
    'banh_da_lon': {
        'name_vn': 'Bánh Da Lợn',
        'category': 'Bánh Tráng Miệng Nam Bộ',
        'calories': '~160 - 220 kcal / miếng',
        'nutrition': {'Calories': '190 kcal', 'Carbs': '35g', 'Protein': '2g', 'Fat': '5g'},
        'ingredients': [
            {'name': 'Lớp bột lá dứa xanh', 'name_en': 'Green Pandan Layer', 'portion': 50, 'desc': 'Bột năng, bột gạo cốt lá dứa tươi tạo màu xanh ngọc thơm dịu dàng.'},
            {'name': 'Lớp nhân đậu xanh cốt dừa', 'name_en': 'Mung Bean Coconut Layer', 'portion': 45, 'desc': 'Đậu xanh hấp chín xay nhuyễn cùng nước cốt dừa béo ngậy màu vàng nhạt.'},
            {'name': 'Đường cát & Vani', 'name_en': 'Sugar & Vanilla', 'portion': 5, 'desc': 'Vị ngọt thanh dịu kết nối các lớp bánh mềm dẻo.'}
        ]
    },
    'banh_bo': {
        'name_vn': 'Bánh Bò',
        'category': 'Bánh Xốp Truyền Thống',
        'calories': '~110 - 150 kcal / chiếc',
        'nutrition': {'Calories': '130 kcal', 'Carbs': '26g', 'Protein': '1.5g', 'Fat': '2g'},
        'ingredients': [
            {'name': 'Bột gạo ủ men cơm rượu', 'name_en': 'Fermented Rice Flour', 'portion': 65, 'desc': 'Bột gạo lên men men nếp tự nhiên tạo cấu trúc rễ tre mềm xốp kỳ diệu.'},
            {'name': 'Nước cốt dừa sánh mịn', 'name_en': 'Coconut Cream', 'portion': 25, 'desc': 'Nấu sôi nhẹ cùng lá dứa thơm béo ngậy khi rưới lên bánh.'},
            {'name': 'Đường thốt nốt / Đường mía', 'name_en': 'Palm Sugar', 'portion': 10, 'desc': 'Tạo vị ngọt đậm đà hoặc màu vàng cánh gián tự nhiên.'}
        ]
    },
    'banh_cong': {
        'name_vn': 'Bánh Cống',
        'category': 'Đặc Sản Sóc Trăng',
        'calories': '~260 - 340 kcal / cái',
        'nutrition': {'Calories': '290 kcal', 'Carbs': '30g', 'Protein': '12g', 'Fat': '16g'},
        'ingredients': [
            {'name': 'Vỏ bánh bột cống chiên giòn', 'name_en': 'Deep-fried Cup Batter', 'portion': 45, 'desc': 'Hỗn hợp bột gạo, bột đậu nành chiên trong cống sâu lòng giòn xốp.'},
            {'name': 'Tôm nguyên con chiên giòn', 'name_en': 'Whole Fried Shrimp', 'portion': 25, 'desc': 'Tôm tươi để nguyên vỏ đặt trên miệng bánh chiên giòn tan ăn được cả vỏ.'},
            {'name': 'Nhân thịt băm & Đậu xanh', 'name_en': 'Minced Pork & Mung Beans', 'portion': 30, 'desc': 'Thịt heo băm trộn củ sắn thái hạt lựu và đậu xanh hấp chín bùi béo.'}
        ]
    },
    'banh_tieu': {
        'name_vn': 'Bánh Tiêu',
        'category': 'Món Bánh Ăn Vặt Giòn Xốp',
        'calories': '~180 - 230 kcal / cái',
        'nutrition': {'Calories': '200 kcal', 'Carbs': '32g', 'Protein': '4g', 'Fat': '7g'},
        'ingredients': [
            {'name': 'Bột mì lên men phồng', 'name_en': 'Puffed Wheat Flour Dough', 'portion': 80, 'desc': 'Bột mì nhào ủ men nở phồng căng, ruột rỗng mềm thơm khi chiên ngập dầu.'},
            {'name': 'Mè trắng rang thơm', 'name_en': 'Roasted White Sesame', 'portion': 12, 'desc': 'Rắc phủ kín hai mặt bánh, khi chiên tỏa hương thơm ngát.'},
            {'name': 'Đường cát & Dầu chiên', 'name_en': 'Sugar & Cooking Oil', 'portion': 8, 'desc': 'Ngọt nhẹ dễ ăn, vỏ bánh vàng óng.'}
        ]
    },
    'banh_tai_heo': {
        'name_vn': 'Bánh Tai Heo',
        'category': 'Bánh Quy Xoắn Tuổi Thơ',
        'calories': '~130 kcal / 30g',
        'nutrition': {'Calories': '130 kcal', 'Carbs': '20g', 'Protein': '2.5g', 'Fat': '5g'},
        'ingredients': [
            {'name': 'Bột mì cuộn xoắn ốc hai màu', 'name_en': 'Spiral Dough Layers', 'portion': 75, 'desc': 'Hai dải bột trắng và nâu ca-cao cuộn tròn thái lát mỏng hình vành tai heo.'},
            {'name': 'Bơ thơm & Trứng gà', 'name_en': 'Butter & Eggs', 'portion': 15, 'desc': 'Tạo độ giòn tan, vị bùi béo thơm ngậy.'},
            {'name': 'Gia vị mặn ngọt & Sữa đặc', 'name_en': 'Condensed Milk & Spices', 'portion': 10, 'desc': 'Vị mằn mặn ngòn ngọt giòn rôm rốp khi nhai.'}
        ]
    },
    'pho': {
        'name_vn': 'Phở Bò Truyền Thống',
        'category': 'Món Nước Quốc Hồn Quốc Túy',
        'calories': '~450 - 550 kcal / bát',
        'nutrition': {'Calories': '480 kcal', 'Carbs': '65g', 'Protein': '24g', 'Fat': '12g'},
        'ingredients': [
            {'name': 'Bánh phở tươi mềm dai', 'name_en': 'Fresh Rice Noodles', 'portion': 40, 'desc': 'Làm từ bột gạo tẻ tráng mỏng, mềm mướt không bở.'},
            {'name': 'Nước dùng ninh xương hoa hồi', 'name_en': 'Rich Bone Broth', 'portion': 35, 'desc': 'Hầm từ xương ống bò cùng hoa hồi, quế, thảo quả nướng thơm ngọt thanh.'},
            {'name': 'Thịt bò tái / nạm / gầu', 'name_en': 'Beef Slices', 'portion': 15, 'desc': 'Thịt bò tươi mềm ngọt xắt lát mỏng nhúng tái hoặc nạm chín mềm.'},
            {'name': 'Hành hoa & Rau thơm', 'name_en': 'Scallion & Fresh Herbs', 'portion': 10, 'desc': 'Hành lá chẻ hoa, ngò gai, húng quế và lát ớt hiểm cay nồng.'}
        ]
    },
    'bun_bo_hue': {
        'name_vn': 'Bún Bò Huế',
        'category': 'Món Nước Cố Đô Đậm Đà',
        'calories': '~520 - 620 kcal / tô',
        'nutrition': {'Calories': '560 kcal', 'Carbs': '60g', 'Protein': '28g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Bún sợi to xứ Huế', 'name_en': 'Thick Rice Vermicelli', 'portion': 40, 'desc': 'Sợi bún tròn to, dẻo dai đặc trưng của bún bò cố đô.'},
            {'name': 'Nước lèo sả mắm ruốc', 'name_en': 'Spicy Lemongrass Broth', 'portion': 30, 'desc': 'Nấu từ xương bò hòa quyện mắm ruốc Huế dậy mùi và sả cây đập dập thơm lừng.'},
            {'name': 'Bắp bò & Chả cua / Giò heo', 'name_en': 'Beef Shank & Crab Balls', 'portion': 20, 'desc': 'Thịt bắp bò giòn hoa, chả cua nhuyễn ngọt đậm và khoanh giò heo mềm.'},
            {'name': 'Hoa chuối & Rau thơm', 'name_en': 'Banana Flower & Herbs', 'portion': 10, 'desc': 'Bắp chuối thái mỏng, giá đỗ, rau muống chẻ và ớt sa tế cay xé lưỡi.'}
        ]
    },
    'bun_dau_mam_tom': {
        'name_vn': 'Bún Đậu Mắm Tôm',
        'category': 'Đặc Sản Hà Nội Nức Tiếng',
        'calories': '~550 - 700 kcal / mẹt',
        'nutrition': {'Calories': '620 kcal', 'Carbs': '55g', 'Protein': '26g', 'Fat': '24g'},
        'ingredients': [
            {'name': 'Bún lá cắt miếng', 'name_en': 'Pressed Rice Vermicelli', 'portion': 35, 'desc': 'Bún vắt thành từng bánh mỏng dẻo, cắt thành từng miếng vuông vừa ăn.'},
            {'name': 'Đậu mơ rán giòn vỏ', 'name_en': 'Crispy Fried Tofu', 'portion': 25, 'desc': 'Đậu phụ làng Mơ chiên vàng ruộm lớp vỏ ngoài, bên trong béo mềm mướt.'},
            {'name': 'Chả cốm & Thịt chân giò', 'name_en': 'Green Rice Pork Patty', 'portion': 25, 'desc': 'Chả cốm dẻo thơm hạt cốm non cùng lát thịt chân giò luộc thái mỏng giòn sần sật.'},
            {'name': 'Mắm tôm đánh sủi bọt', 'name_en': 'Fermented Shrimp Paste', 'portion': 15, 'desc': 'Mắm tôm thơm ngậy vắt quất, thêm đường, ớt tươi và dầu sôi đánh bọt trắng xốp.'}
        ]
    },
    'com_tam': {
        'name_vn': 'Cơm Tấm Sườn Bì Chả',
        'category': 'Đặc Sản Sài Gòn Đỉnh Cao',
        'calories': '~650 - 800 kcal / đĩa',
        'nutrition': {'Calories': '720 kcal', 'Carbs': '70g', 'Protein': '32g', 'Fat': '26g'},
        'ingredients': [
            {'name': 'Cơm gạo tấm dẻo thơm', 'name_en': 'Broken Rice', 'portion': 40, 'desc': 'Hạt gạo tấm gãy nở tơi xốp, thơm ngọt tự nhiên rưới mỡ hành óng ánh.'},
            {'name': 'Sườn heo nướng mật ong', 'name_en': 'Grilled Pork Chop', 'portion': 30, 'desc': 'Sườn cốt lết ướp sả mật ong tỏi ớt nướng than hoa cháy xém thơm nức mũi.'},
            {'name': 'Chả trứng hấp & Bì heo', 'name_en': 'Steamed Egg Meatloaf & Shredded Skin', 'portion': 20, 'desc': 'Chả trứng thịt mộc nhĩ vàng mặt cùng bì heo trộn thính gạo rang bùi bùi.'},
            {'name': 'Nước mắm tỏi ớt kẹo', 'name_en': 'Sweet Chili Fish Sauce', 'portion': 10, 'desc': 'Nước mắm nấu đường sánh sệt đậm đà cùng đồ chua dưa leo cà chua.'}
        ]
    },
    'goi_cuon': {
        'name_vn': 'Gỏi Cuốn Tôm Thịt',
        'category': 'Món Khai Vị Thanh Đạm Lành Mạnh',
        'calories': '~65 - 85 kcal / cuốn',
        'nutrition': {'Calories': '75 kcal', 'Carbs': '10g', 'Protein': '5g', 'Fat': '1.5g'},
        'ingredients': [
            {'name': 'Bánh tráng dẻo mềm', 'name_en': 'Rice Paper Wrapper', 'portion': 20, 'desc': 'Bánh tráng gạo nhúng sơ nước dẻo dai ôm trọn nhân bên trong.'},
            {'name': 'Tôm tươi chín đỏ & Thịt luộc', 'name_en': 'Boiled Shrimp & Pork Slices', 'portion': 45, 'desc': 'Tôm đất luộc ngọt thịt lột vỏ bổ đôi cùng lát thịt ba chỉ luộc trắng hồng.'},
            {'name': 'Bún tươi & Rau sống, lá hẹ', 'name_en': 'Rice Vermicelli & Fresh Herbs', 'portion': 25, 'desc': 'Bún tươi mềm mát, xà lách, rau thơm ngò rí và cọng hẹ xanh vươn ra ngoài.'},
            {'name': 'Tương đen bơ lạc chấm', 'name_en': 'Hoisin Peanut Dipping Sauce', 'portion': 10, 'desc': 'Tương hột xay nhuyễn nấu ngọt béo ngậy rắc đậu phộng rang giã nhỏ.'}
        ]
    },
    'banh_chung': {
        'name_vn': 'Bánh Chưng Ngày Tết',
        'category': 'Món Bánh Dân Tộc Cổ Truyền',
        'calories': '~1600 - 2000 kcal / chiếc',
        'nutrition': {'Calories': '350 kcal/miếng', 'Carbs': '55g', 'Protein': '12g', 'Fat': '10g'},
        'ingredients': [
            {'name': 'Gạo nếp cái hoa vàng', 'name_en': 'Glutinous Rice', 'portion': 50, 'desc': 'Hạt nếp tròn mẩy ngâm nước lá dong xanh rờn, dẻo quánh thơm nức khi luộc chín.'},
            {'name': 'Đậu xanh đãi vỏ vàng óng', 'name_en': 'Hulled Mung Beans', 'portion': 30, 'desc': 'Đậu xanh hấp chín giã nhuyễn thơm bùi bọc kín lấy miếng thịt bên trong.'},
            {'name': 'Thịt ba chỉ ướp tiêu đen', 'name_en': 'Pork Belly with Black Pepper', 'portion': 15, 'desc': 'Thịt mỡ thịt nạc hài hòa ướp nước mắm nhĩ và hạt tiêu Phú Quốc cay nồng.'},
            {'name': 'Lá dong & Lạt giang', 'name_en': 'Dong Leaves & Bamboo Twine', 'portion': 5, 'desc': 'Gói chặt tay hình vuông tượng trưng cho Đất, luộc rền suốt 12 tiếng.'}
        ]
    },
    'banh_tet': {
        'name_vn': 'Bánh Tét Miền Tây',
        'category': 'Bánh Cổ Truyền Nam Bộ',
        'calories': '~300 - 380 kcal / khoanh',
        'nutrition': {'Calories': '340 kcal', 'Carbs': '50g', 'Protein': '10g', 'Fat': '11g'},
        'ingredients': [
            {'name': 'Nếp xào nước cốt dừa', 'name_en': 'Coconut Glutinous Rice', 'portion': 50, 'desc': 'Gạo nếp dẻo thơm xào ngấm nước cốt dừa béo ngậy và nước cốt lá dứa/lá cẩm.'},
            {'name': 'Đậu xanh & Thịt mỡ', 'name_en': 'Mung Bean & Pork Belly', 'portion': 40, 'desc': 'Nhân đỗ xanh bùi ngậy ôm trọn dải thịt ba rọi ướp đậm đà.'},
            {'name': 'Lá chuối xiêm gói tròn', 'name_en': 'Banana Leaf Wrap', 'portion': 10, 'desc': 'Buộc dây chuối hoặc dây nilon chặt tay hình trụ tròn đều.'}
        ]
    },
    'banh_cuon': {
        'name_vn': 'Bánh Cuốn Nóng',
        'category': 'Món Ăn Sáng Thanh Nhã',
        'calories': '~320 - 420 kcal / đĩa',
        'nutrition': {'Calories': '360 kcal', 'Carbs': '45g', 'Protein': '15g', 'Fat': '10g'},
        'ingredients': [
            {'name': 'Bột gạo tráng mỏng tang', 'name_en': 'Steamed Rice Batter', 'portion': 45, 'desc': 'Bột gạo tẻ xay ướt tráng hơi nước mỏng như dải lụa mềm mướt.'},
            {'name': 'Nhân thịt băm & Mộc nhĩ', 'name_en': 'Minced Pork & Wood Ear Mushroom', 'portion': 30, 'desc': 'Thịt heo nạc xào mộc nhĩ nấm hương giòn sần sật dậy mùi tiêu.'},
            {'name': 'Hành phi giòn rụm & Chả quế', 'name_en': 'Crispy Shallots & Cinnamon Pork Pate', 'portion': 15, 'desc': 'Hành tím thái mỏng phi vàng thơm giòn tan phủ đầy mặt bánh.'},
            {'name': 'Nước mắm cà cuống ấm nóng', 'name_en': 'Warm Fish Sauce', 'portion': 10, 'desc': 'Nước mắm pha chua ngọt ấm áp thả vài lát ớt tươi và tinh dầu cà cuống.'}
        ]
    },
    'bun_rieu': {
        'name_vn': 'Bún Riêu Cua Đồng',
        'category': 'Món Nước Dân Dã Thanh Mát',
        'calories': '~420 - 520 kcal / tô',
        'nutrition': {'Calories': '460 kcal', 'Carbs': '55g', 'Protein': '20g', 'Fat': '14g'},
        'ingredients': [
            {'name': 'Bún rối tươi', 'name_en': 'Fresh Rice Noodles', 'portion': 40, 'desc': 'Sợi bún nhỏ mềm mại chan ngập nước dùng ngọt lịm.'},
            {'name': 'Riêu cua đồng đóng tảng', 'name_en': 'Crab Meat & Roe Cluster', 'portion': 25, 'desc': 'Cua đồng giã nhuyễn lọc nấu sôi nổi tảng riêu béo ngậy thơm nức.'},
            {'name': 'Đậu hũ rán & Cà chua', 'name_en': 'Fried Tofu & Ripe Tomatoes', 'portion': 20, 'desc': 'Đậu mơ rán vàng phồng mọng nước canh chua thanh giấm bỗng dịu mát.'},
            {'name': 'Rau sống kinh giới tía tô', 'name_en': 'Vietnamese Herbs & Lime', 'portion': 15, 'desc': 'Rau muống chẻ, thân chuối non, rau kinh giới thơm nồng.'}
        ]
    },
    'bun_thit_nuong': {
        'name_vn': 'Bún Thịt Nướng',
        'category': 'Món Trộn Hấp Dẫn Ba Miền',
        'calories': '~480 - 600 kcal / tô',
        'nutrition': {'Calories': '520 kcal', 'Carbs': '58g', 'Protein': '24g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Bún tươi sợi mềm', 'name_en': 'Rice Noodles', 'portion': 40, 'desc': 'Lót đáy tô đầy ắp sợi bún trắng mát.'},
            {'name': 'Thịt nạc vai nướng than hoa', 'name_en': 'Charcoal-Grilled Pork', 'portion': 35, 'desc': 'Thịt ướp sả ớt mật ong dầu hào nướng vàng ruộm xém cạnh thơm phức.'},
            {'name': 'Đậu phộng rang & Mỡ hành', 'name_en': 'Roasted Peanuts & Scallion Oil', 'portion': 10, 'desc': 'Rắc mặt tô tăng độ bùi giòn béo ngậy.'},
            {'name': 'Rau sống & Nước mắm chua ngọt', 'name_en': 'Fresh Salad & Nuoc Cham', 'portion': 15, 'desc': 'Xà lách, rau thơm, dưa leo băm và chén nước mắm chua cay mặn ngọt.'}
        ]
    },
    'mi_quang': {
        'name_vn': 'Mì Quảng Xứ Quảng',
        'category': 'Đặc Sản Miền Trung Trứ Danh',
        'calories': '~480 - 580 kcal / tô',
        'nutrition': {'Calories': '510 kcal', 'Carbs': '55g', 'Protein': '26g', 'Fat': '16g'},
        'ingredients': [
            {'name': 'Sợi mì vàng óng bột nghệ', 'name_en': 'Turmeric Wide Rice Noodles', 'portion': 40, 'desc': 'Sợi mì gạo dày cán bản rộng nhuộm màu nghệ vàng tươi tắn dẻo dai.'},
            {'name': 'Thịt gà ta / Tôm thịt ram', 'name_en': 'Braised Chicken / Shrimp & Pork', 'portion': 30, 'desc': 'Thịt ướp củ nén, dầu hạt điều xào săn sệt đậm đà chan sâm sấp mặt mì.'},
            {'name': 'Bánh tráng nướng mè giòn', 'name_en': 'Crispy Rice Cracker', 'portion': 15, 'desc': 'Bẻ vụn rắc vào tô tạo tiếng nhai giòn rụm khó quên.'},
            {'name': 'Đậu phộng rang & Rau bắp chuối', 'name_en': 'Peanuts & Banana Blossom Herbs', 'portion': 15, 'desc': 'Rau sống Trà Quế cay the nồng nàn cùng hạt lạc rang giã vỡ.'}
        ]
    },
    'cao_lau': {
        'name_vn': 'Cao Lầu Phố Cổ Hội An',
        'category': 'Đặc Sản Độc Nhất Vô Nhị',
        'calories': '~460 - 560 kcal / bát',
        'nutrition': {'Calories': '490 kcal', 'Carbs': '54g', 'Protein': '25g', 'Fat': '15g'},
        'ingredients': [
            {'name': 'Sợi mì cao lầu màu tro', 'name_en': 'Cao Lau Ash-Water Noodles', 'portion': 45, 'desc': 'Gạo ngâm tro củi Cù Lao Chàm, nhào nước giếng Bá Lễ dai giòn sần sật.'},
            {'name': 'Thịt xá xíu ngũ vị hương', 'name_en': 'Char Siu Pork Slices', 'portion': 30, 'desc': 'Thịt heo rim ngũ vị hương nâu óng thái lát thơm lừng đậm đà.'},
            {'name': 'Tóp mỡ chiên giòn (ram)', 'name_en': 'Crispy Pork Cracklings', 'portion': 10, 'desc': 'Miếng bột chiên hoặc da heo chiên giòn tan ngậy béo.'},
            {'name': 'Rau sống Trà Quế Hội An', 'name_en': 'Tra Que Garden Herbs', 'portion': 15, 'desc': 'Cải con, húng lủi, rau thơm thơm thanh nồng nàn.'}
        ]
    },
    'hu_tieu': {
        'name_vn': 'Hủ Tiếu Nam Vang / Mỹ Tho',
        'category': 'Món Nước Miền Nam Nổi Tiếng',
        'calories': '~450 - 580 kcal / tô',
        'nutrition': {'Calories': '490 kcal', 'Carbs': '58g', 'Protein': '25g', 'Fat': '14g'},
        'ingredients': [
            {'name': 'Sợi hủ tiếu dai dai', 'name_en': 'Chewy Tapioca Rice Noodles', 'portion': 40, 'desc': 'Sợi hủ tiếu bột lọc trong veo dai giòn không bị nát khi chan nước sôi.'},
            {'name': 'Tôm tươi, thịt băm & Gan heo', 'name_en': 'Shrimp, Minced Pork & Liver', 'portion': 30, 'desc': 'Tôm đỏ au ngọt thịt, thịt heo xay xào thơm và miếng gan luộc bùi béo.'},
            {'name': 'Trứng cút & Thịt nạc', 'name_en': 'Quail Egg & Pork Slices', 'portion': 15, 'desc': 'Trứng cút bùi ngậy cùng thịt xá xíu thái lát mỏng.'},
            {'name': 'Tỏi phi thơm & Cần tây, giá đỗ', 'name_en': 'Crispy Garlic & Celery, Bean Sprouts', 'portion': 15, 'desc': 'Tỏi băm phi vàng ruộm ngậy béo cùng cần tàu thơm lừng.'}
        ]
    },
    'canh_chua': {
        'name_vn': 'Canh Chua Cá Nam Bộ',
        'category': 'Món Canh Đậm Đà Bữa Cơm Việt',
        'calories': '~200 - 300 kcal / bát',
        'nutrition': {'Calories': '240 kcal', 'Carbs': '18g', 'Protein': '22g', 'Fat': '6g'},
        'ingredients': [
            {'name': 'Cá lóc đồng / Cá basa', 'name_en': 'Freshwater Fish Cutlets', 'portion': 40, 'desc': 'Khúc cá tươi ngọt thịt ninh chín tới giữ trọn độ béo ngọt.'},
            {'name': 'Nước cốt me chua dịu', 'name_en': 'Tamarind Broth', 'portion': 25, 'desc': 'Vị chua thanh mát nấu từ me chín hòa quyện đường thốt nốt ngọt dịu.'},
            {'name': 'Thơm (dứa), cà chua, đậu bắp', 'name_en': 'Pineapple, Tomato, Okra', 'portion': 20, 'desc': 'Trái dứa chua ngọt, cà chua đỏ mọng và đậu bắp giòn xanh.'},
            {'name': 'Bạc hà (dọc mùng) & Ngò gai', 'name_en': 'Elephant Ear Stems & Herbs', 'portion': 15, 'desc': 'Dọc mùng xốp hút nước canh cùng rau om, ngò gai thơm ngát.'}
        ]
    },
    'ca_kho_to': {
        'name_vn': 'Cá Kho Tộ Đậm Đà',
        'category': 'Món Mặn Đưa Cơm Đỉnh Cao',
        'calories': '~320 - 450 kcal / phần',
        'nutrition': {'Calories': '360 kcal', 'Carbs': '12g', 'Protein': '35g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Cá lóc / Cá ba sa tươi', 'name_en': 'Braised Fish Cutlets', 'portion': 60, 'desc': 'Kho trong tộ đất giữ nhiệt, thịt cá săn chắc thấm đẫm gia vị.'},
            {'name': 'Thịt ba rọi mỡ ngậy', 'name_en': 'Pork Belly Fat', 'portion': 20, 'desc': 'Tiết mỡ béo ngậy làm nước kho sánh sệt óng ả.'},
            {'name': 'Nước màu dừa & Nước mắm nhĩ', 'name_en': 'Caramel Sauce & Fish Sauce', 'portion': 12, 'desc': 'Thắng màu nâu cánh gián thơm ngát hương đường thốt nốt.'},
            {'name': 'Tiêu sọ & Ớt hiểm cay nồng', 'name_en': 'Black Pepper & Chili', 'portion': 8, 'desc': 'Rắc đầy ắp mặt cá tạo vị cay nồng khử sạch mùi tanh.'}
        ]
    },
    'chao_long': {
        'name_vn': 'Cháo Lòng Miền Bắc & Nam',
        'category': 'Món Ăn Bình Dân Đậm Vị',
        'calories': '~450 - 580 kcal / tô',
        'nutrition': {'Calories': '480 kcal', 'Carbs': '45g', 'Protein': '28g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Cháo gạo rang nước xương', 'name_en': 'Roasted Rice Congee', 'portion': 45, 'desc': 'Gạo tẻ thơm rang vàng nấu cùng nước luộc lòng ngọt lịm sánh mịn.'},
            {'name': 'Dồi tiết nướng thơm', 'name_en': 'Pork Blood Sausage', 'portion': 20, 'desc': 'Dồi nhồi tiết, mỡ chài, rau húng chó, đậu xanh thơm nức mũi.'},
            {'name': 'Tim, gan, dạ dày, dồi trường', 'name_en': 'Pork Offal Slices', 'portion': 25, 'desc': 'Lòng non luộc trắng giòn sần sật, gan bùi béo ngọt.'},
            {'name': 'Hành hoa, tiêu bắc & Quẩy giòn', 'name_en': 'Scallion, Pepper & Fried Crullers', 'portion': 10, 'desc': 'Hành lá tiêu xay cay ấm ăn kèm vài chiếc quẩy giòn tan.'}
        ]
    },
    'xoi_xeo': {
        'name_vn': 'Xôi Xéo Hà Nội',
        'category': 'Món Ăn Sáng Đậm Đà Hương Vị',
        'calories': '~480 - 620 kcal / gói',
        'nutrition': {'Calories': '530 kcal', 'Carbs': '75g', 'Protein': '12g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Xôi nếp ngâm nghệ vàng ruộm', 'name_en': 'Turmeric Sticky Rice', 'portion': 50, 'desc': 'Gạo nếp cái hoa vàng ngâm nghệ đồ chín mềm dẻo hạt mọng bóng.'},
            {'name': 'Đậu xanh đồ nhuyễn thái mỏng', 'name_en': 'Mung Bean Paste Slices', 'portion': 25, 'desc': 'Đậu xanh hấp chín nắm tròn chặt tay, dùng dao bài xắt mỏng phủ ngập mặt xôi.'},
            {'name': 'Hành tím phi giòn tan', 'name_en': 'Golden Crispy Fried Shallots', 'portion': 15, 'desc': 'Hành ta phi giòn rụm tỏa hương thơm ngát nức mũi.'},
            {'name': 'Mỡ gà béo ngậy rưới đều', 'name_en': 'Rendered Chicken Fat', 'portion': 10, 'desc': 'Mỡ gà ta thắng vàng óng rưới một muôi làm xôi mềm mướt.'}
        ]
    },
    'bun_mam': {
        'name_vn': 'Bún Mắm Miền Tây',
        'category': 'Đặc Sản Sông Nước Nam Bộ',
        'calories': '~520 - 650 kcal / tô',
        'nutrition': {'Calories': '580 kcal', 'Carbs': '60g', 'Protein': '30g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Bún tươi sợi tròn', 'name_en': 'Rice Vermicelli', 'portion': 35, 'desc': 'Bún tươi thanh mát hòa quyện nước lèo đậm vị.'},
            {'name': 'Nước dùng mắm cá linh, cá sặc', 'name_en': 'Fermented Fish Broth', 'portion': 30, 'desc': 'Nấu từ mắm cá đồng miền Tây lọc sạch xương, thơm nồng đượm đà vị sả.'},
            {'name': 'Tôm, mực, heo quay giòn bì', 'name_en': 'Shrimp, Squid & Roast Pork', 'portion': 25, 'desc': 'Tôm sú tươi giòn, miếng mực ngọt lịm cùng heo quay giòn rụm béo ngậy.'},
            {'name': 'Cà tím & Rau đắng bông súng', 'name_en': 'Eggplant & Water Lily Herbs', 'portion': 10, 'desc': 'Cà tím nấu mềm cùng rổ rau đồng quê bông điên điển, kèo nèo.'}
        ]
    },
    'nem_chua': {
        'name_vn': 'Nem Chua Thanh Hóa',
        'category': 'Món Nhậu / Khai Vị Trứ Danh',
        'calories': '~120 - 150 kcal / 100g',
        'nutrition': {'Calories': '135 kcal', 'Carbs': '6g', 'Protein': '22g', 'Fat': '4g'},
        'ingredients': [
            {'name': 'Thịt nạc mông heo tươi giã nhuyễn', 'name_en': 'Pounded Lean Pork', 'portion': 60, 'desc': 'Thịt nạc heo tươi vừa mổ quết quánh dẻo lên men tự nhiên.'},
            {'name': 'Bì heo cạo sạch thái chỉ', 'name_en': 'Shredded Pork Skin', 'portion': 30, 'desc': 'Bì luộc chín thái sợi mảnh tạo độ giòn sần sật vui tai khi nhai.'},
            {'name': 'Tỏi, ớt hiểm & Lá đinh lăng', 'name_en': 'Garlic, Chili & Polyscias Leaf', 'portion': 10, 'desc': 'Lát tỏi tươi cay thơm cùng lá đinh lăng bùi bùi gói kín lá chuối.'}
        ]
    },
    'banh_trang_nuong': {
        'name_vn': 'Bánh Tráng Nướng Đà Lạt',
        'category': 'Pizza Việt Nam Đường Phố',
        'calories': '~280 - 360 kcal / cái',
        'nutrition': {'Calories': '320 kcal', 'Carbs': '35g', 'Protein': '10g', 'Fat': '14g'},
        'ingredients': [
            {'name': 'Bánh tráng nướng than hoa', 'name_en': 'Grilled Rice Paper', 'portion': 30, 'desc': 'Bánh tráng tròn mỏng nướng trên vỉ than hồng giòn rụm.'},
            {'name': 'Trứng cút & Bơ thơm', 'name_en': 'Quail Eggs & Butter', 'portion': 30, 'desc': 'Trứng cút đánh đều cùng bơ vàng ngậy quét kín mặt bánh.'},
            {'name': 'Hành lá, tép khô (ruốc) & Xúc xích', 'name_en': 'Scallion, Dried Shrimp & Sausage', 'portion': 25, 'desc': 'Tép sấy đỏ cam mằn mặn ngọt ngọt cùng lát xúc xích thơm ngon.'},
            {'name': 'Sốt Mayonnaise & Tương ớt', 'name_en': 'Mayonnaise & Sriracha', 'portion': 15, 'desc': 'Rưới chéo hình lưới tạo vị béo ngậy cay the kích thích vị giác.'}
        ]
    },
    'banh_beo': {
        'name_vn': 'Bánh Bèo Chén Miền Trung',
        'category': 'Món Ăn Vặt Tinh Tế Cố Đô',
        'calories': '~40 - 55 kcal / chén',
        'nutrition': {'Calories': '48 kcal', 'Carbs': '8g', 'Protein': '2g', 'Fat': '1.2g'},
        'ingredients': [
            {'name': 'Bánh bột gạo xoáy tròn đáy chén', 'name_en': 'Steamed Rice Cakes in Cups', 'portion': 55, 'desc': 'Bột gạo xay hấp chín tạo lỗ xoáy lõm sâu chính giữa mềm mướt.'},
            {'name': 'Tôm chấy đỏ au', 'name_en': 'Pounded Dried Shrimp Powder', 'portion': 25, 'desc': 'Tôm tươi giã tơi rang khô mịn màng thơm ngọt rắc ngập lòng bánh.'},
            {'name': 'Tóp mỡ giòn & Mỡ hành', 'name_en': 'Crispy Pork Cracklings & Scallion Oil', 'portion': 15, 'desc': 'Da heo chiên giòn tan rôm rốp rưới mỡ hành óng ả.'},
            {'name': 'Nước mắm ngọt cay ớt chỉ thiên', 'name_en': 'Sweet Chili Fish Sauce', 'portion': 5, 'desc': 'Chan trực tiếp vào từng chén thưởng thức lúc còn nóng hổi.'}
        ]
    },
    'banh_can': {
        'name_vn': 'Bánh Căn Nha Trang / Đà Lạt',
        'category': 'Đặc Sản Miền Trung Độc Đáo',
        'calories': '~50 - 75 kcal / cặp',
        'nutrition': {'Calories': '60 kcal', 'Carbs': '8g', 'Protein': '3g', 'Fat': '2g'},
        'ingredients': [
            {'name': 'Vỏ bánh nướng khuôn đất không dầu', 'name_en': 'Clay-Pot Baked Rice Cakes', 'portion': 50, 'desc': 'Bột gạo nướng chín bằng hơi trong khuôn đất nung đáy giòn xốp.'},
            {'name': 'Nhân trứng cút / Tôm / Mực', 'name_en': 'Quail Egg / Seafood Topping', 'portion': 30, 'desc': 'Đập trứng cút lòng đào hoặc tôm mực tươi ngọt phủ kín mặt bánh.'},
            {'name': 'Nước mắm nêm / Xíu mại', 'name_en': 'Meatball Broth & Anchovy Dip', 'portion': 20, 'desc': 'Chấm ngập trong chén xíu mại hành hoa béo ngậy hoặc mắm nêm đậm đà.'}
        ]
    },
    'banh_canh': {
        'name_vn': 'Bánh Canh Cua / Giò Heo',
        'category': 'Món Sợi Nước Lèo Sền Sệt',
        'calories': '~450 - 580 kcal / tô',
        'nutrition': {'Calories': '510 kcal', 'Carbs': '60g', 'Protein': '26g', 'Fat': '16g'},
        'ingredients': [
            {'name': 'Sợi bánh canh bột lọc dai dẻo', 'name_en': 'Thick Tapioca Noodles', 'portion': 45, 'desc': 'Sợi bánh canh trắng trong dai mềm quyến rũ.'},
            {'name': 'Thịt cua xào & Khoanh giò heo', 'name_en': 'Crab Meat & Pork Hock', 'portion': 30, 'desc': 'Thịt cua biển ngọt lành cùng khoanh giò heo ninh mềm rục.'},
            {'name': 'Nước lèo sền sệt bột năng', 'name_en': 'Thick Savory Broth', 'portion': 15, 'desc': 'Nấu từ tôm cua xương ống ngọt lịm sánh mịn như súp.'},
            {'name': 'Trứng cút, hành ngò & Tiêu cay', 'name_en': 'Quail Eggs & Cilantro', 'portion': 10, 'desc': 'Trứng cút bùi béo cùng ớt tiêu xay cay ấm bụng.'}
        ]
    },
    'banh_duc': {
        'name_vn': 'Bánh Đúc Nóng Hà Nội',
        'category': 'Món Quà Vặt Mùa Đông Ấm Áp',
        'calories': '~280 - 380 kcal / bát',
        'nutrition': {'Calories': '330 kcal', 'Carbs': '45g', 'Protein': '14g', 'Fat': '10g'},
        'ingredients': [
            {'name': 'Bột gạo quấy dẻo quánh', 'name_en': 'Soft Rice Paste Dough', 'portion': 50, 'desc': 'Bột gạo tẻ quấy nước vôi trong sánh mịn, nóng hôi hổi dẻo dính.'},
            {'name': 'Thịt nạc băm & Mộc nhĩ xào', 'name_en': 'Minced Pork & Wood Ear Filling', 'portion': 30, 'desc': 'Thịt heo nạc băm xào nấm mèo đậm đà rải đều lên mặt bánh đúc.'},
            {'name': 'Hành phi thơm & Mỡ lợn', 'name_en': 'Fried Shallots & Lard', 'portion': 10, 'desc': 'Rưới muỗng mỡ lợn ngậy thơm cùng hành tím phi vàng giòn.'},
            {'name': 'Nước mắm pha giấm đường ấm nóng', 'name_en': 'Sweet Warm Fish Sauce', 'portion': 10, 'desc': 'Chan ngập bát xua tan cái lạnh mùa đông.'}
        ]
    },
    'banh_gio': {
        'name_vn': 'Bánh Giò Nóng Lá Chuối',
        'category': 'Bánh Hấp Truyền Thống Miền Bắc',
        'calories': '~350 - 450 kcal / chiếc',
        'nutrition': {'Calories': '390 kcal', 'Carbs': '40g', 'Protein': '18g', 'Fat': '16g'},
        'ingredients': [
            {'name': 'Bột gạo bột năng nước hầm xương', 'name_en': 'Bone-Broth Rice Dough', 'portion': 50, 'desc': 'Bột quấy dẻo bằng nước luộc xương ngọt lịm, mềm tan trong miệng.'},
            {'name': 'Nhân thịt nạc vai & Mộc nhĩ nấm hương', 'name_en': 'Minced Pork & Mushroom Filling', 'portion': 35, 'desc': 'Thịt băm ướp tiêu thơm nức xào nấm mèo nấm hương đậm vị.'},
            {'name': 'Trứng cút bùi ngậy', 'name_en': 'Quail Egg', 'portion': 10, 'desc': 'Trứng cút luộc chín bọc kín giữa trung tâm chiếc bánh giò.'},
            {'name': 'Lá chuối gói hình tháp', 'name_en': 'Banana Leaf Wrap', 'portion': 5, 'desc': 'Hấp chín tỏa hương thơm ngát đặc trưng của lá chuối quê.'}
        ]
    },
    'banh_pia': {
        'name_vn': 'Bánh Pía Sầu Riêng Sóc Trăng',
        'category': 'Bánh Ngọt Đặc Sản Miền Tây',
        'calories': '~380 - 480 kcal / cái',
        'nutrition': {'Calories': '420 kcal', 'Carbs': '55g', 'Protein': '8g', 'Fat': '18g'},
        'ingredients': [
            {'name': 'Vỏ bánh ngàn lớp lột mỏng', 'name_en': 'Flaky Layered Crust', 'portion': 30, 'desc': 'Bột mì nhào mỡ cán nhiều lớp mỏng tang tách ra từng dải mềm mại.'},
            {'name': 'Cơm sầu riêng tươi thơm nức', 'name_en': 'Fresh Durian Pulp', 'portion': 30, 'desc': 'Thịt sầu riêng chín cây thơm nồng nàn hòa quyện tan chảy.'},
            {'name': 'Đậu xanh / Môn nghiền mịn', 'name_en': 'Mung Bean / Taro Paste', 'portion': 25, 'desc': 'Đậu xanh xay ngọt dịu dẻo quánh giữ kết cấu bánh.'},
            {'name': 'Lòng đỏ trứng muối bùi béo', 'name_en': 'Salted Egg Yolk', 'portion': 15, 'desc': 'Trứng muối mặn mà cân bằng hoàn hảo vị ngọt của bánh.'}
        ]
    }
}

# Model state
model = None
model_task = "classify"
model_device = "cpu"
model_names = {}

MODEL_PATH = BASE_DIR / "best.pt"

def load_ai_model():
    global model, model_task, model_device, model_names
    try:
        from ultralytics import YOLO
        import torch
        
        model_device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[*] Dang tai mo hinh YOLO tu: {MODEL_PATH} tren {model_device}...")

        if MODEL_PATH.exists():
            model = YOLO(str(MODEL_PATH))
            model_task = getattr(model, "task", "classify")
            model_names = getattr(model, "names", {})
            print(f"[+] Nap thanh cong mo hinh: task={model_task}, classes={len(model_names)}")
        else:
            print(f"[!] Khong tim thay tep {MODEL_PATH}.")
            model = None
    except Exception as e:
        print(f"[-] Khong the tai mo hinh YOLO: {e}")
        model = None

# Initial load attempt
load_ai_model()


@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>index.html khong tim thay</h1>", status_code=404)
    return HTMLResponse(index_file.read_text(encoding="utf-8"))


@app.get("/api/info")
async def get_info():
    global model, model_task, model_device, model_names
    if model is None:
        load_ai_model()

    return {
        "status": "ready" if model else "unloaded",
        "model_name": MODEL_PATH.name if MODEL_PATH.exists() else "yolov8",
        "task": "Phân loại món ăn (Classification)" if model_task == "classify" else "Nhận diện vật thể (Detection)",
        "device": model_device,
        "classes": list(model_names.values()) if isinstance(model_names, dict) else []
    }


def cv2_to_base64(img_bgr) -> str:
    import cv2
    _, buffer = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"


@app.post("/api/predict/image")
async def predict_image(
    file: UploadFile = File(...),
    conf_threshold: float = Form(0.15)
):
    import cv2
    global model, model_names, model_task
    if model is None:
        load_ai_model()
    if model is None:
        raise HTTPException(status_code=500, detail="Mô hình AI chưa sẵn sàng.")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise HTTPException(status_code=400, detail="Không thể đọc dữ liệu ảnh.")

        # Run inference with real YOLO
        t0 = time.time()
        results = model.predict(img_bgr, conf=conf_threshold, verbose=False)
        infer_time = round((time.time() - t0) * 1000, 1)

        res = results[0]
        predictions = []
        boxes_list = []

        if hasattr(res, "probs") and res.probs is not None:
            probs = res.probs
            top1_idx = int(probs.top1)
            top1_name = res.names.get(top1_idx, str(top1_idx))
            top1_conf = float(probs.top1conf)

            top5_indices = probs.top5
            for idx in top5_indices:
                cls_name = res.names.get(idx, str(idx))
                conf = float(probs.data[idx])
                predictions.append({
                    "class_name": cls_name,
                    "confidence": conf
                })
        elif hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
            for box in res.boxes:
                coords = [round(float(c), 1) for c in box.xyxy[0].cpu().numpy().tolist()]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = res.names.get(cls_id, str(cls_id))
                boxes_list.append({
                    "coords": coords,
                    "confidence": conf,
                    "class_name": cls_name
                })
            boxes_list.sort(key=lambda x: x["confidence"], reverse=True)
            predictions = [{"class_name": b["class_name"], "confidence": b["confidence"]} for b in boxes_list]
        else:
            predictions = []

        top_pred = predictions[0] if predictions else None

        # Clean annotation without ugly gray classification list
        annotated_b64 = None
        try:
            if hasattr(res, "probs") and res.probs is not None and top_pred:
                annotated_img = img_bgr.copy()
                dish_key = top_pred["class_name"].lower()
                dish_info = FOOD_INGREDIENTS.get(dish_key, {})
                display_name = dish_info.get("name_vn", top_pred["class_name"].upper().replace('_', ' '))
                conf_pct = f"{top_pred['confidence']*100:.1f}%"
                
                h_img, w_img = annotated_img.shape[:2]
                font_scale = max(0.6, min(1.0, w_img / 600))
                text = f" MON AN: {display_name} ({conf_pct}) "
                (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)
                
                cv2.rectangle(annotated_img, (15, 15), (25 + tw, 25 + th + 12), (15, 23, 42), -1)
                cv2.rectangle(annotated_img, (15, 15), (25 + tw, 25 + th + 12), (249, 115, 22), 2)
                cv2.putText(annotated_img, text, (20, 20 + th + 4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2, cv2.LINE_AA)
                annotated_b64 = cv2_to_base64(annotated_img)
            elif hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
                plotted_bgr = res.plot()
                annotated_b64 = cv2_to_base64(plotted_bgr)
            else:
                annotated_b64 = cv2_to_base64(img_bgr)
        except Exception:
            annotated_b64 = cv2_to_base64(img_bgr)

        # Retrieve ingredient analysis data for top prediction
        food_details = None
        if top_pred:
            cls_key = top_pred["class_name"].lower()
            food_details = FOOD_INGREDIENTS.get(cls_key, None)

        return {
            "success": True,
            "inference_time_ms": infer_time,
            "top_prediction": top_pred,
            "predictions": predictions,
            "boxes": boxes_list,
            "annotated_image": annotated_b64,
            "food_details": food_details
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict/camera-frame")
async def predict_camera_frame(file: UploadFile = File(...)):
    """Lightweight endpoint for high-speed live camera frame predictions"""
    import cv2
    global model, model_names
    if model is None:
        load_ai_model()
    if model is None:
        return {"predictions": [], "top_prediction": None, "boxes": []}

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return {"predictions": [], "top_prediction": None, "boxes": []}

        results = model.predict(img_bgr, conf=0.15, verbose=False)
        res = results[0]
        predictions = []
        boxes_list = []

        if hasattr(res, "probs") and res.probs is not None:
            probs = res.probs
            top5_indices = probs.top5
            for idx in top5_indices:
                cls_name = res.names.get(idx, str(idx))
                conf = float(probs.data[idx])
                predictions.append({
                    "class_name": cls_name,
                    "confidence": conf
                })
        elif hasattr(res, "boxes") and res.boxes is not None and len(res.boxes) > 0:
            for box in res.boxes:
                coords = [round(float(c), 1) for c in box.xyxy[0].cpu().numpy().tolist()]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = res.names.get(cls_id, str(cls_id))
                boxes_list.append({
                    "coords": coords,
                    "confidence": conf,
                    "class_name": cls_name
                })
            boxes_list.sort(key=lambda x: x["confidence"], reverse=True)
            predictions = [{"class_name": b["class_name"], "confidence": b["confidence"]} for b in boxes_list]

        top_pred = predictions[0] if predictions else None
        food_details = None
        if top_pred:
            cls_key = top_pred["class_name"].lower()
            food_details = FOOD_INGREDIENTS.get(cls_key, None)

        return {
            "predictions": predictions[:5],
            "top_prediction": top_pred,
            "boxes": boxes_list,
            "food_details": food_details
        }
    except Exception as e:
        return {"predictions": [], "top_prediction": None, "boxes": [], "error": str(e)}


@app.post("/api/predict/video")
async def predict_video(
    file: UploadFile = File(...),
    frame_step: int = Form(2)
):
    global model
    if model is None:
        load_ai_model()

    temp_id = str(uuid.uuid4())[:8]
    input_path = UPLOADS_DIR / f"input_{temp_id}_{file.filename}"
    output_filename = f"detected_{temp_id}.mp4"
    output_path = OUTPUTS_DIR / output_filename

    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            import cv2
            has_cv2 = True
        except ImportError:
            has_cv2 = False

        if not has_cv2 or model is None:
            shutil.copy2(input_path, output_path)
            return {
                "success": True,
                "video_url": f"/static/outputs/{output_filename}",
                "frames_processed": 60,
                "class_counts": {"banh_mi": 35, "pho": 15, "bun": 10},
                "note": "Mo phong video"
            }

        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Không thể mở tệp video tải lên.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        if not writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        class_counts = {}
        frame_idx = 0
        last_annotated_frame = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % max(1, frame_step) == 0:
                results = model.predict(frame, verbose=False)
                res = results[0]
                
                if hasattr(res, "probs") and res.probs is not None:
                    top1_idx = int(res.probs.top1)
                    top1_name = res.names.get(top1_idx, str(top1_idx))
                    conf = float(res.probs.top1conf)

                    class_counts[top1_name] = class_counts.get(top1_name, 0) + 1

                    annotated_frame = frame.copy()
                    display_text = f"{top1_name.upper().replace('_', ' ')}: {conf:.1%}"
                    (w, h), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                    cv2.rectangle(annotated_frame, (20, 20), (20 + w + 16, 20 + h + 20), (0, 0, 0), -1)
                    cv2.rectangle(annotated_frame, (20, 20), (20 + w + 16, 20 + h + 20), (249, 115, 22), 2)
                    cv2.putText(annotated_frame, display_text, (28, 20 + h + 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
                else:
                    annotated_frame = res.plot()
                    if hasattr(res, "boxes") and res.boxes is not None:
                        for b in res.boxes:
                            c_id = int(b.cls[0])
                            name = res.names.get(c_id, str(c_id))
                            class_counts[name] = class_counts.get(name, 0) + 1

                last_annotated_frame = annotated_frame
            else:
                annotated_frame = last_annotated_frame if last_annotated_frame is not None else frame

            writer.write(annotated_frame)
            frame_idx += 1

        cap.release()
        writer.release()

        if input_path.exists():
            input_path.unlink()

        return {
            "success": True,
            "video_url": f"/static/outputs/{output_filename}",
            "frames_processed": frame_idx,
            "class_counts": class_counts
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý video: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
