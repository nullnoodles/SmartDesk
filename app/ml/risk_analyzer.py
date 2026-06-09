"""Contract risk analyzer — rule-based scoring + NLP clause classification.

Two-layer analysis:
  Layer 1: Rule-based scoring on rate, revisions, timeline
  Layer 2: Clause classifier on contract text (uses clause_classifier.py)
"""
from __future__ import annotations

import re
from typing import Any

from app.config import MARKET_RATES


class RiskAnalyzer:
    """Analyzes contract terms and produces a risk score + findings."""

    # Regex patterns for risky clauses (fallback when classifier not trained)
    # Scoring: 30+ = Critical, 20-29 = High, 10-19 = Medium, <10 = Low
    RISKY_PATTERNS = [
        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL RISKS (30+ points)
        # ═══════════════════════════════════════════════════════════════════
        
        # UNLIMITED REVISIONS (hidden variations)
        (r"unlimited\s+revision", "Unlimited revisions clause", 35),
        (r"revision.*until.*satisf", "Revisions until satisfaction (unlimited)", 35),
        (r"revision.*client.?(sole|absolute|complete)\s+discretion", "Revisions at client's discretion (unlimited)", 35),
        (r"revision.*as\s+(necessary|needed|required)", "Revisions as necessary (unlimited)", 32),
        (r"modification.*without\s+limitation", "Modifications without limitation", 35),
        (r"alterations?.*at\s+will", "Alterations at will (unlimited)", 33),
        
        # UNLIMITED LIABILITY / INDEMNITY (hidden variations)
        (r"unlimited\s+(liability|indemnif)", "Unlimited liability/indemnity", 40),
        (r"without\s+limitation.*indemnif", "Broad indemnity without limits", 38),
        (r"hold\s+harmless.*any.*claim", "Broad hold harmless clause", 35),
        (r"indemnif.*all\s+(claim|loss|damage|expense)", "Indemnify all claims (unlimited)", 35),
        (r"defend.*any.*claim.*arising", "Duty to defend all claims", 32),
        (r"shall\s+be\s+liable.*all.*consequence", "Liable for all consequences", 38),
        (r"assumption\s+of\s+risk", "Full risk assumption", 30),
        (r"waive.*claim.*client", "Waive all claims against client", 33),
        
        # ═══════════════════════════════════════════════════════════════════
        # HIGH RISKS (20-29 points)
        # ═══════════════════════════════════════════════════════════════════
        
        # IP TRANSFER (hidden variations)
        (r"work.?for.?hire", "Work-for-hire (lose IP ownership)", 28),
        (r"all\s+rights?\s*(transfer|assigned|vest|convey)", "Full IP rights transfer", 28),
        (r"exclusive\s+rights.*perpetuity", "Perpetual exclusive IP transfer", 27),
        (r"complete\s+assignment.*intellectual\s+property", "Complete IP assignment", 28),
        (r"transfer.*upon\s+(execution|signing)", "IP transfers on signing (before payment)", 28),
        (r"proprietary\s+rights.*vest.*client", "Proprietary rights vest in client", 26),
        (r"moral\s+rights.*waive", "Waive moral rights", 24),
        (r"derivative\s+works.*exclusive", "Exclusive derivative works rights", 25),
        
        # PAYMENT DELAYS (hidden variations)
        (r"payment.{0,30}(90|120|180)\s*days", "Net-90+ payment terms (3+ months wait)", 25),
        (r"net.?(90|120|180)", "Net-90+ payment terms", 25),
        (r"payable.*following.*receipt.*invoice.*(\d+).*day", "Extended payment after invoice receipt", 22),
        (r"remittance.*quarter", "Quarterly payment (3 months)", 24),
        (r"arrears", "Payment in arrears (after work)", 20),
        (r"payment.*subject.*approval", "Payment subject to approval (indefinite)", 26),
        
        # TERMINATION WITHOUT PAYMENT (hidden variations)
        (r"no\s+(kill|cancellation|termination)\s*fee", "No cancellation protection/payment", 25),
        (r"terminat.*without.*cause.*no.*payment", "Termination without payment", 28),
        (r"terminat.*at\s+will", "Termination at will (no protection)", 26),
        (r"terminat.*without.*compens", "Termination without compensation", 28),
        (r"cancel.*work.*discretion.*no.*obligation", "Cancellation at discretion, no obligation", 27),
        (r"cease.*work.*notice.*no.*further.*payment", "Cease work without further payment", 26),
        
        # OTHER HIGH RISKS
        (r"non.?compete", "Non-compete restriction", 22),
        (r"consequential\s+damages", "Liable for consequential damages", 24),
        (r"liquidated\s+damages", "Liquidated damages clause", 22),
        (r"specific\s+performance", "Specific performance (forced work)", 20),
        
        # ═══════════════════════════════════════════════════════════════════
        # MEDIUM RISKS (10-19 points)  
        # ═══════════════════════════════════════════════════════════════════
        
        (r"payment.{0,30}(60|75)\s*days", "Net-60/75 payment terms (2+ months wait)", 18),
        (r"net.?(60|75)", "Net-60/75 payment terms", 18),
        (r"indemnif", "General indemnification clause", 15),
        (r"penalty.{0,20}(late|delay)", "Late delivery penalty", 15),
        (r"revision.*reasonable", "Reasonable revisions (vague)", 14),
        (r"rights.*transfer.*upon.*payment", "IP transfer upon final payment", 12),
        (r"payment.{0,30}(30|45)\s*days", "Net-30/45 payment terms", 12),
        (r"net.?(30|45)", "Net-30/45 payment terms", 12),
        (r"audit.*books.*records", "Audit rights (administrative burden)", 10),
        (r"confidentiality.*perpetual", "Perpetual confidentiality", 10),
        
        # ═══════════════════════════════════════════════════════════════════
        # LOW RISKS (< 10 points)
        # ═══════════════════════════════════════════════════════════════════
        
        (r"approval.*sole.*discretion", "Client sole discretion on approval", 8),
        (r"satisfactory.*client.*judgment", "Satisfactory in client's judgment", 8),
    ]

    def analyze_rate(self, rate: float, project_type: str = "General") -> tuple[int, str]:
        market = MARKET_RATES.get(project_type, 500)
        if rate < market * 0.6:
            return 25, "Rate severely below market"
        elif rate < market * 0.85:
            return 15, "Rate slightly below market"
        return 0, "Rate acceptable"

    def analyze_revisions(self, rounds: int) -> tuple[int, str]:
        if rounds == 0 or rounds > 5:
            return 25, "Unlimited or excessive revisions"
        elif rounds > 3:
            return 10, "Above average revision count"
        return 0, "Revision count acceptable"

    def analyze_timeline(self, days: int) -> tuple[int, str]:
        if days < 3:
            return 25, "Extremely tight deadline"
        elif days < 7:
            return 15, "Tight deadline"
        return 0, "Timeline acceptable"

    def scan_text(self, contract_text: str) -> list[dict[str, Any]]:
        """Scan contract text for risky patterns using regex."""
        flags = []
        text_lower = contract_text.lower()
        for pattern, message, score in self.RISKY_PATTERNS:
            if re.search(pattern, text_lower):
                flags.append({"clause": message, "score": score})
        return flags

    def analyze_critical_clauses(self, contract_text: str) -> dict[str, Any]:
        """
        Deep dive analysis of the 5 most dangerous contract clauses for freelancers.
        Returns individual scores for: indemnity, payment_terms, ip_transfer, 
        termination, revision_scope.
        """
        text_lower = contract_text.lower()
        results = {}
        
        # 1. Indemnity Clause (most dangerous)
        indemnity_score = 0
        indemnity_findings = []
        
        # Check for unlimited/broad indemnity (CRITICAL)
        if re.search(r"unlimited\s+(liability|indemnif)", text_lower):
            indemnity_score = 40
            indemnity_findings.append("⚠️ UNLIMITED liability - you could be bankrupted")
        elif re.search(r"without\s+limitation.*indemnif", text_lower):
            indemnity_score = 38
            indemnity_findings.append("⚠️ Broad indemnity without caps or limits")
        elif re.search(r"indemnif.*all\s+(claim|loss|damage|expense)", text_lower):
            indemnity_score = 35
            indemnity_findings.append("⚠️ Must indemnify ALL claims (unlimited scope)")
        elif re.search(r"defend.*any.*claim.*arising", text_lower):
            indemnity_score = 32
            indemnity_findings.append("⚠️ Duty to defend ANY claim (expensive)")
        elif re.search(r"shall\s+be\s+liable.*all.*consequence", text_lower):
            indemnity_score = 38
            indemnity_findings.append("⚠️ Liable for all consequences (unlimited)")
        elif re.search(r"hold\s+harmless", text_lower):
            indemnity_score = 25
            indemnity_findings.append("Hold harmless clause present")
        elif re.search(r"assumption\s+of\s+risk", text_lower):
            indemnity_score = 30
            indemnity_findings.append("⚠️ Full assumption of risk clause")
        elif re.search(r"waive.*claim.*client", text_lower):
            indemnity_score = 33
            indemnity_findings.append("⚠️ Must waive all claims against client")
        elif re.search(r"indemnif", text_lower):
            indemnity_score = 10
            indemnity_findings.append("Standard indemnity clause")
        else:
            indemnity_findings.append("✓ No indemnity clause found")
        
        results["indemnity"] = {
            "score": indemnity_score,
            "findings": indemnity_findings,
            "risk": "CRITICAL" if indemnity_score >= 30 else "HIGH" if indemnity_score >= 20 else "MEDIUM" if indemnity_score > 0 else "LOW"
        }
        
        # 2. Payment Terms
        payment_score = 0
        payment_findings = []
        
        # Check for extended payment terms
        if re.search(r"payment.{0,30}(120|180|240)\s*days", text_lower) or re.search(r"net.?(120|180|240)", text_lower):
            payment_score = 30
            payment_findings.append("⚠️ Net-120+ (4+ months wait for payment)")
        elif re.search(r"payment.{0,30}(90|net.?90)", text_lower) or re.search(r"remittance.*quarter", text_lower):
            payment_score = 25
            payment_findings.append("⚠️ Net-90 / Quarterly (3 months wait)")
        elif re.search(r"payment.{0,30}(60|75|net.?60|net.?75)", text_lower):
            payment_score = 18
            payment_findings.append("Net-60/75 (2+ months wait)")
        elif re.search(r"payment.{0,30}(30|45|net.?30|net.?45)", text_lower):
            payment_score = 10
            payment_findings.append("Net-30/45 (standard but long)")
        
        # Check for payment subject to approval (HIDDEN DELAY)
        if re.search(r"payment.*subject.*approval", text_lower):
            payment_score += 15
            payment_findings.append("⚠️ Payment subject to approval (indefinite delay)")
        
        # Check for payment in arrears
        if re.search(r"arrears|following.*receipt.*invoice", text_lower):
            payment_score += 10
            payment_findings.append("Payment in arrears (after work complete)")
        
        if not payment_findings or payment_score == 0:
            payment_findings.append("✓ No extended payment terms found")
        
        # Check for upfront payment (GOOD)
        if re.search(r"(50|100)%.*upfront|advance.*payment|deposit|retainer", text_lower):
            payment_score = max(0, payment_score - 10)
            payment_findings.append("✓ Upfront payment/deposit/retainer mentioned")
        
        results["payment_terms"] = {
            "score": payment_score,
            "findings": payment_findings,
            "risk": "CRITICAL" if payment_score >= 30 else "HIGH" if payment_score >= 20 else "MEDIUM" if payment_score >= 10 else "LOW"
        }
        
        # 3. IP Transfer
        ip_score = 0
        ip_findings = []
        
        # Check for work-for-hire (worst case)
        if re.search(r"work.?for.?hire", text_lower):
            ip_score = 35
            ip_findings.append("⚠️ WORK-FOR-HIRE - you lose all IP ownership")
        # Check for IP transfer before payment
        elif re.search(r"(transfer|vest|convey|assign).*upon.*(signing|execution)|upon.*(signing|execution).*(transfer|vest)", text_lower):
            ip_score = 30
            ip_findings.append("⚠️ IP transfers on signing (BEFORE payment)")
        # Check for complete assignment
        elif re.search(r"complete\s+assignment.*intellectual\s+property", text_lower):
            ip_score = 28
            ip_findings.append("⚠️ Complete IP assignment to client")
        # Check for proprietary rights vesting
        elif re.search(r"proprietary\s+rights.*vest.*client", text_lower):
            ip_score = 26
            ip_findings.append("⚠️ All proprietary rights vest in client")
        # Check for all rights transfer (general)
        elif re.search(r"all\s+rights?\s*(transfer|assigned|vest|convey)", text_lower):
            ip_score = 25
            ip_findings.append("Full IP rights transfer to client")
        # Check for perpetual exclusive rights
        elif re.search(r"exclusive\s+rights.*perpetuity|perpetual.*exclusive", text_lower):
            ip_score = 28
            ip_findings.append("⚠️ Perpetual exclusive rights (can never reuse)")
        # Check for derivative works
        elif re.search(r"derivative\s+works.*exclusive", text_lower):
            ip_score = 25
            ip_findings.append("Client owns exclusive derivative works rights")
        # Check for moral rights waiver
        elif re.search(r"moral\s+rights.*waive", text_lower):
            ip_score += 15
            ip_findings.append("⚠️ Must waive moral rights (attribution, integrity)")
        
        # Check for you retaining rights (GOOD)
        if re.search(r"retain.*rights|limited.*license|non.?exclusive.*license", text_lower):
            ip_score = max(5, ip_score - 10)
            ip_findings.append("✓ You retain some rights or grant limited license")
        
        if not ip_findings:
            ip_findings.append("✓ No explicit IP transfer found")
        
        results["ip_transfer"] = {
            "score": ip_score,
            "findings": ip_findings,
            "risk": "CRITICAL" if ip_score >= 30 else "HIGH" if ip_score >= 20 else "MEDIUM" if ip_score >= 10 else "LOW"
        }
        
        # 4. Termination Clause
        termination_score = 0
        termination_findings = []
        
        # Check for termination without compensation (worst)
        if re.search(r"terminat.*without.*(cause|notice).*no.*(payment|compens)", text_lower):
            termination_score = 30
            termination_findings.append("⚠️ Client can terminate without paying anything")
        # Check for termination at will
        elif re.search(r"terminat.*at\s+will|cancel.*discretion.*no.*obligation", text_lower):
            termination_score = 28
            termination_findings.append("⚠️ Termination at will, no protection")
        # Check for cease work without payment
        elif re.search(r"cease.*work.*no.*further.*payment", text_lower):
            termination_score = 26
            termination_findings.append("⚠️ Can cease work without further payment")
        # Check for no kill fee (general)
        elif re.search(r"no\s+(kill|cancellation|termination)\s*fee", text_lower):
            termination_score = 25
            termination_findings.append("⚠️ No cancellation fee/protection")
        
        # Check for kill fee present (GOOD)
        if re.search(r"kill.*fee|cancellation.*(payment|fee)|terminat.*(payment|fee)", text_lower):
            termination_score = max(0, termination_score - 20)
            termination_findings.append("✓ Kill fee / cancellation payment present")
        # Check for pro-rata payment (GOOD)
        elif re.search(r"pro.?rata.*payment|partial.*completion|work.*completed.*to.*date", text_lower):
            termination_score = max(0, termination_score - 15)
            termination_findings.append("✓ Pro-rata payment for work completed")
        
        if not termination_findings:
            termination_score = 15
            termination_findings.append("Termination terms unclear or not specified")
        
        results["termination"] = {
            "score": termination_score,
            "findings": termination_findings,
            "risk": "CRITICAL" if termination_score >= 30 else "HIGH" if termination_score >= 20 else "MEDIUM" if termination_score >= 10 else "LOW"
        }
        
        # 5. Revision Scope
        revision_score = 0
        revision_findings = []
        
        # Check for unlimited revisions (explicit)
        if re.search(r"unlimited\s+revision", text_lower):
            revision_score = 40
            revision_findings.append("⚠️ UNLIMITED REVISIONS - project killer!")
        # Check for "until satisfaction" (hidden unlimited)
        elif re.search(r"revision.*until.*satisf|modification.*until.*accept", text_lower):
            revision_score = 38
            revision_findings.append("⚠️ Revisions until satisfaction (UNLIMITED)")
        # Check for "at client discretion" (hidden unlimited)
        elif re.search(r"revision.*(client|sole|absolute|complete).*discretion", text_lower):
            revision_score = 35
            revision_findings.append("⚠️ Revisions at client's discretion (UNLIMITED)")
        # Check for "as necessary" (hidden unlimited)
        elif re.search(r"revision.*as\s+(necessary|needed|required|deemed)", text_lower):
            revision_score = 32
            revision_findings.append("⚠️ Revisions as necessary (UNLIMITED)")
        # Check for "modifications without limitation"
        elif re.search(r"modification.*without\s+limitation|alterations?.*at\s+will", text_lower):
            revision_score = 35
            revision_findings.append("⚠️ Modifications without limitation (UNLIMITED)")
        # Check for "reasonable revisions" (vague)
        elif re.search(r"reasonable\s+revision", text_lower):
            revision_score = 15
            revision_findings.append("'Reasonable revisions' (vague, no number)")
        # Check for "satisfactory in client's judgment" (hidden unlimited)
        elif re.search(r"satisfactory.*client.*judgment|acceptable.*client.*opinion", text_lower):
            revision_score = 30
            revision_findings.append("⚠️ Satisfactory in client's judgment (UNLIMITED)")
        # Check for specific number of rounds
        elif re.search(r"(\d+)\s+revision", text_lower):
            match = re.search(r"(\d+)\s+revision", text_lower)
            rounds = int(match.group(1))
            if rounds <= 2:
                revision_score = 0
                revision_findings.append(f"✓ {rounds} revision round(s) specified (fair)")
            elif rounds <= 4:
                revision_score = 8
                revision_findings.append(f"{rounds} revision rounds (above average)")
            else:
                revision_score = 20
                revision_findings.append(f"⚠️ {rounds} revision rounds (excessive)")
        else:
            revision_score = 12
            revision_findings.append("Revision scope not clearly specified")
        
        results["revision_scope"] = {
            "score": revision_score,
            "findings": revision_findings,
            "risk": "CRITICAL" if revision_score >= 30 else "HIGH" if revision_score >= 20 else "MEDIUM" if revision_score >= 10 else "LOW"
        }
        
        # Overall summary
        total_critical_score = sum(r["score"] for r in results.values())
        results["summary"] = {
            "total_score": total_critical_score,
            "risk_level": "CRITICAL" if total_critical_score >= 100 else "HIGH" if total_critical_score >= 60 else "MEDIUM" if total_critical_score >= 30 else "LOW",
            "critical_count": sum(1 for r in results.values() if r.get("risk") == "CRITICAL"),
            "high_count": sum(1 for r in results.values() if r.get("risk") == "HIGH"),
        }
        
        return results

    def full_analysis(
        self,
        hourly_rate: float,
        revisions: int,
        timeline_days: int,
        project_type: str = "General",
        contract_text: str = "",
    ) -> dict[str, Any]:
        """Run complete risk analysis. Returns score, level, and findings."""
        total = 0
        findings = []

        # Rate check
        rs, rm = self.analyze_rate(hourly_rate, project_type)
        total += rs
        findings.append({"check": "Rate", "result": rm, "score": rs})

        # Revisions check
        vs, vm = self.analyze_revisions(revisions)
        total += vs
        findings.append({"check": "Revisions", "result": vm, "score": vs})

        # Timeline check
        ts, tm = self.analyze_timeline(timeline_days)
        total += ts
        findings.append({"check": "Timeline", "result": tm, "score": ts})

        # Text scan
        if contract_text:
            for flag in self.scan_text(contract_text):
                total += flag["score"]
                findings.append({"check": "Clause", "result": flag["clause"], "score": flag["score"]})

        level = "HIGH" if total >= 50 else "MEDIUM" if total >= 25 else "LOW"

        return {
            "total_score": total,
            "risk_level": level,
            "findings": findings,
        }
