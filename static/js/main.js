/* GESTION DES ÉTAPES */

let etapeActuelle = 1;

function allerEtape(n) {
  // Validation avant de quitter l'étape 1
  if (etapeActuelle === 1 && n === 2) {
    const matricule = document.querySelector('input[name="matricule"]');
    const niveau    = document.querySelector('input[name="niveau"]:checked');
    const filiere   = document.querySelector('input[name="filiere"]:checked');
    const valMat = matricule.value.trim().toUpperCase();

    if (!matricule || !matricule.value.trim()) {
      secourir(matricule);
      afficherToast(' Entre ton matricule.', 'danger'); return;
    }
    if(valMat.length != 8){
      secourir(matricule);
      afficherToast(' Le matricule doit contenir exactement 8 caractères.', 'danger'); return;
    }

    if(!/^\d{2}[A-Z]\d{5}$/.test(valMat)){
      secourir(matricule);
      afficherToast(' Format invalide. Exemple : 22S45838 (2 chiffres + 1 lettre  + 5 chiffres)', 'danger'); return;
    }
    
    matricule.value = valMat;

    if (!niveau) {
      afficherToast(' Sélectionne ton niveau académique.', 'danger'); return;
    }
    if (!filiere) {
      afficherToast(' Sélectionne ta filière.', 'danger'); return;
    }

  }

  // Validation avant de quitter l'étape 2
  if (etapeActuelle === 2 && n === 3) {
    const checked = document.querySelectorAll('input[name="matieres_difficiles"]:checked');
    if (checked.length === 0) {
      afficherToast(' Sélectionne au moins une matière difficile.', 'danger'); return;
    }
  }

  // Masquer étape actuelle
  document.getElementById('step' + etapeActuelle).classList.add('hidden');
  // Afficher nouvelle étape
  document.getElementById('step' + n).classList.remove('hidden');

  // Mettre à jour indicateurs
  for (let i = 1; i <= 3; i++) {
    const ind = document.getElementById('step-ind-' + i);
    if (!ind) continue;
    ind.classList.remove('active', 'done');
    if (i < n)  ind.classList.add('done');
    if (i === n) ind.classList.add('active');
  }

  etapeActuelle = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}


function chargerMatieres(filiere) {
  const liste = (typeof MATIERES !== 'undefined') ? MATIERES[filiere] : [];
  if (!liste) return;

  remplirCheckboxes('checkDifficiles', liste, 'matieres_difficiles');
  remplirCheckboxes('checkPratique',   liste, 'matieres_pratique');
}

function remplirCheckboxes(conteneurId, matieres, name) {
  const conteneur = document.getElementById(conteneurId);
  if (!conteneur) return;
  conteneur.innerHTML = '';

  matieres.forEach(m => {
    const label = document.createElement('label');
    label.className = 'check-item';
    label.innerHTML = `
      <input type="checkbox" name="${name}" value="${m}">
      ${m}
    `;
    conteneur.appendChild(label);
  });
}

//dashboard
function initGraphiques() {
  if (typeof Chart === 'undefined') return;
  if (typeof DATA_DIFF === 'undefined' || typeof DATA_PRAT === 'undefined') return;

  const optionsCommunes = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1C2333',
        borderColor: '#30363D',
        borderWidth: 1,
        titleColor: '#E6EDF3',
        bodyColor: '#7D8590',
      }
    },
    scales: {
      x: {
        grid: { color: '#30363D' },
        ticks: { color: '#7D8590', font: { size: 11 } }
      },
      y: {
        grid: { display: false },
        ticks: { color: '#E6EDF3', font: { size: 11 } }
      }
    }
  };

  // Graphique matières difficiles
  const ctxDiff = document.getElementById('chartDifficiles');
  if (ctxDiff && DATA_DIFF.length > 0) {
    new Chart(ctxDiff, {
      type: 'bar',
      data: {
        labels: DATA_DIFF.map(d => tronquer(d.matiere, 30)),
        datasets: [{
          data: DATA_DIFF.map(d => d.nb),
          backgroundColor: 'rgba(231,76,60,0.7)',
          borderColor: 'rgba(231,76,60,1)',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: optionsCommunes
    });
  }

  // Graphique matières pratique
  const ctxPrat = document.getElementById('chartPratique');
  if (ctxPrat && DATA_PRAT.length > 0) {
    new Chart(ctxPrat, {
      type: 'bar',
      data: {
        labels: DATA_PRAT.map(d => tronquer(d.matiere, 30)),
        datasets: [{
          data: DATA_PRAT.map(d => d.nb),
          backgroundColor: 'rgba(52,152,219,0.7)',
          borderColor: 'rgba(52,152,219,1)',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: optionsCommunes
    });
  }
}


function afficherNiveau(niv, btn) {

  document.querySelectorAll('.niveau-panel').forEach(p => {p.classList.add('hidden')});
  
  document.querySelectorAll('.niveau-tab').forEach(b => {b.classList.remove('active')});
 
  const id = 'panel-' + niv.trim().replace(/\s+/g, '-');
  const panel = document.getElementById(id);
  if (panel){
    panel.classList.remove('hidden');
  }

  if(btn){
  btn.classList.add('active');
} 
}


function afficherToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:1.5rem;right:1.5rem;
    background:${type==='danger'?'#1a0a0a':'#0a1a0f'};
    border:1px solid ${type==='danger'?'#E74C3C':'#2ECC71'};
    color:${type==='danger'?'#E74C3C':'#2ECC71'};
    padding:.9rem 1.5rem;border-radius:10px;
    font-size:.85rem;font-weight:500;
    box-shadow:0 8px 30px rgba(0,0,0,.5);
    z-index:999;animation:slideIn .3s ease;
  `;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}


function tronquer(str, max) {
  return str.length > max ? str.slice(0, max) + '…' : str;
}

function secourir(el) {
  if (!el) return;
  el.style.borderColor = '#E74C3C';
  el.focus();
  setTimeout(() => el.style.borderColor = '', 2000);
}


document.addEventListener('DOMContentLoaded', () => {
  initGraphiques();

  // Si une filière est déjà sélectionnée (retour après erreur)
  const filiereChecked = document.querySelector('input[name="filiere"]:checked');
  if (filiereChecked) chargerMatieres(filiereChecked.value);

  // Validation soumission finale
  const form = document.getElementById('mainForm');
  if (form) {
    form.addEventListener('submit', e => {
      const pratique = document.querySelectorAll('input[name="matieres_pratique"]:checked');
      if (pratique.length === 0) {
        e.preventDefault();
        afficherToast('Sélectionne au moins une matière nécessitant de la pratique.', 'danger');
        return;
      }
      const btn = document.getElementById('submitBtn');
      if (btn) { btn.textContent = 'Envoi en cours…'; btn.disabled = true; }
    });
  }
});
