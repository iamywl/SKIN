/**
 * 대구 메디프라이스 (Daegu MediPrice) Frontend Application Logic v2.0
 * Dual Theme (Light / Dark), Precision Segmentation, Anti-AI Aesthetic
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

function getThemeColors() {
  const isDark = document.documentElement.classList.contains('dark');
  return {
    isDark,
    text: isDark ? '#94a3b8' : '#64748b',
    grid: isDark ? 'rgba(38, 48, 67, 0.6)' : 'rgba(226, 232, 240, 0.8)',
    cardBg: isDark ? '#151b26' : '#ffffff',
    primary: isDark ? '#3b82f6' : '#2563eb',
    emerald: isDark ? '#10b981' : '#059669',
    rose: isDark ? '#ef4444' : '#dc2626',
    amber: isDark ? '#f59e0b' : '#d97706'
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
    if (btn) btn.classList.toggle('active', id === tabId);
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
    btn.className = `chip-btn ${cat.id === currentCategory ? 'active' : ''}`;
    btn.textContent = cat.name;
    btn.onclick = () => selectCategory(cat.id);
    container.appendChild(btn);
  });

  populateTreatmentDropdown();
  populateOutlierTreatmentDropdown();
}

function selectCategory(catId) {
  currentCategory = catId;
  document.querySelectorAll('#categoryChipsContainer .chip-btn').forEach(btn => {
    const data = window.DAEGU_SKIN_DATA;
    const catObj = data.categories.find(c => c.name === btn.textContent);
    btn.classList.toggle('active', catObj && catObj.id === catId);
  });
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
    opt.textContent = `${t.name} (대구 표본 ${t.sample_count}곳)`;
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
    opt.textContent = `${t.name} (표본 ${t.sample_count}개소)`;
    if (key === currentTreatmentKey) opt.selected = true;
    select.appendChild(opt);
  });
}

function onTreatmentSelectChange() {
  const select = document.getElementById('treatmentSelect');
  currentTreatmentKey = select.value;
  const outlierSelect = document.getElementById('outlierTreatmentSelect');
  if (outlierSelect) outlierSelect.value = currentTreatmentKey;

  // 기본 가격을 해당 시술의 중앙값으로 자동 세팅
  const data = window.DAEGU_SKIN_DATA;
  const t = data.treatments[currentTreatmentKey];
  if (t) {
    const median = t.price_inc_vat.median;
    document.getElementById('priceInput').value = median;
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

  // 표본수 뱃지
  const sampleBadge = document.getElementById('sampleCountBadge');
  if (sampleBadge) sampleBadge.textContent = `대구 표본 ${t.sample_count}곳`;

  // 입력 가격
  const rawInput = parseInt(document.getElementById('priceInput').value || '0', 10);
  const vatExclusive = document.getElementById('vatExclusiveCheckbox').checked;

  // 최종 실결제액 계산
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

  document.getElementById('priceFormatted').textContent = `${actualPrice.toLocaleString()}원 (VAT포함)`;

  // 행정구 선택
  const district = document.getElementById('districtSelect').value;

  // 통계 지표 추출
  const stats = t.price_inc_vat;
  const median = stats.median;
  const q1 = stats.q1;
  const q3 = stats.q3;
  const iqr = stats.iqr;
  const lowFence = stats.low_fence;
  const highFence = stats.high_fence;
  const prices = stats.prices_sorted;

  // 백분위수 산출 (저렴한 순)
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

  // 1. 게이지 및 백분위수 텍스트 갱신
  document.getElementById('percentileText').textContent = `상위 ${percentile.toFixed(1)}%`;
  document.getElementById('percentileBar').style.width = `${Math.min(100, Math.max(0, percentile))}%`;
  document.getElementById('percentileNeedle').style.left = `${Math.min(99, Math.max(1, percentile))}%`;

  // 2. 상태 판정 및 뱃지 업데이트
  const badgeIcon = document.getElementById('badgeIcon');
  const badgeText = document.getElementById('badgeText');
  const statusTag = document.getElementById('statusTag');
  const descEl = document.getElementById('diagDescription');

  let statusClass = 'normal';
  let icon = '⚖️';
  let title = '대구 표준 적정 시세';
  let descHtml = '';

  const diffFromMedian = actualPrice - median;
  const diffStr = Math.abs(diffFromMedian).toLocaleString();

  if (actualPrice < lowFence) {
    statusClass = 'lower';
    icon = '🚨';
    title = '통계적 하위 이상치 (미끼·저용량 의심)';
    statusTag.className = 'badge-status lower';
    statusTag.textContent = '미끼 의심';
    descHtml = `
      현재 견적은 대구 통계적 하한선(<strong>${lowFence.toLocaleString()}원</strong>)보다 낮습니다. 
      <br>첫 방문 체험 이벤트가이거나 약제 용량(cc) 희석, 리필팁 사용 등의 우려가 있으므로, 
      <strong>원내 정품 인증서 수령 및 개봉 확인</strong>을 반드시 진행하시기 바랍니다.
    `;
  } else if (actualPrice < q1) {
    statusClass = 'normal';
    icon = '💎';
    title = '대구 최저가 근접 실속 시세';
    statusTag.className = 'badge-status normal';
    statusTag.textContent = '가성비 우수';
    descHtml = `
      대구 하위 25%(Q1: <strong>${q1.toLocaleString()}원</strong>) 이하에 위치하여 매우 경제적인 가격대입니다. 
      동성로/반월당 대형 네트워크 의원의 박리다매 이벤트가 수준이며, 대구 중앙값보다 <strong>${diffStr}원 저렴</strong>합니다.
    `;
  } else if (actualPrice <= q3) {
    statusClass = 'normal';
    icon = '⚖️';
    title = '대구 표준 적정 시세 (IQR 구간)';
    statusTag.className = 'badge-status normal';
    statusTag.textContent = '적정 시세';
    const compText = diffFromMedian <= 0 
      ? `대구 중앙값보다 <strong>${diffStr}원 저렴</strong>하여 매우 합리적입니다.`
      : `대구 중앙값보다 <strong>${diffStr}원 높으나</strong> 정상 시세 범위 내입니다.`;
    descHtml = `
      대구 전체 병의원의 50%가 밀집된 가장 일반적인 정상 가격 구간(<strong>${q1.toLocaleString()}원 ~ ${q3.toLocaleString()}원</strong>)입니다. 
      ${compText} 담당 의료진의 시술 숙련도와 사후 케어를 비교해 결정하세요.
    `;
  } else if (actualPrice <= highFence) {
    statusClass = 'upper';
    icon = '👑';
    title = '상위 프리미엄 시세 (전문의 케어)';
    statusTag.className = 'badge-status upper';
    statusTag.textContent = '프리미엄';
    descHtml = `
      대구 상위 25%(Q3: <strong>${q3.toLocaleString()}원</strong>) 초과 구간입니다. 
      수성구 범어동 피부과 전문의 1:1 맞춤 진료나 프라이빗 룸, 프리미엄 진정 재생 케어가 포함된 경우가 많으며 대구 중앙값 대비 <strong>${diffStr}원 높습니다</strong>.
    `;
  } else {
    statusClass = 'upper';
    icon = '👑';
    title = '통계적 상위 이상치 (최고가 구간)';
    statusTag.className = 'badge-status upper';
    statusTag.textContent = '초고가 이상치';
    descHtml = `
      대구 통계적 상한선(<strong>${highFence.toLocaleString()}원</strong>)을 초과한 초고가 구간입니다. 
      단독 1회 시술 금액이 맞는지, 또는 복합 패키지·VIP 전담 프로그램이 포함된 견적인지 세부 견적서를 반드시 확인하세요.
    `;
  }

  badgeIcon.textContent = icon;
  badgeText.textContent = title;
  descEl.innerHTML = descHtml;

  // 3. 4대 메트릭 값 업데이트
  document.getElementById('metricMyPrice').textContent = `${actualPrice.toLocaleString()}원`;
  document.getElementById('metricMedian').textContent = `${median.toLocaleString()}원`;
  document.getElementById('metricIQR').textContent = `${q1.toLocaleString()} ~ ${q3.toLocaleString()}원`;

  const diffLabel = document.getElementById('metricDiffLabel');
  const metricDiff = document.getElementById('metricDiff');
  if (diffFromMedian < 0) {
    diffLabel.textContent = '중앙값 대비 절감';
    metricDiff.textContent = `-${diffStr}원`;
    metricDiff.className = 'text-sm font-bold font-mono text-emerald-600 dark:text-emerald-400';
  } else if (diffFromMedian > 0) {
    diffLabel.textContent = '중앙값 대비 초과';
    metricDiff.textContent = `+${diffStr}원`;
    metricDiff.className = 'text-sm font-bold font-mono text-amber-600 dark:text-amber-400';
  } else {
    diffLabel.textContent = '중앙값과 동일';
    metricDiff.textContent = '0원';
    metricDiff.className = 'text-sm font-bold font-mono text-blue-600 dark:text-blue-400';
  }

  // 4. 의학 안전 수칙 렌더링
  const precautionsList = document.getElementById('medicalCheckpoints');
  precautionsList.innerHTML = '';
  const precs = t.medical_precautions || [];
  precs.slice(0, 4).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    precautionsList.appendChild(li);
  });

  // 5. 차트 렌더링
  renderDensityChart(t, actualPrice);
  renderDistrictBarChart(t, district);

  lucide.createIcons();
}

// ============================================================================
// 5. Charts Visualization (KDE Bell Curve & District Bars)
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

  const colors = getThemeColors();
  const stats = treatment.price_inc_vat;
  const mean = stats.mean;
  const std = stats.std || (stats.iqr / 1.35) || 50000;
  const q1 = stats.q1;
  const q3 = stats.q3;

  // 가우시안 곡선 데이터 포인트 생성 (50개)
  const minX = Math.max(0, mean - 3 * std);
  const maxX = mean + 3 * std;
  const step = (maxX - minX) / 50;

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
          label: '가격 밀도 곡선',
          data: bellData,
          borderColor: colors.primary,
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
          tension: 0.3
        },
        {
          label: '정상 시세(IQR) 구간',
          data: iqrArea,
          backgroundColor: colors.isDark ? 'rgba(16, 185, 129, 0.18)' : 'rgba(5, 150, 105, 0.12)',
          borderColor: 'transparent',
          pointRadius: 0,
          fill: 'origin',
          tension: 0.3
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
            boxWidth: 12,
            font: { size: 11, family: 'Pretendard' },
            color: colors.text
          }
        },
        tooltip: {
          callbacks: {
            title: (items) => `${parseInt(items[0].label).toLocaleString()}원`,
            label: (item) => `상대 밀도: ${item.formattedValue}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: colors.grid },
          ticks: {
            color: colors.text,
            font: { size: 10, family: 'Pretendard' },
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

  const colors = getThemeColors();
  const dStats = treatment.district_stats || {};
  const districts = ['수성구', '중구', '달서구', '북구', '동구', '달성군', '서구', '남구'];
  const overallMean = treatment.price_inc_vat.mean || 0;

  // 상단 범례 라벨 갱신
  const labelEl = document.getElementById('selectedDistrictLabel');
  if (labelEl) {
    labelEl.textContent = selectedDistrict === '대구전체' ? '대구 전체 (전 구 균일)' : selectedDistrict;
  }

  const labels = [];
  const dataValues = [];
  const barColors = [];

  districts.forEach(d => {
    const mean = dStats[d] ? dStats[d].mean : 0;
    if (mean > 0) {
      labels.push(d);
      dataValues.push(mean);

      // 색상 기준: 내가 선택한 구는 강조 레드, 나머지 일반 구는 균일한 신뢰의 블루
      if (selectedDistrict !== '대구전체' && d === selectedDistrict) {
        barColors.push(colors.rose); // 내가 선택한 권역 강조
      } else {
        barColors.push(colors.isDark ? '#3b82f6' : '#2563eb'); // 일반 구 균일 블루
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
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => {
              const d = items[0].label;
              return d === selectedDistrict ? `${d} [선택된 비교 구]` : `${d} 평균`;
            },
            label: (item) => {
              const val = item.raw;
              const diff = val - overallMean;
              const diffStr = diff > 0 ? `+${diff.toLocaleString()}원` : `${diff.toLocaleString()}원`;
              return [
                `평균 실결제액: ${val.toLocaleString()}원`,
                `대구 전체 평균 대비: ${diffStr}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: colors.text, font: { size: 10, family: 'Pretendard' } }
        },
        y: {
          grid: { color: colors.grid },
          ticks: {
            color: colors.text,
            font: { size: 10, family: 'Pretendard' },
            callback: (val) => `${Math.round(val / 10000)}만`
          }
        }
      }
    }
  });
}

// ============================================================================
// 6. Outlier & Hospital Directory Table
// ============================================================================
function renderOutlierView() {
  const select = document.getElementById('outlierTreatmentSelect');
  const tKey = select ? select.value : currentTreatmentKey;
  const data = window.DAEGU_SKIN_DATA;
  if (!data || !data.treatments) return;

  const t = data.treatments[tKey];
  if (!t) return;

  const stats = t.price_inc_vat;
  document.getElementById('lowOutlierBound').textContent = `경계선: ${stats.low_fence.toLocaleString()}원 미만`;
  document.getElementById('highOutlierBound').textContent = `경계선: ${stats.high_fence.toLocaleString()}원 초과`;

  // 1. 하위 이상치 목록
  const lowContainer = document.getElementById('lowOutliersList');
  lowContainer.innerHTML = '';
  if (t.low_outliers.length === 0) {
    lowContainer.innerHTML = '<p class="text-[11px] text-[var(--text-muted)] py-4 text-center">하위 이상치 병원이 없습니다 (전 병원 정상 시세 유지).</p>';
  } else {
    t.low_outliers.forEach(h => {
      const card = document.createElement('div');
      card.className = 'app-card-sub p-2.5 flex justify-between items-center text-xs';
      card.innerHTML = `
        <div>
          <div class="font-bold text-[var(--text-primary)] flex items-center gap-1.5">
            ${h.hospital_name}
            <span class="tag-pill">${h.district}</span>
          </div>
          <div class="text-[10px] text-[var(--text-muted)] mt-0.5">${h.road_address || h.location}</div>
        </div>
        <div class="text-right">
          <div class="font-bold font-mono text-rose-600 dark:text-rose-400">${h.price_inc_vat_str}</div>
          <span class="text-[10px] text-rose-500 font-semibold">미끼의심</span>
        </div>
      `;
      lowContainer.appendChild(card);
    });
  }

  // 2. 상위 이상치 목록
  const highContainer = document.getElementById('highOutliersList');
  highContainer.innerHTML = '';
  if (t.high_outliers.length === 0) {
    highContainer.innerHTML = '<p class="text-[11px] text-[var(--text-muted)] py-4 text-center">상위 이상치 병원이 없습니다.</p>';
  } else {
    t.high_outliers.forEach(h => {
      const card = document.createElement('div');
      card.className = 'app-card-sub p-2.5 flex justify-between items-center text-xs';
      card.innerHTML = `
        <div>
          <div class="font-bold text-[var(--text-primary)] flex items-center gap-1.5">
            ${h.hospital_name}
            <span class="tag-pill tag-spec">${h.clinic_type}</span>
          </div>
          <div class="text-[10px] text-[var(--text-muted)] mt-0.5">${h.road_address || h.location}</div>
        </div>
        <div class="text-right">
          <div class="font-bold font-mono text-amber-600 dark:text-amber-400">${h.price_inc_vat_str}</div>
          <span class="text-[10px] text-amber-500 font-semibold">하이엔드</span>
        </div>
      `;
      highContainer.appendChild(card);
    });
  }

  // 3. TOP 5 정상 최저가 테이블
  const topBody = document.getElementById('topCheapestTableBody');
  topBody.innerHTML = '';
  (t.normal_cheapest_top5 || []).forEach((h, idx) => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-[var(--bg-card-sub)] transition';
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-bold font-mono text-emerald-600 dark:text-emerald-400">#${idx + 1}</td>
      <td class="py-2.5 px-3 font-semibold text-[var(--text-primary)]">${h.hospital_name}</td>
      <td class="py-2.5 px-3 text-[11px]">${h.district} • ${h.subway_station || '-'}</td>
      <td class="py-2.5 px-3"><span class="tag-pill ${h.is_specialist ? 'tag-spec' : ''}">${h.clinic_type}</span></td>
      <td class="py-2.5 px-3 text-[11px]">${h.procedure_name}</td>
      <td class="py-2.5 px-3 text-right font-mono">${h.price_1session}</td>
      <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600 dark:text-blue-400">${h.price_inc_vat_str}</td>
      <td class="py-2.5 px-3 text-[10px] text-[var(--text-muted)]">${h.note || '-'}</td>
    `;
    topBody.appendChild(tr);
  });

  filterHospitalTable();
  lucide.createIcons();
}

function toggleTagFilter(tag) {
  currentTagFilter = tag;
  const tagBtns = document.querySelectorAll('.tag-pill');
  tagBtns.forEach(btn => {
    if (btn.id.startsWith('tagFilter_')) {
      btn.classList.toggle('active', btn.id === `tagFilter_${tag}`);
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
    // 1. 키워드 검색 (병원명, 도로명 주소, 지하철역)
    if (searchKeyword) {
      const targetStr = `${h.hospital_name} ${h.road_address} ${h.subway_station}`.toLowerCase();
      if (!targetStr.includes(searchKeyword)) return false;
    }
    // 2. 권역 필터
    if (districtFilter !== 'all' && h.district !== districtFilter) return false;
    // 3. 종별 필터
    if (typeFilter !== 'all' && h.clinic_type !== typeFilter) return false;
    // 4. 태그 필터
    if (currentTagFilter !== 'all') {
      const tags = h.tags || [];
      if (!tags.includes(currentTagFilter)) return false;
    }
    return true;
  });

  document.getElementById('hospitalCountSpan').textContent = filtered.length;

  filtered.forEach(h => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-[var(--bg-card-sub)] transition';

    // 태그 칩 생성
    const tagHtml = (h.tags || []).slice(0, 3).map(tag => {
      let cls = 'tag-pill';
      if (tag === '피부과전문의') cls += ' tag-spec';
      if (tag.includes('젠틀맥스') || tag.includes('클라리티')) cls += ' tag-laser';
      return `<span class="${cls}">${tag}</span>`;
    }).join(' ');

    tr.innerHTML = `
      <td class="py-2.5 px-3">
        <div class="font-bold text-[var(--text-primary)]">${h.hospital_name}</div>
        <div class="text-[10px] text-[var(--text-muted)] mt-0.5">${h.clinic_type}</div>
      </td>
      <td class="py-2.5 px-3">
        <div class="text-[11px] text-[var(--text-primary)]">${h.road_address || h.district}</div>
        <div class="text-[10px] text-blue-600 dark:text-blue-400 mt-0.5">${h.subway_station || '-'}</div>
      </td>
      <td class="py-2.5 px-3">
        <div class="flex flex-wrap gap-1">${tagHtml}</div>
      </td>
      <td class="py-2.5 px-3 text-[11px]">${h.procedure_name}</td>
      <td class="py-2.5 px-3 text-right font-mono">${h.price_1session}</td>
      <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600 dark:text-blue-400">${h.price_inc_vat_str}</td>
      <td class="py-2.5 px-3">
        <span class="text-[10px] ${h.vat_included ? 'text-emerald-600 font-semibold' : 'text-slate-400'}">
          ${h.vat_policy || (h.vat_included ? 'VAT 포함' : 'VAT 별도')}
        </span>
      </td>
      <td class="py-2.5 px-3 text-[11px] font-mono text-[var(--text-muted)]">${h.tel || '-'}</td>
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
