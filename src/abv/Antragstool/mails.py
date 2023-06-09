from django.core.mail import send_mail, EmailMessage
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template

from abv.settings import EMAIL_TOOL


# TODO: Überlegungen zu weiteren E-Mails machen & StuRa fragen, ob die E-Mails so in Ordnung sind

#----------{ E-Mails an Antragssteller }----------#

# TODO: Binde Option ein, dass der Antragsteller seinen Antrag mit einem Token im Nachhinein bearbeiten kann
def mailAstellerEingangsbestaetigung(asteller, antrag):
    """
    Sende dem Antragssteller eine Eingangsbestätigung für seinen Antrag
    """
    message = get_template("emails/antrag_bestaetigung.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag ist eingegangen!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[asteller.astellerEmail],
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


def mailAstellerVertagung(asteller, antrag):
    """
    Sende dem Antragssteller eine Information über die Vertagung seines Antrags
    """
    # TODO: E-Mail Nachricht anpassen
    message = get_template("emails/antrag_vertagung.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag wurde vertagt!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[asteller.astellerEmail],
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


def mailAstellerErgenis(asteller, antrag):
    """
    Sende dem Antragssteller eine Information über das Ergebnis seines Antrags
    """
    # TODO: E-Mail Nachricht anpassen
    message = get_template("emails/antrag_ergebnis.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag wurde beschlossen!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[asteller.astellerEmail],
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


#----------{ E-Mails an Referate }----------#

# TODO: Prüfe, ob der Antrag ein Eilantrag ist und verschicke eine andere E-Mail
def mailReferatAntragEingegangen(referat, antrag):
    """
    Sende dem Referat eine Information über den Eingang eines neuen Antrags
    """
    # TODO: E-Mail Nachricht anpassen
    pass

