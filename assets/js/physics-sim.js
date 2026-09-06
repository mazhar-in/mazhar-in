/**
 * MAZHAR.IN - Interactive Physics Canvas Engine
 * Demonstrates: Non-linear Pendulum / Rotational Dynamics with Phase Tracking
 */

(function () {
  'use strict';

  const canvas = document.getElementById('physicsCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height, dpr;

  // Physical State Variables
  let theta = Math.PI / 3.2;    // Current angle (rad)
  let omega = 0.0;             // Angular velocity (rad/s)
  let alpha = 0.0;             // Angular acceleration (rad/s^2)
  const length = 110;          // Pendulum rod length in pixels
  const g = 9.81;              // Gravity constant
  const damping = 0.996;       // Air resistance damping factor
  const bobRadius = 14;

  // Interaction State
  let isDragging = false;
  let isPaused = false;
  let trail = [];
  const maxTrail = 40;

  // Resize and DPI scaling
  function resize() {
    dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    width = rect.width;
    height = rect.height;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
  }

  window.addEventListener('resize', resize);
  resize();

  // Pivot coordinates
  function getPivot() {
    return { x: width / 2, y: 35 };
  }

  function getBobPos() {
    const p = getPivot();
    return {
      x: p.x + length * Math.sin(theta),
      y: p.y + length * Math.cos(theta)
    };
  }

  // Pointer Handling for Dragging Bob
  function getEventCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  }

  function onPointerDown(e) {
    const coords = getEventCoords(e);
    const bob = getBobPos();
    const dist = Math.hypot(coords.x - bob.x, coords.y - bob.y);
    if (dist < bobRadius * 2) {
      isDragging = true;
      omega = 0;
    }
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const coords = getEventCoords(e);
    const pivot = getPivot();
    const dx = coords.x - pivot.x;
    const dy = coords.y - pivot.y;
    theta = Math.atan2(dx, dy);
    omega = 0;
  }

  function onPointerUp() {
    isDragging = false;
  }

  canvas.addEventListener('mousedown', onPointerDown);
  window.addEventListener('mousemove', onPointerMove);
  window.addEventListener('mouseup', onPointerUp);

  canvas.addEventListener('touchstart', onPointerDown, { passive: true });
  window.addEventListener('touchmove', onPointerMove, { passive: true });
  window.addEventListener('touchend', onPointerUp);

  // External Controls
  window.physicsSim = {
    perturb() {
      omega += (Math.random() > 0.5 ? 1 : -1) * (1.2 + Math.random() * 0.8);
    },
    reset() {
      theta = Math.PI / 3.5;
      omega = 0;
      alpha = 0;
      trail = [];
    },
    togglePause() {
      isPaused = !isPaused;
      const pauseBtn = document.getElementById('simToggleBtn');
      if (pauseBtn) pauseBtn.innerText = isPaused ? 'Resume' : 'Pause';
    }
  };

  // Connect Buttons
  const perturbBtn = document.getElementById('simPerturbBtn');
  if (perturbBtn) {
    perturbBtn.addEventListener('click', () => window.physicsSim.perturb());
  }
  const resetBtn = document.getElementById('simResetBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => window.physicsSim.reset());
  }

  // Animation Loop (Verlet / Euler Numerical Integration)
  let lastTime = performance.now();

  function animate(now) {
    requestAnimationFrame(animate);

    const dt = Math.min((now - lastTime) / 1000, 0.05); // cap dt to prevent tunneling
    lastTime = now;

    if (!isPaused && !isDragging) {
      // Equation of motion: alpha = - (g / L) * sin(theta)
      alpha = - (g * 12 / length) * Math.sin(theta);
      omega += alpha * dt * 15;
      omega *= damping;
      theta += omega * dt * 15;
    }

    // Clear Canvas
    ctx.clearRect(0, 0, width, height);

    const pivot = getPivot();
    const bob = getBobPos();

    // Store trail points
    if (!isPaused) {
      trail.push({ x: bob.x, y: bob.y });
      if (trail.length > maxTrail) trail.shift();
    }

    // 1. Draw Subtle Grid Lines & Equilibrium Guide
    ctx.save();
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.12)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(pivot.x, pivot.y);
    ctx.lineTo(pivot.x, pivot.y + length + 25);
    ctx.stroke();
    ctx.restore();

    // 2. Draw Motion Path / Trail
    if (trail.length > 1) {
      ctx.save();
      for (let i = 1; i < trail.length; i++) {
        const alpha = i / trail.length;
        ctx.beginPath();
        ctx.moveTo(trail[i - 1].x, trail[i - 1].y);
        ctx.lineTo(trail[i].x, trail[i].y);
        ctx.strokeStyle = `rgba(56, 189, 248, ${alpha * 0.4})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      ctx.restore();
    }

    // 3. Draw Rod
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(pivot.x, pivot.y);
    ctx.lineTo(bob.x, bob.y);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // 4. Draw Pivot
    ctx.save();
    ctx.beginPath();
    ctx.arc(pivot.x, pivot.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#38bdf8';
    ctx.fill();
    ctx.restore();

    // 5. Draw Velocity Vector Indicator (Tangent)
    const velMagnitude = omega * 18;
    const tangentAngle = theta;
    const vx = -velMagnitude * Math.cos(tangentAngle);
    const vy = velMagnitude * Math.sin(tangentAngle);

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(bob.x, bob.y);
    ctx.lineTo(bob.x + vx, bob.y + vy);
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    // 6. Draw Pendulum Bob (Glow + Sphere)
    ctx.save();
    const gradient = ctx.createRadialGradient(bob.x - 3, bob.y - 3, 2, bob.x, bob.y, bobRadius);
    gradient.addColorStop(0, '#7dd3fc');
    gradient.addColorStop(0.6, '#0284c7');
    gradient.addColorStop(1, '#0369a1');

    ctx.shadowColor = 'rgba(56, 189, 248, 0.5)';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.arc(bob.x, bob.y, bobRadius, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.restore();

    // 7. Telemetry HUD (Angle, Angular Velocity, Restoring Torque)
    ctx.save();
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(148, 163, 184, 0.85)';
    const deg = (theta * 180 / Math.PI).toFixed(1);
    const omegaVal = omega.toFixed(2);
    const tauVal = (-Math.sin(theta)).toFixed(2);
    ctx.fillText(`θ: ${deg}°`, 12, height - 28);
    ctx.fillText(`ω: ${omegaVal} rad/s`, 12, height - 14);
    ctx.fillText(`τ: ${tauVal} N·m`, width - 85, height - 14);
    ctx.restore();
  }

  requestAnimationFrame(animate);
})();
