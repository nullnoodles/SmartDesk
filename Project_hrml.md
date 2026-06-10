Read this HTML/CSS code and extract ONLY the design tokens into a structured list. Do not write any code yet.
Extract:

All hex colors and what they're used for
All font sizes and weights
All spacing values (padding, margin, gap)
All border-radius values
All component dimensions (widths, heights)

<!DOCTYPE html>

<html class="dark" lang="en" style="width: 1280px; height: 1024px; overflow: hidden; position: relative;"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>SmartDesk - Projects</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #12131d;
            color: #e2e1f1;
            margin: 0;
        }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        /* Custom scrollbar for Studio Graphite theme */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #12131a;
        }
        ::-webkit-scrollbar-thumb {
            background: #2d2e42;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #454652;
        }
    </style>
<script id="tailwind-config">tailwind.config = {darkMode: "class", theme: {extend: {colors: {"primary-fixed": "#dfe0ff", "surface-dim": "#12131d", "on-error-container": "#ffdad6", "secondary-container": "#006a47", "text-muted": "#6b6d85", "inverse-on-surface": "#2f303b", "surface-bright": "#383844", primary: "#bcc2ff", tertiary: "#7dd3e3", "bg-deep": "#12131a", "primary-fixed-dim": "#bcc2ff", "primary-container": "#7c8af4", "on-secondary-fixed": "#002113", "on-surface-variant": "#c6c5d5", "tertiary-fixed-dim": "#7dd3e3", "surface-container-lowest": "#0c0d18", "on-primary-fixed-variant": "#2c3ba2", "surface-container-highest": "#333440", "secondary-fixed": "#9df4c7", "surface-container-low": "#1a1b26", "on-primary": "#0f208b", "on-error": "#690005", "status-danger": "#e87c8a", "on-secondary": "#003824", "surface-container": "#1e1f2a", "on-background": "#e2e1f1", surface: "#12131d", "surface-tint": "#bcc2ff", error: "#ffb4ab", "on-primary-fixed": "#000c61", "text-secondary": "#9a9cb8", "on-tertiary-fixed-variant": "#004f58", "inverse-surface": "#e2e1f1", "on-tertiary": "#00363d", "on-tertiary-fixed": "#001f24", "status-warning": "#f0c878", secondary: "#82d8ac", background: "#12131d", "outline-variant": "#454652", "on-secondary-fixed-variant": "#005236", "on-tertiary-container": "#003138", "tertiary-fixed": "#9bf0ff", "secondary-fixed-dim": "#82d8ac", "error-container": "#93000a", "surface-variant": "#333440", "surface-container-high": "#282935", "text-primary": "#e2e4f0", "inverse-primary": "#4654bb", outline: "#908f9e", "tertiary-container": "#459fad", "bg-surface": "#222336", "on-surface": "#e2e1f1", "on-secondary-container": "#90e6ba", "on-primary-container": "#061987"}, borderRadius: {DEFAULT: "0.25rem", lg: "0.5rem", xl: "0.75rem", full: "9999px"}, spacing: {"card-gap": "24px", "row-padding": "10px", gutter: "16px", "sidebar-width": "230px", "main-padding": "32px", "safe-area-inset": "20px", xl: "32px", "tap-target-min": "44px", sm: "12px", md: "16px", xs: "8px", base: "4px", lg: "24px"}, fontFamily: {"headline-xl": ["Inter"], "body-lg": ["Inter"], "body-sm": ["Inter"], "body-md": ["Inter"], "tabular-nums": ["Inter"], "label-caps": ["Inter"], "headline-lg": ["Inter"], "label-sm": ["Inter"], "headline-lg-mobile": ["Inter"], display: ["Inter"], "title-md": ["Inter"], headline: ["Inter"], body: ["Inter"], label: ["Inter"]}, fontSize: {"headline-xl": ["32px", {lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "700"}], "body-lg": ["16px", {lineHeight: "24px", fontWeight: "500"}], "body-sm": ["13px", {lineHeight: "18px", fontWeight: "400"}], "body-md": ["14px", {lineHeight: "20px", fontWeight: "400"}], "tabular-nums": ["14px", {lineHeight: "20px", fontWeight: "500"}], "label-caps": ["11px", {lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "700"}], "headline-lg": ["24px", {lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "700"}], "label-sm": ["12px", {lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "600"}], "headline-lg-mobile": ["24px", {lineHeight: "30px", letterSpacing: "-0.01em", fontWeight: "700"}], display: ["40px", {lineHeight: "48px", letterSpacing: "-0.02em", fontWeight: "700"}], "title-md": ["18px", {lineHeight: "24px", letterSpacing: "0em", fontWeight: "600"}]}}}};</script>
</head>
<body class="bg-background text-on-background">
<!-- SideNavBar from COMPONENTS_6 -->
<aside class="fixed left-0 top-0 h-full w-[230px] bg-bg-deep flex flex-col py-main-padding z-50">
<div class="px-6 mb-10 flex flex-col">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(188,194,255,0.4)]">
<span class="material-symbols-outlined text-on-primary-container text-xl" style="font-variation-settings: 'FILL' 1;">fluid</span>
</div>
<span class="font-headline-lg text-headline-lg text-primary tracking-tight">SmartDesk</span>
</div>
<span class="font-label-caps text-label-caps text-text-secondary mt-1 px-[44px]">Creative Workspace</span>
</div>
<nav class="flex-1 space-y-1 overflow-y-auto">
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="dashboard">dashboard</span>
<span class="font-body-md text-body-md">Dashboard</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="group">group</span>
<span class="font-body-md text-body-md">Clients</span>
</a>
<a class="flex items-center px-6 py-3 text-primary border-l-4 border-primary bg-primary/10 transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3" data-icon="folder_open" style="font-variation-settings: 'FILL' 1;">folder_open</span>
<span class="font-body-md text-body-md">Projects</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="receipt_long">receipt_long</span>
<span class="font-body-md text-body-md">Invoices</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="timer">timer</span>
<span class="font-body-md text-body-md">Time Log</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="description">description</span>
<span class="font-body-md text-body-md">Contracts</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="analytics">analytics</span>
<span class="font-body-md text-body-md">AI Analytics</span>
</a>
<a class="flex items-center px-6 py-3 text-text-secondary hover:bg-surface-container-low transition-colors group active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined mr-3 group-hover:text-primary" data-icon="settings">settings</span>
<span class="font-body-md text-body-md">Settings</span>
</a>
</nav>
<div class="px-6 mt-auto">
</div>
</aside>
<!-- TopAppBar from COMPONENTS_6 -->
<header class="fixed top-0 right-0 left-[230px] h-20 bg-background flex justify-between items-center px-main-padding z-40">
<div class="flex items-center flex-1 max-w-xl">
<div class="relative w-full">
<span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary">search</span>
<input class="w-full bg-surface-container-low border border-outline-variant rounded-xl pl-12 pr-4 py-2.5 text-body-md focus:border-primary outline-none transition-all" placeholder="Search projects, tasks, or files..." type="text"/>
</div>
</div>
<div class="flex items-center gap-6">
<div class="flex items-center gap-4 text-text-secondary">
<button class="hover:bg-surface-container p-2 rounded-lg transition-all active:scale-[0.98]">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="hover:bg-surface-container p-2 rounded-lg transition-all active:scale-[0.98]">
<span class="material-symbols-outlined">help_outline</span>
</button>
</div>
<div class="h-8 w-[1px] bg-outline-variant"></div>
<div class="flex items-center gap-3">
<div class="text-right">
<p class="font-body-sm text-body-sm text-on-surface font-bold leading-tight">Alex Rivera</p>
<p class="font-label-caps text-label-caps text-text-secondary uppercase">Pro Account</p>
</div>
<img alt="User profile" class="w-10 h-10 rounded-full border border-outline-variant object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDzk6OUYLak-d4Efb1mKqtgC4doDiTZKjg55-s5DAn3VvG7_ntHJEmej1V3fX37_l60oiCZQkm7EH7OCZgLjjqOx0XpDvhwAz49Ovf7SYS0s-5OIxug4rdTsZWnsO8nk2purKo0XBiHNfIg0R8e59neWq5H02NVuh0Dv_8I-ct99tJ348FznaKfZKsbw9mPkECNEVej285LhyHHPjF5LcwCK6G8zyxfo8tZ2M790EZVIRLKP2iVr6B_DX95GAGERYXnDGwc88kpRU0"/>
</div>
</div>
</header>
<!-- Main Content Canvas -->
<main class="ml-[230px] pt-20 min-h-screen p-main-padding">
<!-- Header Section -->
<div class="flex justify-between items-end mb-8">
<div>
<div class="flex items-center gap-3 mb-1">
<h1 class="font-headline-xl text-headline-xl text-text-primary">Projects</h1>
<span class="px-2.5 py-0.5 rounded-full bg-surface-container-high text-text-secondary font-tabular-nums text-sm border border-outline-variant">12 Total</span>
</div>
<p class="text-text-secondary font-body-md text-body-md">Manage and track your active production pipeline.</p>
</div>
<button class="h-[40px] bg-primary-container text-on-primary-container font-bold text-body-lg px-6 rounded-lg flex items-center justify-center gap-2 hover:brightness-110 active:scale-[0.98] transition-all shadow-lg shadow-primary/10">
<span class="material-symbols-outlined text-lg">add_circle</span>
                New Project
            </button>
</div>
<!-- Project Stats Cards -->
<div class="grid grid-cols-12 gap-card-gap mb-8">
<div class="col-span-8 grid grid-cols-3 gap-card-gap">
<div class="bg-surface-container-low p-6 rounded-xl border border-outline-variant/30 hover:bg-surface-container-high transition-colors cursor-default">
<div class="flex justify-between items-start mb-4">
<div class="w-10 h-10 rounded-lg bg-tertiary/10 flex items-center justify-center text-tertiary">
<span class="material-symbols-outlined">rocket_launch</span>
</div>
<span class="text-secondary font-tabular-nums text-body-sm">+12%</span>
</div>
<p class="text-text-secondary font-label-caps text-label-caps mb-1">ACTIVE VELOCITY</p>
<h3 class="font-headline-lg text-headline-lg text-text-primary">8 Current</h3>
</div>
<div class="bg-surface-container-low p-6 rounded-xl border border-outline-variant/30 hover:bg-surface-container-high transition-colors cursor-default">
<div class="flex justify-between items-start mb-4">
<div class="w-10 h-10 rounded-lg bg-status-warning/10 flex items-center justify-center text-status-warning">
<span class="material-symbols-outlined">hourglass_empty</span>
</div>
<span class="text-status-danger font-tabular-nums text-body-sm">2 Late</span>
</div>
<p class="text-text-secondary font-label-caps text-label-caps mb-1">UPCOMING DEADLINES</p>
<h3 class="font-headline-lg text-headline-lg text-text-primary">48 Hours</h3>
</div>
<div class="bg-surface-container-low p-6 rounded-xl border border-outline-variant/30 hover:bg-surface-container-high transition-colors cursor-default">
<div class="flex justify-between items-start mb-4">
<div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
<span class="material-symbols-outlined">payments</span>
</div>
<span class="text-secondary font-tabular-nums text-body-sm">$12.4k</span>
</div>
<p class="text-text-secondary font-label-caps text-label-caps mb-1">PIPELINE VALUE</p>
<h3 class="font-headline-lg text-headline-lg text-text-primary">$42,800</h3>
</div>
</div>
<div class="col-span-4 bg-surface-container-low rounded-xl border border-outline-variant/30 p-6 relative overflow-hidden group">
<div class="relative z-10">
<h4 class="font-body-lg text-body-lg text-text-primary mb-2">Workspace Insight</h4>
<p class="text-text-secondary font-body-sm text-body-sm leading-relaxed mb-4">You're currently at 85% capacity. AI suggests shifting the <b>Apex Mobile</b> deadline to avoid burnout.</p>
<button class="text-primary font-label-caps text-label-caps flex items-center gap-1 hover:underline">
                        OPTIMIZE SCHEDULE <span class="material-symbols-outlined text-sm">arrow_forward</span>
</button>
</div>
<div class="absolute -right-10 -bottom-10 w-40 h-40 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all duration-700"></div>
</div>
</div>
<!-- Main Projects Table -->
<div class="bg-surface-container-low rounded-xl border border-outline-variant/30 overflow-hidden">
<div class="overflow-x-auto">
<table class="w-full border-collapse">
<thead>
<tr class="bg-surface-container-low/50">
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">ID</th>
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Project</th>
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Client</th>
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Type</th>
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Status</th>
<th class="px-6 py-4 text-left font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Deadline</th>
<th class="px-6 py-4 text-right font-label-caps text-label-caps text-text-primary uppercase tracking-wider">Actions</th>
</tr>
</thead>
<tbody class="divide-y divide-outline-variant/20">
<!-- Row 1 -->
<tr class="hover:bg-surface-container-low transition-colors group">
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">SD-012</td>
<td class="px-6 py-row-padding">
<div class="font-body-md text-body-md text-text-primary">Brand Identity Redesign</div>
<div class="text-[11px] text-text-secondary">Creative Suite Expansion</div>
</td>
<td class="px-6 py-row-padding">
<div class="flex items-center gap-2">
<div class="w-6 h-6 rounded-full bg-tertiary-container/30 flex items-center justify-center text-[10px] text-tertiary">MP</div>
<span class="font-body-md text-body-md text-text-secondary">Meera Patel</span>
</div>
</td>
<td class="px-6 py-row-padding">
<span class="text-text-secondary font-body-sm text-body-sm">Branding</span>
</td>
<td class="px-6 py-row-padding">
<span class="px-3 py-1 rounded-full text-[12px] font-bold bg-tertiary-container/20 text-tertiary border border-tertiary-container/30">Active</span>
</td>
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">Oct 24, 2023</td>
<td class="px-6 py-row-padding text-right">
<div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
<button class="p-2 text-text-secondary hover:text-primary transition-colors">
<span class="material-symbols-outlined text-[20px]">edit_note</span>
</button>
<button class="p-2 text-text-secondary hover:text-status-danger transition-colors">
<span class="material-symbols-outlined text-[20px]">delete_outline</span>
</button>
</div>
</td>
</tr>
<!-- Row 2 -->
<tr class="bg-surface-container-low/20 hover:bg-surface-container-low transition-colors group">
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">SD-011</td>
<td class="px-6 py-row-padding">
<div class="font-body-md text-body-md text-text-primary">Solaris Dashboard UI</div>
<div class="text-[11px] text-text-secondary">High-Fidelity Prototyping</div>
</td>
<td class="px-6 py-row-padding">
<div class="flex items-center gap-2">
<img alt="Client" class="w-6 h-6 rounded-full" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAsYojMTspVxsjx-B-am8wuxGoqMwAcbx7H7eWBnQd40VLJ-PgFa7Ceph-p9P0x_9VsDkY6M_1LgoPDREiSfL74eXQh5eBtCnfa7VmrR2pI9_3BRZUvo4byKh_c2hVgXiujPtijUkeyPIsldLRQNGDXcZqvMp_Yr-5myinUssKRIGLbTvsHBAYewibtNBDRnnwWhHzDx8tSRp8acAXGCIG_-aL4DETXDIYdfRsWx-jIWG6Pu1P7lAXChcml_6649zWZoyI-J5sD6K4"/>
<span class="font-body-md text-body-md text-text-secondary">Marcus Chen</span>
</div>
</td>
<td class="px-6 py-row-padding">
<span class="text-text-secondary font-body-sm text-body-sm">Product Design</span>
</td>
<td class="px-6 py-row-padding">
<span class="px-3 py-1 rounded-full text-[12px] font-bold bg-secondary-container/20 text-secondary border border-secondary-container/30">Completed</span>
</td>
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">Oct 12, 2023</td>
<td class="px-6 py-row-padding text-right">
<div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
<button class="p-2 text-text-secondary hover:text-primary transition-colors">
<span class="material-symbols-outlined text-[20px]">edit_note</span>
</button>
<button class="p-2 text-text-secondary hover:text-status-danger transition-colors">
<span class="material-symbols-outlined text-[20px]">delete_outline</span>
</button>
</div>
</td>
</tr>
<!-- Row 3 -->
<tr class="hover:bg-surface-container-low transition-colors group">
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">SD-010</td>
<td class="px-6 py-row-padding">
<div class="font-body-md text-body-md text-text-primary">Nexus Landing Page</div>
<div class="text-[11px] text-text-secondary">Marketing Collateral</div>
</td>
<td class="px-6 py-row-padding">
<div class="flex items-center gap-2">
<div class="w-6 h-6 rounded-full bg-primary-container/30 flex items-center justify-center text-[10px] text-primary">SC</div>
<span class="font-body-md text-body-md text-text-secondary">Sarah Connor</span>
</div>
</td>
<td class="px-6 py-row-padding">
<span class="text-text-secondary font-body-sm text-body-sm">Web Dev</span>
</td>
<td class="px-6 py-row-padding">
<span class="px-3 py-1 rounded-full text-[12px] font-bold bg-status-warning/10 text-status-warning border border-status-warning/30">Revision</span>
</td>
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">Oct 30, 2023</td>
<td class="px-6 py-row-padding text-right">
<div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
<button class="p-2 text-text-secondary hover:text-primary transition-colors">
<span class="material-symbols-outlined text-[20px]">edit_note</span>
</button>
<button class="p-2 text-text-secondary hover:text-status-danger transition-colors">
<span class="material-symbols-outlined text-[20px]">delete_outline</span>
</button>
</div>
</td>
</tr>
<!-- Row 4 -->
<tr class="bg-surface-container-low/20 hover:bg-surface-container-low transition-colors group">
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">SD-009</td>
<td class="px-6 py-row-padding">
<div class="font-body-md text-body-md text-text-primary">Apex Mobile App</div>
<div class="text-[11px] text-text-secondary">iOS &amp; Android MVP</div>
</td>
<td class="px-6 py-row-padding">
<div class="flex items-center gap-2">
<div class="w-6 h-6 rounded-full bg-status-danger/30 flex items-center justify-center text-[10px] text-status-danger">DK</div>
<span class="font-body-md text-body-md text-text-secondary">David Kim</span>
</div>
</td>
<td class="px-6 py-row-padding">
<span class="text-text-secondary font-body-sm text-body-sm">Development</span>
</td>
<td class="px-6 py-row-padding">
<span class="px-3 py-1 rounded-full text-[12px] font-bold bg-status-danger/20 text-status-danger border border-status-danger/30">Delayed</span>
</td>
<td class="px-6 py-row-padding font-tabular-nums text-status-danger">In 2 Days</td>
<td class="px-6 py-row-padding text-right">
<div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
<button class="p-2 text-text-secondary hover:text-primary transition-colors">
<span class="material-symbols-outlined text-[20px]">edit_note</span>
</button>
<button class="p-2 text-text-secondary hover:text-status-danger transition-colors">
<span class="material-symbols-outlined text-[20px]">delete_outline</span>
</button>
</div>
</td>
</tr>
<!-- Row 5 -->
<tr class="hover:bg-surface-container-low transition-colors group">
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">SD-008</td>
<td class="px-6 py-row-padding">
<div class="font-body-md text-body-md text-text-primary">Cloud Architecture Audit</div>
<div class="text-[11px] text-text-secondary">Consultancy</div>
</td>
<td class="px-6 py-row-padding">
<div class="flex items-center gap-2">
<div class="w-6 h-6 rounded-full bg-outline flex items-center justify-center text-[10px] text-surface">GL</div>
<span class="font-body-md text-body-md text-text-secondary">Global Logistics</span>
</div>
</td>
<td class="px-6 py-row-padding">
<span class="text-text-secondary font-body-sm text-body-sm">Consulting</span>
</td>
<td class="px-6 py-row-padding">
<span class="px-3 py-1 rounded-full text-[12px] font-bold bg-outline-variant/40 text-on-surface-variant border border-outline-variant/60">Archived</span>
</td>
<td class="px-6 py-row-padding font-tabular-nums text-text-secondary">Sept 28, 2023</td>
<td class="px-6 py-row-padding text-right">
<div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
<button class="p-2 text-text-secondary hover:text-primary transition-colors">
<span class="material-symbols-outlined text-[20px]">edit_note</span>
</button>
<button class="p-2 text-text-secondary hover:text-status-danger transition-colors">
<span class="material-symbols-outlined text-[20px]">delete_outline</span>
</button>
</div>
</td>
</tr>
</tbody>
</table>
</div>
<!-- Table Footer / Pagination -->
<div class="px-6 py-4 flex items-center justify-between border-t border-outline-variant/20 bg-surface-container-low/30">
<div class="flex gap-4">
<button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant text-text-secondary hover:bg-surface-container transition-colors text-body-sm active:scale-95">
<span class="material-symbols-outlined text-sm">edit</span>
                        Batch Edit
                    </button>
<button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant text-text-secondary hover:text-status-danger hover:border-status-danger transition-colors text-body-sm active:scale-95">
<span class="material-symbols-outlined text-sm">delete</span>
                        Delete Selection
                    </button>
</div>
<div class="flex items-center gap-4">
<span class="text-body-sm text-text-secondary">Page 1 of 3</span>
<div class="flex gap-1">
<button class="p-2 rounded-lg border border-outline-variant text-text-secondary hover:bg-surface-container transition-colors disabled:opacity-30" disabled="">
<span class="material-symbols-outlined">chevron_left</span>
</button>
<button class="p-2 rounded-lg border border-outline-variant text-text-secondary hover:bg-surface-container transition-colors">
<span class="material-symbols-outlined">chevron_right</span>
</button>
</div>
</div>
</div>
</div>
</main>
<!-- Contextual Floating Action Layer -->
<div class="fixed bottom-8 right-8 z-[60] pointer-events-none" id="toast-container"><div class="bg-surface-container-highest border border-primary/30 text-text-primary px-6 py-3 rounded-xl shadow-2xl mb-3 flex items-center gap-3 animate-bounce-short pointer-events-auto opacity-0 translate-y-4 transition-all duration-500">
<span class="material-symbols-outlined text-primary">info</span>
<span class="text-body-sm">Action triggered for system processing.</span>
</div></div>
<script>
        // Micro-interactions and effects
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const toast = document.createElement('div');
                toast.className = 'bg-surface-container-highest border border-primary/30 text-text-primary px-6 py-3 rounded-xl shadow-2xl mb-3 flex items-center gap-3 animate-bounce-short pointer-events-auto';
                toast.innerHTML = `
                    <span class="material-symbols-outlined text-primary">info</span>
                    <span class="text-body-sm">Action triggered for system processing.</span>
                `;
                document.getElementById('toast-container').appendChild(toast);
                setTimeout(() => {
                    toast.classList.add('opacity-0', 'translate-y-4', 'transition-all', 'duration-500');
                    setTimeout(() => toast.remove(), 500);
                }, 3000);
            });
        });
    </script>
<style>
        @keyframes bounce-short {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        .animate-bounce-short {
            animation: bounce-short 0.4s ease;
        }
    </style>
<div aria-hidden="true" data-snapdom-sandbox="true" id="snapdom-sandbox" style="position: absolute; left: -9999px; top: -9999px; width: 0px; height: 0px; overflow: hidden;"></div></body></html>
Output as a simple list. Nothing else."