async function analyze() {
  const resume = document.getElementById('resume').value.trim();
  const jd = document.getElementById('jd').value.trim();

  if (!resume || !jd) {
    alert('Please fill both Resume and Job Description!');
    return;
  }

  // Show loader, hide results
  document.getElementById('loader').style.display = 'block';
  document.getElementById('results').style.display = 'none';

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume, jd })
    });

    const data = await response.json();

    // Hide loader
    document.getElementById('loader').style.display = 'none';

    // Update score
    const score = data.score;
    document.getElementById('score-value').textContent = score + '%';
    document.getElementById('matched-count').textContent = data.matched.length;
    document.getElementById('missing-count').textContent = data.missing.length;

    // Progress bar
    document.getElementById('progress-fill').style.width = score + '%';
    document.getElementById('progress-label').textContent = score + '%';

    // Score color + status
    const scoreEl = document.getElementById('score-value');
    const statusEl = document.getElementById('score-status');
    const adviceEl = document.getElementById('advice-text');
    const adviceBox = document.getElementById('advice-box');
    const progressFill = document.getElementById('progress-fill');

    if (score >= 70) {
      scoreEl.style.color = '#1D9E75';
      statusEl.textContent = 'Strong Match!';
      adviceEl.textContent = 'Great! Your resume is well aligned. Apply confidently!';
      adviceBox.style.borderColor = '#1D9E75';
      adviceBox.style.color = '#1D9E75';
      adviceBox.style.background = '#0D2E1E';
      progressFill.style.background = '#1D9E75';
    } else if (score >= 40) {
      scoreEl.style.color = '#F4A426';
      statusEl.textContent = 'Moderate Match';
      adviceEl.textContent = 'Add the missing keywords below to improve your score!';
      adviceBox.style.borderColor = '#F4A426';
      adviceBox.style.color = '#F4A426';
      adviceBox.style.background = '#2E1F0D';
      progressFill.style.background = '#F4A426';
    } else {
      scoreEl.style.color = '#E24B4A';
      statusEl.textContent = 'Weak Match';
      adviceEl.textContent = 'Your resume needs significant keyword improvements.';
      adviceBox.style.borderColor = '#E24B4A';
      adviceBox.style.color = '#E24B4A';
      adviceBox.style.background = '#2E0D0D';
      progressFill.style.background = '#E24B4A';
    }

    // Matched badges
    const matchedBadges = document.getElementById('matched-badges');
    matchedBadges.innerHTML = '';
    data.matched.forEach(k => {
      const badge = document.createElement('span');
      badge.className = 'badge green';
      badge.textContent = k;
      matchedBadges.appendChild(badge);
    });

    // Missing badges
    const missingBadges = document.getElementById('missing-badges');
    missingBadges.innerHTML = '';
    data.missing.forEach(k => {
      const badge = document.createElement('span');
      badge.className = 'badge red';
      badge.textContent = k;
      missingBadges.appendChild(badge);
    });

    // Show results
    document.getElementById('results').style.display = 'block';

    // Smooth scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

  } catch (error) {
    document.getElementById('loader').style.display = 'none';
    alert('Something went wrong! Check if Flask is running.');
  }
}