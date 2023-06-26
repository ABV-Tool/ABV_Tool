from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.template.loader import get_template
from django.db.models.signals import pre_save, post_save

from abv.settings import EMAIL_TOOL

from .models import Antrag, Referat, Sitzung


#----------{ E-Mails an Antragssteller }----------#

def mailAstellerEingangsbestaetigung(antrag: Antrag):
    """
    Sende dem Antragssteller eine Eingangsbestätigung für seinen Antrag
    """
    print("Mail => Eingangsbestätigung an Antragsteller: ", antrag.astellerID.astellerName)
    
    message = get_template("emails/asteller/eingangsbestaetigung_antrag.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag ist bei uns eingegangen!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[antrag.astellerID.astellerEmail], # type: ignore
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


def mailAstellerVertagungAntrag(antrag: Antrag):
    """
    Sende dem Antragssteller eine Information über die Vertagung seines Antrags in eine andere Sitzung
    Signal wird ausgelöst, wenn der Antrag in eine andere Sitzung vertagt wird
    """
    print("Mail => Vertagung Antrag an Antragsteller: ", antrag.astellerID.astellerName)
    
    message = get_template("emails/asteller/vertagung_antrag.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag wurde in eine andere Sitzung vertagt!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[antrag.astellerID.astellerEmail], # type: ignore
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


def mailAstellerVertagungSitzung(sitzung: Sitzung):
    """
    Sende dem Antragssteller eine Information über die Vertagung der Sitzung, in welcher sein Antrag ursprünglich behandelt werden sollte.
    """
    antraege_sitzung = Antrag.objects.filter(sitzID=sitzung.sitzID)
    print("Mail => Vertagung Sitzung an alle Antragsteller: ", [antrag.astellerID.astellerEmail for antrag in antraege_sitzung])
    
    message = get_template("emails/asteller/vertagung_sitzung.html").render({
        'sitzung': sitzung,
        'antraege': antraege_sitzung
    })
    mail = EmailMessage(
        subject="Die Sitzung deines Antrages wurde vertagt!",
        body=message,
        from_email=EMAIL_TOOL,
        # Sende eine E-Mail an alle Antragssteller, deren Anträge in der vertagten Sitzung behandelt werden sollten
        to=[antrag.astellerID.astellerEmail for antrag in antraege_sitzung], # type: ignore
        reply_to=[EMAIL_TOOL, sitzung.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


def mailAstellerErgebnisAntrag(antrag: Antrag):
    """
    Sende dem Antragssteller eine Information über das Ergebnis seines Antrags
    Signal wird ausgelöst, wenn der Antrag eine BeschlussID zugewiesen bekommt
    """
    print("Mail => Ergebnis Beschluss an Antragsteller: ", antrag.astellerID.astellerName)
    
    message = get_template("emails/asteller/ergebnis_antrag.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Dein Antrag wurde beschlossen!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[antrag.astellerID.astellerEmail], # type: ignore
        reply_to=[EMAIL_TOOL, antrag.sitzID.refID.refEmail],
    )
    mail.content_subtype = "html"
    return mail.send()


#----------{ E-Mails an Referate }----------#

def mailReferatAntragEingegangen(antrag: Antrag):
    """
    Sende dem Referat eine Information über den Eingang eines neuen Antrags
    """
    print("Mail => Eingangsbestätigung an Referat: ", antrag.sitzID.refID.refName)
        
    # TODO: E-Mail Nachricht anpassen
    message = get_template("emails/referat/antrag_eingegangen.html").render({
        'antrag': antrag
    })
    mail = EmailMessage(
        subject="Ein neuer Antrag ist eingegangen!",
        body=message,
        from_email=EMAIL_TOOL,
        to=[antrag.sitzID.refID.refEmail],
        reply_to=[EMAIL_TOOL]
    )
    mail.content_subtype = "html"
    return mail.send()
