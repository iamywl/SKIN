/**
 * 따꼼 빠꼼 (DDAKKOM PPAKKOM) Frontend Application Logic
 * Strict Compliance: Price Service Design System (design-system.md)
 * Rules:
 *  - No arbitrary HEX in UI (Strict Semantic Utility Mapping)
 *  - Enforce tabular-nums font-mono for all numeric/price figures
 *  - Enforce text-right for all numerical table columns
 *  - 1.5px clean stroke charts, no gradients, no emojis
 */

let currentCategory = 'all';
let currentTreatmentKey = '울쎄라_300샷';
let currentTagFilter = 'all';
let densityChart = null;
let districtBarChart = null;

// ============================================================================
// 1. Theme Management (Light / Dark)
// ============================================================================
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
    updateThemeIcons(true);
  } else {
    document.documentElement.classList.remove('dark');
    updateThemeIcons(false);
  }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  updateThemeIcons(isDark);
  updateChartsTheme();
}

function updateThemeIcons(isDark) {
  const sun = document.getElementById('themeIconSun');
  const moon = document.getElementById('themeIconMoon');
  if (sun && moon) {
    if (isDark) {
      sun.classList.remove('hidden');
      moon.classList.add('hidden');
    } else {
      sun.classList.add('hidden');
      moon.classList.remove('hidden');
    }
  }
}

function getThemePalette() {
  const isDark = document.documentElement.classList.contains('dark');
  return {
    isDark,
    textPrimary: isDark ? '#f8fafc' : '#0f172a',
    textMuted: isDark ? '#94a3b8' : '#64748b',
    border: isDark ? '#1e293b' : '#e2e8f0',
    barDefault: isDark ? '#334155' : '#cbd5e1',     // slate-700 / slate-300
    barSelected: isDark ? '#f87171' : '#dc2626',    // rose-400 / rose-600
    lineStroke: isDark ? '#f8fafc' : '#0f172a',     // clean terminal monochrome line
    chartGrid: isDark ? '#1e293b' : '#f1f5f9'
  };
}

// ============================================================================
// 2. Navigation Tabs
// ============================================================================
function switchTab(tabId) {
  const tabs = ['calc', 'outliers', 'sources'];
  tabs.forEach(id => {
    const el = document.getElementById('tab' + id.charAt(0).toUpperCase() + id.slice(1));
    const btn = document.getElementById('tabBtn' + id.charAt(0).toUpperCase() + id.slice(1));
    if (el) el.classList.toggle('hidden', id !== tabId);
    if (btn) {
      if (id === tabId) {
        btn.className = 'px-2.5 py-1 rounded font-medium bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 shadow-none';
      } else {
        btn.className = 'px-2.5 py-1 rounded font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100';
      }
    }
  });

  if (tabId === 'outliers') {
    renderOutlierView();
  }
  lucide.createIcons();
}

// ============================================================================
// 3. Category & Treatment Setup
// ============================================================================
function initCategoriesAndTreatments() {
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;

  const container = document.getElementById('categoryChipsContainer');
  container.innerHTML = '';

  data.categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.type = 'button';
    const isActive = cat.id === currentCategory;
    btn.className = `px-2 py-1 text-xs font-medium rounded-md border transition-colors ${
      isActive
        ? 'bg-slate-900 text-white border-slate-900 dark:bg-slate-100 dark:text-slate-900 dark:border-slate-100 font-semibold'
        : 'bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
    }`;
    btn.textContent = cat.name;
    btn.onclick = () => selectCategory(cat.id);
    container.appendChild(btn);
  });

  populateTreatmentDropdown();
  populateOutlierTreatmentDropdown();
}

function selectCategory(catId) {
  currentCategory = catId;
  initCategoriesAndTreatments();
  populateTreatmentDropdown();
  calculatePricePosition();
}

function populateTreatmentDropdown() {
  const select = document.getElementById('treatmentSelect');
  const data = window.DAEGU_SKIN_DATA;
  if (!select || !data) return;

  select.innerHTML = '';
  const entries = Object.entries(data.treatments);

  const filtered = entries.filter(([key, t]) => {
    if (currentCategory === 'all') return true;
    return t.category === currentCategory;
  });

  filtered.forEach(([key, t]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = `${t.name} (표본 ${t.sample_count}곳)`;
    if (key === currentTreatmentKey) opt.selected = true;
    select.appendChild(opt);
  });

  if (filtered.length > 0 && !filtered.some(([k]) => k === currentTreatmentKey)) {
    currentTreatmentKey = filtered[0][0];
    select.value = currentTreatmentKey;
  }
}

function populateOutlierTreatmentDropdown() {
  const select = document.getElementById('outlierTreatmentSelect');
  const data = window.DAEGU_SKIN_DATA;
  if (!select || !data) return;

  select.innerHTML = '';
  Object.entries(data.treatments).forEach(([key, t]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = `${t.name} (표본 ${t.sample_count}곳)`;
    if (key === currentTreatmentKey) opt.selected = true;
    select.appendChild(opt);
  });
}

function onTreatmentSelectChange() {
  const select = document.getElementById('treatmentSelect');
  currentTreatmentKey = select.value;
  const outlierSelect = document.getElementById('outlierTreatmentSelect');
  if (outlierSelect) outlierSelect.value = currentTreatmentKey;

  const data = window.DAEGU_SKIN_DATA;
  const t = data.treatments[currentTreatmentKey];
  if (t) {
    document.getElementById('priceInput').value = t.price_inc_vat.median;
  }

  calculatePricePosition();
}

// ============================================================================
// 4. Quick Price Increment & Calculation
// ============================================================================
function adjustPrice(delta) {
  const input = document.getElementById('priceInput');
  let val = parseInt(input.value || '0', 10);
  val = Math.max(0, val + delta);
  input.value = val;
  calculatePricePosition();
}

function calculatePricePosition() {
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;

  const t = data.treatments[currentTreatmentKey];
  if (!t) return;

  const sampleBadge = document.getElementById('sampleCountBadge');
  if (sampleBadge) sampleBadge.textContent = `표본 ${t.sample_count}곳`;

  const rawInput = parseInt(document.getElementById('priceInput').value || '0', 10);
  const vatExclusive = document.getElementById('vatExclusiveCheckbox').checked;

  let actualPrice = rawInput;
  const vatNotice = document.getElementById('vatComputedNotice');
  const vatAmountSpan = document.getElementById('vatComputedAmount');

  if (vatExclusive) {
    actualPrice = Math.round(rawInput * 1.1);
    vatNotice.classList.remove('hidden');
    vatAmountSpan.textContent = `${actualPrice.toLocaleString()}원`;
  } else {
    vatNotice.classList.add('hidden');
  }

  document.getElementById('priceFormatted').textContent = `${actualPrice.toLocaleString()}원`;

  const district = document.getElementById('districtSelect').value;

  const stats = t.price_inc_vat;
  const median = stats.median;
  const q1 = stats.q1;
  const q3 = stats.q3;
  const lowFence = stats.low_fence;
  const highFence = stats.high_fence;
  const prices = stats.prices_sorted;

  let percentile = 50.0;
  if (prices.length > 0) {
    if (actualPrice <= prices[0]) {
      percentile = 0.0;
    } else if (actualPrice >= prices[prices.length - 1]) {
      percentile = 100.0;
    } else {
      let count = 0;
      for (let i = 0; i < prices.length; i++) {
        if (prices[i] <= actualPrice) count++;
      }
      percentile = Math.round((count / prices.length) * 1000) / 10;
    }
  }

  document.getElementById('percentileText').textContent = `상위 ${percentile.toFixed(1)}%`;
  document.getElementById('percentileBar').style.width = `${Math.min(100, Math.max(0, percentile))}%`;
  document.getElementById('percentileNeedle').style.left = `${Math.min(99, Math.max(1, percentile))}%`;

  const badgeText = document.getElementById('badgeText');
  const statusTag = document.getElementById('statusTag');
  const descEl = document.getElementById('diagDescription');

  let title = '대구 표준 적정 시세';
  let descText = '';

  const diffFromMedian = actualPrice - median;
  const diffStr = Math.abs(diffFromMedian).toLocaleString();

  if (actualPrice < lowFence) {
    title = '통계적 하한선 미만 (시술조건 확인 권장)';
    statusTag.className = 'inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-400 tabular-nums';
    statusTag.textContent = '조건확인 권장';
    descText = `통계적 하한선(${lowFence.toLocaleString()}원) 미만 구간입니다. 1회 첫방문 체험가이거나 세부 부위 한정 조건일 수 있으므로 예약 전 세부 시술 조건(용량/샷수)을 사전 확인하시기를 권장합니다.`;
  } else if (actualPrice < q1) {
    title = '실속 가성비 시세 (Q1 이하)';
    statusTag.className = 'inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-400 tabular-nums';
    statusTag.textContent = '가성비 우수';
    descText = `대구 하위 25%(Q1: ${q1.toLocaleString()}원) 이하의 경제적인 가격대입니다. 대구 중앙값 대비 ${diffStr}원 저렴합니다.`;
  } else if (actualPrice <= q3) {
    title = '대구 표준 적정 시세 (IQR 구간)';
    statusTag.className = 'inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 tabular-nums';
    statusTag.textContent = '적정 시세';
    const compText = diffFromMedian <= 0 ? `중앙값 대비 ${diffStr}원 저렴` : `중앙값 대비 ${diffStr}원 높음`;
    descText = `대구 전체 병의원의 50%가 밀집된 표준 시세 구간(${q1.toLocaleString()}원 ~ ${q3.toLocaleString()}원)입니다. (${compText})`;
  } else if (actualPrice <= highFence) {
    title = '상위 프리미엄 시세 (Q3 초과)';
    statusTag.className = 'inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 tabular-nums';
    statusTag.textContent = '프리미엄';
    descText = `수성구 전문의 1:1 진료 또는 복합 진정 케어가 포함된 상위 25% 구간입니다. 대구 중앙값 대비 ${diffStr}원 높습니다.`;
  } else {
    title = '통계적 상한선 초과 (복합옵션 확인)';
    statusTag.className = 'inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-400 tabular-nums';
    statusTag.textContent = '복합옵션 확인';
    descText = `통계적 상한선(${highFence.toLocaleString()}원)을 초과한 상위 구간입니다. 1:1 맞춤 진료 또는 복합 패키지 포함 여부를 확인하시기 바랍니다.`;
  }

  badgeText.textContent = title;
  descEl.textContent = descText;

  document.getElementById('metricMyPrice').textContent = `${actualPrice.toLocaleString()}원`;
  document.getElementById('metricMedian').textContent = `${median.toLocaleString()}원`;
  document.getElementById('metricIQR').textContent = `${q1.toLocaleString()} ~ ${q3.toLocaleString()}원`;

  const diffLabel = document.getElementById('metricDiffLabel');
  const metricDiff = document.getElementById('metricDiff');
  if (diffFromMedian < 0) {
    diffLabel.textContent = '중앙값 대비 절감';
    metricDiff.textContent = `-${diffStr}원`;
    metricDiff.className = 'text-sm font-bold font-mono tabular-nums text-emerald-700 dark:text-emerald-400';
  } else if (diffFromMedian > 0) {
    diffLabel.textContent = '중앙값 대비 초과';
    metricDiff.textContent = `+${diffStr}원`;
    metricDiff.className = 'text-sm font-bold font-mono tabular-nums text-rose-700 dark:text-rose-400';
  } else {
    diffLabel.textContent = '중앙값과 동일';
    metricDiff.textContent = '0원';
    metricDiff.className = 'text-sm font-bold font-mono tabular-nums text-slate-900 dark:text-slate-100';
  }

  const precautionsList = document.getElementById('medicalCheckpoints');
  precautionsList.innerHTML = '';
  const precs = [...(t.medical_precautions || [])];
  
  if (currentTreatmentKey.includes('1년무제한')) {
    const estCount = currentTreatmentKey.includes('종아리') ? 8 : 9;
    const perSessionPrice = Math.round(actualPrice / estCount);
    precs.unshift(`[1년 무제한권 팩트체크] 모주기(4~6주) 및 예약 규정상 연간 최대 유효 횟수는 ${estCount}회 내외입니다. 현재 입력가 기준 1회당 실질 체감 단가는 약 ${perSessionPrice.toLocaleString()}원입니다.`);
  }

  precs.slice(0, 3).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    precautionsList.appendChild(li);
  });

  renderDensityChart(t, actualPrice);
  renderDistrictBarChart(t, district);

  lucide.createIcons();
}

// ============================================================================
// 5. Terminal-Grade Charts (1.5px Stroke, No Gradients)
// ============================================================================
function updateChartsTheme() {
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;
  const t = data.treatments[currentTreatmentKey];
  if (!t) return;
  const actualPrice = parseInt(document.getElementById('priceInput').value || '0', 10);
  const district = document.getElementById('districtSelect').value;
  renderDensityChart(t, actualPrice);
  renderDistrictBarChart(t, district);
}

function renderDensityChart(treatment, userPrice) {
  const ctx = document.getElementById('densityChart');
  if (!ctx) return;

  const palette = getThemePalette();
  const stats = treatment.price_inc_vat;
  const mean = stats.mean;
  const std = stats.std || (stats.iqr / 1.35) || 50000;
  const q1 = stats.q1;
  const q3 = stats.q3;

  const minX = Math.max(0, mean - 3 * std);
  const maxX = mean + 3 * std;
  const step = (maxX - minX) / 45;

  const labels = [];
  const bellData = [];
  const iqrArea = [];

  for (let x = minX; x <= maxX; x += step) {
    labels.push(Math.round(x));
    const exponent = -0.5 * Math.pow((x - mean) / std, 2);
    const y = (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(exponent) * 1000000;
    bellData.push(y);
    if (x >= q1 && x <= q3) {
      iqrArea.push(y);
    } else {
      iqrArea.push(null);
    }
  }

  if (densityChart) {
    densityChart.destroy();
  }

  densityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '가격 분포 곡선',
          data: bellData,
          borderColor: palette.lineStroke,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.25
        },
        {
          label: '정상 시세(IQR) 구간',
          data: iqrArea,
          backgroundColor: palette.isDark ? 'rgba(51, 65, 85, 0.4)' : 'rgba(203, 213, 225, 0.5)',
          borderColor: 'transparent',
          pointRadius: 0,
          fill: 'origin',
          tension: 0.25
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 10,
            font: { size: 11, family: 'Pretendard' },
            color: palette.textMuted
          }
        },
        tooltip: {
          backgroundColor: palette.isDark ? '#0f172a' : '#ffffff',
          titleColor: palette.textPrimary,
          bodyColor: palette.textMuted,
          borderColor: palette.border,
          borderWidth: 1,
          padding: 8,
          bodyFont: { family: 'JetBrains Mono', size: 11 },
          titleFont: { family: 'JetBrains Mono', size: 12, weight: 'bold' },
          callbacks: {
            title: (items) => `${parseInt(items[0].label).toLocaleString()}원`,
            label: (item) => `밀도: ${item.formattedValue}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: palette.chartGrid },
          ticks: {
            color: palette.textMuted,
            font: { size: 10, family: 'JetBrains Mono' },
            callback: (val, idx) => {
              const num = labels[idx];
              return num ? `${Math.round(num / 10000)}만` : '';
            }
          }
        },
        y: {
          display: false,
          grid: { display: false }
        }
      }
    }
  });
}

function renderDistrictBarChart(treatment, selectedDistrict) {
  const ctx = document.getElementById('districtBarChart');
  if (!ctx) return;

  const palette = getThemePalette();
  const dStats = treatment.district_stats || {};
  const districts = ['수성구', '중구', '달서구', '북구', '동구', '달성군', '서구', '남구'];
  const overallMean = treatment.price_inc_vat.mean || 0;

  const labelEl = document.getElementById('selectedDistrictLabel');
  if (labelEl) {
    labelEl.textContent = selectedDistrict === '대구전체' ? '대구 전체 균일' : selectedDistrict;
  }

  const labels = [];
  const dataValues = [];
  const barColors = [];

  districts.forEach(d => {
    const mean = dStats[d] ? dStats[d].mean : 0;
    if (mean > 0) {
      labels.push(d);
      dataValues.push(mean);
      if (selectedDistrict !== '대구전체' && d === selectedDistrict) {
        barColors.push(palette.barSelected);
      } else {
        barColors.push(palette.barDefault);
      }
    }
  });

  if (districtBarChart) {
    districtBarChart.destroy();
  }

  districtBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: '평균 실결제액',
        data: dataValues,
        backgroundColor: barColors,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: palette.isDark ? '#0f172a' : '#ffffff',
          titleColor: palette.textPrimary,
          bodyColor: palette.textMuted,
          borderColor: palette.border,
          borderWidth: 1,
          padding: 8,
          bodyFont: { family: 'JetBrains Mono', size: 11 },
          titleFont: { family: 'JetBrains Mono', size: 12, weight: 'bold' },
          callbacks: {
            title: (items) => items[0].label,
            label: (item) => {
              const val = item.raw;
              const diff = val - overallMean;
              const diffStr = diff > 0 ? `+${diff.toLocaleString()}원` : `${diff.toLocaleString()}원`;
              return [
                `평균: ${val.toLocaleString()}원`,
                `대구 평균 대비: ${diffStr}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: palette.textMuted, font: { size: 10, family: 'Pretendard' } }
        },
        y: {
          grid: { color: palette.chartGrid },
          ticks: {
            color: palette.textMuted,
            font: { size: 10, family: 'JetBrains Mono' },
            callback: (val) => `${Math.round(val / 10000)}만`
          }
        }
      }
    }
  });
}

// ============================================================================
// 6. Outlier & Strict Right-Aligned Numerical Table
// ============================================================================
function renderOutlierView() {
  const select = document.getElementById('outlierTreatmentSelect');
  const tKey = select ? select.value : currentTreatmentKey;
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;

  const t = data.treatments[tKey];
  if (!t) return;

  const stats = t.price_inc_vat;
  document.getElementById('lowOutlierBound').textContent = `${stats.low_fence.toLocaleString()}원 미만`;
  document.getElementById('highOutlierBound').textContent = `${stats.high_fence.toLocaleString()}원 초과`;

  // 1. 하위 이상치 목록 (Terminal Dense Box)
  const lowContainer = document.getElementById('lowOutliersList');
  lowContainer.innerHTML = '';
  if (t.low_outliers.length === 0) {
    lowContainer.innerHTML = '<p class="text-xs text-slate-400 py-3 text-center font-mono">통계적 하한선 미만 표본 없음 (모든 표본이 정상 시세 구간 유지)</p>';
  } else {
    t.low_outliers.forEach(h => {
      const card = document.createElement('div');
      card.className = 'p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md flex justify-between items-center text-xs';
      card.innerHTML = `
        <div class="text-left">
          <div class="font-bold text-slate-900 dark:text-slate-100">${h.hospital_name}</div>
          <div class="text-xs text-slate-500 font-mono">${h.district} • ${h.subway_station || '-'}</div>
        </div>
        <div class="text-right">
          <div class="font-bold font-mono tabular-nums text-rose-700 dark:text-rose-400">${h.price_inc_vat_str}</div>
          <span class="text-xs font-mono text-slate-500">조건확인</span>
        </div>
      `;
      lowContainer.appendChild(card);
    });
  }

  // 2. 상위 이상치 목록
  const highContainer = document.getElementById('highOutliersList');
  highContainer.innerHTML = '';
  if (t.high_outliers.length === 0) {
    highContainer.innerHTML = '<p class="text-xs text-slate-400 py-3 text-center font-mono">통계적 상한선 초과 표본 없음</p>';
  } else {
    t.high_outliers.forEach(h => {
      const card = document.createElement('div');
      card.className = 'p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md flex justify-between items-center text-xs';
      card.innerHTML = `
        <div class="text-left">
          <div class="font-bold text-slate-900 dark:text-slate-100">${h.hospital_name}</div>
          <div class="text-xs text-slate-500 font-mono">${h.district} • ${h.clinic_type}</div>
        </div>
        <div class="text-right">
          <div class="font-bold font-mono tabular-nums text-slate-900 dark:text-slate-100">${h.price_inc_vat_str}</div>
          <span class="text-xs font-mono text-slate-500">프리미엄</span>
        </div>
      `;
      highContainer.appendChild(card);
    });
  }

  // 3. TOP 5 정상 최저가 테이블 (Strict Right-Aligned Numerics)
  const topBody = document.getElementById('topCheapestTableBody');
  topBody.innerHTML = '';
  (t.normal_cheapest_top5 || []).forEach((h, idx) => {
    const tr = document.createElement('tr');
    tr.className = 'h-11 px-3 border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50/80 dark:hover:bg-slate-900/50 transition-colors';
    tr.innerHTML = `
      <td class="py-2 px-3 font-mono tabular-nums text-slate-500 text-center">표본 ${String.fromCharCode(65 + idx)}-${(idx + 1).toString().padStart(2, '0')}</td>
      <td class="py-2 px-3 text-left font-semibold text-slate-900 dark:text-slate-100">${h.hospital_name}</td>
      <td class="py-2 px-3 text-center text-xs text-slate-500 dark:text-slate-400">${h.district} • ${h.subway_station || '-'}</td>
      <td class="py-2 px-3 text-center text-xs">${h.clinic_type}</td>
      <td class="py-2 px-3 text-left text-xs">${h.procedure_name}</td>
      <td class="py-2 px-3 text-right font-mono tabular-nums text-slate-500 dark:text-slate-400">${h.price_1session}</td>
      <td class="py-2 px-3 text-right font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100">${h.price_inc_vat_str}</td>
      <td class="py-2 px-3 text-left text-xs text-slate-400 font-mono">${h.note || '-'}</td>
    `;
    topBody.appendChild(tr);
  });

  filterHospitalTable();
  lucide.createIcons();
}

function toggleTagFilter(tag) {
  currentTagFilter = tag;
  const tagBtns = document.querySelectorAll('#tabOutliers .chip-btn');
  tagBtns.forEach(btn => {
    if (btn.id.startsWith('tagFilter_')) {
      const isActive = btn.id === `tagFilter_${tag}`;
      btn.className = `chip-btn px-2 py-0.5 text-xs font-mono rounded-md border transition-colors ${
        isActive
          ? 'bg-slate-900 text-white border-slate-900 dark:bg-slate-100 dark:text-slate-900 dark:border-slate-100 font-semibold active'
          : 'bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800'
      }`;
    }
  });
  filterHospitalTable();
}

function filterHospitalTable() {
  const select = document.getElementById('outlierTreatmentSelect');
  const tKey = select ? select.value : currentTreatmentKey;
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;

  const t = data.treatments[tKey];
  if (!t) return;

  const searchKeyword = (document.getElementById('hospitalSearchInput').value || '').trim().toLowerCase();
  const districtFilter = document.getElementById('tableDistrictFilter').value;
  const typeFilter = document.getElementById('tableTypeFilter').value;

  const tbody = document.getElementById('allHospitalsTableBody');
  tbody.innerHTML = '';

  const filtered = t.all_hospitals.filter(h => {
    if (searchKeyword) {
      const targetStr = `${h.hospital_name} ${h.road_address} ${h.subway_station}`.toLowerCase();
      if (!targetStr.includes(searchKeyword)) return false;
    }
    if (districtFilter !== 'all' && h.district !== districtFilter) return false;
    if (typeFilter !== 'all' && h.clinic_type !== typeFilter) return false;
    if (currentTagFilter !== 'all') {
      const tags = h.tags || [];
      if (!tags.includes(currentTagFilter)) return false;
    }
    return true;
  });

  document.getElementById('hospitalCountSpan').textContent = filtered.length;

  filtered.forEach(h => {
    const tr = document.createElement('tr');
    tr.className = 'h-11 px-3 border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50/80 dark:hover:bg-slate-900/50 transition-colors text-xs';

    const tagHtml = (h.tags || []).slice(0, 3).map(tag => {
      return `<span class="inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 tabular-nums">${tag}</span>`;
    }).join(' ');

    tr.innerHTML = `
      <td class="py-2 px-3 text-left">
        <div class="font-bold text-slate-900 dark:text-slate-100">${h.hospital_name}</div>
        <div class="text-xs text-slate-400 font-mono">${h.clinic_type}</div>
      </td>
      <td class="py-2 px-3 text-center">
        <div class="text-xs text-slate-700 dark:text-slate-300">${h.road_address || h.district}</div>
        <div class="text-xs text-slate-400 font-mono">${h.subway_station || '-'}</div>
      </td>
      <td class="py-2 px-3 text-left">
        <div class="flex flex-wrap gap-1">${tagHtml}</div>
      </td>
      <td class="py-2 px-3 text-left text-xs">${h.procedure_name}</td>
      <td class="py-2 px-3 text-right font-mono tabular-nums text-slate-500 dark:text-slate-400">${h.price_1session}</td>
      <td class="py-2 px-3 text-right font-mono font-bold tabular-nums text-slate-900 dark:text-slate-100">${h.price_inc_vat_str}</td>
      <td class="py-2 px-3 text-center font-mono">
        <span class="${h.vat_included ? 'text-emerald-700 dark:text-emerald-400 font-semibold' : 'text-slate-400'}">
          ${h.vat_policy || (h.vat_included ? 'VAT포함' : 'VAT별도')}
        </span>
      </td>
      <td class="py-2 px-3 text-center font-mono text-slate-400 text-xs"><span class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500">비식별 보호</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// ============================================================================
// 7. Initialization on DOM Load
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initCategoriesAndTreatments();
  calculatePricePosition();
  lucide.createIcons();
});
