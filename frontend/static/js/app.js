// app.js — PART 1: Setup & Global State
const canvas = new fabric.Canvas('c', { selection: false });

let perfectImage = null;
let defectURL = null;
let perfectURL = null;
let originalURL = null;
let currentDefect = null;
let placedCount = 0;

let defectClones = [];
let spacing = 30;
let activeBatch = 0;

const spacingSlider = document.getElementById('spacingSlider');
const rotationSlider = document.getElementById('rotateSlider');
const scaleSlider = document.getElementById('scaleSlider');
const previewDefectImg = document.getElementById('previewDefectImg');
const originalDefectImg = document.getElementById('originalDefectImg');
const zoomIndicator = document.getElementById('zoomIndicator');
const placementStatus = document.getElementById('placementStatus');
const saveBtn = document.getElementById('saveBtn');
const resetBtn = document.getElementById('resetDefect');
const downloadBtn = document.getElementById('downloadBtn');
const doneStatus = document.getElementById('doneStatus'); // ✅ New line for tick mark div

// app.js — PART 2: Load Next Image Pair & Clone Defects
function loadNextPair() {
  fetch('/next')
    .then(res => res.json())
    .then(data => {
      if (data.status !== 'ok') return alert(data.message || '🎉 All defects placed.');

      defectURL = `/${data.defect_image}`;
      perfectURL = `/${data.perfect_image}`;
      originalURL = `/${data.original_image}`;
      currentDefect = data.defect_name;
      placedCount = data.count || 0;

      if (data.done) {
        saveBtn.disabled = true;
        saveBtn.textContent = '✅ Done';
        if (doneStatus) doneStatus.style.display = 'block';
      } else {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save';
        if (doneStatus) doneStatus.style.display = 'none';
      }


      canvas.clear();

      fabric.Image.fromURL(perfectURL, (img) => {
        perfectImage = img;
        img.selectable = false;
        canvas.setWidth(img.width);
        canvas.setHeight(img.height);
        canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
      });

      if (previewDefectImg) previewDefectImg.src = defectURL;
      if (originalDefectImg) originalDefectImg.src = originalURL;

      fabric.Image.fromURL(defectURL, (defectImg) => {
        const baseX = canvas.getWidth() * 0.4;
        const baseY = 100;
        const scale = parseFloat(scaleSlider.value);
        const angle = parseInt(rotationSlider.value);

        defectClones = [];
        for (let i = 0; i < 45; i++) {
          const clone = fabric.util.object.clone(defectImg);
          clone.set({
            left: baseX,
            top: baseY + i * spacing,
            scaleX: scale,
            scaleY: scale,
            angle: angle,
            hasControls: false,
            hasBorders: false,
            selectable: false,
            opacity: 1
          });
          canvas.add(clone);
          defectClones.push(clone);
        }

        updateStatus();
        canvas.renderAll();
      });
    });
}
saveBtn?.addEventListener('click', async () => {
  if (!perfectImage || defectClones.length === 0) return alert('⚠️ No defect clones found');
  saveBtn.disabled = true;

  for (let i = 0; i < defectClones.length; i++) {
    canvas.clear();
    canvas.setWidth(perfectImage.width);
    canvas.setHeight(perfectImage.height);
    canvas.setBackgroundImage(perfectImage, canvas.renderAll.bind(canvas));
    canvas.add(defectClones[i]);
    canvas.setActiveObject(defectClones[i]);
    canvas.renderAll();

    const composite = canvas.toDataURL({ format: 'jpeg', quality: 1 });
    const filename = `${currentDefect.replace('.png', '')}_augment_${i + 1}.jpg`; // ✅ Here

    await fetch('/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, composite })
    });
  }

  placedCount++;
  loadNextPair();

  const color = document.getElementById('colorSelector')?.value;
  if (color) updateProgressBar(color);

  saveBtn.disabled = false;
});


resetBtn?.addEventListener('click', () => {
  loadNextPair();
});

downloadBtn?.addEventListener('click', () => {
  const dataURL = canvas.toDataURL({ format: 'jpeg', quality: 1 });
  const a = document.createElement('a');
  a.href = dataURL;
  a.download = `${Date.now()}_preview.jpg`;
  a.click();
});

spacingSlider?.addEventListener('input', () => {
  spacing = parseInt(spacingSlider.value);
  updateClonePositions();
});
// app.js — PART 4: Batch Control & Keyboard Interaction
function updateClonePositions() {
  if (defectClones.length === 0) return;
  const baseX = defectClones[0].left;
  const baseY = defectClones[0].top;
  for (let i = 0; i < defectClones.length; i++) {
    defectClones[i].top = baseY + i * spacing;
  }
  canvas.renderAll();
}

function updateStatus() {
  placementStatus.textContent = `Defect: ${currentDefect} | Batch ${activeBatch + 1}/5`;
}


document.addEventListener('keydown', (e) => {
  if (!defectClones.length) return;

  const moveStep = e.shiftKey ? 10 : 3;
  const scaleStep = 0.05;
  const rotateStep = 5;
  const batchSize = 9;

  const start = activeBatch * batchSize;
  const end = Math.min(start + batchSize, defectClones.length);
  const batch = defectClones.slice(start, end);
  let changed = false;

  switch (e.key) {
    case 'ArrowLeft': batch.forEach(d => d.left -= moveStep); changed = true; break;
    case 'ArrowRight': batch.forEach(d => d.left += moveStep); changed = true; break;
    case 'ArrowUp': batch.forEach(d => d.top -= moveStep); changed = true; break;
    case 'ArrowDown': batch.forEach(d => d.top += moveStep); changed = true; break;
    case '+':
    case '=': batch.forEach(d => { d.scaleX += scaleStep; d.scaleY += scaleStep }); changed = true; break;
    case '-': batch.forEach(d => {
      d.scaleX = Math.max(0.1, d.scaleX - scaleStep);
      d.scaleY = Math.max(0.1, d.scaleY - scaleStep);
    }); changed = true; break;
    case 'r': case 'R': batch.forEach(d => d.angle += rotateStep); changed = true; break;
    case 'l': case 'L': batch.forEach(d => d.angle -= rotateStep); changed = true; break;
    case '0':
      const baseX = canvas.getWidth() * 0.4;
      for (let i = 0; i < defectClones.length; i++) {
        defectClones[i].left = baseX;
        defectClones[i].top = 100 + i * spacing;
        defectClones[i].scaleX = 0.5;
        defectClones[i].scaleY = 0.5;
        defectClones[i].angle = 0;
      }
      changed = true;
      break;
    case '1': case '2': case '3': case '4': case '5':
      activeBatch = parseInt(e.key) - 1;
      updateStatus();
      break;
    case '[':
      spacing = Math.max(5, spacing - 5);
      spacingSlider.value = spacing;
      updateClonePositions();
      break;
    case ']':
      spacing = Math.min(200, spacing + 5);
      spacingSlider.value = spacing;
      updateClonePositions();
      break;
    case 's':
      if (e.ctrlKey) {
        e.preventDefault();
        saveBtn.click();
      }
      break;
  }

  if (changed) {
    batch.forEach(d => d.setCoords());
    canvas.renderAll();
    e.preventDefault();
  }
});

document.getElementById('refreshPerfectBtn')?.addEventListener('click', () => {
  fetch('/refresh_background')
    .then(res => res.json())
    .then(data => {
      if (data.status !== 'ok') return alert(data.message || '⚠️ Could not load another background.');

      defectURL = `/${data.defect_image}`;
      perfectURL = `/${data.perfect_image}`;
      originalURL = `/${data.original_image}`;
      currentDefect = data.defect_name;
      placedCount = data.count || 0;

      // ✅ Handle "done" status here
      if (data.done) {
        saveBtn.disabled = true;
        saveBtn.textContent = '✅ Done';
        if (doneStatus) doneStatus.style.display = 'block';
      } else {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save';
        if (doneStatus) doneStatus.style.display = 'none';
      }

      canvas.clear();

      fabric.Image.fromURL(perfectURL, (img) => {
        perfectImage = img;
        img.selectable = false;
        canvas.setWidth(img.width);
        canvas.setHeight(img.height);
        canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
      });

      if (previewDefectImg) previewDefectImg.src = defectURL;
      if (originalDefectImg) originalDefectImg.src = originalURL;

      fabric.Image.fromURL(defectURL, (defectImg) => {
        const baseX = canvas.getWidth() * 0.4;
        const baseY = 100;
        const scale = parseFloat(scaleSlider.value);
        const angle = parseInt(rotationSlider.value);

        defectClones = [];
        for (let i = 0; i < 45; i++) {
          const clone = fabric.util.object.clone(defectImg);
          clone.set({
            left: baseX,
            top: baseY + i * spacing,
            scaleX: scale,
            scaleY: scale,
            angle: angle,
            hasControls: false,
            hasBorders: false,
            selectable: false,
            opacity: 1
          });
          canvas.add(clone);
          defectClones.push(clone);
        }

        updateStatus();
        canvas.renderAll();
      });
    });
});

// app.js — PART 5: Zoom, Skip, Delete, Init
canvas.on('mouse:wheel', (opt) => {
  if (!opt.e.ctrlKey) return;
  let zoom = canvas.getZoom();
  zoom *= 0.999 ** opt.e.deltaY;
  zoom = Math.max(0.5, Math.min(zoom, 3));
  canvas.setZoom(zoom);
  if (zoomIndicator) zoomIndicator.textContent = `${Math.round(zoom * 100)}%`;
  opt.e.preventDefault();
  opt.e.stopPropagation();
});

canvas.on('mouse:dblclick', (opt) => {
  const target = opt.target;
  if (!target) return;
  canvas.remove(target);
  defectClones = defectClones.filter(d => d !== target);
});

function skip(direction) {
  fetch(`/skip/${direction}`)
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        currentDefect = data.defect;
        placedCount = 0;
        loadNextPair();
      } else {
        alert('❌ Error skipping defect');
      }
    });
}

function updateProgressBar(color) {
  fetch(`/progress/${color}`)
    .then(res => res.json())
    .then(data => {
      const { current, total } = data;
      const percent = total > 0 ? Math.round((current / total) * 100) : 0;
      document.getElementById('progressBar').style.width = `${percent}%`;
      document.getElementById('progressLabel').textContent = `${current} / ${total} (${percent}%)`;
    });
}


document.getElementById('nextBtn')?.addEventListener('click', () => skip('next'));
document.getElementById('prevBtn')?.addEventListener('click', () => skip('prev'));

window.addEventListener('load', () => {
  const initialColor = document.getElementById('colorSelector')?.value;
  if (initialColor) {
    fetch(`/init/${initialColor}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          loadNextPair();
          updateProgressBar(initialColor);  // ✅ Add this line
        }
      });
  }
});

