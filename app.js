'use strict';

(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const EMAIL = 'zhaofeng_du@bit.edu.cn';
  const LANGUAGE_KEY = 'zhaofeng-language';
  const languageToggle = $('#language-toggle');
  let language = 'zh';
  let toastTimer;
  const labels = {
    zh: {
      copy: '复制邮箱', copied: '邮箱已复制',
      pauseScene: '暂停动画', resumeScene: '继续动画',
      play: '播放《四相》', pause: '暂停播放', loading: '取消加载', retry: '重新播放',
      audioLoading: '正在加载歌曲，点击按钮可取消。',
      audioError: '歌曲未能开始播放。请重试，或在网易云音乐收听。',
      audioNetwork: '音乐连接失败。请检查网络后重试，或打开网易云音乐。',
      audioOffline: '当前网络不可用，连接网络后可重新播放。',
      audioSource: '网易云音源无法加载。请重试，或打开网易云音乐。',
      audioDecode: '浏览器未能解码音频。可通过网易云音乐收听。',
      audioBlocked: '浏览器限制了音频播放。请再次点击，或在浏览器中打开本站。',
      audioTimeout: '歌曲加载超时。请重试，或通过网易云音乐收听。',
      audioPlaying: '正在播放痛仰《四相》', audioPaused: '播放已暂停',
      platform: '实物平台', imageAlt: '自建无人机实物平台'
    },
    en: {
      copy: 'Copy email', copied: 'Email copied',
      pauseScene: 'Pause animation', resumeScene: 'Resume animation',
      play: 'Play 四相', pause: 'Pause music', loading: 'Cancel loading', retry: 'Retry playback',
      audioLoading: 'Loading the song. Press the button to cancel.',
      audioError: 'The song could not start. Retry or listen on NetEase Music.',
      audioNetwork: 'The music connection failed. Check your connection and retry, or open NetEase Music.',
      audioOffline: 'You are offline. Reconnect to retry playback.',
      audioSource: 'The NetEase audio source could not load. Retry or open NetEase Music.',
      audioDecode: 'The browser could not decode the audio. Listen on NetEase Music instead.',
      audioBlocked: 'The browser blocked playback. Press play again, or open this site in a browser.',
      audioTimeout: 'The song timed out. Retry or listen on NetEase Music.',
      audioPlaying: 'Playing 四相 by Miserable Faith', audioPaused: 'Music paused',
      platform: 'UAV platform', imageAlt: 'Custom-built UAV platform'
    }
  };
  const t = (key) => labels[language][key];
  const translated = $$('[data-en]');
  translated.forEach((element) => { element.dataset.zh = element.innerHTML; });

  function notify(message) {
    const toast = $('#toast');
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('show');
    toastTimer = setTimeout(() => toast.classList.remove('show'), 4000);
  }

  function setLanguage(value) {
    language = value === 'en' ? 'en' : 'zh';
    document.documentElement.lang = language === 'en' ? 'en' : 'zh-CN';
    translated.forEach((element) => { element.innerHTML = element.dataset[language]; });
    languageToggle.innerHTML = `${language === 'zh' ? 'EN' : '中文'} <span aria-hidden="true">↔</span>`;
    languageToggle.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换为中文');
    document.title = language === 'zh' ? '杜兆丰 Zhaofeng Du | 无人机目标跟踪' : 'Zhaofeng Du (杜兆丰) | UAV Target Tracking';
    try { localStorage.setItem(LANGUAGE_KEY, language); } catch { /* Storage can be disabled for local files. */ }
    $('#copy-label').textContent = t('copy');
    updateSceneLabels();
    updateMusicUI();
    if (platformDialog.open) updatePlatform();
  }
  languageToggle.addEventListener('click', () => setLanguage(language === 'zh' ? 'en' : 'zh'));
  $('#current-year').textContent = new Date().getFullYear();

  const nav = $('#main-nav');
  const menu = $('#menu-toggle');
  function closeMenu() {
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });
  function setActiveLink(id) {
    $$('.main-nav a').forEach((link) => {
      const active = link.hash === '#' + id;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  $$('.main-nav a').forEach((link) => link.addEventListener('click', () => {
    closeMenu();
    setActiveLink(link.hash.slice(1));
  }));
  document.addEventListener('click', (event) => {
    if (nav.classList.contains('open') && !event.target.closest('.site-header')) closeMenu();
  });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeMenu(); });
  if ('IntersectionObserver' in window) {
    const sections = $$('main section[id]');
    const visible = new Map();
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => visible.set(entry.target.id, entry.isIntersecting));
      const active = sections.find((section) => visible.get(section.id));
      if (active) setActiveLink(active.id);
    }, { rootMargin: '-12% 0px -65% 0px', threshold: 0 });
    sections.forEach((section) => sectionObserver.observe(section));
  }

  // The photographs are the user's real platforms, extracted from the supplied CV.
  const platformDialog = $('#platform-dialog');
  const platformImages = ['assets/uav-platform-01.png', 'assets/uav-platform-02.png', 'assets/uav-platform-03.png'];
  let platformIndex = 0;
  function updatePlatform() {
    const number = String(platformIndex + 1).padStart(2, '0');
    $('#platform-dialog-title').textContent = t('platform') + ' ' + number;
    $('#platform-large-image').src = platformImages[platformIndex];
    $('#platform-large-image').alt = t('imageAlt') + ' ' + number;
    $('#platform-count').textContent = (platformIndex + 1) + ' / ' + platformImages.length;
  }
  function changePlatform(step) {
    platformIndex = (platformIndex + step + platformImages.length) % platformImages.length;
    updatePlatform();
  }
  $$('[data-platform]').forEach((button) => button.addEventListener('click', () => {
    platformIndex = Number(button.dataset.platform);
    updatePlatform();
    platformDialog.showModal();
    document.body.classList.add('dialog-open');
  }));
  $('#platform-close').addEventListener('click', () => platformDialog.close());
  $('#platform-prev').addEventListener('click', () => changePlatform(-1));
  $('#platform-next').addEventListener('click', () => changePlatform(1));
  platformDialog.addEventListener('close', () => document.body.classList.remove('dialog-open'));
  platformDialog.addEventListener('click', (event) => {
    const rect = platformDialog.getBoundingClientRect();
    if (event.target === platformDialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) platformDialog.close();
  });
  platformDialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') { event.preventDefault(); changePlatform(1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); changePlatform(-1); }
  });

  // A conceptual illustration, not a replay of experimental tracking measurements.
  const scene = $('#tracking-scene');
  const road = $('#road-path');
  const roadLength = road.getTotalLength();
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let scenePaused = reducedMotion.matches;
  let sceneVisible = true;
  let sceneMode = 'tracking';
  let elapsed = 0;
  let previousTime = 0;
  let frameRequest = null;
  const drone = { x: 190, y: 205 };
  const estimate = { x: 265, y: 370 };
  const trail = [];
  let trailElapsed = 0;

  function updateSceneLabels() {
    $('#motion-toggle').setAttribute('aria-pressed', String(scenePaused));
    $('#motion-toggle').setAttribute('aria-label', t(scenePaused ? 'resumeScene' : 'pauseScene'));
    $('#motion-toggle').firstElementChild.textContent = scenePaused ? '▶' : 'Ⅱ';
  }
  function drawScene(dt) {
    const progress = .49 + .30 * Math.sin(elapsed * .14 - .6);
    const point = road.getPointAtLength(progress * roadLength);
    const ahead = road.getPointAtLength(Math.min(roadLength, progress * roadLength + 2));
    const direction = Math.cos(elapsed * .14 - .6) * (ahead.x - point.x) >= 0 ? 1 : -1;
    const y = point.y - 13;
    $('#motorcycle').setAttribute('transform', `translate(${point.x.toFixed(2)} ${y.toFixed(2)}) scale(${direction} 1)`);
    const smooth = dt ? 1 - Math.exp(-dt * 7) : 1;
    estimate.x += (point.x - estimate.x) * smooth;
    estimate.y += (y - estimate.y) * smooth;
    const lag = dt ? 1 - Math.exp(-dt * 2) : 1;
    drone.x += (estimate.x - 73 - drone.x) * lag;
    drone.y += (estimate.y - 164 - drone.y) * lag;
    const bob = Math.sin(elapsed * 2) * 3;
    $('#uav').setAttribute('transform', `translate(${drone.x.toFixed(2)} ${(drone.y + bob).toFixed(2)})`);
    $('#tracking-beam').setAttribute('d', `M${drone.x},${drone.y + 12 + bob} L${estimate.x - 38},${estimate.y + 11} L${estimate.x + 38},${estimate.y + 11} Z`);
    $('#target-box').setAttribute('transform', `translate(${estimate.x.toFixed(2)} ${estimate.y.toFixed(2)})`);
    const cooperative = sceneMode === 'cooperation';
    $('#uav-second').setAttribute('visibility', cooperative ? 'visible' : 'hidden');
    $('#second-beam').setAttribute('visibility', cooperative ? 'visible' : 'hidden');
    if (cooperative) {
      const secondX = Math.min(586, estimate.x + 93);
      const secondY = estimate.y - 189 - bob;
      $('#uav-second').setAttribute('transform', `translate(${secondX.toFixed(2)} ${secondY.toFixed(2)})`);
      $('#second-beam').setAttribute('d', `M${secondX},${secondY + 12} L${estimate.x},${estimate.y - 6}`);
    }
    trailElapsed += dt;
    if (trailElapsed > .14) {
      trail.push({x: point.x, y: point.y});
      if (trail.length > 50) trail.shift();
      $('#tracking-trail').setAttribute('d', trail.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' '));
      trailElapsed = 0;
    }
  }
  function animateScene(time) {
    frameRequest = null;
    if (scenePaused || !sceneVisible || document.hidden) { previousTime = 0; return; }
    const dt = previousTime ? Math.min((time - previousTime) / 1000, .05) : 0;
    previousTime = time;
    elapsed += dt;
    drawScene(dt);
    frameRequest = requestAnimationFrame(animateScene);
  }
  function syncScene() {
    if (frameRequest !== null) cancelAnimationFrame(frameRequest);
    frameRequest = null;
    previousTime = 0;
    if (!scenePaused && sceneVisible && !document.hidden) frameRequest = requestAnimationFrame(animateScene);
  }
  $('#motion-toggle').addEventListener('click', () => {
    scenePaused = !scenePaused;
    updateSceneLabels();
    syncScene();
  });
  $$('[data-mode]').forEach((button) => button.addEventListener('click', () => {
    sceneMode = button.dataset.mode;
    $$('[data-mode]').forEach((item) => {
      const active = button === item;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    drawScene(0);
    updateSceneLabels();
  }));
  reducedMotion.addEventListener('change', (event) => {
    scenePaused = event.matches;
    updateSceneLabels();
    syncScene();
  });
  drawScene(0);
  if ('IntersectionObserver' in window) {
    const sceneObserver = new IntersectionObserver(([entry]) => {
      sceneVisible = entry.isIntersecting;
      syncScene();
    }, {threshold: .01});
    sceneObserver.observe(scene);
  }
  syncScene();

  // Stream through NetEase's public external-player endpoint; do not cache its CDN redirect.
  const player = $('#music-player');
  const musicButton = $('#music-toggle');
  const progressControl = $('#music-progress');
  const audioStatus = $('#audio-status');
  const audioSource = player.getAttribute('src');
  const AUDIO_LOAD_TIMEOUT = 12000;
  let musicState = 'idle';
  let musicError = '';
  let playbackRequest = 0;
  let audioLoadTimer = null;
  const formatTime = (seconds) => {
    const safe = Number.isFinite(seconds) ? Math.max(0, Math.floor(seconds)) : 0;
    return Math.floor(safe / 60) + ':' + String(safe % 60).padStart(2, '0');
  };
  function updateMusicUI() {
    const playing = musicState === 'playing';
    const loading = musicState === 'loading';
    const failed = musicState === 'error';
    musicButton.setAttribute('aria-pressed', String(playing));
    musicButton.setAttribute('aria-busy', String(loading));
    $('#music-label').textContent = t(loading ? 'loading' : (failed ? 'retry' : (playing ? 'pause' : 'play')));
    musicButton.querySelector('.play-symbol').textContent = loading ? '×' : (playing ? 'Ⅱ' : '▶');
    audioStatus.classList.toggle('sr-only', !failed);
    audioStatus.classList.toggle('music-error', failed);
    audioStatus.textContent = failed ? t(musicError) : (loading ? t('audioLoading') : (playing ? t('audioPlaying') : (musicState === 'paused' ? t('audioPaused') : '')));
  }
  function updateMusicTime() {
    const hasDuration = musicState !== 'error' && Number.isFinite(player.duration) && player.duration > 0;
    $('#music-time').textContent = formatTime(player.currentTime) + (hasDuration ? ' / ' + formatTime(player.duration) : '');
    progressControl.disabled = !hasDuration;
    progressControl.value = hasDuration ? String(player.currentTime / player.duration * 100) : '0';
    progressControl.setAttribute('aria-valuetext', formatTime(player.currentTime));
  }
  function clearAudioTimeout() {
    clearTimeout(audioLoadTimer);
    audioLoadTimer = null;
  }
  function resetAudioSource() {
    // Aborts a pending request and clears a fatal MediaError before the next click.
    player.removeAttribute('src');
    player.load();
  }
  function stopMusic() {
    const wasLoading = musicState === 'loading';
    playbackRequest += 1;
    clearAudioTimeout();
    musicState = 'paused';
    player.pause();
    if (wasLoading) resetAudioSource();
    updateMusicUI();
    updateMusicTime();
  }
  function failMusic(reason) {
    playbackRequest += 1;
    clearAudioTimeout();
    musicState = 'error';
    musicError = reason;
    player.pause();
    resetAudioSource();
    updateMusicUI();
    updateMusicTime();
  }
  function audioErrorLabel(error) {
    if (!navigator.onLine) return 'audioOffline';
    if (error?.name === 'NotAllowedError') return 'audioBlocked';
    if (player.error?.code === 2) return 'audioNetwork';
    if (player.error?.code === 3) return 'audioDecode';
    if (player.error?.code === 4 || error?.name === 'NotSupportedError') return 'audioSource';
    return 'audioError';
  }
  function startAudioTimeout() {
    if (audioLoadTimer !== null) return;
    const request = playbackRequest;
    audioLoadTimer = setTimeout(() => {
      if (request === playbackRequest && musicState === 'loading') failMusic('audioTimeout');
    }, AUDIO_LOAD_TIMEOUT);
  }
  function markMusicPlaying() {
    if (player.paused || !['loading', 'playing'].includes(musicState)) return;
    clearAudioTimeout();
    musicState = 'playing';
    musicError = '';
    updateMusicUI();
  }
  musicButton.addEventListener('click', async () => {
    if (['loading', 'playing'].includes(musicState)) { stopMusic(); return; }
    const request = ++playbackRequest;
    musicState = 'loading';
    musicError = '';
    if (!player.getAttribute('src') || player.error) {
      player.src = audioSource;
      player.load();
    }
    updateMusicUI();
    startAudioTimeout();
    try {
      // Call play directly within the click, preserving browser user activation.
      await player.play();
      if (request === playbackRequest) markMusicPlaying();
    } catch (error) {
      // Pausing, cancelling, or leaving the page rejects a pending play promise.
      if (request === playbackRequest) failMusic(audioErrorLabel(error));
    }
  });
  player.addEventListener('playing', markMusicPlaying);
  player.addEventListener('waiting', () => {
    if (player.paused || !['playing', 'loading'].includes(musicState)) return;
    musicState = 'loading';
    startAudioTimeout();
    updateMusicUI();
  });
  player.addEventListener('pause', () => {
    if (player.paused && ['playing', 'loading'].includes(musicState)) stopMusic();
  });
  player.addEventListener('ended', () => {
    stopMusic();
    player.currentTime = 0;
    updateMusicTime();
  });
  player.addEventListener('loadedmetadata', updateMusicTime);
  player.addEventListener('emptied', updateMusicTime);
  player.addEventListener('timeupdate', updateMusicTime);
  player.addEventListener('error', () => {
    if (player.error && musicState !== 'error') failMusic(audioErrorLabel());
  });
  progressControl.addEventListener('input', () => {
    if (Number.isFinite(player.duration) && player.duration > 0) {
      player.currentTime = Number(progressControl.value) / 100 * player.duration;
      updateMusicTime();
    }
  });
  document.addEventListener('visibilitychange', () => {
    syncScene();
    if (document.hidden && ['loading', 'playing'].includes(musicState)) stopMusic();
  });
  window.addEventListener('pagehide', () => {
    if (['loading', 'playing'].includes(musicState)) stopMusic();
  });

  $('#copy-email').addEventListener('click', async () => {
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(EMAIL);
      else {
        const field = document.createElement('textarea');
        field.value = EMAIL;
        field.setAttribute('readonly', '');
        field.style.cssText = 'position:fixed;opacity:0';
        document.body.append(field);
        field.select();
        const success = document.execCommand('copy');
        field.remove();
        if (!success) throw new Error('Clipboard unavailable');
      }
      $('#copy-label').textContent = t('copied');
      notify(t('copied'));
      setTimeout(() => { $('#copy-label').textContent = t('copy'); }, 2500);
    } catch { notify(EMAIL); }
  });

  let storedLanguage = '';
  try { storedLanguage = localStorage.getItem(LANGUAGE_KEY); } catch { /* Use the default language. */ }
  const queryLanguage = new URLSearchParams(location.search).get('lang');
  setLanguage(queryLanguage || storedLanguage || 'zh');
})();
