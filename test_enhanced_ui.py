"""Test script for Enhanced Contract Risk Analyzer UI."""
from __future__ import annotations

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.risk_analyzer import RiskAnalyzer


def test_dangerous_contract():
    """Test analyzer with dangerous contract."""
    print("\n" + "="*70)
    print("TEST 1: DANGEROUS CONTRACT")
    print("="*70)
    
    # Read dangerous contract
    with open("test_contracts/dangerous_contract.txt", "r", encoding="utf-8") as f:
        contract_text = f.read()
    
    analyzer = RiskAnalyzer()
    
    # Test full analysis
    print("\n1. Full Analysis:")
    result = analyzer.full_analysis(
        hourly_rate=300,  # Below market
        revisions=10,     # Excessive
        timeline_days=2,  # Extremely tight
        project_type="Design",
        contract_text=contract_text,
    )
    
    print(f"   Total Score: {result['total_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Findings: {len(result['findings'])} issues detected")
    
    # Test critical clause analysis
    print("\n2. Critical Clause Analysis:")
    critical = analyzer.analyze_critical_clauses(contract_text)
    
    print(f"\n   Overall Critical Score: {critical['summary']['total_score']}")
    print(f"   Overall Risk Level: {critical['summary']['risk_level']}")
    print(f"   Critical Issues: {critical['summary']['critical_count']}")
    print(f"   High Issues: {critical['summary']['high_count']}")
    
    print("\n   Individual Risk Areas:")
    for key in ["indemnity", "payment_terms", "ip_transfer", "termination", "revision_scope"]:
        if key in critical:
            data = critical[key]
            print(f"\n   {key.upper().replace('_', ' ')}:")
            print(f"      Score: {data['score']}")
            print(f"      Risk: {data['risk']}")
            print(f"      Findings: {len(data['findings'])}")
            for finding in data['findings'][:3]:  # Show first 3
                print(f"         - {finding}")
    
    # Validation
    assert result['total_score'] > 100, "Dangerous contract should score >100"
    assert critical['summary']['total_score'] > 100, "Critical analysis should score >100"
    assert critical['summary']['critical_count'] >= 3, "Should have >=3 critical issues"
    
    print("\n   ✅ Dangerous contract correctly identified as CRITICAL")


def test_safe_contract():
    """Test analyzer with safe contract."""
    print("\n" + "="*70)
    print("TEST 2: SAFE CONTRACT")
    print("="*70)
    
    # Read safe contract
    with open("test_contracts/safe_contract.txt", "r", encoding="utf-8") as f:
        contract_text = f.read()
    
    analyzer = RiskAnalyzer()
    
    # Test full analysis
    print("\n1. Full Analysis:")
    result = analyzer.full_analysis(
        hourly_rate=600,  # Above market
        revisions=2,      # Reasonable
        timeline_days=21, # Acceptable
        project_type="Design",
        contract_text=contract_text,
    )
    
    print(f"   Total Score: {result['total_score']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Findings: {len(result['findings'])} issues detected")
    
    # Test critical clause analysis
    print("\n2. Critical Clause Analysis:")
    critical = analyzer.analyze_critical_clauses(contract_text)
    
    print(f"\n   Overall Critical Score: {critical['summary']['total_score']}")
    print(f"   Overall Risk Level: {critical['summary']['risk_level']}")
    print(f"   Critical Issues: {critical['summary']['critical_count']}")
    print(f"   High Issues: {critical['summary']['high_count']}")
    
    print("\n   Individual Risk Areas:")
    for key in ["indemnity", "payment_terms", "ip_transfer", "termination", "revision_scope"]:
        if key in critical:
            data = critical[key]
            print(f"\n   {key.upper().replace('_', ' ')}:")
            print(f"      Score: {data['score']}")
            print(f"      Risk: {data['risk']}")
            print(f"      Findings: {len(data['findings'])}")
            for finding in data['findings'][:2]:  # Show first 2
                print(f"         - {finding}")
    
    # Validation
    assert result['total_score'] < 50, "Safe contract should score <50"
    assert critical['summary']['total_score'] < 50, "Critical analysis should score <50"
    assert critical['summary']['critical_count'] == 0, "Should have 0 critical issues"
    
    print("\n   ✅ Safe contract correctly identified as LOW/MEDIUM risk")


def test_ui_component():
    """Test that UI components exist and can be imported."""
    print("\n" + "="*70)
    print("TEST 3: UI COMPONENT VERIFICATION")
    print("="*70)
    
    try:
        from app.ui.pages.contracts_page import ContractsPage, RiskCriteriaCard
        print("\n   ✅ ContractsPage imported successfully")
        print("   ✅ RiskCriteriaCard imported successfully")
        
        # Check for key methods
        assert hasattr(ContractsPage, '_build_ui'), "ContractsPage should have _build_ui"
        assert hasattr(ContractsPage, '_analyze'), "ContractsPage should have _analyze"
        assert hasattr(ContractsPage, 'refresh'), "ContractsPage should have refresh"
        assert hasattr(RiskCriteriaCard, 'set_result'), "RiskCriteriaCard should have set_result"
        
        print("   ✅ All required methods present")
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        raise


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ENHANCED CONTRACT RISK ANALYZER UI - TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Dangerous contract
        test_dangerous_contract()
        
        # Test 2: Safe contract
        test_safe_contract()
        
        # Test 3: UI components
        test_ui_component()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print("\n   ✅ All tests passed!")
        print("\n   The enhanced UI is ready to deploy:")
        print("      1. Run: python main.py")
        print("      2. Navigate to Contracts page")
        print("      3. Upload test_contracts/dangerous_contract.txt")
        print("      4. Verify visual layout matches design")
        print("      5. Test with test_contracts/safe_contract.txt")
        print("\n" + "="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n   ❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
