let pdfFile = null;

// =========================
// ANIMATED COUNTER
// =========================
function animateValue(elementId, start, end, duration) {
  const element = document.getElementById(elementId);
  if (!element) return;

  let startTimestamp = null;

  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;

    const progress = Math.min((timestamp - startTimestamp) / duration, 1);

    element.textContent =
      Math.floor(progress * (end - start) + start) + "%";

    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };

  window.requestAnimationFrame(step);
}

// =========================
// HANDLE PDF UPLOAD
// =========================
function handlePDF(input) {
  if (input.files && input.files[0]) {
    pdfFile = input.files[0];

    document.getElementById("pdf-name").textContent = pdfFile.name;
    document.getElementById("upload-box").classList.add("active");
    document.getElementById("upload-box").querySelector("p").textContent =
      "✅ PDF loaded!";

    // Clear textarea when PDF selected
    document.getElementById("resume").value = "";
    document.getElementById("resume").placeholder =
      "PDF loaded! Or paste text to override...";
  }
}

// =========================
// MAIN ANALYZE FUNCTION
// =========================
async function analyze() {
  const analyzeBtn = document.querySelector(".analyze-btn");
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  const resume = document.getElementById("resume").value.trim();
  const jd = document.getElementById("jd").value.trim();
  const targetRole = document.getElementById("target-role").value.trim();

  // =========================
  // VALIDATION
  // =========================
  if (!jd) {
    alert("Please fill the Job Description!");
    return;
  }

  if (!resume && !pdfFile) {
    alert("Please upload a PDF or paste your resume text!");
    return;
  }

  /// =========================
  // SHOW LOADER
  // =========================
  document.getElementById("loader").style.display = "flex";

  const loadingFill = document.getElementById("loading-progress-fill");
  const loadingPercent = document.getElementById("loading-percent");
  const loadingText = document.getElementById("loading-text");

  let progress = 0;

  const progressInterval = setInterval(() => {
    if (progress < 95) {
      progress += Math.floor(Math.random() * 8) + 1;

      if (progress > 95) progress = 95;

      loadingFill.style.width = `${progress}%`;
      loadingPercent.textContent = `${progress}%`;

      if (progress < 25) {
        loadingText.textContent = "Parsing Resume...";
      } else if (progress < 50) {
        loadingText.textContent = "Matching Keywords...";
      } else if (progress < 75) {
        loadingText.textContent = "Scoring ATS...";
      } else {
        loadingText.textContent = "Finalizing Report...";
      }
    }
  }, 120);

  document.getElementById("results").style.display = "none";

  try {
    const formData = new FormData();

    // Resume text overrides PDF
    if (resume) {
      formData.append("resume", resume);
    } else if (pdfFile) {
      formData.append("resume_pdf", pdfFile);
    }

    formData.append("jd", jd);
    formData.append("target_role", targetRole);

    // =========================
    // API CALL
    // =========================
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const responseData = await response.json();
    const data = responseData.data || responseData;

    clearInterval(progressInterval);

    loadingFill.style.width = "100%";
    loadingPercent.textContent = "100%";
    loadingText.textContent = "Analysis Complete!";

    setTimeout(() => {
      loadingText.textContent = "Analyzing your resume...";
      loadingFill.style.width = "0%";
      loadingPercent.textContent = "0%";
    }, 400);

    setTimeout(() => {
      document.getElementById("loader").style.display = "none";
    }, 500);

    if (data.error) {
      alert(data.error);
      return;
    }
    // =========================
    // EXTRACT DATA
    // =========================
    const score = data.score || 0;
    const matched = data.matched || [];
    const missing = data.missing || [];
    const techScore = data.tech_score || 0;
    const formatScore = data.format_score || 0;
    const trustScore = data.trust_score || 0;
    const readinessScore = Math.round(
    (score * 0.4) +
    (trustScore * 0.35) +
    (formatScore * 0.25)
    );
    const suggestions = data.suggestions || [];

    const matchedBadges = document.getElementById("matched-badges") || null;
    const missingBadges = document.getElementById("missing-badges") || null;
    const suggestionsList = document.getElementById("suggestions-list") || null;
    const whyScoreList = document.getElementById("why-score-list") || null;
    const priorityList = document.getElementById("priority-list") || null;
    // =========================
    // SCORE CARDS (Animated)
    // =========================
    animateValue("score-value", 0, score, 1200);
    animateValue("tech-score", 0, techScore, 1200);
    animateValue("format-score", 0, formatScore, 1200);
    animateValue("trust-score", 0, trustScore, 1200);

    document.getElementById("matched-count").textContent = matched.length;
    document.getElementById("missing-count").textContent = missing.length;

    // =========================
    // PROGRESS BAR
    // =========================
    const progressFill = document.getElementById("progress-fill");

    progressFill.style.width = "0%";

    setTimeout(() => {
      progressFill.style.width = score + "%";
    }, 100);

    document.getElementById("progress-label").textContent = score + "%";

    // =========================
    // UI ELEMENTS
    // =========================
    const scoreEl = document.getElementById("score-value");
    const statusEl = document.getElementById("score-status");
    const confidenceEl = document.getElementById("confidence-level");
    const benchmarkEl = document.getElementById("benchmark-level");
    const verdictEl = document.getElementById("verdict-badge");
    const readinessEl = document.getElementById("readiness-level");
    const adviceEl = document.getElementById("advice-text");
    const adviceBox = document.getElementById("advice-box");

    // =========================
    // PROFESSIONAL SCORE STATUS
    // =========================
        // =========================
    // PROFESSIONAL SCORE STATUS
    // =========================
    if (score >= 75) {

      readinessEl.textContent =
        `Resume Readiness: ${readinessScore}% (Ready to Apply)`;

      readinessEl.style.color = "#1D9E75";
      scoreEl.style.color = "#1D9E75";
      statusEl.textContent = "High Job Alignment";

      confidenceEl.textContent = "Confidence: High";
      confidenceEl.style.color = "#1D9E75";

      benchmarkEl.textContent = "Benchmark: Above top candidate average";
      benchmarkEl.style.color = "#1D9E75";
    
      verdictEl.textContent = "Verdict: Apply Now";
      verdictEl.style.color = "#1D9E75";
      
      adviceEl.textContent =
        "Excellent match. Your resume strongly aligns with this role.";

      adviceBox.style.borderColor = "#1D9E75";
      adviceBox.style.color = "#1D9E75";
      adviceBox.style.background = "#0D2E1E";

      progressFill.style.background = "#1D9E75";

    } else if (score >= 50) {


      readinessEl.textContent =
        `Resume Readiness: ${readinessScore}% (Almost Ready)`;

      readinessEl.style.color = "#F4A426";
      scoreEl.style.color = "#F4A426";
      statusEl.textContent = "Needs Optimization";

      confidenceEl.textContent = "Confidence: Medium";
      confidenceEl.style.color = "#F4A426";

      benchmarkEl.textContent = "Benchmark: Near competitive range";
      benchmarkEl.style.color = "#F4A426";

            // VERDICT
      verdictEl.textContent = "Verdict: Improve Before Applying";
      verdictEl.style.color = "#F4A426";

      adviceEl.textContent =
        "Good foundation. Improve missing technical keywords for better ATS trust.";

      adviceBox.style.borderColor = "#F4A426";
      adviceBox.style.color = "#F4A426";
      adviceBox.style.background = "#2E1F0D";

      progressFill.style.background = "#F4A426";

    } else {


      readinessEl.textContent =
        `Resume Readiness: ${readinessScore}% (Needs Work)`;

      readinessEl.style.color = "#E24B4A";
      scoreEl.style.color = "#E24B4A";
      statusEl.textContent = "Low ATS Alignment";

      confidenceEl.textContent = "Confidence: Low";
      confidenceEl.style.color = "#E24B4A";

      benchmarkEl.textContent = "Benchmark: Below recruiter shortlist range";
      benchmarkEl.style.color = "#E24B4A";

            // VERDICT
      verdictEl.textContent = "Verdict: Major Resume Upgrade Needed";
      verdictEl.style.color = "#E24B4A";

      adviceEl.textContent =
        "Your resume needs stronger alignment with this job description.";

      adviceBox.style.borderColor = "#E24B4A";
      adviceBox.style.color = "#E24B4A";
      adviceBox.style.background = "#2E0D0D";

      progressFill.style.background = "#E24B4A";
    }
    // =========================
    // MATCHED BADGES
    // =========================
    if (matchedBadges) matchedBadges.innerHTML = "";

        matched.forEach((keyword) => {
        const badge = document.createElement("span");
        badge.className = "badge green";
        badge.textContent = keyword;

        if (matchedBadges) {
            matchedBadges.appendChild(badge);
        }
        });
    // =========================
    // MISSING BADGES
    // =========================
    if (missingBadges) missingBadges.innerHTML = "";

        missing.forEach((keyword) => {
        const badge = document.createElement("span");
        badge.className = "badge red";
        badge.textContent = keyword;

        if (missingBadges) {
            missingBadges.appendChild(badge);
        }
        });
    // =========================
    // SUGGESTIONS
    // =========================
    if (suggestionsList) suggestionsList.innerHTML = "";

        suggestions.forEach((item) => {
        const tip = document.createElement("p");
        tip.className = "suggestion-item";
        tip.textContent = "• " + item;

        if (suggestionsList) {
            suggestionsList.appendChild(tip);
        }
        });

    // =========================
    // WHY YOUR SCORE
    // =========================
    if (whyScoreList) whyScoreList.innerHTML = "";

    const scoreReasons = [];

    // Strong matches
    if (matched.length >= 8) {
      scoreReasons.push("• Strong keyword alignment with job description.");
    } else if (matched.length >= 4) {
      scoreReasons.push("• Moderate keyword match with room for stronger targeting.");
    } else {
      scoreReasons.push("• Limited keyword overlap with this job description.");
    }

    // Missing skills
    if (missing.length > 0) {
      scoreReasons.push(
        `• Missing critical keywords like ${missing.slice(0, 3).join(", ")}.`
      );
    }

    // Formatting
    if (formatScore >= 85) {
      scoreReasons.push("• Resume formatting appears ATS-friendly.");
    } else {
      scoreReasons.push("• Resume formatting may reduce ATS performance.");
    }

    // Technical strength
    if (techScore >= 75) {
      scoreReasons.push("• Technical stack is highly relevant for this role.");
    } else if (techScore >= 50) {
      scoreReasons.push("• Technical foundation is decent but can improve.");
    } else {
      scoreReasons.push("• Technical alignment is currently below recruiter expectations.");
    }

    // Render
    if (whyScoreList) {
    scoreReasons.forEach((reason) => {
        const item = document.createElement("p");
        item.className = "suggestion-item";
        item.textContent = reason;
        whyScoreList.appendChild(item);
    });
    }

    // =========================
    // PRIORITY FIXES
    // =========================
    if (priorityList) priorityList.innerHTML = "";

    const priorityFixes = [];

    // Missing technical keywords first
    missing.slice(0, 3).forEach((keyword) => {
      priorityFixes.push(`Add ${keyword} to skills, projects, or summary.`);
    });

    // Formatting issue
    if (formatScore < 75) {
      priorityFixes.push(
        "Improve ATS formatting with clearer Skills, Projects, and Education sections."
      );
    }

    // Technical issue
    if (techScore < 60) {
      priorityFixes.push(
        "Strengthen technical stack relevance for this role."
      );
    }

    // If already strong
    if (priorityFixes.length === 0) {
      priorityFixes.push(
        "Your resume is already competitive. Focus on role-specific optimization."
      );
    }

    // Render
    if (priorityList) {
    priorityFixes.forEach((fix, index) => {
        const item = document.createElement("p");
        item.className = "suggestion-item";
        item.textContent = `${index + 1}. ${fix}`;
        priorityList.appendChild(item);
    });
    }



    // =========================
    // TECHNICAL + FORMATTING ANALYSIS
    // =========================
    const techAnalysisText = document.getElementById("tech-analysis-text");
    const formatAnalysisText = document.getElementById("format-analysis-text");
    const trustAnalysisText = document.getElementById("trust-analysis-text");

    // Technical Analysis
    if (techScore >= 80) {
      techAnalysisText.textContent =
        "Your technical skills strongly align with this role.";

    } else if (techScore >= 55) {
      techAnalysisText.textContent =
        "Your technical base is solid, but adding missing stack keywords can improve ATS trust.";

    } else {
      techAnalysisText.textContent =
        "Your technical alignment is currently weak for this role.";
    }

    // Formatting Analysis
    if (formatScore >= 85) {
      formatAnalysisText.textContent =
        "Your resume formatting appears ATS-friendly and professional.";

    } else if (formatScore >= 65) {
      formatAnalysisText.textContent =
        "Your formatting is decent, but stronger sections may improve ATS performance.";

    } else {
      formatAnalysisText.textContent =
        "Your resume may need better structure, sections, or ATS-safe formatting.";
    }


        // =========================
    // TRUST ANALYSIS TEXT
    // =========================
    if (trustScore >= 90) {
      trustAnalysisText.textContent =
        "Your resume demonstrates strong professionalism and recruiter trust signals.";

    } else if (trustScore >= 75) {
      trustAnalysisText.textContent =
        "Your resume appears credible, but adding stronger trust indicators can improve confidence.";

    } else {
      trustAnalysisText.textContent =
        "Your resume may need stronger professional signals like LinkedIn, GitHub, or ATS-safe structure.";
    }

    // =========================
    // SHOW RESULTS
    // =========================
    document.getElementById("results").style.display = "block";
    loadHistory();

    document.getElementById("results").scrollIntoView({
      behavior: "smooth",
    });

  } catch (error) {
    // Reset loader safely
    document.getElementById("loader").style.display = "none";

    const loadingFill = document.getElementById("loading-progress-fill");
    const loadingPercent = document.getElementById("loading-percent");
    const loadingText = document.getElementById("loading-text");

    if (loadingFill) loadingFill.style.width = "0%";
    if (loadingPercent) loadingPercent.textContent = "0%";
    if (loadingText) loadingText.textContent = "Analyzing your resume...";

    // Debug
    console.error("Analyze Error:", error);

    // User alert
    alert("Error: " + error.message);
  }
}

// =========================
// LOAD SCAN HISTORY
// =========================
async function loadHistory() {
  try {
    const historyRes = await fetch("/api/history");
    const statsRes = await fetch("/api/stats");

    const historyData = await historyRes.json();
    const statsData = await statsRes.json();

    const historyList = document.getElementById("history-list");
    const totalScans = document.getElementById("total-scans");
    const avgScore = document.getElementById("avg-score");
    const bestScore = document.getElementById("best-score");
    

    if (!historyList || !totalScans || !avgScore || !bestScore) return;

    // Stats
    if (statsData.success) {
      totalScans.textContent = `Total Scans: ${statsData.data.total_scans}`;
      avgScore.textContent = `Average Score: ${statsData.data.average_score}%`;
      bestScore.textContent = `Best Score: ${statsData.data.highest_score}%`;
    }

    // History
    historyList.innerHTML = "";

    if (!historyData.data || historyData.data.length === 0) {
      historyList.innerHTML = "<p>No scan history yet.</p>";
      return;
    }

    historyData.data.forEach((scan) => {
      const item = document.createElement("div");
      item.className = "history-item";

      item.innerHTML = `
        <span class="history-score">${scan.target_role || "not mention Role "} - ATS: ${scan.score}%</span>
        <span>Matched: ${scan.matched_count}</span>
        <span>Missing: ${scan.missing_count}</span>
        <span class="history-date">${scan.timestamp}</span>
      `;

      historyList.appendChild(item);
    });

  } catch (error) {
    console.error("History Load Error:", error);
  }
}


// =========================
// CLEAR HISTORY
// =========================
async function clearHistory() {
  const confirmClear = confirm("Are you sure you want to delete all scan history?");

  if (!confirmClear) return;

  try {
    const response = await fetch("/api/clear-history", {
      method: "DELETE"
    });

    const data = await response.json();

    if (data.success) {
      loadHistory();
      alert("Scan history cleared successfully!");
    } else {
      alert("Failed to clear history.");
    }

  } catch (error) {
    console.error("Clear History Error:", error);
    alert("Something went wrong.");
  }
}


// =========================
// INITIAL LOAD
// =========================
document.addEventListener("DOMContentLoaded", () => {
  loadHistory();
});