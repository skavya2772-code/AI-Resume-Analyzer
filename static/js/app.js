/* ============================================================
   SkillAlign AI - Core Frontend Logic
   ============================================================ */

let currentParsedData = null;
let currentAnalysisData = null;
let currentRoleResume = null;

// Toast Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'warning') icon = 'fa-exclamation-triangle';
    if (type === 'danger') icon = 'fa-times-circle';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// 1-Click Demo Resume Loader
async function loadSampleResume() {
    showToast('Loading pre-packaged student resume (Alex Kumar)...', 'info');
    try {
        const resp = await fetch('/api/load-sample', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            localStorage.setItem('current_resume_id', data.resume_id);
            localStorage.setItem('current_parsed_data', JSON.stringify(data.parsed_data));
            showToast('Sample student resume loaded successfully!', 'success');
            setTimeout(() => {
                window.location.href = `/analyze?resume_id=${data.resume_id}&role=Frontend Developer`;
            }, 800);
        } else {
            showToast(data.error || 'Failed to load sample resume', 'danger');
        }
    } catch (err) {
        showToast('Network error loading sample resume: ' + err.message, 'danger');
    }
}

// Tab Switching on Upload Page
function switchUploadTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    event.currentTarget.classList.add('active');
    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
}

// Display Selected Filename in Dropzone
function displaySelectedFilename(input) {
    const display = document.getElementById('selected-file-name');
    if (input.files && input.files[0]) {
        display.innerHTML = `<i class="fa-solid fa-file"></i> Selected: <strong>${input.files[0].name}</strong> (${(input.files[0].size / 1024).toFixed(1)} KB)`;
    }
}

// Setup Drag & Drop Listeners
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-file');

    if (dropZone && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                displaySelectedFilename(fileInput);
            }
        });
    }
});

// Handle File Upload Form Submission
async function handleFileUpload(event) {
    event.preventDefault();
    const fileInput = document.getElementById('resume-file');
    if (!fileInput.files || !fileInput.files[0]) {
        showToast('Please select a PDF or DOCX resume file first.', 'warning');
        return;
    }

    const btn = document.getElementById('upload-submit-btn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Extracting Resume Details...`;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const resp = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Upload & Extract Details`;

        if (data.success) {
            currentParsedData = data.parsed_data;
            localStorage.setItem('current_resume_id', data.resume_id);
            localStorage.setItem('current_parsed_data', JSON.stringify(data.parsed_data));
            showToast('Resume parsed successfully!', 'success');
            renderExtractionPreview(data.parsed_data);
        } else {
            showToast(data.error || 'Upload failed', 'danger');
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Upload & Extract Details`;
        showToast('Network error during upload: ' + err.message, 'danger');
    }
}

// Handle Raw Text Form Submission
async function handleTextUpload(event) {
    event.preventDefault();
    const rawText = document.getElementById('resume-text').value.trim();
    if (!rawText) {
        showToast('Please paste some resume text first.', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('raw_text', rawText);

    try {
        const resp = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        if (data.success) {
            currentParsedData = data.parsed_data;
            localStorage.setItem('current_resume_id', data.resume_id);
            localStorage.setItem('current_parsed_data', JSON.stringify(data.parsed_data));
            showToast('Resume text parsed successfully!', 'success');
            renderExtractionPreview(data.parsed_data);
        } else {
            showToast(data.error || 'Parsing failed', 'danger');
        }
    } catch (err) {
        showToast('Error parsing text: ' + err.message, 'danger');
    }
}

// Render Extraction Preview Card
function renderExtractionPreview(parsed) {
    document.getElementById('extraction-placeholder').style.display = 'none';
    const resBox = document.getElementById('extraction-results');
    resBox.style.display = 'block';

    const statusBadge = document.getElementById('extraction-status-badge');
    statusBadge.className = 'badge badge-success';
    statusBadge.textContent = 'Extracted Cleanly';

    document.getElementById('ext-name').textContent = parsed.name || 'Candidate';
    document.getElementById('ext-contact').textContent = [parsed.email, parsed.phone].filter(Boolean).join('  |  ') || 'No contact specified';

    // Links
    const linksBox = document.getElementById('ext-links');
    linksBox.innerHTML = '';
    if (parsed.github) linksBox.innerHTML += `<span class="badge badge-subtle"><i class="fa-brands fa-github"></i> ${parsed.github}</span>`;
    if (parsed.linkedin) linksBox.innerHTML += `<span class="badge badge-subtle"><i class="fa-brands fa-linkedin"></i> ${parsed.linkedin}</span>`;

    // Skills
    const skillsBox = document.getElementById('ext-skills-container');
    skillsBox.innerHTML = '';
    const skills = parsed.skills || [];
    document.getElementById('ext-skills-count').textContent = skills.length;
    skills.slice(0, 15).forEach(s => {
        const name = typeof s === 'string' ? s : s.name;
        skillsBox.innerHTML += `<span class="badge badge-primary">${name}</span>`;
    });
    if (skills.length > 15) {
        skillsBox.innerHTML += `<span class="badge badge-subtle">+${skills.length - 15} more</span>`;
    }

    // Projects
    const projectsBox = document.getElementById('ext-projects-list');
    projectsBox.innerHTML = '';
    const projs = parsed.projects || [];
    document.getElementById('ext-projects-count').textContent = projs.length;
    projs.forEach(p => {
        projectsBox.innerHTML += `
            <div class="mini-list-item">
                <strong>${p.title}</strong>
                ${p.technologies ? `<span class="text-muted"> (${p.technologies})</span>` : ''}
            </div>
        `;
    });

    // Education
    const eduBox = document.getElementById('ext-education-list');
    eduBox.innerHTML = '';
    (parsed.education || []).forEach(e => {
        eduBox.innerHTML += `
            <div class="mini-list-item">
                <strong>${e.degree || 'Degree'}</strong> – ${e.institution || 'University'} ${e.year ? `(${e.year})` : ''}
            </div>
        `;
    });
}

// Proceed from Upload to Analyze Page
function proceedToAnalyze() {
    const resumeId = localStorage.getItem('current_resume_id');
    const roleSelect = document.getElementById('target-role-select');
    const selectedRole = roleSelect ? roleSelect.value : 'Frontend Developer';
    const jdText = document.getElementById('job-description-text') ? document.getElementById('job-description-text').value.trim() : '';

    if (jdText) {
        localStorage.setItem('current_jd_text', jdText);
    } else {
        localStorage.removeItem('current_jd_text');
    }

    if (resumeId) {
        window.location.href = `/analyze?resume_id=${resumeId}&role=${encodeURIComponent(selectedRole)}`;
    } else {
        showToast('Please upload a resume first.', 'warning');
    }
}

// Insert Sample Job Descriptions
async function insertSampleJD(type) {
    try {
        const resp = await fetch('/api/sample-data');
        const data = await resp.json();
        if (data.success) {
            const targetArea = document.getElementById('job-description-text') || document.getElementById('analysis-jd-input');
            if (targetArea) {
                if (type === 'frontend') {
                    targetArea.value = data.sample_frontend_jd;
                    const roleSelect = document.getElementById('target-role-select') || document.getElementById('analysis-role-select');
                    if (roleSelect) roleSelect.value = 'Frontend Developer';
                } else if (type === 'aiml') {
                    targetArea.value = data.sample_aiml_jd;
                    const roleSelect = document.getElementById('target-role-select') || document.getElementById('analysis-role-select');
                    if (roleSelect) roleSelect.value = 'AI/ML Engineer';
                }
                showToast(`Loaded sample ${type === 'frontend' ? 'Frontend' : 'AI/ML'} Job Description!`, 'success');
            }
        }
    } catch (err) {
        showToast('Failed to load sample JD: ' + err.message, 'danger');
    }
}

// -------------------------------------------------------------
// Analysis Page Logic
// -------------------------------------------------------------

async function runAnalysis(resumeId, targetRole, jdText = null) {
    showToast(`Analyzing profile for ${targetRole}...`, 'info');
    
    // Check if JD was stored or passed
    const jd = jdText !== null ? jdText : (localStorage.getItem('current_jd_text') || '');
    if (document.getElementById('analysis-jd-input') && jd) {
        document.getElementById('analysis-jd-input').value = jd;
    }

    try {
        const resp = await fetch('/api/analyze-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_id: parseInt(resumeId),
                target_role: targetRole,
                job_description: jd
            })
        });

        const data = await resp.json();
        if (data.success) {
            currentAnalysisData = data.analysis;
            renderAnalysisDashboard(data.analysis, targetRole);
            showToast(`Analysis complete for ${targetRole}!`, 'success');
        } else {
            showToast(data.error || 'Analysis failed', 'danger');
        }
    } catch (err) {
        showToast('Error during analysis: ' + err.message, 'danger');
    }
}

function renderAnalysisDashboard(analysis, targetRole) {
    // Role labels
    document.getElementById('target-role-label').textContent = targetRole;
    if (document.getElementById('action-role-text')) {
        document.getElementById('action-role-text').textContent = targetRole;
    }

    // Engine Banner
    const engineText = document.getElementById('engine-text');
    if (engineText) {
        if (analysis.engine && analysis.engine.includes('gemini')) {
            engineText.innerHTML = `<strong>Gemini 2.5 AI Engine Active:</strong> Evaluated using official Gemini API. Strict anti-hallucination verification enforced.`;
        } else {
            engineText.innerHTML = `<strong>Deterministic Local Engine Active:</strong> Deterministic keyword taxonomy, section heuristics, and anti-hallucination evidence mapping.`;
        }
    }

    // Scores
    animateScore('ats-score-val', 'ats-bar', analysis.ats_score);
    animateScore('skill-match-val', 'skill-bar', analysis.skill_match);
    animateScore('role-align-val', 'role-bar', analysis.role_alignment);
    animateScore('structure-score-val', 'structure-bar', analysis.structure_score);
    animateScore('evidence-strength-val', 'evidence-bar', analysis.evidence_strength);

    // Section 5: Skills breakdown
    renderSkillsColumns(analysis.matched_skills || [], analysis.missing_skills || [], analysis.weak_skills || []);

    // Section 6: Evidence Mapping
    renderEvidenceMapping(analysis.evidence_map || []);

    // Section 7: Improvements
    renderImprovements(analysis.improvements || []);
}

function animateScore(valElementId, barElementId, score) {
    const valEl = document.getElementById(valElementId);
    const barEl = document.getElementById(barElementId);
    if (!valEl || !barEl) return;

    valEl.textContent = `${score}%`;
    barEl.style.width = '0%';
    setTimeout(() => {
        barEl.style.width = `${Math.min(100, Math.max(5, score))}%`;
    }, 100);
}

function renderSkillsColumns(matched, missing, weak) {
    // Matched
    const matchedContainer = document.getElementById('matched-skills-list');
    document.getElementById('matched-count').textContent = matched.length;
    matchedContainer.innerHTML = '';
    matched.forEach(item => {
        matchedContainer.innerHTML += `
            <div class="skill-analysis-item">
                <div class="skill-item-header">
                    <span class="skill-item-name"><i class="fa-solid fa-check text-success"></i> ${item.name}</span>
                    <span class="badge badge-success">${item.category || 'Core'}</span>
                </div>
                <p class="skill-item-reason">${item.reason}</p>
            </div>
        `;
    });

    // Missing
    const missingContainer = document.getElementById('missing-skills-list');
    document.getElementById('missing-count').textContent = missing.length;
    missingContainer.innerHTML = '';
    missing.forEach(item => {
        missingContainer.innerHTML += `
            <div class="skill-analysis-item">
                <div class="skill-item-header">
                    <span class="skill-item-name"><i class="fa-solid fa-xmark text-danger"></i> ${item.name}</span>
                    <span class="badge badge-danger">${item.importance || 'Required'}</span>
                </div>
                <p class="skill-item-reason">${item.reason}</p>
            </div>
        `;
    });

    // Weak / Unverified
    const weakContainer = document.getElementById('weak-skills-list');
    document.getElementById('weak-count').textContent = weak.length;
    weakContainer.innerHTML = '';
    if (weak.length === 0) {
        weakContainer.innerHTML = `<p class="text-muted p-2" style="font-size: 0.85rem;">All claimed skills have verified supporting evidence!</p>`;
    } else {
        weak.forEach(item => {
            weakContainer.innerHTML += `
                <div class="skill-analysis-item">
                    <div class="skill-item-header">
                        <span class="skill-item-name"><i class="fa-solid fa-triangle-exclamation text-warning"></i> ${item.name}</span>
                        <span class="badge badge-warning">Unsubstantiated</span>
                    </div>
                    <p class="skill-item-reason">${item.reason}</p>
                </div>
            `;
        });
    }
}

function renderEvidenceMapping(evidenceMap) {
    const tbody = document.getElementById('evidence-table-body');
    tbody.innerHTML = '';

    let verifiedCount = 0;
    evidenceMap.forEach(item => {
        if (item.verified) verifiedCount++;
        const rowClass = item.verified ? 'evidence-row-verified' : 'evidence-row-unverified';
        const badge = item.verified 
            ? `<span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Verified</span>`
            : `<span class="badge badge-danger"><i class="fa-solid fa-circle-xmark"></i> Not verified</span>`;

        tbody.innerHTML += `
            <tr class="${rowClass}">
                <td><strong>${item.skill}</strong></td>
                <td>${badge}</td>
                <td>
                    <div class="evidence-source">${item.evidence}</div>
                    ${item.details ? `<div class="evidence-snippet">${item.details}</div>` : ''}
                </td>
            </tr>
        `;
    });

    const pillText = document.getElementById('verified-pill-text');
    if (pillText) {
        pillText.textContent = `${verifiedCount} / ${evidenceMap.length} Skills Verified with Evidence`;
    }
}

function renderImprovements(improvements) {
    const container = document.getElementById('improvements-container');
    container.innerHTML = '';

    if (improvements.length === 0) {
        container.innerHTML = `<div class="p-3 text-muted">No critical improvements flagged. Great job!</div>`;
        return;
    }

    improvements.forEach(imp => {
        container.innerHTML += `
            <div class="improvement-card" data-category="${imp.category}">
                <div class="imp-header">
                    <span class="imp-title">${imp.title}</span>
                    <span class="badge badge-primary">${imp.category}</span>
                </div>
                <p class="imp-rec">${imp.recommendation}</p>
                <div class="diff-box">
                    <div class="diff-before">
                        <strong>Before:</strong> "${imp.before}"
                    </div>
                    <div class="diff-suggested">
                        <strong>Suggested:</strong> "${imp.suggested}"
                    </div>
                </div>
            </div>
        `;
    });
}

function filterImprovements(category) {
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    event.currentTarget.classList.add('active');

    const cards = document.querySelectorAll('.improvement-card');
    cards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category').toLowerCase() === category.toLowerCase()) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

function changeAnalysisRole() {
    const select = document.getElementById('analysis-role-select');
    const resumeId = localStorage.getItem('current_resume_id');
    if (select && resumeId) {
        runAnalysis(resumeId, select.value);
    }
}

function reRunAnalysis() {
    changeAnalysisRole();
}

function reRunAnalysisWithJD() {
    const jdInput = document.getElementById('analysis-jd-input');
    const select = document.getElementById('analysis-role-select');
    const resumeId = localStorage.getItem('current_resume_id');
    const jd = jdInput ? jdInput.value.trim() : '';
    localStorage.setItem('current_jd_text', jd);

    if (resumeId && select) {
        runAnalysis(resumeId, select.value, jd);
    }
}

function generateAndGoToPreview() {
    const resumeId = localStorage.getItem('current_resume_id');
    const select = document.getElementById('analysis-role-select');
    const role = select ? select.value : 'Frontend Developer';
    if (resumeId) {
        window.location.href = `/preview?resume_id=${resumeId}&role=${encodeURIComponent(role)}`;
    } else {
        showToast('Please upload or load a resume first.', 'warning');
    }
}

// -------------------------------------------------------------
// Preview & Live Editor Logic
// -------------------------------------------------------------

async function loadResumePreview(resumeId, role = 'Frontend Developer', versionId = null) {
    showToast(`Generating role-tailored resume draft for ${role}...`, 'info');
    try {
        const resp = await fetch('/api/generate-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_id: parseInt(resumeId),
                target_role: role
            })
        });

        const data = await resp.json();
        if (data.success) {
            currentRoleResume = data.role_resume;
            populateEditorAndSheet(currentRoleResume, role);
            showToast(`Role-tailored resume ready for ${role}!`, 'success');
        } else {
            showToast(data.error || 'Could not generate role preview', 'danger');
        }
    } catch (err) {
        showToast('Network error loading preview: ' + err.message, 'danger');
    }
}

function populateEditorAndSheet(resumeData, role) {
    const contact = resumeData.contact || {};
    document.getElementById('edit-name').value = contact.name || '';
    document.getElementById('edit-email').value = contact.email || '';
    document.getElementById('edit-phone').value = contact.phone || '';
    document.getElementById('edit-github').value = contact.github || '';
    document.getElementById('edit-linkedin').value = contact.linkedin || '';

    // Summary
    document.getElementById('edit-summary').value = resumeData.summary || '';

    // Skills
    const skillsList = resumeData.raw_skills || [];
    document.getElementById('edit-skills').value = skillsList.join(', ');

    // Projects Editor
    const projContainer = document.getElementById('edit-projects-container');
    projContainer.innerHTML = '';
    (resumeData.projects || []).forEach((p, idx) => {
        projContainer.innerHTML += `
            <div class="dynamic-row-card mb-2" data-proj-index="${idx}">
                <div class="form-group mb-1">
                    <label class="form-label-sm">Project Title</label>
                    <input type="text" class="form-control-sm edit-proj-title" value="${p.title}" oninput="updateSheetPreview()">
                </div>
                <div class="form-group mb-1">
                    <label class="form-label-sm">Technologies</label>
                    <input type="text" class="form-control-sm edit-proj-tech" value="${p.technologies || ''}" oninput="updateSheetPreview()">
                </div>
                <div class="form-group">
                    <label class="form-label-sm">Description Bullet</label>
                    <textarea class="form-control-sm edit-proj-desc" rows="2" oninput="updateSheetPreview()">${p.description || ''}</textarea>
                </div>
            </div>
        `;
    });

    // Education Editor
    const eduContainer = document.getElementById('edit-education-container');
    eduContainer.innerHTML = '';
    (resumeData.education || []).forEach((e, idx) => {
        eduContainer.innerHTML += `
            <div class="dynamic-row-card mb-2" data-edu-index="${idx}">
                <div class="form-group mb-1">
                    <label class="form-label-sm">Degree</label>
                    <input type="text" class="form-control-sm edit-edu-degree" value="${e.degree || ''}" oninput="updateSheetPreview()">
                </div>
                <div class="form-group mb-1">
                    <label class="form-label-sm">Institution</label>
                    <input type="text" class="form-control-sm edit-edu-inst" value="${e.institution || ''}" oninput="updateSheetPreview()">
                </div>
                <div class="grid-2-col">
                    <div>
                        <label class="form-label-sm">Year</label>
                        <input type="text" class="form-control-sm edit-edu-year" value="${e.year || ''}" oninput="updateSheetPreview()">
                    </div>
                    <div>
                        <label class="form-label-sm">GPA</label>
                        <input type="text" class="form-control-sm edit-edu-gpa" value="${e.gpa || ''}" oninput="updateSheetPreview()">
                    </div>
                </div>
            </div>
        `;
    });

    // Certifications Editor
    const certs = (resumeData.certifications || []).map(c => typeof c === 'string' ? c : `${c.name || ''} – ${c.issuer || ''}`);
    document.getElementById('edit-certifications').value = certs.join('\n');

    // Achievements Editor
    const achs = resumeData.achievements || [];
    document.getElementById('edit-achievements').value = achs.join('\n');

    // Update sheet
    updateSheetPreview();
}

function updateSheetPreview() {
    // Header
    const name = document.getElementById('edit-name').value.trim() || 'CANDIDATE NAME';
    const email = document.getElementById('edit-email').value.trim();
    const phone = document.getElementById('edit-phone').value.trim();
    const github = document.getElementById('edit-github').value.trim();
    const linkedin = document.getElementById('edit-linkedin').value.trim();

    document.getElementById('sheet-name').textContent = name.toUpperCase();
    const contactParts = [email, phone, github, linkedin].filter(Boolean);
    document.getElementById('sheet-contact').textContent = contactParts.join('  |  ');

    // Summary
    const summary = document.getElementById('edit-summary').value.trim();
    document.getElementById('sheet-summary-body').textContent = summary;
    document.getElementById('sheet-summary-section').style.display = summary ? 'block' : 'none';

    // Skills
    const skillsText = document.getElementById('edit-skills').value.trim();
    const skillsArr = skillsText.split(',').map(s => s.trim()).filter(Boolean);
    const skillsBody = document.getElementById('sheet-skills-body');
    skillsBody.innerHTML = `<strong>Skills:</strong> ${skillsArr.join(', ')}`;
    document.getElementById('sheet-skills-section').style.display = skillsArr.length ? 'block' : 'none';

    // Projects
    const projectsBody = document.getElementById('sheet-projects-body');
    projectsBody.innerHTML = '';
    const projCards = document.querySelectorAll('#edit-projects-container .dynamic-row-card');
    projCards.forEach(card => {
        const title = card.querySelector('.edit-proj-title').value.trim();
        const tech = card.querySelector('.edit-proj-tech').value.trim();
        const desc = card.querySelector('.edit-proj-desc').value.trim();

        if (title) {
            projectsBody.innerHTML += `
                <div class="sheet-item">
                    <div class="sheet-item-header">
                        <span>${title}</span>
                        ${tech ? `<span class="sheet-item-sub">| ${tech}</span>` : ''}
                    </div>
                    ${desc ? `<div class="sheet-bullet">${desc}</div>` : ''}
                </div>
            `;
        }
    });

    // Education
    const eduBody = document.getElementById('sheet-education-body');
    eduBody.innerHTML = '';
    const eduCards = document.querySelectorAll('#edit-education-container .dynamic-row-card');
    eduCards.forEach(card => {
        const degree = card.querySelector('.edit-edu-degree').value.trim();
        const inst = card.querySelector('.edit-edu-inst').value.trim();
        const year = card.querySelector('.edit-edu-year').value.trim();
        const gpa = card.querySelector('.edit-edu-gpa').value.trim();

        if (degree || inst) {
            eduBody.innerHTML += `
                <div class="sheet-item">
                    <div class="sheet-item-header">
                        <span>${degree} – ${inst}</span>
                        <span>${[year, gpa ? `GPA: ${gpa}` : ''].filter(Boolean).join(', ')}</span>
                    </div>
                </div>
            `;
        }
    });

    // Certifications
    const certsText = document.getElementById('edit-certifications').value.trim();
    const certLines = certsText.split('\n').map(l => l.trim()).filter(Boolean);
    const certBody = document.getElementById('sheet-certifications-body');
    certBody.innerHTML = '';
    certLines.forEach(c => {
        certBody.innerHTML += `<div class="sheet-bullet">${c}</div>`;
    });
    document.getElementById('sheet-certifications-section').style.display = certLines.length ? 'block' : 'none';

    // Achievements
    const achText = document.getElementById('edit-achievements').value.trim();
    const achLines = achText.split('\n').map(l => l.trim()).filter(Boolean);
    const achBody = document.getElementById('sheet-achievements-body');
    achBody.innerHTML = '';
    achLines.forEach(a => {
        achBody.innerHTML += `<div class="sheet-bullet">${a}</div>`;
    });
    document.getElementById('sheet-achievements-section').style.display = achLines.length ? 'block' : 'none';
}

function switchRolePreview() {
    const roleSelect = document.getElementById('preview-role-select');
    const resumeId = localStorage.getItem('current_resume_id');
    const role = roleSelect.value;
    document.getElementById('version-name-input').value = `${role} Version`;
    loadResumePreview(resumeId, role);
}

async function saveCurrentVersion() {
    const resumeId = localStorage.getItem('current_resume_id');
    const roleSelect = document.getElementById('preview-role-select');
    const versionName = document.getElementById('version-name-input').value.trim() || 'Role Version';

    if (!resumeId) {
        showToast('No active resume to save.', 'warning');
        return;
    }

    // Collect current edited state
    const currentPayload = collectCurrentSheetData();

    try {
        const resp = await fetch('/api/create-version', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_id: parseInt(resumeId),
                version_name: versionName,
                target_role: roleSelect.value,
                formatted_resume: currentPayload,
                ats_score: 80
            })
        });

        const data = await resp.json();
        if (data.success) {
            showToast(`Saved '${versionName}' to database!`, 'success');
            setTimeout(() => { window.location.href = `/versions?resume_id=${resumeId}`; }, 800);
        } else {
            showToast(data.error || 'Failed to save version', 'danger');
        }
    } catch (err) {
        showToast('Error saving version: ' + err.message, 'danger');
    }
}

function collectCurrentSheetData() {
    const name = document.getElementById('edit-name').value.trim();
    const email = document.getElementById('edit-email').value.trim();
    const phone = document.getElementById('edit-phone').value.trim();
    const github = document.getElementById('edit-github').value.trim();
    const linkedin = document.getElementById('edit-linkedin').value.trim();
    const summary = document.getElementById('edit-summary').value.trim();

    const skills = document.getElementById('edit-skills').value.split(',').map(s => s.trim()).filter(Boolean);

    const projects = [];
    document.querySelectorAll('#edit-projects-container .dynamic-row-card').forEach(card => {
        projects.push({
            title: card.querySelector('.edit-proj-title').value.trim(),
            technologies: card.querySelector('.edit-proj-tech').value.trim(),
            description: card.querySelector('.edit-proj-desc').value.trim()
        });
    });

    const education = [];
    document.querySelectorAll('#edit-education-container .dynamic-row-card').forEach(card => {
        education.push({
            degree: card.querySelector('.edit-edu-degree').value.trim(),
            institution: card.querySelector('.edit-edu-inst').value.trim(),
            year: card.querySelector('.edit-edu-year').value.trim(),
            gpa: card.querySelector('.edit-edu-gpa').value.trim()
        });
    });

    const certifications = document.getElementById('edit-certifications').value.split('\n').map(c => c.trim()).filter(Boolean);
    const achievements = document.getElementById('edit-achievements').value.split('\n').map(a => a.trim()).filter(Boolean);

    return {
        contact: { name, email, phone, github, linkedin },
        summary,
        skills: { "Key Skills": skills },
        raw_skills: skills,
        projects,
        education,
        certifications,
        achievements
    };
}

function downloadPdf(event) {
    event.preventDefault();
    const resumeId = localStorage.getItem('current_resume_id');
    const roleSelect = document.getElementById('preview-role-select');
    const role = roleSelect ? roleSelect.value : 'General';

    if (!resumeId) {
        showToast('No active resume to export.', 'warning');
        return;
    }

    showToast('Generating ATS-compliant PDF...', 'info');
    window.location.href = `/api/export/${resumeId}?role=${encodeURIComponent(role)}`;
}

function goToAnalysis() {
    const resumeId = localStorage.getItem('current_resume_id');
    const roleSelect = document.getElementById('preview-role-select');
    const role = roleSelect ? roleSelect.value : 'Frontend Developer';
    window.location.href = `/analyze?resume_id=${resumeId}&role=${encodeURIComponent(role)}`;
}

// -------------------------------------------------------------
// Versions Page Logic
// -------------------------------------------------------------

async function loadResumeVersions(resumeId) {
    try {
        const resp = await fetch(`/api/versions/${resumeId}`);
        const data = await resp.json();

        // Also fetch candidate name
        const candResp = await fetch(`/api/resume/${resumeId}`);
        const candData = await candResp.json();
        if (candData.success && candData.resume) {
            const parsed = candData.resume.parsed_data || {};
            document.getElementById('versions-candidate-name').textContent = parsed.name || 'Candidate';
        }

        if (data.success) {
            renderVersionsGrid(data.versions || [], resumeId);
        }
    } catch (err) {
        showToast('Failed to load versions: ' + err.message, 'danger');
    }
}

function renderVersionsGrid(versions, resumeId) {
    const container = document.getElementById('versions-container');
    const badge = document.getElementById('versions-count-badge');
    badge.textContent = versions.length;

    if (versions.length === 0) {
        container.innerHTML = `
            <div class="placeholder-state card" style="grid-column: 1 / -1;">
                <div class="placeholder-icon"><i class="fa-solid fa-folder-open"></i></div>
                <h3>No Saved Role Versions Yet</h3>
                <p class="text-muted">Generate and save tailored versions for Frontend Developer, AI/ML Engineer, etc. in Preview.</p>
                <div class="mt-3">
                    <a href="/preview?resume_id=${resumeId}" class="btn btn-primary">Go to Preview</a>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = '';
    versions.forEach(v => {
        container.innerHTML += `
            <div class="version-card">
                <div>
                    <div class="version-card-header">
                        <div>
                            <h3 class="version-title">${v.version_name}</h3>
                            <div class="version-meta">Created on ${v.created_at ? v.created_at.slice(0, 10) : 'Recent'}</div>
                        </div>
                        <span class="badge badge-primary">${v.target_role}</span>
                    </div>
                    <p class="text-muted" style="font-size: 0.85rem;">ATS-optimized tailored configuration for ${v.target_role}.</p>
                </div>
                <div class="version-actions">
                    <a href="/preview?resume_id=${resumeId}&version_id=${v.id}&role=${encodeURIComponent(v.target_role)}" class="btn btn-outline-primary btn-sm">
                        <i class="fa-solid fa-eye"></i> Preview
                    </a>
                    <a href="/api/export/${resumeId}?version_id=${v.id}" class="btn btn-primary btn-sm">
                        <i class="fa-solid fa-file-pdf"></i> Download PDF
                    </a>
                </div>
            </div>
        `;
    });
}

// -------------------------------------------------------------
// Resume Builder Helpers
// -------------------------------------------------------------

function addProjectRow(title = '', tech = '', desc = '', url = '') {
    const container = document.getElementById('projects-container');
    const idx = container.children.length;
    const card = document.createElement('div');
    card.className = 'dynamic-row-card';
    card.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.closest('.dynamic-row-card').remove()">
            <i class="fa-solid fa-trash"></i>
        </button>
        <div class="grid-2-col mb-2">
            <div class="form-group mb-0">
                <label class="form-label-sm">Project Title *</label>
                <input type="text" class="form-control b-proj-title" placeholder="e.g. Movie Success Prediction System" value="${title}" required>
            </div>
            <div class="form-group mb-0">
                <label class="form-label-sm">Technologies Used *</label>
                <input type="text" class="form-control b-proj-tech" placeholder="e.g. Python, Machine Learning, Scikit-Learn" value="${tech}" required>
            </div>
        </div>
        <div class="form-group mb-2">
            <label class="form-label-sm">Description & Implementation Evidence *</label>
            <textarea class="form-control b-proj-desc" rows="2" placeholder="Explain what you built, algorithms/libraries used, and outcomes..." required>${desc}</textarea>
        </div>
        <div class="form-group mb-0">
            <label class="form-label-sm">GitHub / Live URL</label>
            <input type="text" class="form-control b-proj-url" placeholder="https://github.com/..." value="${url}">
        </div>
    `;
    container.appendChild(card);
}

function addEducationRow(degree = '', inst = '', year = '', gpa = '') {
    const container = document.getElementById('education-container');
    const card = document.createElement('div');
    card.className = 'dynamic-row-card';
    card.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.closest('.dynamic-row-card').remove()">
            <i class="fa-solid fa-trash"></i>
        </button>
        <div class="grid-2-col mb-2">
            <div class="form-group mb-0">
                <label class="form-label-sm">Degree / Program *</label>
                <input type="text" class="form-control b-edu-degree" placeholder="e.g. B.Tech in Computer Science" value="${degree}" required>
            </div>
            <div class="form-group mb-0">
                <label class="form-label-sm">Institution / University *</label>
                <input type="text" class="form-control b-edu-inst" placeholder="e.g. Apex Institute of Technology" value="${inst}" required>
            </div>
        </div>
        <div class="grid-2-col">
            <div class="form-group mb-0">
                <label class="form-label-sm">Year / Graduation</label>
                <input type="text" class="form-control b-edu-year" placeholder="e.g. 2021 - 2025" value="${year}">
            </div>
            <div class="form-group mb-0">
                <label class="form-label-sm">GPA / Marks</label>
                <input type="text" class="form-control b-edu-gpa" placeholder="e.g. 3.8 / 4.0" value="${gpa}">
            </div>
        </div>
    `;
    container.appendChild(card);
}

function addExperienceRow(role = '', comp = '', dur = '', desc = '') {
    const container = document.getElementById('experience-container');
    const card = document.createElement('div');
    card.className = 'dynamic-row-card';
    card.innerHTML = `
        <button type="button" class="remove-btn" onclick="this.closest('.dynamic-row-card').remove()">
            <i class="fa-solid fa-trash"></i>
        </button>
        <div class="grid-3-col mb-2">
            <div class="form-group mb-0">
                <label class="form-label-sm">Role / Title</label>
                <input type="text" class="form-control b-exp-role" placeholder="e.g. Frontend Web Intern" value="${role}">
            </div>
            <div class="form-group mb-0">
                <label class="form-label-sm">Company / Org</label>
                <input type="text" class="form-control b-exp-comp" placeholder="e.g. Apex Tech Solutions" value="${comp}">
            </div>
            <div class="form-group mb-0">
                <label class="form-label-sm">Duration</label>
                <input type="text" class="form-control b-exp-dur" placeholder="e.g. Jun 2024 - Aug 2024" value="${dur}">
            </div>
        </div>
        <div class="form-group mb-0">
            <label class="form-label-sm">Responsibilities & Achievements</label>
            <textarea class="form-control b-exp-desc" rows="2" placeholder="Tasks executed, tools used, and results...">${desc}</textarea>
        </div>
    `;
    container.appendChild(card);
}

function appendSkill(skill) {
    const input = document.getElementById('b-skills-input');
    const current = input.value.split(',').map(s => s.trim()).filter(Boolean);
    if (!current.includes(skill)) {
        current.push(skill);
        input.value = current.join(', ');
    }
}

function prefillBuilderDemo() {
    document.getElementById('b-name').value = "Alex Kumar";
    document.getElementById('b-email').value = "alex.kumar@example.com";
    document.getElementById('b-phone').value = "+1 (555) 234-5678";
    document.getElementById('b-github').value = "github.com/alexkumar-dev";
    document.getElementById('b-linkedin').value = "linkedin.com/in/alexkumar-dev";
    document.getElementById('b-summary').value = "Motivated Computer Science student with hands-on experience developing full-stack web applications and machine learning models.";
    document.getElementById('b-skills-input').value = "Python, JavaScript, React, HTML, CSS, Node.js, SQL, Machine Learning, Scikit-Learn, Git";

    document.getElementById('projects-container').innerHTML = '';
    addProjectRow(
        "Movie Success Prediction System",
        "Python, Machine Learning, Scikit-Learn, Pandas",
        "Engineered an end-to-end predictive pipeline analyzing historical box office metrics to forecast film revenue.",
        "https://github.com/alexkumar-dev/movie-success-pred"
    );
    addProjectRow(
        "Student Portfolio & Campus Portal",
        "HTML, CSS, JavaScript, React, Git",
        "Designed and deployed a responsive web portal allowing campus students to track study clubs and peer notes.",
        "https://github.com/alexkumar-dev/campus-portal"
    );

    document.getElementById('education-container').innerHTML = '';
    addEducationRow("Bachelor of Technology in Computer Science", "Apex Institute of Technology", "2021 - 2025", "3.8 / 4.0");

    document.getElementById('experience-container').innerHTML = '';
    addExperienceRow("Frontend Development Intern", "Apex Web Solutions", "June 2024 - August 2024", "Built responsive web pages using HTML, CSS, JavaScript, improving accessible navigation.");

    document.getElementById('b-certifications').value = "Meta Front-End Developer Professional Certificate - Coursera\nPython for Data Science - Udemy";
    document.getElementById('b-achievements').value = "First Place Winner - Apex Hackathon 2024\nSolved 250+ LeetCode problems (Rating: 1680)\nDean's Honor List";

    showToast('Pre-filled sample student profile data!', 'success');
}

async function handleBuilderSubmit(event) {
    event.preventDefault();
    const data = collectBuilderFormData();
    try {
        const resp = await fetch('/api/save-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parsed_data: data })
        });
        const res = await resp.json();
        if (res.success) {
            localStorage.setItem('current_resume_id', res.resume_id);
            localStorage.setItem('current_parsed_data', JSON.stringify(data));
            showToast('Resume saved successfully! Redirecting to preview...', 'success');
            setTimeout(() => { window.location.href = `/preview?resume_id=${res.resume_id}`; }, 800);
        } else {
            showToast(res.error || 'Failed to save', 'danger');
        }
    } catch (err) {
        showToast('Error saving resume: ' + err.message, 'danger');
    }
}

async function saveAndAnalyze() {
    const data = collectBuilderFormData();
    try {
        const resp = await fetch('/api/save-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parsed_data: data })
        });
        const res = await resp.json();
        if (res.success) {
            localStorage.setItem('current_resume_id', res.resume_id);
            localStorage.setItem('current_parsed_data', JSON.stringify(data));
            showToast('Resume saved! Proceeding to evidence audit...', 'success');
            setTimeout(() => { window.location.href = `/analyze?resume_id=${res.resume_id}&role=Frontend Developer`; }, 800);
        }
    } catch (err) {
        showToast('Error: ' + err.message, 'danger');
    }
}

function collectBuilderFormData() {
    const name = document.getElementById('b-name').value.trim();
    const email = document.getElementById('b-email').value.trim();
    const phone = document.getElementById('b-phone').value.trim();
    const github = document.getElementById('b-github').value.trim();
    const linkedin = document.getElementById('b-linkedin').value.trim();
    const summary = document.getElementById('b-summary').value.trim();

    const skillsRaw = document.getElementById('b-skills-input').value.split(',').map(s => s.trim()).filter(Boolean);
    const skills = skillsRaw.map(s => ({ name: s, category: 'Technical' }));

    const projects = [];
    document.querySelectorAll('#projects-container .dynamic-row-card').forEach(c => {
        projects.push({
            title: c.querySelector('.b-proj-title').value.trim(),
            technologies: c.querySelector('.b-proj-tech').value.trim(),
            description: c.querySelector('.b-proj-desc').value.trim(),
            github_url: c.querySelector('.b-proj-url').value.trim()
        });
    });

    const education = [];
    document.querySelectorAll('#education-container .dynamic-row-card').forEach(c => {
        education.push({
            degree: c.querySelector('.b-edu-degree').value.trim(),
            institution: c.querySelector('.b-edu-inst').value.trim(),
            year: c.querySelector('.b-edu-year').value.trim(),
            gpa: c.querySelector('.b-edu-gpa').value.trim()
        });
    });

    const experience = [];
    document.querySelectorAll('#experience-container .dynamic-row-card').forEach(c => {
        experience.push({
            role: c.querySelector('.b-exp-role').value.trim(),
            company: c.querySelector('.b-exp-comp').value.trim(),
            duration: c.querySelector('.b-exp-dur').value.trim(),
            description: c.querySelector('.b-exp-desc').value.trim()
        });
    });

    const certsRaw = document.getElementById('b-certifications').value.split('\n').map(s => s.trim()).filter(Boolean);
    const certifications = certsRaw.map(c => ({ name: c, issuer: '' }));

    const achievements = document.getElementById('b-achievements').value.split('\n').map(s => s.trim()).filter(Boolean);

    return {
        name,
        email,
        phone,
        github,
        linkedin,
        summary,
        skills,
        projects,
        education,
        experience,
        certifications,
        achievements
    };
}
