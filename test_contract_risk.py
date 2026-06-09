"""Test the enhanced Contract Risk Analyzer with real-world examples."""

from app.ml.risk_analyzer import RiskAnalyzer

# Test contract with ALL 5 critical risks
DANGEROUS_CONTRACT = """
FREELANCE DESIGN AGREEMENT

1. WORK-FOR-HIRE: All work created under this agreement is work-for-hire,
   and all rights, title, and interest shall vest in Client upon signing.

2. PAYMENT TERMS: Payment shall be made net-90 days from invoice date.

3. REVISIONS: Contractor shall provide unlimited revisions until Client
   is satisfied with the final deliverables.

4. INDEMNIFICATION: Contractor shall indemnify, defend, and hold harmless
   Client without limitation from any and all claims, damages, losses, or
   expenses arising from or related to the work performed.

5. TERMINATION: Client may terminate this agreement at any time without
   cause and without payment for work completed.
"""

# Safe contract with protections
SAFE_CONTRACT = """
FREELANCE DESIGN AGREEMENT

1. LICENSE: Client receives a non-exclusive, perpetual license to use the
   work. Contractor retains all rights and may use the work in portfolio.

2. PAYMENT: 50% upfront deposit, 50% within 14 days of final delivery.

3. REVISIONS: Two (2) rounds of revisions are included in the quoted price.

4. TERMINATION: Either party may terminate with 7 days written notice.
   Pro-rata payment shall be made for all work completed to date.

5. LIABILITY: Contractor's liability is limited to the project fee.
"""

def test_dangerous_contract():
    """Test detection of all 5 critical risks."""
    print("=" * 70)
    print("TEST 1: DANGEROUS CONTRACT (Should be CRITICAL)")
    print("=" * 70)
    
    analyzer = RiskAnalyzer()
    
    # Full analysis
    result = analyzer.full_analysis(
        hourly_rate=300,  # Below market (₹500)
        revisions=0,      # Indicates unlimited
        timeline_days=5,  # Tight
        project_type="Design",
        contract_text=DANGEROUS_CONTRACT
    )
    
    print(f"\n📊 Overall Risk Analysis:")
    print(f"   Total Score: {result['total_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"\n📝 Findings:")
    for finding in result['findings']:
        print(f"   • {finding['check']}: {finding['result']} ({finding['score']} pts)")
    
    # Critical clause analysis
    critical = analyzer.analyze_critical_clauses(DANGEROUS_CONTRACT)
    
    print(f"\n🔍 Critical Clause Analysis:")
    print(f"   Critical Issues: {critical['summary']['critical_count']}")
    print(f"   High Issues: {critical['summary']['high_count']}")
    print(f"   Total Score: {critical['summary']['total_score']}")
    
    for clause_name, clause_data in critical.items():
        if clause_name == "summary":
            continue
        print(f"\n   {clause_name.upper().replace('_', ' ')}:")
        print(f"   Risk: {clause_data['risk']} ({clause_data['score']} pts)")
        for finding in clause_data['findings']:
            print(f"      - {finding}")
    
    print(f"\n{'❌ DO NOT SIGN THIS CONTRACT' if result['risk_level'] == 'CRITICAL' else '⚠️  PROCEED WITH CAUTION'}")
    print()

def test_safe_contract():
    """Test that safe contract scores low."""
    print("=" * 70)
    print("TEST 2: SAFE CONTRACT (Should be LOW)")
    print("=" * 70)
    
    analyzer = RiskAnalyzer()
    
    result = analyzer.full_analysis(
        hourly_rate=600,  # Above market
        revisions=2,      # Reasonable
        timeline_days=21, # Comfortable
        project_type="Design",
        contract_text=SAFE_CONTRACT
    )
    
    print(f"\n📊 Overall Risk Analysis:")
    print(f"   Total Score: {result['total_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    
    critical = analyzer.analyze_critical_clauses(SAFE_CONTRACT)
    
    print(f"\n🔍 Critical Clause Analysis:")
    print(f"   Critical Issues: {critical['summary']['critical_count']}")
    print(f"   High Issues: {critical['summary']['high_count']}")
    print(f"   Total Score: {critical['summary']['total_score']}")
    
    for clause_name, clause_data in critical.items():
        if clause_name == "summary":
            continue
        print(f"\n   {clause_name.upper().replace('_', ' ')}:")
        print(f"   Risk: {clause_data['risk']} ({clause_data['score']} pts)")
        for finding in clause_data['findings']:
            print(f"      - {finding}")
    
    print(f"\n✅ {'ACCEPTABLE RISK' if result['risk_level'] in ['LOW', 'MEDIUM'] else 'STILL RISKY'}")
    print()

def test_individual_patterns():
    """Test individual pattern detection."""
    print("=" * 70)
    print("TEST 3: INDIVIDUAL PATTERN DETECTION")
    print("=" * 70)
    
    analyzer = RiskAnalyzer()
    
    patterns_to_test = [
        ("unlimited liability", "Unlimited liability should score 35+"),
        ("payment within 90 days", "Net-90 should score 25"),
        ("work-for-hire", "Work-for-hire should score 35"),
        ("no kill fee", "No kill fee should score 25"),
        ("unlimited revisions", "Unlimited revisions should score 35+"),
    ]
    
    for text, expected in patterns_to_test:
        critical = analyzer.analyze_critical_clauses(text)
        total = critical['summary']['total_score']
        print(f"\n   '{text}'")
        print(f"   Expected: {expected}")
        print(f"   Result: {total} pts, {critical['summary']['risk_level']} risk")

if __name__ == "__main__":
    print("\n🧪 SmartDesk Contract Risk Analyzer - Enhancement Tests\n")
    
    test_dangerous_contract()
    print("\n")
    test_safe_contract()
    print("\n")
    test_individual_patterns()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 70)
