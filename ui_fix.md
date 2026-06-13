



"Read this HTML/CSS file and extract ONLY the visual styling values. 
Extract everything

layout:Card,button,text positions
Background colors for: page, cards, table, header, rows
Text colors for: titles, labels, values, muted text
Border colors and widths
Border radius values for: cards, badges, buttons, inputs
Font sizes and weights for: page title, card labels, card values, table headers, table rows
Padding values for: cards, table rows, table header
Button colors and styles
Status badge colors for each status
Any hover state colors






<!DOCTYPE html>

<html class="dark" lang="en" style="width: 1280px; height: 1024px; overflow: hidden; position: relative;"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Contract Risk Analyzer</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "on-surface-variant": "#c6c5d5",
                        "surface-tint": "#bcc2ff",
                        "bg-surface": "#222336",
                        "bg-deep": "#12131a",
                        "surface-container-high": "#282935",
                        "primary-container": "#7c8af4",
                        "text-muted": "#6b6d85",
                        "on-error-container": "#ffdad6",
                        "text-secondary": "#9a9cb8",
                        "status-danger": "#e87c8a",
                        "on-secondary": "#003824",
                        "inverse-on-surface": "#2f303b",
                        "on-tertiary-fixed-variant": "#004f58",
                        "surface-variant": "#333440",
                        "on-primary-container": "#061987",
                        "surface-dim": "#12131d",
                        "secondary-fixed": "#9df4c7",
                        "on-primary-fixed": "#000c61",
                        "on-background": "#e2e1f1",
                        "tertiary-container": "#459fad",
                        "background": "#12131d",
                        "tertiary-fixed": "#9bf0ff",
                        "tertiary": "#7dd3e3",
                        "on-secondary-container": "#90e6ba",
                        "status-warning": "#f0c878",
                        "on-tertiary-fixed": "#001f24",
                        "tertiary-fixed-dim": "#7dd3e3",
                        "on-tertiary-container": "#003138",
                        "on-primary": "#0f208b",
                        "on-tertiary": "#00363d",
                        "on-primary-fixed-variant": "#2c3ba2",
                        "on-surface": "#e2e1f1",
                        "surface-container-lowest": "#0c0d18",
                        "surface-container-highest": "#333440",
                        "outline-variant": "#454652",
                        "surface-bright": "#383844",
                        "secondary": "#82d8ac",
                        "error-container": "#93000a",
                        "primary": "#bcc2ff",
                        "inverse-surface": "#e2e1f1",
                        "error": "#ffb4ab",
                        "primary-fixed-dim": "#bcc2ff",
                        "on-secondary-fixed": "#002113",
                        "on-error": "#690005",
                        "surface-container": "#1e1f2a",
                        "secondary-container": "#006a47",
                        "on-secondary-fixed-variant": "#005236",
                        "primary-fixed": "#dfe0ff",
                        "outline": "#908f9e",
                        "surface": "#12131d",
                        "inverse-primary": "#4654bb",
                        "surface-container-low": "#1a1b26",
                        "secondary-fixed-dim": "#82d8ac",
                        "text-primary": "#e2e4f0"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                    "spacing": {
                        "sidebar-width": "230px",
                        "row-padding": "10px",
                        "gutter": "16px",
                        "main-padding": "32px",
                        "card-gap": "24px"
                    },
                    "fontFamily": {
                        "label-caps": ["Inter"],
                        "body-md": ["Inter"],
                        "headline-lg": ["Inter"],
                        "body-sm": ["Inter"],
                        "tabular-nums": ["Inter"],
                        "body-lg": ["Inter"],
                        "headline-xl": ["Inter"]
                    },
                    "fontSize": {
                        "label-caps": ["11px", { "lineHeight": "16px", "letterSpacing": "0.05em", "fontWeight": "700" }],
                        "body-md": ["14px", { "lineHeight": "20px", "fontWeight": "400" }],
                        "headline-lg": ["24px", { "lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "700" }],
                        "body-sm": ["13px", { "lineHeight": "18px", "fontWeight": "400" }],
                        "tabular-nums": ["14px", { "lineHeight": "20px", "fontWeight": "500" }],
                        "body-lg": ["16px", { "lineHeight": "24px", "fontWeight": "500" }],
                        "headline-xl": ["32px", { "lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "700" }]
                    }
                }
            }
        }
    </script>
<style>
        body { background-color: theme('colors.background'); color: theme('colors.text-primary'); }
        .glass-card { background: theme('colors.bg-surface'); border: 1px solid theme('colors.surface-variant'); border-radius: 14px; padding: 24px; transition: background-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease; }
        .glass-card:hover { background: theme('colors.surface-container-high'); }
        
        .risk-card { background: theme('colors.surface-container-low'); border: 1px solid theme('colors.surface-variant'); border-radius: 14px; padding: 24px; transition: all 0.3s ease; }
        .risk-card:hover { transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.3); }
        .risk-card.border-status-danger:hover { box-shadow: 0 0 15px 0 rgba(232, 124, 138, 0.2); }
        .risk-card.border-status-warning:hover { box-shadow: 0 0 15px 0 rgba(240, 200, 120, 0.2); }
        .risk-card.border-secondary:hover { box-shadow: 0 0 15px 0 rgba(130, 216, 172, 0.2); }

        .btn-primary { background: theme('colors.primary-container'); color: theme('colors.on-primary-container'); border-radius: 10px; padding: 10px 20px; font-weight: 500; transition: transform 0.2s; position: relative; overflow: hidden; }
        .btn-primary:active { transform: scale(0.98); }
        
        .btn-shimmer::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.3), transparent);
            transform: skewX(-20deg);
            animation: shimmer 3s infinite;
        }
        @keyframes shimmer {
            0% { left: -100%; }
            20% { left: 200%; }
            100% { left: 200%; }
        }

        .btn-ghost { border: 1px solid theme('colors.surface-variant'); color: theme('colors.primary'); border-radius: 10px; padding: 10px 20px; font-weight: 500; transition: transform 0.2s, background-color 0.2s; }
        .btn-ghost:active { transform: scale(0.98); }
        .btn-ghost:hover { background-color: theme('colors.surface-container-high'); }
        
        .input-field { background: theme('colors.surface-container-low'); border: 1px solid theme('colors.surface-variant'); color: theme('colors.text-primary'); border-radius: 6px; padding: 8px 12px; width: 100%; transition: all 0.3s ease; }
        .input-field:focus { outline: none; border-color: theme('colors.primary-container'); box-shadow: 0 0 0 2px rgba(124, 138, 244, 0.2); }
        .input-field::placeholder { color: theme('colors.text-muted'); }

        .nav-link { transition: all 0.2s ease; }
        .nav-link:hover .nav-icon { transform: scale(1.15); color: theme('colors.primary'); }
        .nav-icon { transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s ease; }

        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-entrance {
            animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
        }
        .delay-100 { animation-delay: 100ms; }
        .delay-200 { animation-delay: 200ms; }
        .delay-300 { animation-delay: 300ms; }
        .delay-400 { animation-delay: 400ms; }

        #particle-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.5;
        }
    </style>
</head>
<body class="flex h-screen overflow-hidden bg-background">
<!-- SideNavBar Component -->
<nav class="fixed left-0 top-0 h-full w-[230px] flex flex-col py-main-padding bg-bg-deep dark:bg-bg-deep z-50 shadow-[1px_0_0_0_#2d2e42]">
<div class="px-6 mb-8 flex items-center gap-3">
<div class="w-8 h-8 rounded bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-lg">S</div>
<div>
<h1 class="font-headline-lg text-headline-lg text-primary text-[18px] leading-tight">SmartDesk</h1>
<p class="font-body-sm text-body-sm text-text-muted text-[11px]">Creative Workspace</p>
</div>
</div>
<div class="flex-1 overflow-y-auto flex flex-col gap-1 px-3">
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">dashboard</span>
<span class="font-body-md text-body-md">Dashboard</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">group</span>
<span class="font-body-md text-body-md">Clients</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">folder_open</span>
<span class="font-body-md text-body-md">Projects</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">receipt_long</span>
<span class="font-body-md text-body-md">Invoices</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">timer</span>
<span class="font-body-md text-body-md">Time Log</span>
</a>
<a class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-primary border-l-4 border-primary bg-primary/10 active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined">description</span>
<span class="font-body-md text-body-md">Contracts</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200" href="#">
<span class="material-symbols-outlined nav-icon">analytics</span>
<span class="font-body-md text-body-md">AI Analytics</span>
</a>
<a class="nav-link flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:bg-surface-container-low transition-colors active:scale-95 duration-200 mt-auto" href="#">
<span class="material-symbols-outlined nav-icon">settings</span>
<span class="font-body-md text-body-md">Settings</span>
</a>
</div>
<div class="px-4 mt-4">
<button class="w-full btn-primary flex items-center justify-center gap-2 py-2.5">
<span class="material-symbols-outlined text-[18px]">add</span>
<span class="font-body-md text-body-md">New Workspace</span>
</button>
</div>
</nav>
<!-- Main Content Canvas -->
<div class="ml-[230px] flex-1 flex flex-col h-full bg-background relative z-0" style="min-width: 1050px;">
<canvas height="1024" id="particle-canvas" width="1050"></canvas>
<!-- TopAppBar Component -->
<header class="fixed top-0 right-0 left-[230px] h-16 bg-surface-dim border-b border-surface-variant z-40 flex justify-between items-center px-main-padding">
<div class="flex items-center gap-4 flex-1">
<div class="relative w-full max-w-md"><span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-[20px]">search</span><input class="w-full bg-surface-container-low border border-surface-variant rounded-lg py-2 pl-10 pr-4 text-body-md focus:outline-none focus:border-primary transition-colors" placeholder="Search contracts, clauses, or clients..." type="text"/></div>
</div>
<div class="flex items-center gap-4"><div class="flex items-center gap-3"><button class="w-10 h-10 rounded-full flex items-center justify-center text-text-secondary hover:bg-surface-container-high transition-colors"><span class="material-symbols-outlined">notifications</span></button><button class="w-10 h-10 rounded-full flex items-center justify-center text-text-secondary hover:bg-surface-container-high transition-colors"><span class="material-symbols-outlined">help</span></button><div class="w-8 h-8 rounded-full bg-surface-variant overflow-hidden border border-surface-variant cursor-pointer ml-2"><img alt="User profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDhcx3zlSX-0Zq5OpXHPiVxxdqVfR8PV2g3yp-yvur1Mdv84xPougGePOSQpA9jQq1w065N_lrTNc3ezXqzT_UsHyNyAKA4loXly7r-eqd4JYc_ybLxnbIOWh9fIHz60ybHnIkoUB0KgcGoru8q8yXHMCa0xv0QukWfMvSZKDM_eu_YzQt-36tMTNU01osVSFi1bqPCQ1trJSJr0gNMi5d90RuEiBLwA4NxRZOA-7gMDY6q8obinHNI5kVjiRZBY8FgryxDn1hGYv4"/></div></div></div>
</header>
<!-- Scrollable Content Area -->
<main class="flex-1 overflow-y-auto pt-20 px-main-padding pb-main-padding relative z-10">
<div class="max-w-[1200px] mx-auto w-full">
<!-- Page Header -->
<div class="flex justify-between items-end mb-8 animate-entrance">
<div>
<div class="flex items-center gap-3 mb-2">
<h1 class="font-headline-xl text-headline-xl text-text-primary">Contract Risk Analyzer</h1>
<span class="bg-surface-variant text-text-secondary px-3 py-1 rounded-full font-label-caps text-label-caps border border-surface-bright flex items-center gap-1">
<span class="">🛡️</span> 5 Core Risks
                            </span>
</div>
<p class="font-body-lg text-body-lg text-text-secondary">AI-powered analysis of 55+ dangerous contract clauses</p>
</div>
<div class="flex gap-3">
</div>
</div>
<!-- Input Grid Section -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-card-gap mb-card-gap">
<!-- Contract Upload -->
<div class="glass-card flex flex-col h-full animate-entrance delay-100">
<h2 class="font-headline-lg text-[18px] mb-4 text-text-primary">Upload Contract</h2>
<div class="border-2 border-dashed border-surface-variant rounded-xl p-8 flex flex-col items-center justify-center text-center hover:border-primary-container transition-colors cursor-pointer group flex-1 bg-surface-container-low">
<div class="w-16 h-16 rounded-full bg-surface-container-low flex items-center justify-center mb-4 group-hover:bg-primary-container/20 transition-colors">
<span class="material-symbols-outlined text-3xl text-text-muted group-hover:text-primary-container">upload_file</span>
</div>
<h3 class="font-body-lg text-body-lg text-text-primary mb-1">Drag &amp; Drop PDF or DOCX</h3>
<p class="font-body-sm text-body-sm text-text-muted mb-4">or click to browse from your computer</p>
<button class="btn-ghost text-sm py-1.5 px-4">Select File</button>
</div>
</div>
<!-- Project Parameters -->
<div class="glass-card flex flex-col animate-entrance delay-200">
<h2 class="font-headline-lg text-[18px] mb-4 text-text-primary">Project Parameters</h2>
<form class="space-y-4 flex-1 flex flex-col">
<div>
<label class="block font-label-caps text-label-caps text-text-secondary mb-1">CLIENT NAME</label>
<input class="input-field bg-surface-container-low border-surface-variant" placeholder="e.g. Acme Corp" type="text"/>
</div>
<div class="grid grid-cols-2 gap-4">
<div>
<label class="block font-label-caps text-label-caps text-text-secondary mb-1">BUDGET</label>
<div class="relative">
<span class="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted font-body-md">$</span>
<input class="input-field pl-8 bg-surface-container-low border-surface-variant" placeholder="10,000" type="text"/>
</div>
</div>
<div>
<label class="block font-label-caps text-label-caps text-text-secondary mb-1">TIMELINE</label>
<input class="input-field bg-surface-container-low border-surface-variant" placeholder="e.g. 6 Months" type="text"/>
</div>
</div>
<div>
<label class="block font-label-caps text-label-caps text-text-secondary mb-1">YOUR JURISDICTION</label>
<select class="input-field appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%239a9cb8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-no-repeat bg-[right_12px_center] bg-[length:16px] bg-surface-container-low border-surface-variant">
<option class="text-text-muted" disabled="" selected="" value="">Select State/Country</option>
<option value="ca">California, US</option>
<option value="ny">New York, US</option>
<option value="uk">United Kingdom</option>
</select>
</div>
<div class="mt-auto pt-4">
<button class="w-full bg-[#7c8af4] text-[#061987] font-bold rounded-lg py-3 flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
<span class="material-symbols-outlined">analytics</span>
    Analyze Contract
</button>
</div>
</form>
</div>
</div>
<!-- Overall Risk Assessment -->
<div class="glass-card mb-card-gap relative overflow-hidden animate-entrance delay-300">
<div class="absolute inset-0 bg-gradient-to-r from-status-danger/5 to-transparent pointer-events-none"></div>
<div class="flex flex-col md:flex-row items-center gap-8 relative z-10">
<div class="flex-shrink-0 relative w-[120px] h-[120px] flex items-center justify-center">
<!-- Circular Progress -->
<svg class="w-full h-full transform -rotate-90" viewbox="0 0 100 100">
<circle cx="50" cy="50" fill="none" r="45" stroke="#282935" stroke-width="8"></circle>
<circle cx="50" cy="50" fill="none" id="risk-circle" r="45" stroke="#e87c8a" stroke-dasharray="282.7" stroke-dashoffset="282.7" stroke-linecap="round" stroke-width="8" style="transition: stroke-dashoffset 2s ease-out; stroke-dashoffset: 70.6858;"></circle>
</svg>
<div class="absolute inset-0 flex flex-col items-center justify-center">
<span class="font-headline-xl text-3xl font-bold text-status-danger" id="risk-counter">0</span>
<span class="font-label-caps text-[10px] text-text-secondary">RISK SCORE</span>
</div>
</div>
<div class="flex-1 w-full">
<h2 class="font-headline-lg text-[22px] mb-2 text-text-primary flex items-center gap-2">
                                Critical Risk Level Detected
                                <span class="material-symbols-outlined text-status-danger text-2xl" style="font-variation-settings: 'FILL' 1;">warning</span>
</h2>
<p class="font-body-md text-text-secondary mb-4 max-w-2xl">Based on the uploaded document, 3 severe clauses require immediate attention before signing. The intellectual property transfer terms are highly unfavorable.</p>
<div class="w-full h-3 bg-surface-container-high rounded-full overflow-hidden flex">
<div class="h-full bg-status-danger" style="width: 45%;"></div>
<div class="h-full bg-status-warning" style="width: 30%;"></div>
<div class="h-full bg-secondary" style="width: 25%;"></div>
</div>
<div class="flex justify-between mt-2 font-label-caps text-text-muted">
<span class="">Low Risk (0-30)</span>
<span class="">Medium (31-60)</span>
<span class="text-status-danger">High Risk (61-100)</span>
</div>
</div>
</div>
</div>
<!-- 5 Critical Risk Areas Grid -->
<div class="animate-entrance delay-400">
<h3 class="font-headline-lg text-[18px] mb-4 text-text-primary px-1">Detailed Risk Breakdown</h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-card-gap">
<!-- Risk Card 1: Intellectual Property -->
<div class="risk-card relative overflow-hidden group border-status-danger/30 hover:border-status-danger">
<div class="absolute top-0 right-0 w-12 h-12 bg-status-danger/10 flex items-center justify-center rounded-bl-xl">
<span class="font-tabular-nums font-bold text-status-danger">92%</span>
</div>
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-status-danger">
<span class="material-symbols-outlined">copyright</span>
</div>
<h4 class="font-body-lg font-bold text-text-primary text-[15px]">Intellectual Property</h4>
</div>
<p class="font-body-sm text-text-secondary mb-4 pr-8 line-clamp-2">Complete assignment of all pre-existing IP rights to the client without compensation.</p>
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-status-danger" style="width: 92%;"></div>
</div>
<div class="mt-4 pt-4 border-t border-surface-variant flex justify-between items-center">
<span class="font-label-caps text-status-danger flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">error</span> CRITICAL FIX</span>
<button class="text-primary hover:text-primary-container font-body-sm text-[12px] flex items-center gap-1">View Clause <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
</div>
</div>
<!-- Risk Card 2: Payment Terms -->
<div class="risk-card relative overflow-hidden group border-status-warning/30 hover:border-status-warning">
<div class="absolute top-0 right-0 w-12 h-12 bg-status-warning/10 flex items-center justify-center rounded-bl-xl">
<span class="font-tabular-nums font-bold text-status-warning">68%</span>
</div>
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-status-warning">
<span class="material-symbols-outlined">payments</span>
</div>
<h4 class="font-body-lg font-bold text-text-primary text-[15px]">Payment Terms</h4>
</div>
<p class="font-body-sm text-text-secondary mb-4 pr-8 line-clamp-2">Net-90 payment schedule with vague 'client satisfaction' contingencies for final milestone.</p>
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-status-warning" style="width: 68%;"></div>
</div>
<div class="mt-4 pt-4 border-t border-surface-variant flex justify-between items-center">
<span class="font-label-caps text-status-warning flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">warning</span> REVIEW NEEDED</span>
<button class="text-primary hover:text-primary-container font-body-sm text-[12px] flex items-center gap-1">View Clause <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
</div>
</div>
<!-- Risk Card 3: Scope Creep -->
<div class="risk-card relative overflow-hidden group border-status-danger/30 hover:border-status-danger">
<div class="absolute top-0 right-0 w-12 h-12 bg-status-danger/10 flex items-center justify-center rounded-bl-xl">
<span class="font-tabular-nums font-bold text-status-danger">85%</span>
</div>
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-status-danger">
<span class="material-symbols-outlined">zoom_out_map</span>
</div>
<h4 class="font-body-lg font-bold text-text-primary text-[15px]">Scope Creep Control</h4>
</div>
<p class="font-body-sm text-text-secondary mb-4 pr-8 line-clamp-2">Unlimited revisions clause detected without hourly rate fallbacks or caps.</p>
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-status-danger" style="width: 85%;"></div>
</div>
<div class="mt-4 pt-4 border-t border-surface-variant flex justify-between items-center">
<span class="font-label-caps text-status-danger flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">error</span> CRITICAL FIX</span>
<button class="text-primary hover:text-primary-container font-body-sm text-[12px] flex items-center gap-1">View Clause <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
</div>
</div>
<!-- Risk Card 4: Termination -->
<div class="risk-card relative overflow-hidden group border-secondary/30 hover:border-secondary">
<div class="absolute top-0 right-0 w-12 h-12 bg-secondary/10 flex items-center justify-center rounded-bl-xl">
<span class="font-tabular-nums font-bold text-secondary">20%</span>
</div>
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-secondary">
<span class="material-symbols-outlined">cancel</span>
</div>
<h4 class="font-body-lg font-bold text-text-primary text-[15px]">Termination Rights</h4>
</div>
<p class="font-body-sm text-text-secondary mb-4 pr-8 line-clamp-2">Standard 30-day notice period. Mutual termination rights clearly defined.</p>
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-secondary" style="width: 20%;"></div>
</div>
<div class="mt-4 pt-4 border-t border-surface-variant flex justify-between items-center">
<span class="font-label-caps text-secondary flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">check_circle</span> ACCEPTABLE</span>
<button class="text-primary hover:text-primary-container font-body-sm text-[12px] flex items-center gap-1">View Clause <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
</div>
</div>
<!-- Risk Card 5: Liability -->
<div class="risk-card relative overflow-hidden group border-status-warning/30 hover:border-status-warning">
<div class="absolute top-0 right-0 w-12 h-12 bg-status-warning/10 flex items-center justify-center rounded-bl-xl">
<span class="font-tabular-nums font-bold text-status-warning">55%</span>
</div>
<div class="flex items-center gap-3 mb-4">
<div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-status-warning">
<span class="material-symbols-outlined">shield</span>
</div>
<h4 class="font-body-lg font-bold text-text-primary text-[15px]">Liability Caps</h4>
</div>
<p class="font-body-sm text-text-secondary mb-4 pr-8 line-clamp-2">Liability capped at total contract value, but lacks specific exclusion for indirect damages.</p>
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-status-warning" style="width: 55%;"></div>
</div>
<div class="mt-4 pt-4 border-t border-surface-variant flex justify-between items-center">
<span class="font-label-caps text-status-warning flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">warning</span> REVIEW NEEDED</span>
<button class="text-primary hover:text-primary-container font-body-sm text-[12px] flex items-center gap-1">View Clause <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
<script>
    // Particle Background
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];

    function initCanvas() {
        width = canvas.width = window.innerWidth - 230; // Account for sidebar
        height = canvas.height = window.innerHeight;
        
        particles = [];
        const particleCount = Math.floor((width * height) / 25000); // Density
        
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 1.5 + 0.5,
                alpha: Math.random() * 0.5 + 0.1
            });
        }
    }

    function drawParticles() {
        ctx.clearRect(0, 0, width, height);
        
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;

            // Wrap around
            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(188, 194, 255, ${p.alpha})`; // surface-tint / primary color
            ctx.fill();
        });

        requestAnimationFrame(drawParticles);
    }

    window.addEventListener('resize', initCanvas);
    
    // Risk Score Animation
    function animateRiskScore() {
        const targetValue = 75;
        const duration = 2000; // ms
        const counterElement = document.getElementById('risk-counter');
        const circleElement = document.getElementById('risk-circle');
        
        // Circle SVG config
        const radius = 45;
        const circumference = 2 * Math.PI * radius; // ~282.7
        
        // Trigger circle stroke animation
        setTimeout(() => {
            const offset = circumference - (targetValue / 100) * circumference;
            circleElement.style.strokeDashoffset = offset;
        }, 100);

        // Counter animation
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            
            // Easing function (easeOutExpo)
            const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            
            counterElement.textContent = Math.floor(easeProgress * targetValue);
            
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                counterElement.textContent = targetValue;
            }
        };
        window.requestAnimationFrame(step);
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        initCanvas();
        drawParticles();
        
        // Small delay to ensure entrance animations have started before numbers count up
        setTimeout(animateRiskScore, 300);
    });
</script>
<div aria-hidden="true" data-snapdom-sandbox="true" id="snapdom-sandbox" style="position: absolute; left: -9999px; top: -9999px; width: 0px; height: 0px; overflow: hidden;"></div></body></html>

Output as a simple list of name: value pairs. Nothing else.
