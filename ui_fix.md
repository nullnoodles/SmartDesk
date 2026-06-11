"Read this HTML/CSS file and extract ONLY design tokens as a simple list. Do not write any Python code.
Extract:

All hex colors and what element they're used on
All font sizes and weights
All spacing values (padding, margin, gap)
All border-radius values
All component widths and heights
All component names and their structure

<!DOCTYPE html>

<html class="dark" lang="en" style="width: 1280px; height: 1024px; overflow: hidden; position: relative;"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>SmartDesk - Time Tracker</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&amp;family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "on-tertiary-container": "#003138",
                        "on-background": "#e2e1f1",
                        "background": "#12131d",
                        "inverse-primary": "#4654bb",
                        "inverse-on-surface": "#2f303b",
                        "surface-container": "#1e1f2a",
                        "surface": "#12131d",
                        "status-warning": "#f0c878",
                        "tertiary-container": "#459fad",
                        "secondary": "#82d8ac",
                        "primary-container": "#7c8af4",
                        "primary-fixed": "#dfe0ff",
                        "surface-container-lowest": "#0c0d18",
                        "status-danger": "#e87c8a",
                        "on-surface-variant": "#c6c5d5",
                        "outline-variant": "#454652",
                        "tertiary-fixed": "#9bf0ff",
                        "bg-deep": "#12131a",
                        "error-container": "#93000a",
                        "surface-dim": "#12131d",
                        "on-surface": "#e2e1f1",
                        "on-secondary-container": "#90e6ba",
                        "text-primary": "#e2e4f0",
                        "on-primary-fixed-variant": "#2c3ba2",
                        "on-secondary-fixed": "#002113",
                        "surface-container-high": "#282935",
                        "tertiary": "#7dd3e3",
                        "tertiary-fixed-dim": "#7dd3e3",
                        "surface-container-low": "#1a1b26",
                        "outline": "#908f9e",
                        "text-muted": "#6b6d85",
                        "bg-surface": "#1a1b26",
                        "on-tertiary-fixed-variant": "#004f58",
                        "primary": "#7c8af4",
                        "on-error-container": "#ffdad6",
                        "surface-container-highest": "#333440",
                        "on-error": "#690005",
                        "text-secondary": "#9a9cb8",
                        "inverse-surface": "#e2e1f1",
                        "surface-variant": "#333440",
                        "on-primary-container": "#061987",
                        "secondary-fixed": "#9df4c7",
                        "surface-tint": "#bcc2ff",
                        "secondary-container": "#006a47",
                        "primary-fixed-dim": "#bcc2ff",
                        "on-secondary": "#003824",
                        "surface-bright": "#383844",
                        "on-secondary-fixed-variant": "#005236",
                        "on-tertiary": "#00363d",
                        "on-primary": "#0f208b",
                        "on-tertiary-fixed": "#001f24",
                        "on-primary-fixed": "#000c61",
                        "error": "#ffb4ab",
                        "secondary-fixed-dim": "#82d8ac"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                    "spacing": {
                        "card-gap": "24px",
                        "main-padding": "32px",
                        "sidebar-width": "230px",
                        "gutter": "16px",
                        "row-padding": "10px"
                    },
                    "fontFamily": {
                        "headline-xl": ["Inter"],
                        "body-lg": ["Inter"],
                        "body-sm": ["Inter"],
                        "headline-lg": ["Inter"],
                        "label-caps": ["Inter"],
                        "tabular-nums": ["Inter"],
                        "body-md": ["Inter"]
                    },
                    "fontSize": {
                        "headline-xl": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "700"}],
                        "body-lg": ["16px", {"lineHeight": "24px", "fontWeight": "500"}],
                        "body-sm": ["13px", {"lineHeight": "18px", "fontWeight": "400"}],
                        "headline-lg": ["24px", {"lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "700"}],
                        "label-caps": ["11px", {"lineHeight": "16px", "letterSpacing": "0.05em", "fontWeight": "700"}],
                        "tabular-nums": ["14px", {"lineHeight": "20px", "fontWeight": "500"}],
                        "body-md": ["14px", {"lineHeight": "20px", "fontWeight": "400"}]
                    }
                },
            },
        }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #12131d; }
        ::-webkit-scrollbar-thumb { background: #2d2e42; border-radius: 10px; }
        .table-row-alt:nth-child(even) { background-color: #1e1f2b; }
    </style>
</head>
<body class="bg-background text-on-surface font-body-md overflow-hidden">
<!-- SideNavBar from COMPONENTS_6 -->
<aside class="fixed left-0 top-0 h-full w-[230px] bg-bg-deep flex flex-col py-main-padding z-50">
<div class="px-6 mb-10">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-[8px] bg-primary flex items-center justify-center text-white shadow-lg">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">waves</span>
</div>
<div>
<h1 class="font-headline-lg text-headline-lg text-primary tracking-tight leading-none">SmartDesk</h1>
<p class="text-[10px] text-text-muted font-label-caps tracking-widest mt-0.5">CREATIVE WORKSPACE</p>
</div>
</div>
</div>
<nav class="flex-1 space-y-1 overflow-y-auto">
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">dashboard</span>
<span class="font-body-md text-body-md">Dashboard</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">group</span>
<span class="font-body-md text-body-md">Clients</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">folder_open</span>
<span class="font-body-md text-body-md">Projects</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">receipt_long</span>
<span class="font-body-md text-body-md">Invoices</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-primary border-l-4 border-primary bg-primary/10 transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3" style="font-variation-settings: 'FILL' 1;">timer</span>
<span class="font-body-md text-body-md">Time Log</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">description</span>
<span class="font-body-md text-body-md">Contracts</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">analytics</span>
<span class="font-body-md text-body-md">AI Analytics</span>
</a>
<a class="group relative flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3">settings</span>
<span class="font-body-md text-body-md">Settings</span>
</a>
</nav>
<div class="px-6 mt-auto">
</div>
</aside>
<!-- TopAppBar from COMPONENTS_6 -->
<header class="fixed top-0 right-0 left-[230px] h-20 bg-background flex justify-between items-center px-main-padding z-40">
<div class="flex items-center gap-4 w-1/3">
<div class="relative w-full max-w-md">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">search</span>
<input class="w-full bg-surface-container-low border border-outline-variant rounded-full py-2 pl-10 pr-4 focus:ring-1 focus:ring-primary outline-none text-body-md placeholder:text-text-muted transition-all" placeholder="Search tasks or logs..." type="text"/>
</div>
</div>
<div class="flex items-center gap-6">
<button class="flex items-center gap-2 px-4 h-[40px] bg-primary text-white rounded-[8px] font-bold hover:brightness-110 active:scale-[0.98] transition-all">
<span class="material-symbols-outlined text-[20px]">add</span>
<span class="">New Item</span>
</button>
<div class="flex items-center gap-4">
<button class="p-2 text-text-secondary hover:bg-surface-container rounded-full transition-all">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="p-2 text-text-secondary hover:bg-surface-container rounded-full transition-all">
<span class="material-symbols-outlined">help_outline</span>
</button>
</div>
<div class="h-8 w-[1px] bg-outline-variant"></div>
<button class="flex items-center gap-3 hover:bg-surface-container p-1 pr-3 rounded-full transition-all group">
<img alt="Alex Rivera" class="w-8 h-8 rounded-full border border-outline-variant object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAuVK16TUQmeLEwl_Yz0buAjzrfDWk-Xl8BKZgT1vTRWifPDHGuLU4Vis-VtQvb-tTEhjMV0yrhTkeAx_558384PeZS5Zjts1cRQ4WaFWvPrbyz58eC-HCa69Cnosy73f17-fbXUVad1njFADuawI0vqIch4KfUs-hyDDnwPI579to2WUMZaVS7PWn_TziA-SLldzuxFgSObmbcpoGkQdbKof78ZHWO-5Ngsegn8ayMzzkqdAiSmSpuaGkjHPhcddFl8AIP6257DM0"/>
<span class="font-body-md text-body-md text-on-surface">Alex Rivera</span>
</button>
</div>
</header>
<!-- Main Content -->
<main class="ml-[230px] pt-20 h-screen overflow-y-auto bg-background">
<div class="max-w-[1200px] mx-auto p-main-padding space-y-card-gap"><!-- Top Metrics Row -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-card-gap">
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 shadow-sm">
<div class="flex items-center justify-between mb-2">
<span class="text-text-secondary text-body-md">Total Hours Logged</span>
<span class="material-symbols-outlined text-primary">history</span>
</div>
<div class="text-headline-lg font-headline-lg text-on-surface">1,240.5</div>
<div class="mt-1 text-body-sm text-text-muted">Lifetime tracking</div>
</div>
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 shadow-sm">
<div class="flex items-center justify-between mb-2">
<span class="text-text-secondary text-body-md">This Week</span>
<span class="material-symbols-outlined text-primary">calendar_today</span>
</div>
<div class="text-headline-lg font-headline-lg text-on-surface">32.5 Hours</div>
<div class="mt-1 text-body-sm text-secondary flex items-center gap-1">
<span class="material-symbols-outlined text-sm">trending_up</span> 12% vs last week
        </div>
</div>
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 shadow-sm">
<div class="flex items-center justify-between mb-2">
<span class="text-text-secondary text-body-md">Entries</span>
<span class="material-symbols-outlined text-primary">list_alt</span>
</div>
<div class="text-headline-lg font-headline-lg text-on-surface">128</div>
<div class="mt-1 text-body-sm text-text-muted">Total logs recorded</div>
</div>
</div>
<!-- Middle Row: Live Timer & Manual Entry -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-card-gap">
<!-- Live Timer Card -->
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 flex flex-col shadow-sm">
<div class="flex justify-between items-center mb-6">
<h3 class="font-headline-lg text-body-lg text-on-surface">Live Timer</h3>
<select class="bg-surface-container border border-outline-variant text-text-secondary rounded-[8px] px-3 h-8 text-body-sm outline-none focus:border-primary">
<option>Select Project</option>
<option>Neon Branding</option>
<option>Skyline App UI</option>
</select>
</div>
<input class="block w-full bg-transparent border-none p-0 text-body-lg font-body-lg text-on-surface placeholder:text-text-muted focus:ring-0 outline-none mb-8" placeholder="What are you working on?" type="text"/>
<div class="flex items-center justify-between mt-auto">
<div class="font-headline-xl text-[48px] leading-none text-primary tracking-tighter tabular-nums">00:00:00</div>
<button class="h-12 px-8 rounded-full bg-secondary text-on-secondary flex items-center justify-center font-bold hover:brightness-110 active:scale-95 transition-all">
                Start
            </button>
</div>
</div>
<!-- Manual Entry Card -->
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 flex flex-col shadow-sm">
<div class="flex justify-between items-center mb-6">
<h3 class="font-headline-lg text-body-lg text-on-surface">Manual Entry</h3>
<select class="bg-surface-container border border-outline-variant text-text-secondary rounded-[8px] px-3 h-8 text-body-sm outline-none focus:border-primary">
<option>Select Project</option>
<option>Neon Branding</option>
<option>Skyline App UI</option>
</select>
</div>
<div class="grid grid-cols-12 gap-3 mb-6">
<div class="col-span-4">
<input class="w-full bg-surface-container border border-outline-variant rounded-[8px] px-4 py-2 text-on-surface outline-none focus:border-primary text-body-md" placeholder="Hours (e.g. 1.5)" step="0.1" type="number"/>
</div>
<div class="col-span-8">
<input class="w-full bg-surface-container border border-outline-variant rounded-[8px] px-4 py-2 text-on-surface outline-none focus:border-primary text-body-md" placeholder="Description" type="text"/>
</div>
</div>
<button class="w-full h-[40px] bg-primary text-white rounded-[8px] font-bold hover:brightness-110 transition-all active:scale-95 mt-auto">
            + Add Entry
        </button>
</div>
</div>
<!-- Chart Section -->
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] p-6 shadow-sm">
<h3 class="font-headline-lg text-body-lg text-on-surface mb-6">Hours by Project</h3>
<div class="flex items-end gap-6 h-48 px-4">
<div class="flex-1 flex flex-col items-center gap-2">
<div class="w-full bg-primary/20 rounded-t-lg relative group" style="height: 80%">
<div class="absolute inset-0 bg-primary rounded-t-lg opacity-80"></div>
<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-body-sm font-tabular-nums">12.5h</div>
</div>
<span class="text-[10px] text-text-muted uppercase tracking-wider truncate w-full text-center">Neon Branding</span>
</div>
<div class="flex-1 flex flex-col items-center gap-2">
<div class="w-full bg-primary/20 rounded-t-lg relative group" style="height: 60%">
<div class="absolute inset-0 bg-primary rounded-t-lg opacity-80"></div>
<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-body-sm font-tabular-nums">8.0h</div>
</div>
<span class="text-[10px] text-text-muted uppercase tracking-wider truncate w-full text-center">Skyline App UI</span>
</div>
<div class="flex-1 flex flex-col items-center gap-2">
<div class="w-full bg-primary/20 rounded-t-lg relative group" style="height: 45%">
<div class="absolute inset-0 bg-primary rounded-t-lg opacity-80"></div>
<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-body-sm font-tabular-nums">6.2h</div>
</div>
<span class="text-[10px] text-text-muted uppercase tracking-wider truncate w-full text-center">Logo Design</span>
</div>
<div class="flex-1 flex flex-col items-center gap-2">
<div class="w-full bg-primary/20 rounded-t-lg relative group" style="height: 35%">
<div class="absolute inset-0 bg-primary rounded-t-lg opacity-80"></div>
<div class="absolute -top-6 left-1/2 -translate-x-1/2 text-body-sm font-tabular-nums">4.5h</div>
</div>
<span class="text-[10px] text-text-muted uppercase tracking-wider truncate w-full text-center">Internal</span>
</div>
</div>
</div>
<!-- Table Section -->
<div class="bg-surface-container-low border border-outline-variant/30 rounded-[8px] overflow-hidden shadow-sm">
<div class="px-6 py-4 flex justify-between items-center border-b border-outline-variant/30">
<h3 class="font-headline-lg text-body-lg text-on-surface">Time Entries</h3>
<span class="text-body-sm text-text-muted">12 Total Records</span>
</div>
<div class="overflow-x-auto">
<table class="w-full text-left border-collapse">
<thead class="bg-surface-container-lowest">
<tr>
<th class="px-6 py-3 text-label-caps font-label-caps text-on-surface tracking-wider">PROJECT</th>
<th class="px-6 py-3 text-label-caps font-label-caps text-on-surface tracking-wider">DATE</th>
<th class="px-6 py-3 text-label-caps font-label-caps text-on-surface tracking-wider">HOURS</th>
<th class="px-6 py-3 text-label-caps font-label-caps text-on-surface tracking-wider">DESCRIPTION</th>
</tr>
</thead>
<tbody>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
<td class="px-6 py-4 font-body-md text-on-surface">Neon Branding</td>
<td class="px-6 py-4 text-text-secondary font-tabular-nums">Oct 24, 2023</td>
<td class="px-6 py-4">
<span class="px-2.5 py-1 rounded-full bg-secondary-container/20 text-secondary text-tabular-nums font-tabular-nums">2.50h</span>
</td>
<td class="px-6 py-4 text-text-muted truncate max-w-[300px]">Iterating on logo animations</td>
</tr>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high transition-colors">
<td class="px-6 py-4 font-body-md text-on-surface">Skyline App UI</td>
<td class="px-6 py-4 text-text-secondary font-tabular-nums">Oct 23, 2023</td>
<td class="px-6 py-4">
<span class="px-2.5 py-1 rounded-full bg-primary-container/20 text-primary text-tabular-nums font-tabular-nums">4.25h</span>
</td>
<td class="px-6 py-4 text-text-muted truncate max-w-[300px]">Design system documentation</td>
</tr>
</tbody>
</table>
</div>
</div></div>
</main>
<script>
        let timerSeconds = 0;
        let timerInterval = null;
        let isRunning = false;

        const timerDisplay = document.getElementById('timer-display');
        const timerBtn = document.getElementById('timer-btn');
        const timerIcon = document.getElementById('timer-icon');

        function updateTimer() {
            timerSeconds++;
            const h = Math.floor(timerSeconds / 3600).toString().padStart(2, '0');
            const m = Math.floor((timerSeconds % 3600) / 60).toString().padStart(2, '0');
            const s = (timerSeconds % 60).toString().padStart(2, '0');
            timerDisplay.textContent = `${h}:${m}:${s}`;
        }

        timerBtn.addEventListener('click', () => {
            if (isRunning) {
                clearInterval(timerInterval);
                timerBtn.classList.remove('bg-status-danger', 'text-on-error-container');
                timerBtn.classList.add('bg-primary', 'text-white');
                timerIcon.textContent = 'play_arrow';
                isRunning = false;
            } else {
                timerInterval = setInterval(updateTimer, 1000);
                timerBtn.classList.remove('bg-primary', 'text-white');
                timerBtn.classList.add('bg-status-danger', 'text-white');
                timerIcon.textContent = 'stop';
                isRunning = true;
            }
        });

        // Navigation active state handling
        const navItems = document.querySelectorAll('nav a');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                navItems.forEach(i => {
                    i.classList.remove('text-primary', 'border-l-4', 'border-primary', 'bg-primary/10');
                    i.classList.add('text-text-secondary');
                    const span = i.querySelector('.material-symbols-outlined');
                    if(span) span.style.fontVariationSettings = "'FILL' 0";
                });
                item.classList.add('text-primary', 'border-l-4', 'border-primary', 'bg-primary/10');
                item.classList.remove('text-text-secondary');
                const activeSpan = item.querySelector('.material-symbols-outlined');
                if(activeSpan) activeSpan.style.fontVariationSettings = "'FILL' 1";
            });
        });
    </script>
<div aria-hidden="true" data-snapdom-sandbox="true" id="snapdom-sandbox" style="position: absolute; left: -9999px; top: -9999px; width: 0px; height: 0px; overflow: hidden;"></div></body></html>


Output as a clean numbered list. Nothing else."