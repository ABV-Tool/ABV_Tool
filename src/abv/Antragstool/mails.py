from django.core.mail import send_mail

# Sendet eine Mail an den Antragssteller, dass sein Antrag eingegangen ist
def mailAstellerEingangsbestaetigung(asteller, antrag):
    send_mail(
        f"Dein { antrag.typID.typName } ist eingegeangen!",
        f"Hi { asteller.astellerVorname },\n\nDein Antrag ist bei uns eingegangen und wird in der nächsten Sitzung des Referats behandelt.\n\nViele Grüße,\nDein StuRa-Team",
        "abv@stura.htw-dresden.de",
        [asteller.astellerEmail],
        fail_silently=False,
    )

# Sendet eine Mail an den Antragssteller, dass sein Antrag vertagt wurde und in der nächsten Sitzung behandelt wird
def mailAstellerAntragVertagt(asteller, antrag):
    pass

# Sendet eine Mail an das Referat, dass ein neuer Antrag eingegangen ist
def mailReferatAntragEingegangen(referat, antrag):
    pass

# Sendet eine Mail an das Referat, dass ein neuer Eilantrag eingegangen ist
def mailReferatEilantragEingegangen(referat, antrag):
    pass
    