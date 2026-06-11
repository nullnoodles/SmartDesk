"Read this HTML/CSS file and extract ONLY design tokens as a simple list. Do not write any Python code.
Extract:

All hex colors and what element they're used on
All font sizes and weights
All spacing values (padding, margin, gap)
All border-radius values
All component widths and heights
All component names and their structure

<!DOCTYPE html>

<html class="dark" lang="en"><head></head><body class="font-body-md text-body-md bg-background text-on-background"><svg aria-hidden="true" class="inline-defs-container" style="position:absolute;width:0;height:0;overflow:hidden"></svg>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>SmartDesk | AI Analytics</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        "colors": {
                "status-warning": "#f0c878",
                "on-tertiary-fixed-variant": "#004f58",
                "surface-dim": "#12131d",
                "text-primary": "#e2e4f0",
                "primary-container": "#7c8af4",
                "surface-container-high": "#282935",
                "on-primary-fixed-variant": "#2c3ba2",
                "surface-container-lowest": "#0c0d18",
                "surface": "#12131d",
                "primary-fixed": "#dfe0ff",
                "on-background": "#e2e1f1",
                "on-primary-container": "#061987",
                "surface-bright": "#383844",
                "on-tertiary": "#00363d",
                "surface-container-low": "#1a1b26",
                "text-muted": "#6b6d85",
                "on-secondary": "#003824",
                "secondary": "#82d8ac",
                "outline-variant": "#454652",
                "surface-tint": "#bcc2ff",
                "on-secondary-fixed": "#002113",
                "background": "#12131d",
                "bg-deep": "#12131a",
                "on-secondary-container": "#90e6ba",
                "tertiary-fixed-dim": "#7dd3e3",
                "on-surface-variant": "#c6c5d5",
                "secondary-fixed": "#9df4c7",
                "surface-variant": "#333440",
                "on-tertiary-fixed": "#001f24",
                "on-error-container": "#ffdad6",
                "surface-container": "#1e1f2a",
                "primary": "#bcc2ff",
                "error": "#ffb4ab",
                "bg-surface": "#222336",
                "on-surface": "#e2e1f1",
                "primary-fixed-dim": "#bcc2ff",
                "tertiary": "#7dd3e3",
                "surface-container-highest": "#333440",
                "inverse-primary": "#4654bb",
                "on-secondary-fixed-variant": "#005236",
                "on-primary": "#0f208b",
                "tertiary-container": "#459fad",
                "tertiary-fixed": "#9bf0ff",
                "inverse-on-surface": "#2f303b",
                "error-container": "#93000a",
                "on-tertiary-container": "#003138",
                "inverse-surface": "#e2e1f1",
                "status-danger": "#e87c8a",
                "outline": "#908f9e",
                "secondary-fixed-dim": "#82d8ac",
                "secondary-container": "#006a47",
                "on-error": "#690005",
                "on-primary-fixed": "#000c61",
                "text-secondary": "#9a9cb8"
        },
        "borderRadius": {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
        },
        "spacing": {
                "sidebar-width": "230px",
                "main-padding": "32px",
                "row-padding": "10px",
                "gutter": "16px",
                "card-gap": "24px"
        },
        "fontFamily": {
                "body-md": [
                        "Inter"
                ],
                "tabular-nums": [
                        "Inter"
                ],
                "headline-lg": [
                        "Inter"
                ],
                "body-sm": [
                        "Inter"
                ],
                "headline-xl": [
                        "Inter"
                ],
                "label-caps": [
                        "Inter"
                ],
                "body-lg": [
                        "Inter"
                ]
        },
        "fontSize": {
                "body-md": [
                        "14px",
                        {
                                "lineHeight": "20px",
                                "fontWeight": "400"
                        }
                ],
                "tabular-nums": [
                        "14px",
                        {
                                "lineHeight": "20px",
                                "fontWeight": "500"
                        }
                ],
                "headline-lg": [
                        "24px",
                        {
                                "lineHeight": "32px",
                                "letterSpacing": "-0.01em",
                                "fontWeight": "700"
                        }
                ],
                "body-sm": [
                        "13px",
                        {
                                "lineHeight": "18px",
                                "fontWeight": "400"
                        }
                ],
                "headline-xl": [
                        "32px",
                        {
                                "lineHeight": "40px",
                                "letterSpacing": "-0.02em",
                                "fontWeight": "700"
                        }
                ],
                "label-caps": [
                        "11px",
                        {
                                "lineHeight": "16px",
                                "letterSpacing": "0.05em",
                                "fontWeight": "700"
                        }
                ],
                "body-lg": [
                        "16px",
                        {
                                "lineHeight": "24px",
                                "fontWeight": "500"
                        }
                ]
        }
},
    },
  }
</script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        
        body {
            background-color: #12131d;
            color: #e2e1f1;
            overflow-x: hidden;
        }
        
        .glass-card {
            background: #1a1b26;
            border: 1px solid #454652;
        }

        /* Animations */
        @keyframes popIn {
            0% { transform: scale(0.95); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        @keyframes slideUp {
            0% { transform: translateY(20px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        @keyframes scaleIn {
            0% { transform: scale(0); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        .animate-pop-in {
            animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }

        .animate-slide-up {
            opacity: 0;
            animation: slideUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }

        .animate-scale-in {
            opacity: 0;
            animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }

        .stagger-1 { animation-delay: 0.1s; }
        .stagger-2 { animation-delay: 0.2s; }
        .stagger-3 { animation-delay: 0.3s; }

        .active-tab-indicator {
            position: absolute;
            bottom: -1px;
            height: 2px;
            background-color: #7c8af4;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @media (prefers-reduced-motion: reduce) {
            .animate-pop-in, .animate-slide-up, .animate-scale-in, .active-tab-indicator {
                animation: none !important;
                transition: none !important;
                opacity: 1 !important;
                transform: none !important;
            }
            .path-animate {
                stroke-dasharray: none !important;
                stroke-dashoffset: 0 !important;
            }
        }

        .path-animate {
            stroke-dasharray: 1000;
            stroke-dashoffset: 1000;
        }
    </style>
<!-- Side Navigation Bar from COMPONENTS_6 -->
<aside class="fixed left-0 top-0 h-full w-[230px] bg-bg-deep flex flex-col py-main-padding z-50 animate-pop-in" style="background-color: #12131d;">
<div class="px-6 mb-10">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center">
<span class="material-symbols-outlined text-on-primary-container" style="font-variation-settings: 'FILL' 1;">cloud_done</span>
</div>
<h1 class="font-headline-lg text-headline-lg text-primary tracking-tight">SmartDesk</h1>
</div>
<p class="text-text-muted text-body-sm mt-1">Creative Workspace</p>
</div>
<nav class="flex-1 space-y-1"><a class="flex items-center gap-3 px-6 py-3 text-text-secondary hover:bg-surface-container-low hover:text-text-primary transition-colors border-l-4 border-transparent" href="#"><span class="material-symbols-outlined">dashboard</span><span class="font-body-md font-medium">Dashboard</span></a><a class="flex items-center gap-3 px-6 py-3 text-text-secondary hover:bg-surface-container-low hover:text-text-primary transition-colors border-l-4 border-transparent" href="#"><span class="material-symbols-outlined">folder_open</span><span class="font-body-md font-medium">Projects</span></a><a class="flex items-center gap-3 px-6 py-3 text-text-secondary hover:bg-surface-container-low hover:text-text-primary transition-colors border-l-4 border-transparent" href="#"><span class="material-symbols-outlined">receipt_long</span><span class="font-body-md font-medium">Invoices</span></a><a class="flex items-center gap-3 px-6 py-3 text-text-secondary hover:bg-surface-container-low hover:text-text-primary transition-colors border-l-4 border-transparent" href="#"><span class="material-symbols-outlined">group</span><span class="font-body-md font-medium">Clients</span></a><a class="flex items-center px-6 py-3 text-primary border-l-4 border-primary bg-primary/10 transition-colors" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">analytics</span><span class="font-bold">AI Analytics</span></a><a class="flex items-center gap-3 px-6 py-3 text-text-secondary hover:bg-surface-container-low hover:text-text-primary transition-colors border-l-4 border-transparent" href="#"><span class="material-symbols-outlined">settings</span><span class="font-body-md font-medium">Settings</span></a></nav>
<div class="px-4 mt-auto"><div class="flex items-center gap-3 p-4 border-t border-surface-container"><img alt="User Avatar" class="w-10 h-10 rounded-full border border-surface-container-high" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC-dLism0qhwEO0PAmixm3MX-IUXoWQsMBhUUktL0uisfMm1I51TcT_WSg6n2nZQIVMfMMwBcYiwTA13bdmi4dn2jAD-r2ik-l1SMMM0XR9Hn3l3BFIdjqfoNrTSsL64fDe_prZSeKUd6LvIo2TyUVbWqadtFOspBNdj9LJSKMujyOsMiS-FylbshCqcG5onPpxeaItU2xV-oPjR9F8iNl5Vsr2PhkbJd6wcfy4P3QSfEb1F_FuKRhTObr1Tkbv08WU9T5qzC8amYs"/><div><p class="font-body-sm font-medium text-text-primary">Alex Rivera</p><p class="font-label-caps text-text-muted">Pro User</p></div></div></div>
</aside>
<!-- Top App Bar from COMPONENTS_6 -->
<header class="fixed top-0 right-0 left-[230px] h-20 bg-background flex justify-between items-center px-main-padding z-40"><div class="flex items-center w-1/3"><div class="relative w-full max-w-md"><span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">search</span><input class="w-full bg-surface-container border-none rounded-lg pl-10 pr-4 py-2 text-text-primary focus:ring-1 focus:ring-primary" placeholder="Search analytics..." type="text"/></div></div><div class="flex items-center gap-4"><button class="w-10 h-10 rounded-lg border border-surface-variant flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-variant transition-colors"><span class="material-symbols-outlined">notifications</span></button><button class="w-10 h-10 rounded-lg border border-surface-variant flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-variant transition-colors"><span class="material-symbols-outlined">help_outline</span></button><div class="flex items-center gap-3 border-l border-outline-variant pl-6"><img alt="User profile" class="w-10 h-10 rounded-full border border-outline-variant" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC-dLism0qhwEO0PAmixm3MX-IUXoWQsMBhUUktL0uisfMm1I51TcT_WSg6n2nZQIVMfMMwBcYiwTA13bdmi4dn2jAD-r2ik-l1SMMM0XR9Hn3l3BFIdjqfoNrTSsL64fDe_prZSeKUd6LvIo2TyUVbWqadtFOspBNdj9LJSKMujyOsMiS-FylbshCqcG5onPpxeaItU2xV-oPjR9F8iNl5Vsr2PhkbJd6wcfy4P3QSfEb1F_FuKRhTObr1Tkbv08WU9T5qzC8amYs"/></div></div></header>
<!-- Main Canvas -->
<main class="ml-[230px] pt-20 min-h-screen">
<div class="p-main-padding">
<!-- Page Header -->
<div class="flex justify-between items-end mb-8">
<div>
<h2 class="font-headline-xl text-headline-xl text-text-primary mb-2">AI Analytics</h2>
<p class="text-text-secondary">Leverage machine learning to optimize your freelance business and cash flow.</p>
</div>
<div class="flex gap-2">
<button class="px-4 h-10 bg-surface-container text-text-primary border border-outline-variant rounded-lg text-body-sm font-bold hover:bg-surface-container-high transition-all flex items-center justify-center">
                        Export Report
                    </button>
<button class="px-4 h-10 bg-primary-container text-[#ffffff] rounded-lg text-body-sm font-bold hover:bg-primary-container/90 transition-all flex items-center justify-center gap-2">
<span class="material-symbols-outlined text-[18px]">bolt</span>
                        Refresh AI
                    </button>
</div>
</div>
<!-- Tabbed Interface -->
<div class="mb-8 border-b border-outline-variant flex gap-8 relative" id="tabs-container">
<button class="pb-4 text-primary font-bold transition-all" id="tab-btn-smart-pricing" onclick="switchTab('smart-pricing', this)">
                    Smart Pricing
                </button>
<button class="pb-4 text-text-muted hover:text-text-primary transition-all" id="tab-btn-payment-predictor" onclick="switchTab('payment-predictor', this)">
                    Payment Predictor
                </button>
<button class="pb-4 text-text-muted hover:text-text-primary transition-all" id="tab-btn-income-forecast" onclick="switchTab('income-forecast', this)">
                    Income Forecast
                </button>
<div class="active-tab-indicator" id="sliding-indicator" style="width: 93px; left: 0px;"></div>
</div>
<!-- Tab Content: Smart Pricing -->
<div class="grid grid-cols-12 gap-card-gap" id="tab-smart-pricing">
<div class="col-span-4 bg-surface-container-low border border-outline-variant p-6 rounded-lg">
<h3 class="font-headline-lg text-headline-lg text-text-primary mb-6 flex items-center gap-2">
<span class="material-symbols-outlined text-primary">psychology</span>
                        Project Details
                    </h3>
<form class="space-y-6">
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Project Scope</label>
<select class="w-full bg-surface-container border border-outline-variant rounded-lg py-2.5 px-4 text-text-primary focus:ring-1 focus:ring-primary focus:border-primary transition-all">
<option>Brand Identity Design</option>
<option>Full-stack Web App</option>
<option>UI/UX Audit</option>
<option>Social Media Campaign</option>
</select>
</div>
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Complexity (1-10)</label>
<input class="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary" type="range"/>
<div class="flex justify-between text-[10px] text-text-muted mt-2">
<span class="">MINIMAL</span>
<span class="">COMPLEX</span>
</div>
</div>
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Duration (Weeks)</label>
<input class="w-full bg-surface-container border border-outline-variant rounded-lg py-2.5 px-4 text-text-primary focus:ring-1 focus:ring-primary" type="number" value="4"/>
</div>
<button class="w-full h-10 bg-primary-container text-[#ffffff] rounded-lg font-bold hover:brightness-110 active:scale-95 transition-all" type="button">
                            Calculate Price Range
                        </button>
</form>
</div>
<div class="col-span-8 space-y-card-gap">
<div class="glass-card p-6 rounded-lg">
<h4 class="text-label-caps text-primary tracking-widest mb-6 uppercase">AI Pricing recommendation</h4>
<div class="grid grid-cols-3 gap-6">
<div class="p-6 bg-surface-container-lowest rounded-xl border border-outline-variant/30 text-center animate-slide-up stagger-1">
<p class="text-text-muted text-body-sm mb-2">Competitive (Low)</p>
<p class="text-headline-lg font-headline-xl text-text-primary">₹45,000</p>
<span class="inline-block mt-3 px-2 py-1 bg-status-warning/10 text-status-warning text-[10px] font-bold rounded uppercase">Market Entry</span>
</div>
<div class="p-6 bg-primary/5 rounded-xl border border-primary/30 text-center relative overflow-hidden animate-slide-up stagger-2">
<div class="absolute top-0 right-0 bg-primary text-on-primary text-[10px] px-3 py-1 font-bold rounded-bl-lg uppercase">Recommended</div>
<p class="text-primary text-body-sm mb-2">Market Sweet Spot</p>
<p class="text-headline-lg font-headline-xl text-text-primary">₹68,500</p>
<span class="inline-block mt-3 px-2 py-1 bg-primary/20 text-primary text-[10px] font-bold rounded uppercase">High Margin</span>
</div>
<div class="p-6 bg-surface-container-lowest rounded-xl border border-outline-variant/30 text-center animate-slide-up stagger-3">
<p class="text-text-muted text-body-sm mb-2">Premium (High)</p>
<p class="text-headline-lg font-headline-xl text-text-primary">₹92,000</p>
<span class="inline-block mt-3 px-2 py-1 bg-tertiary/10 text-tertiary text-[10px] font-bold rounded uppercase">Expert Level</span>
</div>
</div>
<div class="mt-8 pt-8 border-t border-outline-variant/30 animate-slide-up stagger-3">
<h5 class="text-body-lg font-bold text-text-primary mb-4 flex items-center gap-2">
<span class="material-symbols-outlined text-secondary">verified</span>
                                AI Reasoning
                            </h5>
<ul class="space-y-3 text-text-secondary text-body-md">
<li class="flex items-start gap-3">
<span class="w-1.5 h-1.5 rounded-full bg-primary mt-2"></span>
<span class="">Current market demand for <b>Brand Identity</b> is up by 12% this quarter.</span>
</li>
<li class="flex items-start gap-3">
<span class="w-1.5 h-1.5 rounded-full bg-primary mt-2"></span>
<span class="">Based on your historical projects, a 4-week timeline usually involves 65 hours of work.</span>
</li>
<li class="flex items-start gap-3">
<span class="w-1.5 h-1.5 rounded-full bg-primary mt-2"></span>
<span class="">Competitor pricing for similar complexity ranges from ₹60k to ₹85k.</span>
</li>
</ul>
</div>
</div>
</div>
</div>
<!-- Tab Content: Payment Predictor -->
<div class="hidden grid grid-cols-12 gap-card-gap" id="tab-payment-predictor">
<div class="col-span-4 bg-surface-container-low border border-outline-variant p-6 rounded-lg">
<h3 class="font-headline-lg text-headline-lg text-text-primary mb-6 flex items-center gap-2">
<span class="material-symbols-outlined text-tertiary">timeline</span>
                        Transaction Input
                    </h3>
<div class="space-y-6">
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Invoice Amount (₹)</label>
<input class="w-full bg-surface-container border border-outline-variant rounded-lg py-2.5 px-4 text-text-primary" type="text" value="1,20,000"/>
</div>
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Payment Term (Days)</label>
<select class="w-full bg-surface-container border border-outline-variant rounded-lg py-2.5 px-4 text-text-primary">
<option>Net 15</option>
<option selected="">Net 30</option>
<option>Net 45</option>
<option>Net 60</option>
</select>
</div>
<div>
<label class="block text-label-caps text-text-muted mb-2 uppercase">Client History Grade</label>
<div class="grid grid-cols-4 gap-2">
<button class="py-2 rounded-lg bg-surface-container-highest border border-outline-variant text-text-primary font-bold">A</button>
<button class="py-2 rounded-lg bg-primary-container text-on-primary-container font-bold">B</button>
<button class="py-2 rounded-lg bg-surface-container-highest border border-outline-variant text-text-primary font-bold">C</button>
<button class="py-2 rounded-lg bg-surface-container-highest border border-outline-variant text-text-primary font-bold">D</button>
</div>
</div>
<button class="w-full h-10 bg-primary-container text-[#ffffff] rounded-lg font-bold active:scale-95 transition-all">
                            Run Prediction
                        </button>
</div>
</div>
<div class="col-span-8">
<div class="glass-card p-6 rounded-lg h-full flex flex-col">
<div class="flex justify-between items-start mb-10">
<div>
<h4 class="text-headline-lg font-headline-xl text-text-primary mb-1">Likely On-Time</h4>
<p class="text-text-secondary">Based on current client liquidity and historical data.</p>
</div>
<div class="text-right">
<div class="text-headline-xl font-headline-xl text-secondary">88%</div>
<p class="text-label-caps text-text-muted uppercase tracking-widest">Confidence Score</p>
</div>
</div>
<div class="flex-1 space-y-10">
<div>
<div class="flex justify-between text-body-sm mb-3">
<span class="text-text-primary font-bold uppercase tracking-wider">Payment Probability</span>
<span class="text-secondary">Low Risk</span>
</div>
<div class="w-full h-4 bg-surface-container-highest rounded-full overflow-hidden flex">
<div class="h-full bg-secondary" style="width: 88%"></div>
<div class="h-full bg-status-warning" style="width: 8%"></div>
<div class="h-full bg-status-danger" style="width: 4%"></div>
</div>
<div class="flex justify-between mt-3 text-[11px] text-text-muted font-bold uppercase">
<span class="">ON-TIME (88%)</span>
<span class="">DELAYED 1-7 DAYS (8%)</span>
<span class="">LATE (4%)</span>
</div>
</div>
<div class="grid grid-cols-2 gap-card-gap">
<div class="p-4 bg-surface-container rounded-lg border border-outline-variant/30 animate-slide-up stagger-1">
<p class="text-label-caps text-text-muted mb-2 uppercase">Projected Payment Date</p>
<p class="text-body-lg font-bold text-text-primary">Oct 24, 2023</p>
<p class="text-body-sm text-status-warning mt-1 flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">info</span>
                                        ~2 days after Net 30
                                    </p>
</div>
<div class="p-4 bg-surface-container rounded-lg border border-outline-variant/30 animate-slide-up stagger-2">
<p class="text-label-caps text-text-muted mb-2 uppercase">Liquidity Impact</p>
<p class="text-body-lg font-bold text-text-primary">+14.2%</p>
<p class="text-body-sm text-secondary mt-1">Improves runway to 6 months</p>
</div>
</div>
</div>
</div>
</div>
</div>
<!-- Tab Content: Income Forecast -->
<div class="hidden" id="tab-income-forecast">
<div class="glass-card p-6 rounded-lg">
<div class="flex justify-between items-center mb-10">
<div>
<h3 class="font-headline-lg text-headline-lg text-text-primary">Income Forecast (Q4)</h3>
<p class="text-text-secondary">Projected revenue based on signed contracts and pipeline.</p>
</div>
<div class="flex items-center gap-4">
<div class="flex items-center gap-2">
<span class="w-3 h-3 rounded-full bg-primary"></span>
<span class="text-body-sm text-text-primary">Projected</span>
</div>
<div class="flex items-center gap-2">
<span class="w-3 h-3 rounded-full bg-outline"></span>
<span class="text-body-sm text-text-primary">Actual (2022)</span>
</div>
</div>
</div>
<!-- SVG Chart with Animation -->
<div class="relative h-64 w-full mb-8">
<svg class="w-full h-full overflow-visible" id="forecast-chart" viewbox="0 0 1000 200">
<line stroke="#2d2e42" stroke-width="1" x1="0" x2="1000" y1="0" y2="0"></line>
<line stroke="#2d2e42" stroke-width="1" x1="0" x2="1000" y1="50" y2="50"></line>
<line stroke="#2d2e42" stroke-width="1" x1="0" x2="1000" y1="100" y2="100"></line>
<line stroke="#2d2e42" stroke-width="1" x1="0" x2="1000" y1="150" y2="150"></line>
<line stroke="#2d2e42" stroke-width="1" x1="0" x2="1000" y1="200" y2="200"></line>
<path d="M0,180 L250,140 L500,160 L750,80 L1000,60 V200 H0 Z" fill="url(#grad1)" id="forecast-area" opacity="0"></path>
<defs>
<lineargradient id="grad1" x1="0%" x2="0%" y1="0%" y2="100%">
<stop offset="0%" style="stop-color:#7c8af4;stop-opacity:0.2"></stop>
<stop offset="100%" style="stop-color:#7c8af4;stop-opacity:0"></stop>
</lineargradient>
</defs>
<path class="path-animate" d="M0,170 C100,165 200,180 333,160 C466,140 600,170 733,150 C866,130 950,145 1000,140" fill="none" id="baseline-path" stroke="#6b6d85" stroke-dasharray="4" stroke-width="2"></path>
<path class="path-animate" d="M0,180 L250,140 L500,160 L750,80 L1000,60" fill="none" id="forecast-path" stroke="#7c8af4" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"></path>
<g id="chart-points">
<circle class="animate-scale-in" cx="250" cy="140" fill="#7c8af4" r="5" style="animation-delay: 0.8s;"></circle>
<circle class="animate-scale-in" cx="500" cy="160" fill="#7c8af4" r="5" style="animation-delay: 1.0s;"></circle>
<circle class="animate-scale-in" cx="750" cy="80" fill="#7c8af4" r="5" style="animation-delay: 1.2s;"></circle>
<circle class="animate-scale-in" cx="1000" cy="60" fill="#7c8af4" r="5" style="animation-delay: 1.4s;"></circle>
</g>
</svg>
<!-- Tooltip -->
<div class="absolute left-[75%] top-[10%] -translate-x-1/2 bg-surface-bright p-3 rounded-lg border border-primary shadow-2xl z-10 pointer-events-none animate-pop-in" style="animation-delay: 1.6s;">
<p class="text-[10px] text-text-muted font-bold uppercase mb-1">December Projection</p>
<p class="text-body-lg font-bold text-text-primary">₹3,45,000</p>
<p class="text-[10px] text-secondary font-bold">+22% vs Prev Month</p>
</div>
</div>
<div class="flex justify-between px-2 text-label-caps text-text-muted font-bold uppercase tracking-widest">
<span class="">September</span>
<span class="">October</span>
<span class="">November</span>
<span class="">December</span>
</div>
</div>
<div class="grid grid-cols-3 gap-card-gap mt-card-gap">
<div class="p-6 bg-surface-container rounded-lg border border-outline-variant animate-slide-up stagger-1">
<p class="text-label-caps text-text-muted uppercase mb-2">Quarterly Potential</p>
<p class="text-headline-lg font-headline-xl text-text-primary">₹8,92,000</p>
<p class="text-body-sm text-secondary mt-1">Strong Pipeline</p>
</div>
<div class="p-6 bg-surface-container rounded-lg border border-outline-variant animate-slide-up stagger-2">
<p class="text-label-caps text-text-muted uppercase mb-2">Churn Risk</p>
<p class="text-headline-lg font-headline-xl text-status-warning">Low (5%)</p>
<p class="text-body-sm text-text-muted mt-1">2 retainer renewals pending</p>
</div>
<div class="p-6 bg-surface-container rounded-lg border border-outline-variant animate-slide-up stagger-3">
<p class="text-label-caps text-text-muted uppercase mb-2">Tax Reserve</p>
<p class="text-headline-lg font-headline-xl text-status-danger">₹1,60,560</p>
<p class="text-body-sm text-text-muted mt-1">Based on 18% GST estimate</p>
</div>
</div>
</div>
</div>
</main>
<script>
        function updateIndicator(activeBtn) {
            const indicator = document.getElementById('sliding-indicator');
            if (activeBtn && indicator) {
                indicator.style.width = activeBtn.offsetWidth + 'px';
                indicator.style.left = activeBtn.offsetLeft + 'px';
            }
        }

        function animateForecast() {
            const forecastPath = document.getElementById('forecast-path');
            const baselinePath = document.getElementById('baseline-path');
            const forecastArea = document.getElementById('forecast-area');
            
            if (!forecastPath) return;

            // Reset
            forecastPath.style.transition = 'none';
            forecastPath.style.strokeDashoffset = '1000';
            baselinePath.style.transition = 'none';
            baselinePath.style.strokeDashoffset = '1000';
            forecastArea.style.opacity = '0';
            forecastArea.style.transition = 'none';

            // Trigger Reflow
            void forecastPath.offsetWidth;

            // Animate paths
            forecastPath.style.transition = 'stroke-dashoffset 1.5s ease-out';
            forecastPath.style.strokeDashoffset = '0';
            
            baselinePath.style.transition = 'stroke-dashoffset 2s ease-out';
            baselinePath.style.strokeDashoffset = '0';

            // Animate area fill
            setTimeout(() => {
                forecastArea.style.transition = 'opacity 1s ease-in';
                forecastArea.style.opacity = '1';
            }, 800);
        }

        function switchTab(tabId, btn) {
            // Hide all tabs
            document.getElementById('tab-smart-pricing').classList.add('hidden');
            document.getElementById('tab-payment-predictor').classList.add('hidden');
            document.getElementById('tab-income-forecast').classList.add('hidden');
            
            // Reset button text colors
            document.querySelectorAll('#tabs-container button').forEach(b => {
                b.classList.remove('text-primary', 'font-bold');
                b.classList.add('text-text-muted');
            });
            
            // Show active tab
            document.getElementById('tab-' + tabId).classList.remove('hidden');
            btn.classList.add('text-primary', 'font-bold');
            btn.classList.remove('text-text-muted');

            // Update sliding indicator
            updateIndicator(btn);

            // Special handling for forecast chart animation when tab becomes visible
            if (tabId === 'income-forecast') {
                animateForecast();
            }
        }

        // Initial positioning
        window.addEventListener('load', () => {
            const activeBtn = document.getElementById('tab-btn-smart-pricing');
            updateIndicator(activeBtn);
        });

        // Responsive indicator resize
        window.addEventListener('resize', () => {
            const activeBtn = document.querySelector('#tabs-container button.font-bold');
            updateIndicator(activeBtn);
        });
    </script>
</body></html>

Output as a clean numbered list. Nothing else."