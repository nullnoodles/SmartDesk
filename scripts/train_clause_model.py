"""Script to train the clause classifier on sample data.

Run this once to bootstrap the NLP model with labeled examples.
You can expand the training data over time for better accuracy.

Usage:
    python scripts/train_clause_model.py
"""
import sys
sys.path.insert(0, ".")

from app.ml.clause_classifier import ClauseClassifier


# Sample training data — expand this with real contract clauses
TRAINING_DATA = [
    # IP Transfer
    ("All intellectual property rights shall be transferred to the client upon payment.", "ip_transfer"),
    ("The contractor assigns all rights, title, and interest in the work product.", "ip_transfer"),
    ("All work created shall be considered work for hire and owned by the client.", "ip_transfer"),
    ("Copyright and all related rights are assigned to the commissioning party.", "ip_transfer"),
    ("The freelancer retains no rights to the deliverables after final payment.", "ip_transfer"),

    # Payment Terms
    ("Payment shall be made within 60 days of invoice submission.", "payment_terms"),
    ("Net 30 payment terms apply to all invoices.", "payment_terms"),
    ("50% advance payment is required before work commences.", "payment_terms"),
    ("Final payment is due upon delivery and acceptance of all deliverables.", "payment_terms"),
    ("Late payments will incur a 2% monthly interest charge.", "payment_terms"),

    # Termination
    ("Either party may terminate this agreement with 30 days written notice.", "termination"),
    ("The client may terminate at any time without cause or compensation.", "termination"),
    ("No kill fee shall be payable upon early termination of this contract.", "termination"),
    ("Upon termination, all work completed to date shall be delivered.", "termination"),
    ("Cancellation after project start incurs a 25% cancellation fee.", "termination"),

    # Liability
    ("The contractor shall indemnify the client against all claims and damages.", "liability"),
    ("Total liability shall not exceed the total contract value.", "liability"),
    ("The freelancer assumes all liability for errors in the delivered work.", "liability"),
    ("Neither party shall be liable for indirect or consequential damages.", "liability"),
    ("The contractor carries professional indemnity insurance of 1 million.", "liability"),

    # Revisions
    ("Unlimited revisions are included in the project scope.", "revisions"),
    ("The project includes up to 3 rounds of revisions at no extra cost.", "revisions"),
    ("Additional revisions beyond the included rounds will be billed hourly.", "revisions"),
    ("Major revisions requiring more than 2 hours will incur additional charges.", "revisions"),
    ("The client is entitled to unlimited changes until satisfied.", "revisions"),

    # Safe / Standard
    ("The project timeline is estimated at 4 weeks from kickoff.", "safe"),
    ("Weekly progress updates will be provided via email.", "safe"),
    ("The freelancer will maintain confidentiality of all client information.", "safe"),
    ("Both parties agree to communicate professionally and respectfully.", "safe"),
    ("The project scope is defined in the attached brief document.", "safe"),
]


def main():
    print("Training clause classifier...")
    texts = [t for t, _ in TRAINING_DATA]
    labels = [l for _, l in TRAINING_DATA]

    classifier = ClauseClassifier()
    accuracy = classifier.train(texts, labels)
    print(f"Training complete. Accuracy: {accuracy * 100:.1f}%")
    print(f"Model saved to: {classifier.model_path}")

    # Quick test
    test_clauses = [
        "All rights to the design work are transferred to the buyer.",
        "Payment is due within 90 days of invoice date.",
        "The project will take approximately 2 weeks.",
    ]
    print("\nTest predictions:")
    for clause in test_clauses:
        result = classifier.classify_clause(clause)
        print(f"  [{result['category']}] ({result['confidence']}%) {clause[:60]}...")


if __name__ == "__main__":
    main()
