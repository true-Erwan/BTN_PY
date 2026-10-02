/**
 * TRAQUE URBAINE — Frontend Client Tactique (Steam Grade)
 * Communication via API FastAPI + Rendu Canvas FX + Audio Engine
 */

// ═══════════════════════════════════════════════════════════
//                    AUDIO ENGINE
// ═══════════════════════════════════════════════════════════
class AudioEngine {
  constructor() {
    this.enabled = true;
    this.ctx = null;
    this.customSounds = {};
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  // Joue un son custom depuis /sons/ ou fallback sur le synthétiseur
  play(name, durationMs = null) {
    if (!this.enabled) return;
    this.init();

    // Tente de jouer depuis /sons/{name}.wav ou .mp3
    const audio = new Audio(`/sons/${name}.wav`);
    audio.volume = 0.7;

    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          if (durationMs) {
            setTimeout(() => {
              // Fadeout court avant d'arrêter
              audio.pause();
            }, durationMs);
          }
        })
        .catch(() => {
          // Si le fichier n'existe pas encore dans /sons/, jouer le synthétiseur Web Audio
          this.synth(name, durationMs);
        });
    }
  }

  synth(type, durationMs) {
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    const dur = durationMs ? durationMs / 1000 : 0.3;

    if (type === 'clic') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1200, t);
      osc.frequency.exponentialRampToValueAtTime(400, t + 0.05);
      gain.gain.setValueAtTime(0.2, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.05);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.05);
    } else if (type === 'rate') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, t);
      osc.frequency.exponentialRampToValueAtTime(140, t + 0.25);
      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.25);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.25);
    } else if (type === 'touche' || type.startsWith('touche_')) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, t);
      osc.frequency.exponentialRampToValueAtTime(800, t + 0.15);
      gain.gain.setValueAtTime(0.4, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + (dur || 0.3));
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + (dur || 0.3));
    } else if (type === 'epave') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(90, t);
      osc.frequency.exponentialRampToValueAtTime(40, t + 0.6);
      gain.gain.setValueAtTime(0.6, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.6);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.6);
    } else if (type === 'radar') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(400, t);
      osc.frequency.linearRampToValueAtTime(1800, t + 0.4);
      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.4);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.4);
    } else if (type === 'bombe') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(120, t);
      osc.frequency.exponentialRampToValueAtTime(30, t + 0.5);
      gain.gain.setValueAtTime(0.7, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.6);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.6);
    } else if (type === 'laser') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(1400, t);
      osc.frequency.exponentialRampToValueAtTime(100, t + 0.35);
      gain.gain.setValueAtTime(0.6, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.45);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.45);
    } else if (type === 'coin') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(987.77, t);
      osc.frequency.setValueAtTime(1318.51, t + 0.08);
      gain.gain.setValueAtTime(0.25, t);
      gain.gain.exponentialRampToValueAtTime(0.01, t + 0.35);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.35);
    } else if (type === 'victoire') {
      const notes = [523.25, 659.25, 783.99, 1046.5];
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const startT = t + idx * 0.12;
        osc.frequency.setValueAtTime(freq, startT);
        gain.gain.setValueAtTime(0.3, startT);
        gain.gain.exponentialRampToValueAtTime(0.01, startT + 0.4);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(startT);
        osc.stop(startT + 0.4);
      });
    }
  }
}

// ═══════════════════════════════════════════════════════════
//                 PARTICLE & FX CANVAS
// ═══════════════════════════════════════════════════════════
class FXEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.loop();
  }

  resize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  addSparks(x, y, count = 16) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 5 + 2;
      this.particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1,
        decay: Math.random() * 0.03 + 0.02,
        color: Math.random() > 0.5 ? '#ff7700' : '#ffd000',
        size: Math.random() * 3 + 1,
        gravity: 0.1
      });
    }
  }

  addSmoke(x, y, count = 8) {
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: x + (Math.random() - 0.5) * 10,
        y: y + (Math.random() - 0.5) * 10,
        vx: (Math.random() - 0.5) * 0.6,
        vy: -Math.random() * 1.5 - 0.5,
        life: 1,
        decay: Math.random() * 0.02 + 0.01,
        color: 'rgba(120, 125, 140, 0.4)',
        size: Math.random() * 8 + 4,
        gravity: -0.02
      });
    }
  }

  addConfetti(count = 70) {
    const colors = ['#00f0ff', '#ffd000', '#00ff7f', '#ff3344', '#ff7700'];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: window.innerWidth * 0.5 + (Math.random() - 0.5) * 200,
        y: window.innerHeight * 0.4,
        vx: (Math.random() - 0.5) * 12,
        vy: -Math.random() * 10 - 4,
        life: 1,
        decay: Math.random() * 0.015 + 0.008,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 6 + 3,
        gravity: 0.18
      });
    }
  }

  loop() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.life -= p.decay;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      this.ctx.save();
      this.ctx.globalAlpha = p.life;
      this.ctx.fillStyle = p.color;
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();
    }
    requestAnimationFrame(() => this.loop());
  }
}

// ═══════════════════════════════════════════════════════════
//                 RADAR SWEEP EFFECT
// ═══════════════════════════════════════════════════════════
class RadarSweep {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.angle = 0;
    this.animate();
  }

  resize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
  }

  animate() {
    const w = this.canvas.width;
    const h = this.canvas.height;
    if (w > 0 && h > 0) {
      this.ctx.clearRect(0, 0, w, h);
      const cx = w / 2;
      const cy = h / 2;
      const radius = Math.max(w, h);

      this.angle += 0.025;
      if (this.angle > Math.PI * 2) this.angle = 0;

      // Faisceau radar
      const grad = this.ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, 'rgba(0, 240, 255, 0.08)');
      grad.addColorStop(1, 'transparent');

      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.moveTo(cx, cy);
      this.ctx.arc(cx, cy, radius, this.angle - 0.35, this.angle);
      this.ctx.closePath();
      this.ctx.fillStyle = 'rgba(0, 255, 127, 0.06)';
      this.ctx.fill();

      // Ligne principale verte fluorescente
      this.ctx.beginPath();
      this.ctx.moveTo(cx, cy);
      this.ctx.lineTo(cx + Math.cos(this.angle) * radius, cy + Math.sin(this.angle) * radius);
      this.ctx.strokeStyle = 'rgba(0, 255, 127, 0.35)';
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();
      this.ctx.restore();
    }
    requestAnimationFrame(() => this.animate());
  }
}

// ═══════════════════════════════════════════════════════════
//                 APPLICATION CONTROLLER
// ═══════════════════════════════════════════════════════════
class GameApp {
  constructor() {
    this.audio = new AudioEngine();
    this.fx = new FXEngine('fx-canvas');
    this.radarSweep = new RadarSweep('radar-sweep-canvas');

    this.partie = null;
    this.records = { rallye: null, grand_prix: null };
    this.armeSelectionnee = null;
    this.dernierOr = 0;
    this.radarInfo = null;

    this.dom = {
      grid: document.getElementById('parking-grid'),
      gridContainer: document.getElementById('grid-container'),
      reticle: document.getElementById('radar-reticle'),
      targetList: document.getElementById('target-list'),
      statMode: document.getElementById('stat-mode'),
      statTour: document.getElementById('stat-tour'),
      statGold: document.getElementById('stat-gold'),
      goldFloatContainer: document.getElementById('gold-float-container'),
      statScans: document.getElementById('stat-scans'),
      statCibles: document.getElementById('stat-cibles'),
      reconLast: document.getElementById('recon-last-event'),
      terminalFeed: document.getElementById('terminal-feed'),
      recRallye: document.getElementById('rec-rallye-val'),
      recGp: document.getElementById('rec-grand-prix-val'),
      cardRecRallye: document.getElementById('card-rec-rallye'),
      cardRecGp: document.getElementById('card-rec-gp'),

      // Shop elements
      shopZone: document.getElementById('shop-zone'),
      shopGoldCount: document.getElementById('shop-gold-count'),
      shopItemsList: document.getElementById('shop-items-list'),
      shopActiveBanner: document.getElementById('shop-active-banner'),
      shopActiveText: document.getElementById('shop-active-text'),
      btnShopCancel: document.getElementById('btn-shop-cancel'),
      shopRallyeNotice: document.getElementById('shop-rallye-notice'),
      btnShopScan: document.getElementById('btn-shop-scan'),
      btnShopBombeCroix: document.getElementById('btn-shop-bombe-croix'),
      btnShopBombeLigne: document.getElementById('btn-shop-bombe-ligne'),

      btnAudio: document.getElementById('btn-audio-toggle'),
      lblAudio: document.getElementById('lbl-audio'),
      modalMenu: document.getElementById('modal-menu'),
      modalVictoire: document.getElementById('modal-victoire'),
      btnCloseModal: document.getElementById('btn-close-modal'),
      btnMenuOpen: document.getElementById('btn-menu-open'),
      vicScans: document.getElementById('vic-scans'),
      vicModeName: document.getElementById('vic-mode-name'),
      vicRank: document.getElementById('vic-rank'),
      vicRecordAlert: document.getElementById('vic-record-alert'),
      btnVicReplay: document.getElementById('btn-vic-replay'),
      btnVicMenu: document.getElementById('btn-vic-menu')
    };

    this.initEvents();
    this.chargerRecords();
  }

  async chargerRecords() {
    try {
      const res = await fetch('/api/records');
      if (res.ok) {
        this.records = await res.json();
        this.updateRecordsUI();
      }
    } catch (e) {
      console.warn("Records non disponibles", e);
    }
  }

  updateRecordsUI() {
    const r = this.records.rallye !== null ? `${this.records.rallye} scans` : '--';
    const gp = this.records.grand_prix !== null ? `${this.records.grand_prix} scans` : '--';
    if (this.dom.recRallye) this.dom.recRallye.textContent = r;
    if (this.dom.recGp) this.dom.recGp.textContent = gp;
    if (this.dom.cardRecRallye) this.dom.cardRecRallye.textContent = r;
    if (this.dom.cardRecGp) this.dom.cardRecGp.textContent = gp;
  }

  initEvents() {
    // Mode selection
    document.querySelectorAll('.mode-card').forEach(card => {
      card.addEventListener('click', () => {
        const mode = card.dataset.mode;
        this.lancerPartie(mode);
      });
    });

    // Audio toggle
    if (this.dom.btnAudio) {
      this.dom.btnAudio.addEventListener('click', () => {
        this.audio.enabled = !this.audio.enabled;
        this.dom.lblAudio.textContent = this.audio.enabled ? 'SON ON' : 'SON OFF';
        this.dom.btnAudio.querySelector('.icon-speaker').textContent = this.audio.enabled ? '🔊' : '🔇';
        if (this.audio.enabled) this.audio.play('clic');
      });
    }

    // Shop weapons
    if (this.dom.btnShopScan) {
      this.dom.btnShopScan.addEventListener('click', () => this.selectionnerArme('scan'));
    }
    if (this.dom.btnShopBombeCroix) {
      this.dom.btnShopBombeCroix.addEventListener('click', () => this.selectionnerArme('bombe_croix'));
    }
    if (this.dom.btnShopBombeLigne) {
      this.dom.btnShopBombeLigne.addEventListener('click', () => this.selectionnerArme('bombe_ligne_colonne'));
    }
    if (this.dom.btnShopCancel) {
      this.dom.btnShopCancel.addEventListener('click', () => this.deselectionnerArme());
    }

    // Reticle & hover tracking
    if (this.dom.gridContainer) {
      this.dom.gridContainer.addEventListener('mousemove', (e) => this.handleGridHover(e));
      this.dom.gridContainer.addEventListener('mouseleave', () => {
        this.nettoyerSurvol();
        if (this.dom.reticle) this.dom.reticle.classList.add('hidden');
      });
    }

    // Menu modals
    if (this.dom.btnMenuOpen) {
      this.dom.btnMenuOpen.addEventListener('click', () => {
        this.dom.modalMenu.classList.add('active');
        this.dom.btnCloseModal.style.display = this.partie ? 'block' : 'none';
        this.audio.play('clic');
      });
    }

    if (this.dom.btnCloseModal) {
      this.dom.btnCloseModal.addEventListener('click', () => {
        this.dom.modalMenu.classList.remove('active');
        this.audio.play('clic');
      });
    }

    if (this.dom.btnVicReplay) {
      this.dom.btnVicReplay.addEventListener('click', () => {
        this.dom.modalVictoire.classList.remove('active');
        if (this.partie) this.lancerPartie(this.partie.mode);
      });
    }

    if (this.dom.btnVicMenu) {
      this.dom.btnVicMenu.addEventListener('click', () => {
        this.dom.modalVictoire.classList.remove('active');
        this.dom.modalMenu.classList.add('active');
        this.dom.btnCloseModal.style.display = 'none';
        this.audio.play('clic');
      });
    }

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (this.armeSelectionnee) {
          this.deselectionnerArme();
        } else if (this.dom.modalVictoire.classList.contains('active')) {
          this.dom.modalVictoire.classList.remove('active');
          this.dom.modalMenu.classList.add('active');
        } else {
          this.dom.modalMenu.classList.toggle('active');
        }
      } else if (e.key === '1') {
        this.selectionnerArme('scan');
      } else if (e.key === '2') {
        this.selectionnerArme('bombe_croix');
      } else if (e.key === '3') {
        this.selectionnerArme('bombe_ligne_colonne');
      } else if (e.key === 'm' || e.key === 'M') {
        if (this.dom.btnAudio) this.dom.btnAudio.click();
      }
    });

    window.addEventListener('resize', () => {
      this.ajusterTailleGrille();
    });
  }

  ajusterTailleGrille() {
    if (!this.partie || !this.dom.grid) return;
    const t = this.partie.taille;
    const maxDimension = t === 5 ? 380 : 440;
    this.dom.grid.style.width = `${maxDimension}px`;
    this.dom.grid.style.height = `${maxDimension}px`;
    if (this.radarSweep) {
      this.radarSweep.resize(maxDimension, maxDimension);
    }
  }

  async lancerPartie(mode) {
    this.audio.play('clic');
    this.dom.modalMenu.classList.remove('active');

    try {
      const res = await fetch('/api/partie', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });

      if (!res.ok) throw new Error("Erreur démarrage");
      this.partie = await res.json();
      this.armeSelectionnee = null;
      this.dernierOr = this.partie.or || 0;
      this.radarInfo = null;

      this.logTerminal(`> Opération "${mode.toUpperCase()}" initialisée.`);
      if (mode === 'grand_prix') {
        this.logTerminal(`> Marché noir activé : +10 OR générés à chaque fin de tour.`);
      }
      this.logTerminal(`> Secteur balayé. Prêt pour les tirs.`);
      this.dom.reconLast.textContent = "Secteur prêt pour ciblage";

      this.buildGrid();
      this.updateHUD();
      this.renderTargets();
      this.updateShopUI();
    } catch (e) {
      alert("Erreur lors de l'initialisation du jeu : " + e.message);
    }
  }

  buildGrid() {
    const t = this.partie.taille;
    const grid = this.dom.grid;
    grid.innerHTML = '';
    grid.style.gridTemplateColumns = `repeat(${t}, 1fr)`;
    grid.style.gridTemplateRows = `repeat(${t}, 1fr)`;

    this.ajusterTailleGrille();

    const lettres = "ABCDEFGH";

    for (let y = 0; y < t; y++) {
      for (let x = 0; x < t; x++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.dataset.x = x;
        cell.dataset.y = y;
        cell.textContent = `${lettres[x]}${y + 1}`;

        cell.addEventListener('click', () => this.handleCellClick(x, y, cell));
        grid.appendChild(cell);
      }
    }
  }

  selectionnerArme(arme) {
    if (!this.partie || this.partie.fini || this.partie.mode !== 'grand_prix') return;
    const prixMap = { scan: 20, bombe_croix: 40, bombe_ligne_colonne: 80 };
    const prix = prixMap[arme];
    const currentOr = this.partie.or || 0;

    if (currentOr < prix) {
      this.audio.play('rate', 250);
      this.logTerminal(`> OR INSUFFISANT : Il vous faut ${prix} OR pour cette arme (Vous avez ${currentOr} OR).`, 'log-miss');
      this.dom.reconLast.textContent = `Or insuffisant : ${currentOr}/${prix} OR requis`;
      return;
    }

    if (this.armeSelectionnee === arme) {
      this.deselectionnerArme();
      return;
    }

    this.armeSelectionnee = arme;
    this.audio.play('clic');
    this.updateShopUI();
  }

  deselectionnerArme() {
    this.armeSelectionnee = null;
    this.nettoyerSurvol();
    this.updateShopUI();
  }

  nettoyerSurvol() {
    const cells = document.querySelectorAll('.grid-cell');
    cells.forEach(c => {
      c.classList.remove('preview-scan', 'preview-bomb-center', 'preview-bomb-adj', 'preview-laser-line', 'preview-laser-center');
    });
  }

  handleGridHover(e) {
    this.nettoyerSurvol();
    if (!this.partie || !this.armeSelectionnee) return;

    const rect = this.dom.grid.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
      const t = this.partie.taille;
      const cellSize = rect.width / t;
      const gx = Math.floor(x / cellSize);
      const gy = Math.floor(y / cellSize);

      if (this.armeSelectionnee === 'scan') {
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            const cx = gx + dx, cy = gy + dy;
            if (cx >= 0 && cx < t && cy >= 0 && cy < t) {
              const cell = document.querySelector(`.grid-cell[data-x="${cx}"][data-y="${cy}"]`);
              if (cell) cell.classList.add('preview-scan');
            }
          }
        }
      } else if (this.armeSelectionnee === 'bombe_croix') {
        const centerCell = document.querySelector(`.grid-cell[data-x="${gx}"][data-y="${gy}"]`);
        if (centerCell) centerCell.classList.add('preview-bomb-center');

        const adjs = [[gx, gy - 1], [gx, gy + 1], [gx - 1, gy], [gx + 1, gy]];
        adjs.forEach(([ax, ay]) => {
          if (ax >= 0 && ax < t && ay >= 0 && ay < t) {
            const cell = document.querySelector(`.grid-cell[data-x="${ax}"][data-y="${ay}"]`);
            if (cell) cell.classList.add('preview-bomb-adj');
          }
        });
      } else if (this.armeSelectionnee === 'bombe_ligne_colonne') {
        for (let i = 0; i < t; i++) {
          const rowCell = document.querySelector(`.grid-cell[data-x="${i}"][data-y="${gy}"]`);
          if (rowCell) rowCell.classList.add('preview-laser-line');
          const colCell = document.querySelector(`.grid-cell[data-x="${gx}"][data-y="${i}"]`);
          if (colCell) colCell.classList.add('preview-laser-line');
        }
        const centerCell = document.querySelector(`.grid-cell[data-x="${gx}"][data-y="${gy}"]`);
        if (centerCell) {
          centerCell.classList.remove('preview-laser-line');
          centerCell.classList.add('preview-laser-center');
        }
      }
    }
  }

  async handleCellClick(x, y, cellEl) {
    if (!this.partie || this.partie.fini) return;

    const key = `${x},${y}`;

    // Si une arme spéciale du shop est armée
    if (this.armeSelectionnee) {
      const arme = this.armeSelectionnee;
      this.deselectionnerArme();

      try {
        const res = await fetch('/api/shop/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: arme, x, y })
        });

        if (!res.ok) {
          const err = await res.json();
          this.logTerminal(`> Erreur : ${err.detail}`, 'log-miss');
          return;
        }

        const data = await res.json();
        this.partie = data.partie;
        const lettres = "ABCDEFGH";
        const coordStr = `${lettres[x]}${y + 1}`;

        // Screen Shake sur la grille
        this.dom.gridContainer.classList.add('screen-shake');
        setTimeout(() => this.dom.gridContainer.classList.remove('screen-shake'), 450);

        if (arme === 'scan') {
          this.audio.play('radar', 1200);
          const scanRes = data.resultat;
          if (scanRes.type === 'balayage') {
            this.logTerminal(`> 📡 SCAN RADAR (${coordStr}) : ${scanRes.compteur} véhicule(s) dans la zone 3×3.`, 'log-radar');
            this.dom.reconLast.textContent = `SCAN (${coordStr}) : ${scanRes.compteur} signature(s)`;
          } else {
            this.logTerminal(`> 📡 SCAN RADAR (${coordStr}) : CONTACT DIRECT CONFIRMÉ !`, 'log-radar');
            this.dom.reconLast.textContent = `SCAN : CONTACT DIRECT (${coordStr}) !`;
          }
          this.applyRadarVisuals(scanRes);
        } else {
          // Détonation de bombe
          if (arme === 'bombe_croix') {
            this.audio.play('bombe', 800);
            this.logTerminal(`> 💣 BOMBE EN CROIX (${coordStr}) : Déflagration sur 5 cases adjacentes !`, 'log-hit');
            this.dom.reconLast.textContent = `💣 IMPACT CROIX SUR ${coordStr} !`;
          } else {
            this.audio.play('laser', 500);
            setTimeout(() => this.audio.play('bombe', 800), 100);
            this.logTerminal(`> ⚡ FRAPPE ORBITALE (${coordStr}) : Ligne ${y + 1} & Colonne ${lettres[x]} pulvérisées !`, 'log-wreck');
            this.dom.reconLast.textContent = `⚡ FRAPPE ORBITALE EN LIGNE ${y + 1} & COL ${lettres[x]} !`;
          }

          // Traitement visuel de chaque impact
          const impacts = data.resultat.impacts || [];
          let nbHits = 0;
          let nbWrecks = 0;

          impacts.forEach(imp => {
            const cx = imp.x, cy = imp.y;
            const cEl = document.querySelector(`.grid-cell[data-x="${cx}"][data-y="${cy}"]`);
            if (!cEl) return;

            cEl.classList.add('cell-blast');
            setTimeout(() => cEl.classList.remove('cell-blast'), 500);

            const rect = cEl.getBoundingClientRect();
            const px = rect.left + rect.width / 2;
            const py = rect.top + rect.height / 2;

            if (imp.resultat === 'vide') {
              cEl.className = 'grid-cell state-vide flashed';
            } else if (imp.resultat === 'touche') {
              cEl.className = 'grid-cell state-touche flashed';
              this.fx.addSparks(px, py, 18);
              nbHits++;
            } else if (imp.resultat === 'epave') {
              cEl.className = 'grid-cell state-epave flashed';
              this.fx.addSparks(px, py, 28);
              this.fx.addSmoke(px, py, 10);
              nbWrecks++;
              if (imp.cases) {
                for (const [vx, vy] of imp.cases) {
                  const epEl = document.querySelector(`.grid-cell[data-x="${vx}"][data-y="${vy}"]`);
                  if (epEl) epEl.className = 'grid-cell state-epave flashed';
                }
              }
            }
          });

          if (nbWrecks > 0) {
            this.logTerminal(`> ☠ ${nbWrecks} véhicule(s) neutralisé(s) lors de cette frappe !`, 'log-wreck');
          }
        }

        this.updateHUD();
        this.renderTargets();
        this.updateShopUI();

        if (data.partie.fini) {
          this.declencherVictoire(data.nouveau_record);
        }
      } catch (err) {
        console.error(err);
      }
      return;
    }

    // Tir flash classique
    if (this.partie.cases_flashees[key]) return;

    try {
      const res = await fetch('/api/flash', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y })
      });

      if (!res.ok) return;
      const data = await res.json();
      this.partie = data.partie;

      const resultat = data.resultat;
      const lettres = "ABCDEFGH";
      const coordStr = `${lettres[x]}${y + 1}`;

      const rect = cellEl.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;

      if (resultat.resultat === 'vide') {
        cellEl.className = 'grid-cell state-vide flashed';
        this.audio.play('rate', 400);
        this.logTerminal(`> Tir ${coordStr} : Place vide. 0 contact.`, 'log-miss');
        this.dom.reconLast.textContent = `${coordStr} — Place vide`;
      } else if (resultat.resultat === 'touche') {
        cellEl.className = 'grid-cell state-touche flashed';
        this.audio.play(resultat.vehicule, 600);
        this.fx.addSparks(cx, cy, 22);
        this.logTerminal(`> Tir ${coordStr} : Cible ${resultat.vehicule} TOUCHÉE !`, 'log-hit');
        this.dom.reconLast.textContent = `IMPACT DIRECT SUR ${resultat.vehicule} !`;
      } else if (resultat.resultat === 'epave') {
        this.audio.play('epave', 800);
        this.fx.addSparks(cx, cy, 35);
        this.fx.addSmoke(cx, cy, 14);
        this.logTerminal(`> Tir ${coordStr} : ${resultat.vehicule} TOTALEMENT DÉTRUIT (ÉPAVE) !`, 'log-wreck');
        this.dom.reconLast.textContent = `ÉPAVE : ${resultat.vehicule} NEUTRALISÉ !`;

        for (const [vx, vy] of resultat.cases) {
          const c = document.querySelector(`.grid-cell[data-x="${vx}"][data-y="${vy}"]`);
          if (c) c.className = 'grid-cell state-epave flashed';
        }
      }

      this.updateHUD();
      this.renderTargets();
      this.updateShopUI();

      if (data.partie.fini) {
        this.declencherVictoire(data.nouveau_record);
      }
    } catch (e) {
      console.error(e);
    }
  }

  applyRadarVisuals(info) {
    if (info.type === 'balayage') {
      info.zone.forEach(([zx, zy]) => {
        const c = document.querySelector(`.grid-cell[data-x="${zx}"][data-y="${zy}"]`);
        if (c) c.classList.add('radar-echo');
      });
      const centerEl = document.querySelector(`.grid-cell[data-x="${info.centre[0]}"][data-y="${info.centre[1]}"]`);
      if (centerEl) {
        centerEl.classList.add('radar-center-badge');
        centerEl.setAttribute('data-radar-count', info.compteur);
      }
    } else {
      for (const key in info.adjacents) {
        const [ax, ay] = key.split(',').map(Number);
        const occupe = info.adjacents[key];
        const c = document.querySelector(`.grid-cell[data-x="${ax}"][data-y="${ay}"]`);
        if (c) {
          c.classList.add('radar-echo');
          if (occupe) c.classList.add('echo-direct');
        }
      }
    }
  }

  afficherGainOr(gain) {
    if (!this.dom.goldFloatContainer || gain <= 0) return;
    const el = document.createElement('div');
    el.className = 'gold-float-anim';
    el.textContent = `+${gain} OR`;
    this.dom.goldFloatContainer.appendChild(el);
    setTimeout(() => el.remove(), 1200);
  }

  updateHUD() {
    if (!this.partie) return;

    this.dom.statMode.textContent = this.partie.mode === 'rallye' ? 'RALLYE (5×5)' : 'GRAND PRIX (8×8)';
    if (this.dom.statTour) this.dom.statTour.textContent = this.partie.tour || 1;
    this.dom.statScans.textContent = this.partie.nb_scans;

    const currentGold = this.partie.or || 0;
    if (this.dom.statGold) this.dom.statGold.textContent = currentGold;
    if (this.dom.shopGoldCount) this.dom.shopGoldCount.textContent = currentGold;

    if (currentGold > this.dernierOr) {
      this.afficherGainOr(currentGold - this.dernierOr);
      this.audio.play('coin');
    }
    this.dernierOr = currentGold;

    let totalVehicules = Object.keys(this.partie.vehicules).length;
    let epavesCount = Object.values(this.partie.vehicules).filter(v => v.epave).length;
    this.dom.statCibles.textContent = `${epavesCount}/${totalVehicules}`;
  }

  renderTargets() {
    if (!this.partie) return;
    const container = this.dom.targetList;
    container.innerHTML = '';

    Object.values(this.partie.vehicules).forEach(v => {
      const card = document.createElement('div');
      card.className = `target-card ${v.epave ? 'wrecked' : ''}`;

      let badgeClass = 'stealth';
      let badgeText = 'EN FUITE';
      if (v.epave) {
        badgeClass = 'wreck';
        badgeText = 'ÉPAVE';
      } else if (v.touches > 0) {
        badgeClass = 'hit';
        badgeText = `${v.touches}/${v.taille} TOUCHÉ`;
      }

      let pipsHtml = '';
      for (let i = 0; i < v.taille; i++) {
        let pipClass = 'active';
        if (v.epave) {
          pipClass = 'wrecked';
        } else if (i < v.touches) {
          pipClass = 'damaged';
        }
        pipsHtml += `<div class="health-pip ${pipClass}"></div>`;
      }

      card.innerHTML = `
        <div class="target-card-top">
          <span class="target-name">${v.nom}</span>
          <span class="target-badge ${badgeClass}">${badgeText}</span>
        </div>
        <div class="health-pip-bar">
          ${pipsHtml}
        </div>
      `;

      container.appendChild(card);
    });
  }

  updateShopUI() {
    if (!this.partie) return;
    const isGrandPrix = this.partie.mode === 'grand_prix';

    if (!isGrandPrix) {
      if (this.dom.shopItemsList) this.dom.shopItemsList.style.display = 'none';
      if (this.dom.shopRallyeNotice) this.dom.shopRallyeNotice.classList.remove('hidden');
      if (this.dom.shopActiveBanner) this.dom.shopActiveBanner.classList.add('hidden');
      return;
    }

    if (this.dom.shopItemsList) this.dom.shopItemsList.style.display = 'flex';
    if (this.dom.shopRallyeNotice) this.dom.shopRallyeNotice.classList.add('hidden');

    const currentOr = this.partie.or || 0;
    const prixMap = {
      scan: 20,
      bombe_croix: 40,
      bombe_ligne_colonne: 80
    };

    const labels = {
      scan: 'SCAN RADAR (3×3)',
      bombe_croix: 'BOMBE EN CROIX (5 cases)',
      bombe_ligne_colonne: 'FRAPPE ORBITALE (Ligne + Col)'
    };

    const btns = [
      { el: this.dom.btnShopScan, id: 'scan' },
      { el: this.dom.btnShopBombeCroix, id: 'bombe_croix' },
      { el: this.dom.btnShopBombeLigne, id: 'bombe_ligne_colonne' }
    ];

    btns.forEach(({ el, id }) => {
      if (!el) return;
      const prix = prixMap[id];
      const affordable = currentOr >= prix;
      el.classList.toggle('insufficient', !affordable);
      el.classList.toggle('active', this.armeSelectionnee === id);
    });

    if (this.armeSelectionnee) {
      if (this.dom.shopActiveBanner) this.dom.shopActiveBanner.classList.remove('hidden');
      if (this.dom.shopActiveText) {
        this.dom.shopActiveText.textContent = `ARMÉ : ${labels[this.armeSelectionnee]} — Cliquez sur la grille`;
      }
    } else {
      if (this.dom.shopActiveBanner) this.dom.shopActiveBanner.classList.add('hidden');
    }
  }

  logTerminal(text, cls = '') {
    const p = document.createElement('p');
    if (cls) p.className = cls;
    p.textContent = text;
    this.dom.terminalFeed.appendChild(p);

    // Taille fixe du terminal : conserver exactement les 8 logs les plus récents
    const MAX_LIGNES = 8;
    while (this.dom.terminalFeed.children.length > MAX_LIGNES) {
      this.dom.terminalFeed.removeChild(this.dom.terminalFeed.firstChild);
    }
  }

  declencherVictoire(nouveauRecord) {
    this.audio.play('victoire', 2500);
    this.fx.addConfetti(90);

    this.dom.vicScans.textContent = this.partie.nb_scans;
    this.dom.vicModeName.textContent = this.partie.mode === 'rallye' ? 'Rallye Urbain (5×5)' : 'Grand Prix (8×8)';

    const t = this.partie.taille;
    const scans = this.partie.nb_scans;
    let rank = 'RANG B';
    if (scans <= (t === 5 ? 12 : 28)) rank = 'RANG S (LÉGENDAIRE)';
    else if (scans <= (t === 5 ? 16 : 38)) rank = 'RANG A (VÉTÉRAN)';
    this.dom.vicRank.textContent = rank;

    if (nouveauRecord) {
      this.dom.vicRecordAlert.classList.remove('hidden');
      this.chargerRecords();
    } else {
      this.dom.vicRecordAlert.classList.add('hidden');
    }

    setTimeout(() => {
      this.dom.modalVictoire.classList.add('active');
    }, 600);
  }
}

// Démarrage de l'application
window.addEventListener('DOMContentLoaded', () => {
  window.app = new GameApp();
});
