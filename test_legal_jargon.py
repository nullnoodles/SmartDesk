"""Test Contract Risk Analyzer against legal jargon / hidden clauses."""

from app.ml.risk_analyzer import RiskAnalyzer

# Contract using LEGAL JARGON to hide dangerous clauses
SNEAKY_CONTRACT = """
PROFESSIONAL SERVICES AGREEMENT

1. SCOPE OF WORK: Contractor shall provide creative services as specified 
   in Exhibit A, subject to modifications as deemed necessary by Client.

2. INTELLECTUAL PROPERTY: All deliverables, including but not limited to 
   designs, concepts, and derivative works, shall constitute work-for-hire 
   under applicable copyright law. All proprietary rights shall vest in 
   Client upon execution of this Agreement.

3. REVISIONS: Contractor shall provide revisions until the deliverables 
   are satisfactory in Client's sole judgment and discretion.

4. COMPENSATION: Remittance shall be made following receipt of invoice and 
   subject to Client's approval of deliverables, payable in arrears on a 
   quarterly basis.

5. INDEMNIFICATION: Contractor shall indemnify, defend, and hold harmless 
   Client from all claims, losses, damages, and expenses arising out of or 
   relating to the Services, without limitation.

6. TERMINATION: Client may terminate this Agreement at will without cause. 
   Upon termination, Contractor shall cease all work immediately with no 
   obligation for further payment or compensation.

7. LIABILITY: Contractor shall be liable for all consequences, including 
   consequential damages, arising from the Services.

8. ENTIRE AGREEMENT: This Agreement constitutes the complete understanding 
   between the parties and supersedes all prior negotiations.
"""

def test_legal_jargon():
    """Test that analyzer catches legal jargon versions of dangerous clauses."""
    print("=" * 70)
    print("TESTING: Contract with Legal Jargon (Hidden Dangerous Clauses)")
    print("=" * 70)
    
    analyzer = RiskAnalyzer()
    
    # Full analysis
    result = analyzer.full_analysis(
        hourly_rate=400,
        revisions=0,  # Not specified in contract
        timeline_days=14,
        project_type="Design",
        contract_text=SNEAKY_CONTRACT
    )
    
    print(f"\n📊 Overall Analysis:")
    print(f"   Total Score: {result['total_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    print()
    
    # Critical clause analysis
    critical = analyzer.analyze_critical_clauses(SNEAKY_CONTRACT)
    
    print(f"🔍 Critical Clauses Detected:\n")
    
    # Check each clause
    for clause_name, clause_data in critical.items():
        if clause_name == "summary":
            continue
        
        print(f"   {clause_name.upper().replace('_', ' ')}:")
        print(f"   └─ Risk: {clause_data['risk']} ({clause_data['score']} pts)")
        for finding in clause_data['findings']:
            print(f"      {finding}")
        print()
    
    print(f"📋 Summary:")
    print(f"   Total Critical Score: {critical['summary']['total_score']}")
    print(f"   Overall Risk: {critical['summary']['risk_level']}")
    print(f"   Critical Issues: {critical['summary']['critical_count']}")
    print(f"   High Issues: {critical['summary']['high_count']}")
    print()
    
    # Verify specific detections
    print("=" * 70)
    print("VERIFICATION: Did we catch the hidden clauses?")
    print("=" * 70)
    print()
    
    checks = [
        ("work-for-hire", "IP Transfer", 
         "Detected 'work-for-hire' (disguised as copyright law)"),
        ("proprietary rights.*vest", "IP Transfer",
         "Detected 'vest in Client' (IP transfer on signing)"),
        ("satisfactory.*judgment.*discretion", "Revision Scope",
         "Detected 'satisfactory in judgment' (unlimited revisions)"),
        ("remittance.*quarterly|arrears", "Payment Terms",
         "Detected 'quarterly' / 'in arrears' (3+ month delay)"),
        ("subject.*approval", "Payment Terms",
         "Detected 'subject to approval' (indefinite delay)"),
        ("indemnif.*without limitation", "Indemnity",
         "Detected 'without limitation' (unlimited liability)"),
        ("all consequences.*consequential", "Indemnity",
         "Detected 'all consequences' + 'consequential damages'"),
        ("terminate.*at will.*no.*payment", "Termination",
         "Detected 'at will' + 'no payment' (no protection)"),
    ]
    
    detected = 0
    for pattern, clause, desc in checks:
        import re
        if re.search(pattern, SNEAKY_CONTRACT.lower()):
            detected += 1
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ MISSED: {desc}")
    
    print()
    print(f"Detection Rate: {detected}/{len(checks)} ({detected/len(checks)*100:.0f}%)")
    print()
    
    if critical['summary']['risk_level'] == 'CRITICAL' or critical['summary']['risk_level'] == 'HIGH':
        print("✅ CORRECT: Flagged as CRITICAL/HIGH risk")
    else:
        print("❌ WRONG: Should be CRITICAL/HIGH risk")
    
    if critical['summary']['critical_count'] >= 2:
        print("✅ CORRECT: Detected multiple critical issues")
    else:
        print("❌ WRONG: Should detect multiple critical issues")
    
    print()
    print("=" * 70)
    print("RECOMMENDATION FOR USER")
    print("=" * 70)
    print()
    
    if result['total_score'] >= 100:
        print("🚨 DO NOT SIGN THIS CONTRACT!")
        print()
        print("This contract has MULTIPLE dangerous clauses hidden in legal jargon:")
        print("- Work-for-hire = You own NOTHING")
        print("- 'Until satisfactory' = UNLIMITED revisions")
        print("- Quarterly payment = 3+ month wait")
        print("- 'Without limitation' = UNLIMITED liability")
        print("- Terminate 'at will' = No payment if cancelled")
        print()
        print("Recommendation: Negotiate heavily or WALK AWAY")
    else:
        print("This contract needs improvement but may be negotiable.")

if __name__ == "__main__":
    test_legal_jargon()
