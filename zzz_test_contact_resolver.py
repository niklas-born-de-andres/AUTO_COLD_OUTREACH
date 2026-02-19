from services.contact_resolver import ContactResolver

resolver = ContactResolver()

# Test contact lookup
contact = resolver.get_contact("Maria", "Gonzalez")
print("=== CONTACT ===")
print(contact)



# Test team member lookup
team_member = resolver.get_team_member("Juan")
print("\n=== TEAM MEMBER ===")
print(team_member)

contact = resolver.get_contact("Juan", "Gonzalez")
print("=== CONTACT ===")
print(contact)