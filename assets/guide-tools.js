/* Progressive enhancement: static content and source links work without JS. */
document.querySelectorAll('[data-checklist]').forEach((box) => {
  const inputs = [...box.querySelectorAll('input[type="checkbox"]')];
  const key = `kakegawa-check-v1-${box.dataset.checklist}`;
  let storageAvailable = true;
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    if (Array.isArray(saved)) inputs.forEach(i => { i.checked = saved.includes(i.value); });
  } catch { storageAvailable = false; }
  function update(save = false) {
    const selected = inputs.filter(i => i.checked).map(i => i.value);
    if (save && storageAvailable) {
      try { localStorage.setItem(key, JSON.stringify(selected)); }
      catch { storageAvailable = false; }
    }
    box.querySelector('.check-progress').textContent = `${inputs.length}項目中${selected.length}項目を確認済み${storageAvailable ? '' : '（このブラウザーでは保存できません）'}`;
  }
  inputs.forEach(i => i.addEventListener('change', () => update(true)));
  box.querySelector('.check-reset').addEventListener('click', () => {
    inputs.forEach(i => { i.checked = false; });
    try { localStorage.removeItem(key); } catch { storageAvailable = false; }
    update();
  });
  update();
});
const query = document.querySelector('#place-query');
const group = document.querySelector('#place-group');
if (query && group) {
  query.closest('.directory-controls').hidden = false;
  const cards = [...document.querySelectorAll('.place-card[data-name]')];
  function filter() {
    const term = query.value.normalize('NFKC').trim().toLocaleLowerCase('ja');
    let count = 0;
    cards.forEach(card => {
      const match = (!group.value || card.dataset.group === group.value) &&
        card.dataset.name.normalize('NFKC').toLocaleLowerCase('ja').includes(term);
      card.hidden = !match;
      if (match) count++;
    });
    document.querySelector('#place-count').textContent = `${cards.length}件中${count}件を表示${count === 0 ? '。言葉や分野を変えて探してください。' : ''}`;
  }
  query.addEventListener('input', filter);
  group.addEventListener('change', filter);
  filter();
}
