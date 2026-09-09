/* School calendar behaviour — reads CALENDAR_DATA, does not own styles or event records. */

(function () {
    const data = window.CALENDAR_DATA;
    const events = data.events;
    const months = data.months;
    const school = data.school;

    let currentMonthFocusIdx = 0;
    let activeCategoryFilter = 'all';
    let currentActiveDayKey = null;

    function eventsOnDate(dateStr) {
        return events.filter(function (ev) {
            if (ev.endDate) {
                return dateStr >= ev.date && dateStr <= ev.endDate;
            }
            return ev.date === dateStr;
        });
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
            if (navBar) navBar.style.display = 'none';
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
        document.getElementById('focusMonthTitle').innerText = months[currentMonthFocusIdx].name;
        const currentEl = document.getElementById(months[currentMonthFocusIdx].id);
        if (currentEl) {
            currentEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
            if (text.includes(query) || title.includes(query)) {
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
            const text = item.innerText.toLowerCase();
            item.style.display = text.includes(query) ? 'block' : 'none';
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

        titleEl.innerText = formattedDate || dateStr;

        const matching = eventsOnDate(dateStr);

        if (matching.length === 0) {
            container.innerHTML =
                '<div class="modal-event-card">' +
                '<div class="modal-event-title">📚 Навчальний день за розкладом</div>' +
                '<div class="modal-event-desc">Цього дня в ліцеї проходять регулярні уроки згідно з розкладом 1-го класу. Спеціальних загальношкільних чи виїзних заходів не заплановано.</div>' +
                '</div>';
        } else {
            container.innerHTML = matching.map(function (ev) {
                const gcalUrl = createGoogleCalendarUrl(ev);
                return (
                    '<div class="modal-event-card" data-glean-id="modal-' + ev.id + '">' +
                    '<div class="modal-event-title">' + ev.title + '</div>' +
                    '<div class="modal-event-pl">Офіційно (PL): ' + ev.titlePl + '</div>' +
                    '<div class="modal-event-desc">' +
                    '<div><b>Час / тривалість:</b> ' + ev.time + '</div>' +
                    '<div><b>Опис:</b> ' + ev.description + '</div>' +
                    '<div><b>Локація:</b> ' + ev.location + '</div>' +
                    '</div>' +
                    '<div class="modal-grade1-tip">💡 <b>Для 1-х класів:</b> ' + ev.grade1Note + '</div>' +
                    '<div class="modal-actions">' +
                    '<a class="modal-btn" href="' + gcalUrl + '" target="_blank">📅 Додати до Google Calendar</a>' +
                    '<button type="button" class="modal-btn" onclick="downloadSingleEventICS(\'' + ev.id + '\')">📥 Завантажити .ICS</button>' +
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
        showToast('Замітку успішно збережено!');
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
                    badge.title = 'Особиста замітка: ' + notes[dayId];
                    header.appendChild(badge);
                } else {
                    badge.title = 'Особиста замітка: ' + notes[dayId];
                }
            } else if (badge) {
                badge.remove();
            }
        });
    }

    function showToast(msg) {
        const t = document.getElementById('toastMsg');
        t.innerText = msg;
        t.style.display = 'block';
        setTimeout(function () {
            t.style.display = 'none';
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
        const text = encodeURIComponent(ev.title);
        const details = encodeURIComponent(ev.description + '\n\n1-й клас ліцею.\nОфіційна назва: ' + ev.titlePl);
        const loc = encodeURIComponent(ev.location);
        return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + text + '&dates=' + startD + '/' + endD + '&details=' + details + '&location=' + loc;
    }

    function downloadSingleEventICS(evId) {
        const ev = events.find(function (e) {
            return e.id === evId;
        });
        if (!ev) return;
        downloadFile(generateICS([ev]), ev.id + '.ics', 'text/calendar');
    }

    function downloadAllEventsICS() {
        downloadFile(generateICS(events), 'kalendarz_szkolny_2026_2027_1_klasa.ics', 'text/calendar');
        showToast('Календар .ICS завантажено! Тепер відкрийте його для імпорту в Google/Apple Calendar.');
    }

    function generateICS(eventList) {
        const lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//LXXVIII LO Warszawa//Klasa 1 Kalendarz//UK',
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
            lines.push('SUMMARY:' + ev.title.replace(/[,;]/g, ' '));
            lines.push('DESCRIPTION:' + (ev.description + ' ' + ev.grade1Note).replace(/\n/g, ' '));
            lines.push('LOCATION:' + ev.location);
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
                const formatted = dNum + ' ' + m.nameGenitive;
                cell.setAttribute('data-day-key', dateStr);
                cell.title = 'Натисніть, щоб відкрити деталі та замітки на ' + formatted;
                cell.addEventListener('click', function () {
                    openDayModal(dateStr, formatted);
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
        renderNotesBadges();
        setupGleanBridge();
    });

    window.setViewMode = setViewMode;
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
