from services.research import ResearchService

research = ResearchService()

result = research.research(
    first_name="Elon",
    last_name="Musk",
    company="Tesla"
)

print("=== PERSON CONTEXT ===")
print(result["person_context"])
print("\n=== COMPANY CONTEXT ===")
print(result["company_context"])