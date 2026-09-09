/* School calendar behaviour — reads CALENDAR_DATA and I18N. */

(function () {
    const data = window.CALENDAR_DATA;
    const events = data.events;
    const months = data.months;
    const school = data.school;
    const LANGS = ['uk', 'pl', 'en'];
    const LANG_KEY = school.langStorageKey || 'lyceum_78_lang';

    const TODAY_KEY = (function () {
        const now = new Date();
        return (
            now.getFullYear() +
            '-' +
            String(now.getMonth() + 1).padStart(2, '0') +
            '-' +
            String(now.getDate()).padStart(2, '0')
        );
    })();

    let currentLang = 'uk';
    let currentMonthFocusIdx = 0;
    let activeCategoryFilter = 'all';
    let currentActiveDayKey = null;
    let cellsBound = false;

    function t(key) {
        const pack = window.I18N[currentLang] || window.I18N.uk;
        return pack[key] || window.I18N.uk[key] || key;
    }

    function loc(field) {
        if (field == null) return '';
        if (typeof field === 'string') return field;
        return field[currentLang] || field.uk || field.pl || field.en || '';
    }

    function eventById(id) {
        return events.find(function (e) {
            return e.id === id;
        });
    }

    function eventsOnDate(dateStr) {
        return events.filter(function (ev) {
            if (ev.endDate) {
                return dateStr >= ev.date && dateStr <= ev.endDate;
            }
            return ev.date === dateStr;
        });
    }

    function badgeText(ev, dateStr) {
        if (ev.badgeByDate && ev.badgeByDate[dateStr]) {
            return loc(ev.badgeByDate[dateStr]);
        }
        return loc(ev.badgeShort) || loc(ev.title);
    }

    function monthIndexForDate(dateStr) {
        const year = parseInt(dateStr.slice(0, 4), 10);
        const month = parseInt(dateStr.slice(5, 7), 10);
        return months.findIndex(function (m) {
            return m.year === year && m.month === month;
        });
    }

    function formatDayHeading(dateStr) {
        const parts = dateStr.split('-');
        const month = months.find(function (m) {
            return m.year === parseInt(parts[0], 10) && m.month === parseInt(parts[1], 10);
        });
        const dayNum = parseInt(parts[2], 10);
        return dayNum + ' ' + loc(month ? month.nameGenitive : dateStr);
    }

    function searchBlob(ev) {
        return [
            loc(ev.title),
            ev.officialTitle,
            loc(ev.description),
            loc(ev.grade1Note),
            loc(ev.categoryName),
            loc(ev.badgeShort)
        ].join(' ').toLowerCase();
    }

    function readStoredLang() {
        try {
            const saved = localStorage.getItem(LANG_KEY);
            if (LANGS.indexOf(saved) !== -1) return saved;
        } catch (e) {}

        const systemLanguages =
            navigator.languages && navigator.languages.length
                ? navigator.languages
                : [navigator.language || navigator.userLanguage || 'en'];

        for (let i = 0; i < systemLanguages.length; i++) {
            const language = String(systemLanguages[i]).toLowerCase().split('-')[0];
            if (language === 'uk' || language === 'pl') return language;
            if (language === 'en') return 'en';
        }
        return 'en';
    }

    function setLanguage(lang) {
        if (LANGS.indexOf(lang) === -1) lang = 'uk';
        currentLang = lang;
        try {
            localStorage.setItem(LANG_KEY, lang);
        } catch (e) {}
        applyLanguage();
        const search = document.getElementById('eventSearch');
        if (search && search.value) handleSearch(search.value);
        if (activeCategoryFilter !== 'all') filterByCategory(activeCategoryFilter);
        const modal = document.getElementById('eventModal');
        if (modal && modal.classList.contains('active') && currentActiveDayKey) {
            openDayModal(currentActiveDayKey, formatDayHeading(currentActiveDayKey));
        }
    }

    function applyLanguage() {
        document.documentElement.lang = currentLang;
        document.title = t('docTitle');

        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            el.textContent = t(el.getAttribute('data-i18n'));
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder')));
        });
        document.querySelectorAll('[data-i18n-alt]').forEach(function (el) {
            el.setAttribute('alt', t(el.getAttribute('data-i18n-alt')));
        });

        document.querySelectorAll('.lang-btn').forEach(function (btn) {
            const lang = btn.getAttribute('data-lang');
            const isActive = lang === currentLang;
            const label = t('lang.' + lang);
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-pressed', String(isActive));
            btn.setAttribute('aria-label', label);
            btn.title = label;
        });

        months.forEach(function (m) {
            const section = document.getElementById(m.id);
            if (!section) return;
            const title = section.querySelector('.month-title');
            const sub = section.querySelector('.month-subtitle');
            if (title) title.textContent = loc(m.name);
            if (sub) sub.textContent = currentLang === 'pl' ? m.name.uk : m.name.pl;
        });

        document.querySelectorAll('.agenda-item[data-event-id]').forEach(function (item) {
            const ev = eventById(item.getAttribute('data-event-id'));
            if (!ev) return;
            const dateEl = item.querySelector('.agenda-date');
            const typeEl = item.querySelector('.agenda-type');
            const descEl = item.querySelector('.agenda-desc');
            if (dateEl) dateEl.textContent = loc(ev.dateFormatted);
            if (typeEl) typeEl.textContent = loc(ev.categoryName);
            if (descEl) descEl.textContent = loc(ev.description);
        });

        months.forEach(function (m) {
            const section = document.getElementById(m.id);
            if (!section) return;
            section.querySelectorAll('.day-cell:not(.empty)').forEach(function (cell) {
                const dateStr = cell.getAttribute('data-day-key');
                if (!dateStr) return;
                const dayEvents = eventsOnDate(dateStr);
                const badges = cell.querySelectorAll('.event-badge');
                const used = {};
                badges.forEach(function (badge) {
                    const cls = Array.prototype.find.call(badge.classList, function (c) {
                        return c.indexOf('badge-') === 0;
                    });
                    let ev = dayEvents.find(function (e) {
                        return !used[e.id] && 'badge-' + e.category === cls;
                    });
                    if (!ev) {
                        ev = dayEvents.find(function (e) {
                            return !used[e.id];
                        });
                    }
                    if (!ev) return;
                    used[ev.id] = true;
                    const titleEl = badge.querySelector('.badge-title');
                    const text = badgeText(ev, dateStr);
                    if (titleEl) titleEl.textContent = text;
                    badge.title = loc(ev.title);
                });
                cell.setAttribute('data-search', dayEvents.map(searchBlob).join(' '));
                cell.title = t('cell.openTitle') + ' ' + formatDayHeading(dateStr);
            });
        });

        const focusTitle = document.getElementById('focusMonthTitle');
        if (focusTitle) focusTitle.textContent = loc(months[currentMonthFocusIdx].name);

        renderTodayMarker();
        renderNotesBadges();
        syncStickyOffsets();
    }

    function renderTodayMarker() {
        const cell = document.querySelector('.day-cell[data-day-key="' + TODAY_KEY + '"]');
        if (!cell) return;
        cell.classList.add('is-today');
        const header = cell.querySelector('.day-header');
        if (!header) return;
        let chip = header.querySelector('.today-chip');
        if (!chip) {
            chip = document.createElement('span');
            chip.className = 'today-chip';
            header.appendChild(chip);
        }
        chip.textContent = t('today.label');
    }

    function syncStickyOffsets() {
        const toolbar = document.querySelector('.interactive-toolbar');
        if (!toolbar) return;
        const navTop = Math.round(toolbar.getBoundingClientRect().height) + 16;
        document.documentElement.style.setProperty('--sticky-nav-top', navTop + 'px');
    }

    function isRailLayout() {
        return window.matchMedia('(min-width: 1100px)').matches;
    }

    function stickyStackHeight() {
        // Side rails sit beside the calendar, so only bars stuck to the top steal room.
        return ['.interactive-toolbar', '.nav-container'].reduce(function (total, selector) {
            const el = document.querySelector(selector);
            if (!el || window.getComputedStyle(el).position !== 'sticky') return total;
            return total + el.offsetHeight;
        }, 0);
    }

    function scrollBelowStickyBars(el, behavior) {
        const top = window.scrollY + el.getBoundingClientRect().top - stickyStackHeight() - 30;
        window.scrollTo({ top: Math.max(top, 0), behavior: behavior || 'auto' });
    }

    function scrollToToday() {
        const section = document.getElementById(months[currentMonthFocusIdx].id);
        if (!section) return;
        markNavButton(document.querySelector('.nav-btn[data-month-id="' + section.id + '"]'));
        scrollBelowStickyBars(section.querySelector('.day-cell.is-today') || section);
    }

    function setViewMode(mode) {
        const allBtn = document.getElementById('modeAllBtn');
        const focusBtn = document.getElementById('modeFocusBtn');
        const focusBar = document.getElementById('focusNavBar');
        const navBar = document.querySelector('.nav-container');

        if (mode === 'all') {
            allBtn.classList.add('active');
            focusBtn.classList.remove('active');
            focusBar.style.display = 'none';
            if (navBar) navBar.style.display = 'flex';
            months.forEach(function (m) {
                const el = document.getElementById(m.id);
                if (el) el.style.display = 'block';
            });
        } else {
            focusBtn.classList.add('active');
            allBtn.classList.remove('active');
            focusBar.style.display = 'flex';
            // The side rail stays: hiding it would leave an empty column.
            if (navBar) navBar.style.display = isRailLayout() ? 'flex' : 'none';
            updateFocusMonthDisplay();
        }
    }

    function updateFocusMonthDisplay() {
        months.forEach(function (m, idx) {
            const el = document.getElementById(m.id);
            if (el) {
                el.style.display = idx === currentMonthFocusIdx ? 'block' : 'none';
            }
        });
        document.getElementById('focusMonthTitle').innerText = loc(months[currentMonthFocusIdx].name);
        const currentEl = document.getElementById(months[currentMonthFocusIdx].id);
        if (currentEl) {
            scrollBelowStickyBars(currentEl, 'smooth');
        }
    }

    function prevMonthFocus() {
        if (currentMonthFocusIdx > 0) {
            currentMonthFocusIdx--;
            updateFocusMonthDisplay();
        }
    }

    function nextMonthFocus() {
        if (currentMonthFocusIdx < months.length - 1) {
            currentMonthFocusIdx++;
            updateFocusMonthDisplay();
        }
    }

    function markNavButton(clicked) {
        document.querySelectorAll('.nav-btn').forEach(function (btn) {
            btn.classList.remove('active');
        });
        if (clicked) clicked.classList.add('active');
    }

    function scrollToMonth(id, clicked) {
        const el = document.getElementById(id);
        if (!el) return;
        scrollBelowStickyBars(el, 'smooth');
        markNavButton(clicked);
    }

    function showAllMonths(clicked) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        markNavButton(clicked);
    }

    function handleSearch(query) {
        query = query.trim().toLowerCase();
        document.querySelectorAll('.day-cell').forEach(function (cell) {
            if (cell.classList.contains('empty')) return;
            if (!query) {
                cell.classList.remove('dimmed', 'highlighted');
                return;
            }
            const text = cell.innerText.toLowerCase();
            const title = (cell.getAttribute('title') || '').toLowerCase();
            const extra = (cell.getAttribute('data-search') || '').toLowerCase();
            if (text.includes(query) || title.includes(query) || extra.includes(query)) {
                cell.classList.remove('dimmed');
                cell.classList.add('highlighted');
            } else {
                cell.classList.add('dimmed');
                cell.classList.remove('highlighted');
            }
        });

        document.querySelectorAll('.agenda-item').forEach(function (item) {
            if (!query) {
                item.style.display = 'block';
                return;
            }
            const ev = eventById(item.getAttribute('data-event-id'));
            const blob = (item.innerText + ' ' + (ev ? searchBlob(ev) : '')).toLowerCase();
            item.style.display = blob.includes(query) ? 'block' : 'none';
        });
    }

    function filterByCategory(cat) {
        activeCategoryFilter = cat;
        document.querySelectorAll('.filter-chip').forEach(function (btn) {
            btn.classList.toggle('active', btn.getAttribute('data-cat') === cat);
        });

        document.querySelectorAll('.day-cell').forEach(function (cell) {
            if (cell.classList.contains('empty')) return;
            if (cat === 'all') {
                cell.classList.remove('dimmed', 'highlighted');
                cell.querySelectorAll('.event-badge').forEach(function (b) {
                    b.classList.remove('dimmed');
                });
                return;
            }

            let hasMatchingEvent = false;
            cell.querySelectorAll('.event-badge').forEach(function (b) {
                const cls = b.className;
                let match = false;
                if (cat === 'vacation' && (cls.includes('badge-vacation') || cls.includes('badge-holiday') || cls.includes('badge-off'))) match = true;
                if (cat === 'meeting' && cls.includes('badge-meeting')) match = true;
                if (cat === 'trip' && (cls.includes('badge-trip') || cls.includes('badge-integ'))) match = true;
                if (cat === 'grade' && (cls.includes('badge-grade') || cls.includes('badge-council'))) match = true;

                if (match) {
                    b.classList.remove('dimmed');
                    hasMatchingEvent = true;
                } else {
                    b.classList.add('dimmed');
                }
            });

            if (hasMatchingEvent) {
                cell.classList.remove('dimmed');
                cell.classList.add('highlighted');
            } else {
                cell.classList.add('dimmed');
                cell.classList.remove('highlighted');
            }
        });
    }

    function openDayModal(dateStr, formattedDate) {
        currentActiveDayKey = dateStr;
        const modal = document.getElementById('eventModal');
        const titleEl = document.getElementById('modalDateTitle');
        const container = document.getElementById('modalEventsContainer');
        const noteInput = document.getElementById('modalNoteInput');
        const statusMsg = document.getElementById('noteSavedStatus');
        statusMsg.style.display = 'none';

        titleEl.innerText = formattedDate || formatDayHeading(dateStr);

        const matching = eventsOnDate(dateStr);

        if (matching.length === 0) {
            container.innerHTML =
                '<div class="modal-event-card">' +
                '<div class="modal-event-title">' + t('modal.emptyTitle') + '</div>' +
                '<div class="modal-event-desc">' + t('modal.emptyDesc') + '</div>' +
                '</div>';
        } else {
            container.innerHTML = matching.map(function (ev) {
                const gcalUrl = createGoogleCalendarUrl(ev);
                const officialRow =
                    currentLang === 'pl'
                        ? ''
                        : '<div class="modal-event-pl">' + t('modal.official') + ' ' + ev.officialTitle + '</div>';
                return (
                    '<div class="modal-event-card" data-glean-id="modal-' + ev.id + '">' +
                    '<div class="modal-event-title">' + loc(ev.title) + '</div>' +
                    officialRow +
                    '<div class="modal-event-desc">' +
                    '<div><b>' + t('modal.time') + '</b> ' + loc(ev.time) + '</div>' +
                    '<div><b>' + t('modal.desc') + '</b> ' + loc(ev.description) + '</div>' +
                    '<div><b>' + t('modal.location') + '</b> ' + loc(ev.location) + '</div>' +
                    '</div>' +
                    '<div class="modal-grade1-tip">💡 <b>' + t('modal.grade1') + '</b> ' + loc(ev.grade1Note) + '</div>' +
                    '<div class="modal-actions">' +
                    '<a class="modal-btn" href="' + gcalUrl + '" target="_blank">' + t('modal.gcal') + '</a>' +
                    '<button type="button" class="modal-btn" onclick="downloadSingleEventICS(\'' + ev.id + '\')">' + t('modal.ics') + '</button>' +
                    '</div></div>'
                );
            }).join('');
        }

        const notes = getStoredNotes();
        noteInput.value = notes[dateStr] || '';
        modal.classList.add('active');
    }

    function closeEventModal() {
        document.getElementById('eventModal').classList.remove('active');
    }

    function closeModalOnBackdrop(e) {
        if (e.target.id === 'eventModal') closeEventModal();
    }

    function getStoredNotes() {
        try {
            return JSON.parse(localStorage.getItem(school.notesStorageKey) || '{}');
        } catch (e) {
            return {};
        }
    }

    function saveCurrentDayNote() {
        if (!currentActiveDayKey) return;
        const text = document.getElementById('modalNoteInput').value.trim();
        const notes = getStoredNotes();
        if (text) {
            notes[currentActiveDayKey] = text;
        } else {
            delete notes[currentActiveDayKey];
        }
        try {
            localStorage.setItem(school.notesStorageKey, JSON.stringify(notes));
        } catch (e) {}

        document.getElementById('noteSavedStatus').style.display = 'inline';
        showToast(t('toast.noteSaved'));
        renderNotesBadges();
    }

    function renderNotesBadges() {
        const notes = getStoredNotes();
        document.querySelectorAll('.day-cell').forEach(function (cell) {
            const dayId = cell.getAttribute('data-day-key');
            if (!dayId) return;
            const header = cell.querySelector('.day-header');
            if (!header) return;
            let badge = header.querySelector('.day-note-badge');
            if (notes[dayId]) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'day-note-badge';
                    badge.innerText = '⭐';
                    header.appendChild(badge);
                }
                badge.title = t('note.badgeTitle') + ' ' + notes[dayId];
            } else if (badge) {
                badge.remove();
            }
        });
    }

    function showToast(msg) {
        const toastEl = document.getElementById('toastMsg');
        toastEl.innerText = msg;
        toastEl.style.display = 'block';
        setTimeout(function () {
            toastEl.style.display = 'none';
        }, 3000);
    }

    function createGoogleCalendarUrl(ev) {
        const startD = ev.date.replace(/-/g, '');
        let endD = ev.endDate ? ev.endDate.replace(/-/g, '') : startD;
        if (endD === startD) {
            const d = new Date(ev.date);
            d.setDate(d.getDate() + 1);
            endD = d.toISOString().slice(0, 10).replace(/-/g, '');
        }
        const text = encodeURIComponent(loc(ev.title));
        const details = encodeURIComponent(
            loc(ev.description) + '\n\n' + loc(ev.grade1Note) + '\n' + t('modal.official') + ' ' + ev.officialTitle
        );
        const location = encodeURIComponent(loc(ev.location));
        return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + text + '&dates=' + startD + '/' + endD + '&details=' + details + '&location=' + location;
    }

    function downloadSingleEventICS(evId) {
        const ev = eventById(evId);
        if (!ev) return;
        downloadFile(generateICS([ev]), ev.id + '.ics', 'text/calendar');
    }

    function downloadAllEventsICS() {
        downloadFile(generateICS(events), 'kalendarz_szkolny_2026_2027_1_klasa.ics', 'text/calendar');
        showToast(t('toast.ics'));
    }

    function generateICS(eventList) {
        const lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//LXXVIII LO Warszawa//Klasa 1 Kalendarz//' + currentLang.toUpperCase(),
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            'X-WR-CALNAME:' + school.icsCalendarName,
            'X-WR-TIMEZONE:' + school.timezone
        ];

        eventList.forEach(function (ev) {
            const sDate = ev.date.replace(/-/g, '');
            const endObj = new Date(ev.endDate || ev.date);
            endObj.setDate(endObj.getDate() + 1);
            const eDateExclusive = endObj.toISOString().slice(0, 10).replace(/-/g, '');

            lines.push('BEGIN:VEVENT');
            lines.push('UID:' + ev.id + '-2026-2027@lo78.edu.pl');
            lines.push('DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z');
            lines.push('DTSTART;VALUE=DATE:' + sDate);
            lines.push('DTEND;VALUE=DATE:' + eDateExclusive);
            lines.push('SUMMARY:' + loc(ev.title).replace(/[,;]/g, ' '));
            lines.push('DESCRIPTION:' + (loc(ev.description) + ' ' + loc(ev.grade1Note)).replace(/\n/g, ' '));
            lines.push('LOCATION:' + loc(ev.location));
            lines.push('END:VEVENT');
        });

        lines.push('END:VCALENDAR');
        return lines.join('\r\n');
    }

    function downloadFile(content, filename, type) {
        const blob = new Blob([content], { type: type + ';charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function bindDayCells() {
        if (cellsBound) return;
        cellsBound = true;
        months.forEach(function (m) {
            const section = document.getElementById(m.id);
            if (!section) return;
            section.querySelectorAll('.day-cell:not(.empty)').forEach(function (cell) {
                const numEl = cell.querySelector('.day-number');
                if (!numEl) return;
                const dNum = parseInt(numEl.innerText.trim(), 10);
                if (isNaN(dNum)) return;

                const dateStr =
                    m.year + '-' + String(m.month).padStart(2, '0') + '-' + String(dNum).padStart(2, '0');
                cell.setAttribute('data-day-key', dateStr);
                cell.addEventListener('click', function () {
                    openDayModal(dateStr, formatDayHeading(dateStr));
                });
            });
        });
    }

    function setupGleanBridge() {
        if (!window.GleanBridge) return;
        window.GleanBridge.postMessage({
            actionId: 'export-pdf',
            type: 'glean-add-menu',
            metadata: { label: 'Export as PDF', icon: 'export' }
        });
        window.GleanBridge.onMessage('action', function (msg) {
            if (msg.actionId === 'export-pdf') window.print();
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        bindDayCells();
        const todayIdx = monthIndexForDate(TODAY_KEY);
        if (todayIdx !== -1) currentMonthFocusIdx = todayIdx;
        setLanguage(readStoredLang());
        if (todayIdx !== -1) scrollToToday();
        setupGleanBridge();
        window.addEventListener('resize', syncStickyOffsets);
    });

    window.setViewMode = setViewMode;
    window.setLanguage = setLanguage;
    window.prevMonthFocus = prevMonthFocus;
    window.nextMonthFocus = nextMonthFocus;
    window.scrollToMonth = scrollToMonth;
    window.showAllMonths = showAllMonths;
    window.handleSearch = handleSearch;
    window.filterByCategory = filterByCategory;
    window.openDayModal = openDayModal;
    window.closeEventModal = closeEventModal;
    window.closeModalOnBackdrop = closeModalOnBackdrop;
    window.saveCurrentDayNote = saveCurrentDayNote;
    window.downloadSingleEventICS = downloadSingleEventICS;
    window.downloadAllEventsICS = downloadAllEventsICS;
})();
