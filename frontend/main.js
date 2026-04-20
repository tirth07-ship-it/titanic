// ===== PARTICLE SYSTEM =====
function createParticles() {
  const container = document.getElementById('particles');
  const count = 30;
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
    const duration = (Math.random() * 20 + 10) + 's';
    const delay = (Math.random() * 20) + 's';
    p.style.animation = `float ${duration} ${delay} linear infinite`;
    container.appendChild(p);
  }
}
createParticles();

// ===== BUTTON GROUPS =====
document.querySelectorAll('.btn-group').forEach(group => {
  const groupId = group.id;
  const hiddenId = groupId.replace('-group', '');
  const hidden = document.getElementById(hiddenId);

  group.querySelectorAll('.opt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      group.querySelectorAll('.opt-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      hidden.value = btn.dataset.value;
    });
  });
});

// ===== SLIDERS =====
const ageSlider = document.getElementById('age');
const fareSlider = document.getElementById('fare');
const ageDisplay = document.getElementById('age-display');
const fareDisplay = document.getElementById('fare-display');

ageSlider.addEventListener('input', () => {
  ageDisplay.textContent = ageSlider.value;
});

fareSlider.addEventListener('input', () => {
  fareDisplay.textContent = '£' + fareSlider.value;
});

// ===== NUMBER INPUTS =====
function changeNum(field, delta) {
  const hidden = document.getElementById(field);
  const display = document.getElementById(field + '-val');
  let val = parseInt(hidden.value) + delta;
  val = Math.max(0, Math.min(8, val));
  hidden.value = val;
  display.textContent = val;
}

// ===== PREDICT =====
async function predict() {
  const btn = document.getElementById('predict-btn');
  const btnText = btn.querySelector('.btn-text');
  const placeholder = document.getElementById('result-placeholder');
  const resultContent = document.getElementById('result-content');

  btn.classList.add('loading');
  btnText.textContent = 'PREDICTING...';
  btn.disabled = true;

  const payload = {
    pclass: document.getElementById('pclass').value,
    sex: document.getElementById('sex').value,
    age: document.getElementById('age').value,
    sibsp: document.getElementById('sibsp').value,
    parch: document.getElementById('parch').value,
    fare: document.getElementById('fare').value,
    embarked: document.getElementById('embarked').value
  };

  try {
    const res = await fetch('http://127.0.0.1:5000/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.error) {
      alert('Error: ' + data.error);
      return;
    }

    // Show result
    placeholder.classList.add('hidden');
    resultContent.classList.remove('hidden');

    const icon = document.getElementById('result-icon');
    const verdict = document.getElementById('result-verdict');
    const sub = document.getElementById('result-sub');
    const survBar = document.getElementById('survival-bar');
    const dieBar = document.getElementById('death-bar');
    const survPct = document.getElementById('survival-pct');
    const diePct = document.getElementById('death-pct');

    if (data.survived === 1) {
      icon.textContent = '🛟';
      verdict.textContent = 'SURVIVED';
      verdict.className = 'result-verdict survived-verdict';
      sub.textContent = 'This passenger made it out alive';
    } else {
      icon.textContent = '⚰️';
      verdict.textContent = 'PERISHED';
      verdict.className = 'result-verdict died-verdict';
      sub.textContent = 'This passenger did not survive';
    }

    // Animate bars
    survBar.style.width = '0%';
    dieBar.style.width = '0%';
    survPct.textContent = '';
    diePct.textContent = '';

    setTimeout(() => {
      survBar.style.width = data.survival_probability + '%';
      dieBar.style.width = data.death_probability + '%';
      survPct.textContent = data.survival_probability + '%';
      diePct.textContent = data.death_probability + '%';
    }, 100);

  } catch (err) {
    alert('Connection error. Make sure Flask server is running.');
    console.error(err);
  } finally {
    btn.classList.remove('loading');
    btnText.textContent = 'PREDICT FATE';
    btn.disabled = false;
  }
}

// ===== FETCH STATS & ANIMATE ON LOAD =====
window.addEventListener('load', async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/stats');
    const stats = await res.json();
    
    // Populate header stats
    document.getElementById('stat-accuracy').textContent = stats.accuracy;
    document.getElementById('stat-train_size').textContent = stats.train_size;
    document.getElementById('stat-survived_pct').textContent = stats.survived_pct;
    document.getElementById('stat-total_passengers').textContent = stats.total_passengers;

    // Populate Feature Importance
    const impList = document.getElementById('importance-list');
    const features = [
      { name: 'Sex', val: stats.feature_importances['Sex_encoded'], icon: '♀♂' },
      { name: 'Fare', val: stats.feature_importances['Fare'], icon: '£' },
      { name: 'Age', val: stats.feature_importances['Age'], icon: '🎂' },
      { name: 'Class', val: stats.feature_importances['Pclass'], icon: '🎫' },
      { name: 'Siblings/Spouse', val: stats.feature_importances['SibSp'], icon: '👥' },
      { name: 'Parents/Children', val: stats.feature_importances['Parch'], icon: '👨‍👩‍👧' },
      { name: 'Embarked', val: stats.feature_importances['Embarked_encoded'], icon: '⚓' }
    ];

    features.forEach(f => {
      const pct = (f.val * 100).toFixed(1);
      const row = document.createElement('div');
      row.className = 'imp-row';
      row.innerHTML = `
        <span class="imp-icon">${f.icon}</span>
        <span class="imp-name">${f.name}</span>
        <div class="imp-track">
          <div class="imp-fill" style="width: 0%" data-target="${pct}%"></div>
        </div>
        <span class="imp-val">${pct}%</span>
      `;
      impList.appendChild(row);
    });

    // Animate bars
    setTimeout(() => {
      document.querySelectorAll('.imp-fill').forEach(fill => {
        fill.style.width = fill.dataset.target;
      });
    }, 400);

  } catch (err) {
    console.error('Failed to fetch stats:', err);
  }
});

// ===== KEYBOARD SHORTCUT =====
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !document.getElementById('predict-btn').disabled) {
    predict();
  }
});
