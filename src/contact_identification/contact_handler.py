from contact_manager import ContactTableManager


def identify_contact(data):
    try:
        contact_table_manager = ContactTableManager()
        email = data.get('email')
        phoneNumber = data.get('phoneNumber')
        matched_contacts = contact_table_manager.get_contacts(email, phoneNumber)

        if not matched_contacts:
            primary_contact_id = contact_table_manager.create_contact(email, phoneNumber)
        else:
            primary_contact_id = matched_contacts[0][0]
            contact_table_manager.update_contact(email, phoneNumber, primary_contact_id)

        matched_contacts = contact_table_manager.get_contacts(email, phoneNumber)

        primary_contact_id = matched_contacts[0][0]
        primary_email = matched_contacts[0][2]
        primary_phoneNumber = matched_contacts[0][1]
        emails = list(set([contact[2] for contact in matched_contacts[1:]]))
        phoneNumbers = list(set([contact[1] for contact in matched_contacts[1:]]))
        secondaryContactIds = [contact[0] for contact in matched_contacts[1:]]

        response = {
            "primaryContactId": primary_contact_id,
            "emails": emails,
            "phoneNumbers": phoneNumbers,
            "secondaryContactIds": secondaryContactIds
        }

        if primary_email not in emails:
            response['emails'].insert(0, primary_email)
        if primary_phoneNumber not in phoneNumbers:
            response['phoneNumbers'].insert(0, primary_phoneNumber)

        return response
    except Exception as e:
        return None
