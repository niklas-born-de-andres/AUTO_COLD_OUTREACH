from services.research import ResearchService

research = ResearchService()

result = research.research(
    first_name="Kevin",
    last_name="Berghoff",
    company="QuantumDiamonds"
)

print("=== PERSON CONTEXT ===")
print(result["person_context"])
print("\n=== COMPANY CONTEXT ===")
print(result["company_context"])

