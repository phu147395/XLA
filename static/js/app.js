// AI Food Vision - Frontend Application Logic

let currentTab = 'image';
let selectedImageFile = null;
let selectedVideoFile = null;
let isAnalyzingImage = false;
let isProcessingVideo = false;

// Camera state
let webcamStream = null;
let cameraActive = false;
let cameraIntervalId = null;
let lastSpokenClass = null;
let lastSpeechTime = 0;
let lastFrameTime = performance.now();
let frameCount = 0;
let fps = 0;
let fpsInterval = null;

// Audio synthesis
const synth = window.speechSynthesis;

// Vietnamese translation dictionary & food info
const DISH_INFO = {
    'banh_mi': {
        name_vn: 'Bánh Mì',
        calories: '~350 - 450 kcal',
        desc: 'Món ăn đường phố biểu tượng của Việt Nam, nhân thịt, chả, pa-tê, rau ngò dưa chuột giòn rụm.'
    },
    'pho': {
        name_vn: 'Phở',
        calories: '~350 - 500 kcal',
        desc: 'Món quốc hồn quốc túy với nước dùng ninh từ xương thơm nồng thảo quả, quế, hồi và bánh phở dẻo mềm.'
    },
    'bun': {
        name_vn: 'Bún (Bún bò / Bún riêu)',
        calories: '~400 - 550 kcal',
        desc: 'Sợi bún tươi kết hợp nước dùng đậm đà hoặc nước mắm chua ngọt, ăn kèm nhiều loại rau thơm tươi ngon.'
    },
    'bun_cha': {
        name_vn: 'Bún Chả',
        calories: '~450 - 600 kcal',
        desc: 'Đặc sản Hà Nội trứ danh gồm chả thịt nướng than hoa thơm lừng, bún tươi và nước mắm chua ngọt đu đủ.'
    },
    'banh_xeo': {
        name_vn: 'Bánh Xèo',
        calories: '~300 - 450 kcal / cái',
        desc: 'Vỏ bánh vàng giòn từ bột gạo và nghệ, nhân tôm, thịt ba chỉ, giá đỗ giòn ngọt, cuốn bánh tráng chấm mắm chua ngọt.'
    },
    'banh_khot': {
        name_vn: 'Bánh Khọt',
        calories: '~50 - 80 kcal / cái',
        desc: 'Đặc sản miền Nam giòn rụm với tôm tươi bên trên, rưới mỡ hành béo ngậy, ăn kèm rau sống và nước mắm chua ngọt.'
    },
    'goi_cuon': {
        name_vn: 'Gỏi Cuốn',
        calories: '~60 - 80 kcal / cuốn',
        desc: 'Món thanh đạm lành mạnh gồm tôm tươi, thịt luộc, bún, rau thơm cuộn trong bánh tráng dẻo, chấm tương bơ lạc.'
    },
    'bot_chien': {
        name_vn: 'Bột Chiên',
        calories: '~400 - 500 kcal',
        desc: 'Từng miếng bột gạo chiên giòn cháy cạnh với trứng gà, phủ hành lá xắt nhuyễn và đu đủ bào ngâm giấm.'
    },
    'banh_trung_thu': {
        name_vn: 'Bánh Trung Thu',
        calories: '~600 - 900 kcal / cái',
        desc: 'Bánh nướng truyền thống nhân đậu xanh, thập cẩm hoặc khoai môn với lòng đỏ trứng muối bùi béo.'
    },
    'banh_bot_loc': {
        name_vn: 'Bánh Bột Lọc',
        calories: '~45 - 60 kcal / cái',
        desc: 'Vỏ bánh trong suốt dai dai từ bột lọc, bên trong có tôm rim và thịt mỡ đậm đà chấm mắm ớt cay.'
    },
    'banh_da_lon': {
        name_vn: 'Bánh Da Lợn',
        calories: '~150 - 200 kcal / miếng',
        desc: 'Bánh ngọt tráng từng lớp xen kẽ giữa bột lá dứa xanh ngát và nhân đậu xanh nước cốt dừa thơm béo.'
    },
    'banh_bo': {
        name_vn: 'Bánh Bò',
        calories: '~100 - 150 kcal / cái',
        desc: 'Bánh xốp ngọt ngào với cấu trúc rễ tre mềm mại, hương thơm men rượu nếp thoang thoảng.'
    },
    'banh_cong': {
        name_vn: 'Bánh Cống',
        calories: '~250 - 350 kcal / cái',
        desc: 'Đặc sản Sóc Trăng giòn rụm làm từ bột gạo, đậu xanh, thịt băm và phủ nguyên con tôm tươi trên mặt.'
    },
    'banh_tieu': {
        name_vn: 'Bánh Tiêu',
        calories: '~180 - 220 kcal / cái',
        desc: 'Bánh rán phồng vàng ruộm rắc mè trắng thơm phức, ruột rỗng mềm ngọt nhẹ.'
    },
    'banh_tai_heo': {
        name_vn: 'Bánh Tai Heo',
        calories: '~120 kcal / 30g',
        desc: 'Bánh quy xoắn ốc giòn tan tuổi thơ, vị mằn mặn ngòn ngọt thơm bơ.'
    }
};

function formatClassName(rawName) {
    if (!rawName) return '--';
    let clean = rawName.toLowerCase().replace(/[\s-]+/g, '_');
    if (DISH_INFO[clean]) {
        return DISH_INFO[clean].name_vn;
    }
    // Clean string fallback
    return rawName.replace(/[_-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getDishDetails(rawName) {
    if (!rawName) return null;
    let clean = rawName.toLowerCase().replace(/[\s-]+/g, '_');
    return DISH_INFO[clean] || null;
}

// ---------------- TAB SWITCHING ----------------
function switchTab(tabName) {
    currentTab = tabName;
    const tabs = ['image', 'video', 'camera'];
    
    tabs.forEach(t => {
        const btn = document.getElementById(`tabBtn-${t}`);
        const sec = document.getElementById(`section-${t}`);
        if (t === tabName) {
            btn.classList.add('active');
            sec.classList.remove('hidden');
        } else {
            btn.classList.remove('active');
            sec.classList.add('hidden');
        }
    });

    // If leaving camera tab, pause camera if user wants, or keep running
    if (tabName !== 'camera' && cameraActive) {
        // Can keep running or pause
    }
}

// ---------------- APP INITIALIZATION ----------------
window.addEventListener('DOMContentLoaded', async () => {
    initModelInfo();
    initImageTab();
    initVideoTab();
    initCameraTab();
});

async function initModelInfo() {
    try {
        const res = await fetch('/api/info');
        const data = await res.json();
        
        document.getElementById('modelInfoText').textContent = `${data.model_name || 'YOLOv8'} (${data.task || 'Phân loại'})`;
        document.getElementById('deviceBadge').textContent = (data.device || 'CPU').toUpperCase();

        if (data.classes && data.classes.length > 0) {
            console.log(`Loaded ${data.classes.length} classes:`, data.classes);
        }
    } catch (err) {
        console.warn('Could not fetch model info:', err);
        document.getElementById('modelInfoText').textContent = 'Mô hình sẵn sàng';
    }
}

// ================= TAB 1: IMAGE LOGIC =================
function initImageTab() {
    const dropZone = document.getElementById('imageDropZone');
    const fileInput = document.getElementById('imageFileInput');
    const preview = document.getElementById('imagePreview');
    const emptyPrompt = document.getElementById('imageEmptyPrompt');
    const btnAnalyze = document.getElementById('btnAnalyzeImage');

    // Populate Sample Images
    const sampleContainer = document.getElementById('sampleImagesContainer');
    if (sampleContainer) {
        const samples = [
            { label: '🥮 Bánh Trung Thu', file: 'sample_banh_trung_thu.jpg' },
            { label: '🍜 Phở Bò', file: 'sample_pho.jpg' },
            { label: '🥖 Bánh Mì', file: 'sample_banh_mi.jpg' },
            { label: '🥩 Cơm Tấm', file: 'sample_com_tam.jpg' },
            { label: '🍲 Bún Bò Huế', file: 'sample_bun_bo_hue.jpg' },
            { label: '🥢 Bún Đậu', file: 'sample_bun_dau_mam_tom.jpg' },
            { label: '🥞 Bánh Xèo', file: 'sample_banh_xeo.jpg' },
            { label: '🥟 Bánh Cuốn', file: 'sample_banh_cuon.jpg' },
            { label: '🎋 Bánh Chưng', file: 'sample_banh_chung.jpg' },
            { label: '🌯 Gỏi Cuốn', file: 'sample_goi_cuon.jpg' },
            { label: '🍜 Mì Quảng', file: 'sample_mi_quang.jpg' },
            { label: '🍤 Bánh Khọt', file: 'sample_banh_khot.jpg' }
        ];

        sampleContainer.innerHTML = '';
        samples.forEach(s => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5';
            btn.innerHTML = `<span>${s.label}</span>`;
            btn.onclick = async () => {
                try {
                    const imgUrl = `/static/samples/${s.file}`;
                    const res = await fetch(imgUrl);
                    const blob = await res.blob();
                    const fileObj = new File([blob], s.file, { type: 'image/jpeg' });
                    handleImageFile(fileObj);
                } catch (e) {
                    console.error('Không thể nạp ảnh mẫu:', e);
                }
            };
            sampleContainer.appendChild(btn);
        });
    }

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleImageFile(e.target.files[0]);
        }
    });

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('border-orange-500', 'bg-slate-900/80');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('border-orange-500', 'bg-slate-900/80');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleImageFile(e.dataTransfer.files[0]);
        }
    });

    btnAnalyze.addEventListener('click', analyzeImage);
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Vui lòng chọn một tệp hình ảnh hợp lệ (JPG, PNG, WEBP).');
        return;
    }
    selectedImageFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('imagePreview');
        const emptyPrompt = document.getElementById('imageEmptyPrompt');
        preview.src = e.target.result;
        preview.classList.remove('hidden');
        emptyPrompt.classList.add('hidden');
        document.getElementById('btnAnalyzeImage').disabled = false;
    };
    reader.readAsDataURL(file);
}

async function analyzeImage() {
    if (!selectedImageFile || isAnalyzingImage) return;

    isAnalyzingImage = true;
    const btnAnalyze = document.getElementById('btnAnalyzeImage');
    const btnText = document.getElementById('btnAnalyzeText');
    const originalText = btnText.textContent;
    btnAnalyze.disabled = true;
    btnText.textContent = 'Đang phân tích hình ảnh...';

    const formData = new FormData();
    formData.append('file', selectedImageFile);

    const startTime = performance.now();

    try {
        const res = await fetch('/api/predict/image', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            throw new Error(`Lỗi máy chủ (${res.status})`);
        }

        const data = await res.json();
        const duration = Math.round(performance.now() - startTime);
        
        displayImageResults(data, duration);
    } catch (err) {
        console.error(err);
        alert('Có lỗi xảy ra khi phân tích: ' + err.message);
    } finally {
        isAnalyzingImage = false;
        btnAnalyze.disabled = false;
        btnText.textContent = originalText;
    }
}

function displayImageResults(data, durationMs) {
    document.getElementById('imageResultEmpty').classList.add('hidden');
    const resultContent = document.getElementById('imageResultContent');
    resultContent.classList.remove('hidden');

    // Inference badge
    const badge = document.getElementById('inferenceTimeBadge');
    badge.textContent = `${durationMs} ms (${data.inference_time_ms ? data.inference_time_ms + 'ms AI' : ''})`;
    badge.classList.remove('hidden');

    // Result Image
    const displayImg = document.getElementById('imageResultDisplay');
    if (data.annotated_image) {
        displayImg.src = data.annotated_image;
    } else {
        displayImg.src = URL.createObjectURL(selectedImageFile);
    }

    // Top 1 Prediction
    const top = data.top_prediction || (data.predictions && data.predictions[0]);
    const foodDetails = data.food_details;

    if (top) {
        const nameVn = foodDetails ? foodDetails.name_vn : formatClassName(top.class_name);
        document.getElementById('topClassName').textContent = nameVn;
        document.getElementById('topConfidence').textContent = `${(top.confidence * 100).toFixed(1)}%`;
        
        if (foodDetails) {
            document.getElementById('topClassDesc').textContent = foodDetails.category || 'Món ăn truyền thống Việt Nam';
            document.getElementById('dishCategoryBadge').textContent = foodDetails.category || 'Món ăn Việt Nam';
            document.getElementById('dishInfoCard').classList.remove('hidden');
            
            // Nutrition
            document.getElementById('nutritionCaloriesBadge').textContent = foodDetails.calories || '--';
            const macrosGrid = document.getElementById('nutritionMacrosGrid');
            macrosGrid.innerHTML = '';
            
            const nutrition = foodDetails.nutrition || {};
            const macroConfig = [
                { key: 'Carbs', label: 'Tinh Bột', color: 'text-amber-400', bg: 'bg-amber-950/40 border-amber-800/50' },
                { key: 'Protein', label: 'Chất Đạm', color: 'text-emerald-400', bg: 'bg-emerald-950/40 border-emerald-800/50' },
                { key: 'Fat', label: 'Chất Béo', color: 'text-rose-400', bg: 'bg-rose-950/40 border-rose-800/50' }
            ];

            macroConfig.forEach(m => {
                const val = nutrition[m.key] || '--';
                const col = document.createElement('div');
                col.className = `p-2 rounded-lg border ${m.bg}`;
                col.innerHTML = `
                    <div class="text-[11px] text-slate-400">${m.label}</div>
                    <div class="font-bold font-mono text-sm ${m.color} mt-0.5">${val}</div>
                `;
                macrosGrid.appendChild(col);
            });

            // Ingredient Breakdown List
            const ingContainer = document.getElementById('ingredientCardsContainer');
            ingContainer.innerHTML = '';
            
            const ingredients = foodDetails.ingredients || [];
            ingredients.forEach((ing, i) => {
                const card = document.createElement('div');
                card.className = 'p-3 rounded-xl bg-slate-900/80 border border-slate-700/80 hover:border-orange-500/50 transition-colors';
                
                const portion = ing.portion || 20;
                card.innerHTML = `
                    <div class="flex items-center justify-between mb-1.5">
                        <div class="flex items-center gap-2">
                            <span class="w-5 h-5 rounded-full bg-orange-500/20 text-orange-400 flex items-center justify-center text-xs font-bold font-mono">${i + 1}</span>
                            <span class="font-semibold text-slate-100 text-xs">${ing.name}</span>
                            <span class="text-[11px] text-slate-400 italic">(${ing.name_en})</span>
                        </div>
                        <span class="font-mono text-xs font-bold text-orange-400 bg-orange-950/60 px-2 py-0.5 rounded border border-orange-800/40">${portion}%</span>
                    </div>
                    <p class="text-[11px] text-slate-400 leading-relaxed mb-2">${ing.desc}</p>
                    <div class="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                        <div class="bg-gradient-to-r from-orange-500 to-amber-400 h-1.5 rounded-full transition-all duration-700" style="width: ${portion}%"></div>
                    </div>
                `;
                ingContainer.appendChild(card);
            });
        } else {
            document.getElementById('topClassDesc').textContent = `Mã lớp: ${top.class_name}`;
            document.getElementById('dishInfoCard').classList.add('hidden');
        }
    } else {
        document.getElementById('topClassName').textContent = 'Chưa phát hiện món ăn';
        document.getElementById('topConfidence').textContent = '0%';
        document.getElementById('topClassDesc').textContent = 'Không tìm thấy món ăn nào đạt ngưỡng tin cậy. Hãy thử góc chụp rõ hơn hoặc ảnh khác.';
        document.getElementById('dishInfoCard').classList.add('hidden');
        document.getElementById('ingredientCardsContainer').innerHTML = '<p class="text-xs text-slate-500 text-center py-4">Chưa có thông tin nguyên liệu</p>';
    }
}

// ================= TAB 2: VIDEO LOGIC =================
function initVideoTab() {
    const dropZone = document.getElementById('videoDropZone');
    const fileInput = document.getElementById('videoFileInput');
    const preview = document.getElementById('videoInputPreview');
    const emptyPrompt = document.getElementById('videoEmptyPrompt');
    const btnProcess = document.getElementById('btnProcessVideo');
    const frameStepInput = document.getElementById('frameStepInput');
    const frameStepVal = document.getElementById('frameStepVal');

    frameStepInput.addEventListener('input', (e) => {
        frameStepVal.textContent = `Mỗi ${e.target.value} khung hình`;
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleVideoFile(e.target.files[0]);
        }
    });

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('border-orange-500', 'bg-slate-900/80');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('border-orange-500', 'bg-slate-900/80');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleVideoFile(e.dataTransfer.files[0]);
        }
    });

    btnProcess.addEventListener('click', processVideo);
}

function handleVideoFile(file) {
    if (!file.type.startsWith('video/')) {
        alert('Vui lòng chọn một tệp video hợp lệ (MP4, WEBM, MOV, AVI).');
        return;
    }
    selectedVideoFile = file;

    const preview = document.getElementById('videoInputPreview');
    const emptyPrompt = document.getElementById('videoEmptyPrompt');
    preview.src = URL.createObjectURL(file);
    preview.classList.remove('hidden');
    emptyPrompt.classList.add('hidden');
    document.getElementById('btnProcessVideo').disabled = false;
}

async function processVideo() {
    if (!selectedVideoFile || isProcessingVideo) return;

    isProcessingVideo = true;
    const btnProcess = document.getElementById('btnProcessVideo');
    const btnText = document.getElementById('btnProcessVideoText');
    const progressWrapper = document.getElementById('videoProgressWrapper');
    const progressBar = document.getElementById('videoProgressBar');
    const statusText = document.getElementById('videoStatusText');
    const percentText = document.getElementById('videoPercentText');

    btnProcess.disabled = true;
    btnText.textContent = 'Đang xử lý video...';
    progressWrapper.classList.remove('hidden');
    progressBar.style.width = '15%';
    percentText.textContent = '15%';
    statusText.textContent = 'Đang tải lên và trích xuất khung hình...';

    const frameStep = document.getElementById('frameStepInput').value;
    const formData = new FormData();
    formData.append('file', selectedVideoFile);
    formData.append('frame_step', frameStep);

    // Simulated progress increment while server processes
    let progressTimer = setInterval(() => {
        let currentWidth = parseInt(progressBar.style.width) || 15;
        if (currentWidth < 90) {
            currentWidth += 5;
            progressBar.style.width = currentWidth + '%';
            percentText.textContent = currentWidth + '%';
            if (currentWidth > 50) {
                statusText.textContent = 'Mô hình AI đang gán nhãn từng khung hình...';
            }
        }
    }, 1200);

    try {
        const res = await fetch('/api/predict/video', {
            method: 'POST',
            body: formData
        });

        clearInterval(progressTimer);

        if (!res.ok) {
            throw new Error(`Lỗi máy chủ (${res.status})`);
        }

        progressBar.style.width = '100%';
        percentText.textContent = '100%';
        statusText.textContent = 'Xử lý video hoàn tất!';

        const data = await res.json();
        displayVideoResults(data);
    } catch (err) {
        clearInterval(progressTimer);
        console.error(err);
        alert('Có lỗi xảy ra khi xử lý video: ' + err.message);
    } finally {
        isProcessingVideo = false;
        btnProcess.disabled = false;
        btnText.textContent = 'Bắt Đầu Xử Lý Video';
    }
}

function displayVideoResults(data) {
    document.getElementById('videoResultEmpty').classList.add('hidden');
    const resultContent = document.getElementById('videoResultContent');
    resultContent.classList.remove('hidden');

    const videoPlayer = document.getElementById('videoOutputPlayer');
    videoPlayer.src = data.video_url;
    videoPlayer.load();

    const downloadBtn = document.getElementById('btnDownloadVideo');
    downloadBtn.href = data.video_url;
    downloadBtn.classList.remove('hidden');

    // Video Stats
    const statsContainer = document.getElementById('videoStatsContainer');
    statsContainer.innerHTML = '';
    
    if (data.class_counts) {
        for (const [cls, count] of Object.entries(data.class_counts)) {
            const chip = document.createElement('div');
            chip.className = 'p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex justify-between items-center';
            chip.innerHTML = `
                <span class="text-slate-300 font-medium">${formatClassName(cls)}</span>
                <span class="font-mono text-orange-400 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-700/60">${count} frames</span>
            `;
            statsContainer.appendChild(chip);
        }
    }
}

// ================= TAB 3: CAMERA TRỰC TIẾP =================
function initCameraTab() {
    const btnToggle = document.getElementById('btnToggleCamera');
    const btnSnapshot = document.getElementById('btnCaptureSnapshot');
    const camSelect = document.getElementById('cameraSelect');
    const freqSlider = document.getElementById('analysisFreqSlider');
    const freqVal = document.getElementById('analysisFreqVal');

    // Enumerate devices
    enumerateCameras();

    btnToggle.addEventListener('click', toggleCamera);
    btnSnapshot.addEventListener('click', captureSnapshot);

    freqSlider.addEventListener('input', (e) => {
        freqVal.textContent = `${e.target.value} lần / giây`;
        if (cameraActive) {
            restartCameraAnalysisLoop();
        }
    });
}

async function enumerateCameras() {
    const select = document.getElementById('cameraSelect');
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
            select.innerHTML = '<option value="">Camera không hỗ trợ trên trình duyệt này</option>';
            return;
        }

        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');

        select.innerHTML = '';
        if (videoDevices.length === 0) {
            select.innerHTML = '<option value="">Không tìm thấy camera</option>';
            return;
        }

        videoDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${index + 1}`;
            select.appendChild(option);
        });
    } catch (err) {
        console.warn('Lỗi dò camera:', err);
    }
}

async function toggleCamera() {
    if (cameraActive) {
        stopCamera();
    } else {
        await startCamera();
    }
}

async function startCamera() {
    const video = document.getElementById('webcamElement');
    const select = document.getElementById('cameraSelect');
    const btnToggleText = document.getElementById('btnToggleCameraText');
    const placeholder = document.getElementById('cameraOffPlaceholder');
    const btnSnapshot = document.getElementById('btnCaptureSnapshot');
    const statusDot = document.getElementById('camStatusDot');
    const statusText = document.getElementById('camStatusText');

    const deviceId = select.value;
    const constraints = {
        video: deviceId ? { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } } : { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
    };

    try {
        webcamStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = webcamStream;
        await video.play();

        cameraActive = true;
        placeholder.classList.add('hidden');
        btnToggleText.textContent = 'Tắt Camera';
        btnSnapshot.disabled = false;
        
        statusDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
        statusText.textContent = 'Đang nhận diện Live';

        // Re-enumerate to get labels if permissions were just granted
        enumerateCameras();

        startCameraAnalysisLoop();
        startFpsMonitor();
    } catch (err) {
        console.error('Không thể mở camera:', err);
        alert('Không thể mở camera: ' + err.message + '\nVui lòng kiểm tra quyền cho phép truy cập camera trong trình duyệt.');
    }
}

function stopCamera() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }

    if (cameraIntervalId) {
        clearInterval(cameraIntervalId);
        cameraIntervalId = null;
    }

    if (fpsInterval) {
        clearInterval(fpsInterval);
        fpsInterval = null;
    }

    const video = document.getElementById('webcamElement');
    video.srcObject = null;

    // Clear overlay canvas
    const canvas = document.getElementById('overlayCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    cameraActive = false;
    document.getElementById('cameraOffPlaceholder').classList.remove('hidden');
    document.getElementById('btnToggleCameraText').textContent = 'Bật Camera';
    document.getElementById('btnCaptureSnapshot').disabled = true;
    document.getElementById('liveDetectionBadge').classList.add('hidden');

    const statusDot = document.getElementById('camStatusDot');
    const statusText = document.getElementById('camStatusText');
    statusDot.className = 'w-2 h-2 rounded-full bg-slate-600';
    statusText.textContent = 'Đã dừng';
    document.getElementById('fpsCounter').textContent = '0';
}

function startCameraAnalysisLoop() {
    if (cameraIntervalId) clearInterval(cameraIntervalId);
    
    const freq = parseInt(document.getElementById('analysisFreqSlider').value) || 5;
    const intervalMs = Math.round(1000 / freq);

    cameraIntervalId = setInterval(captureAndAnalyzeFrame, intervalMs);
}

function restartCameraAnalysisLoop() {
    if (cameraActive) {
        startCameraAnalysisLoop();
    }
}

let isFrameAnalyzing = false;
async function captureAndAnalyzeFrame() {
    if (!cameraActive || isFrameAnalyzing) return;
    
    const video = document.getElementById('webcamElement');
    if (!video.videoWidth || !video.videoHeight) return;

    isFrameAnalyzing = true;

    // Create a temporary canvas for grabbing frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    tempCanvas.toBlob(async (blob) => {
        if (!blob) {
            isFrameAnalyzing = false;
            return;
        }

        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        try {
            const res = await fetch('/api/predict/camera-frame', {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                const data = await res.json();
                renderLiveDetection(data, video.videoWidth, video.videoHeight);
                frameCount++;
            }
        } catch (err) {
            console.debug('Frame predict error:', err);
        } finally {
            isFrameAnalyzing = false;
        }
    }, 'image/jpeg', 0.85);
}

function renderLiveDetection(data, videoW, videoH) {
    const canvas = document.getElementById('overlayCanvas');
    canvas.width = videoW;
    canvas.height = videoH;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const top = data.top_prediction || (data.predictions && data.predictions[0]);
    if (!top) return;

    const nameVn = formatClassName(top.class_name);
    const scorePct = (top.confidence * 100).toFixed(1);

    // Update HUD Badge
    const hudBadge = document.getElementById('liveDetectionBadge');
    hudBadge.classList.remove('hidden');
    document.getElementById('liveDetectionDish').textContent = nameVn;
    document.getElementById('liveDetectionScore').textContent = `${scorePct}%`;

    // Draw HUD graphics on canvas if detection/classification
    if (data.boxes && data.boxes.length > 0) {
        data.boxes.forEach(b => {
            const [x1, y1, x2, y2] = b.coords;
            ctx.lineWidth = 3;
            ctx.strokeStyle = '#22c55e';
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            ctx.fillStyle = '#22c55e';
            ctx.fillRect(x1, Math.max(0, y1 - 26), 180, 26);

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 14px sans-serif';
            ctx.fillText(`${formatClassName(b.class_name)} ${(b.confidence * 100).toFixed(0)}%`, x1 + 6, Math.max(18, y1 - 8));
        });
    } else {
        // Draw elegant corner bounding bracket indicating live active tracking
        const pad = 30;
        ctx.strokeStyle = 'rgba(249, 115, 22, 0.7)';
        ctx.lineWidth = 3;
        const cornerLen = 40;

        // Top-left
        ctx.beginPath();
        ctx.moveTo(pad, pad + cornerLen);
        ctx.lineTo(pad, pad);
        ctx.lineTo(pad + cornerLen, pad);
        ctx.stroke();

        // Top-right
        ctx.beginPath();
        ctx.moveTo(videoW - pad - cornerLen, pad);
        ctx.lineTo(videoW - pad, pad);
        ctx.lineTo(videoW - pad, pad + cornerLen);
        ctx.stroke();

        // Bottom-left
        ctx.beginPath();
        ctx.moveTo(pad, videoH - pad - cornerLen);
        ctx.lineTo(pad, videoH - pad);
        ctx.lineTo(pad + cornerLen, videoH - pad);
        ctx.stroke();

        // Bottom-right
        ctx.beginPath();
        ctx.moveTo(videoW - pad - cornerLen, videoH - pad);
        ctx.lineTo(videoW - pad, videoH - pad);
        ctx.lineTo(videoW - pad, videoH - pad - cornerLen);
        ctx.stroke();
    }

    // Update Live Ingredients in Sidebar
    const liveBarsContainer = document.getElementById('livePredictionBars');
    liveBarsContainer.innerHTML = '';
    const ingredients = (data.food_details && data.food_details.ingredients) ? data.food_details.ingredients : [];
    
    if (ingredients.length > 0) {
        ingredients.forEach((ing) => {
            const row = document.createElement('div');
            row.className = 'p-2 rounded-lg bg-slate-900/80 border border-slate-700/60 text-xs';
            row.innerHTML = `
                <div class="flex justify-between items-center mb-1">
                    <span class="text-slate-200 font-semibold">${ing.name}</span>
                    <span class="font-mono text-orange-400 font-bold">${ing.portion}%</span>
                </div>
                <div class="w-full bg-slate-950 rounded-full h-1 overflow-hidden">
                    <div class="bg-gradient-to-r from-orange-500 to-amber-400 h-1 rounded-full" style="width: ${ing.portion}%"></div>
                </div>
            `;
            liveBarsContainer.appendChild(row);
        });
    } else {
        (data.predictions || []).slice(0, 3).forEach((p, idx) => {
            const pct = (p.confidence * 100).toFixed(1);
            const dishName = formatClassName(p.class_name);
            const row = document.createElement('div');
            row.className = 'space-y-1';
            row.innerHTML = `
                <div class="flex justify-between text-xs">
                    <span class="text-slate-300 font-medium">${idx + 1}. ${dishName}</span>
                    <span class="font-mono text-orange-400 font-bold">${pct}%</span>
                </div>
                <div class="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-700/60">
                    <div class="bg-gradient-to-r from-orange-500 to-amber-400 h-1.5 rounded-full transition-all duration-300" style="width: ${pct}%"></div>
                </div>
            `;
            liveBarsContainer.appendChild(row);
        });
    }

    // Optional Audio Voice Speech
    const chkAudio = document.getElementById('chkAudioTTS');
    if (chkAudio && chkAudio.checked && top.confidence > 0.65) {
        speakDishName(nameVn);
    }
}

function speakDishName(dishName) {
    if (!synth) return;
    const now = Date.now();
    // Throttle speech to once every 4 seconds per new dish
    if (lastSpokenClass === dishName && (now - lastSpeechTime) < 4000) {
        return;
    }
    if ((now - lastSpeechTime) < 2500) {
        return;
    }

    lastSpokenClass = dishName;
    lastSpeechTime = now;

    const utter = new SpeechSynthesisUtterance(dishName);
    utter.lang = 'vi-VN';
    utter.rate = 1.0;
    synth.speak(utter);
}

function startFpsMonitor() {
    frameCount = 0;
    fpsInterval = setInterval(() => {
        document.getElementById('fpsCounter').textContent = frameCount;
        frameCount = 0;
    }, 1000);
}

// Snapshot capture
let snapshotCount = 0;
function captureSnapshot() {
    const video = document.getElementById('webcamElement');
    const overlay = document.getElementById('overlayCanvas');
    if (!video.videoWidth) return;

    const snapCanvas = document.createElement('canvas');
    snapCanvas.width = video.videoWidth;
    snapCanvas.height = video.videoHeight;
    const ctx = snapCanvas.getContext('2d');

    // Draw video frame then overlay
    ctx.drawImage(video, 0, 0, snapCanvas.width, snapCanvas.height);
    ctx.drawImage(overlay, 0, 0, snapCanvas.width, snapCanvas.height);

    const dataUrl = snapCanvas.toDataURL('image/jpeg');

    const gallery = document.getElementById('snapshotGallery');
    const img = document.createElement('img');
    img.src = dataUrl;
    img.className = 'snapshot-thumb';
    img.title = 'Bấm để tải về';
    img.onclick = () => {
        const link = document.createElement('a');
        link.download = `snapshot_${Date.now()}.jpg`;
        link.href = dataUrl;
        link.click();
    };

    gallery.prepend(img);
    snapshotCount++;
    document.getElementById('snapshotCount').textContent = snapshotCount;
}
