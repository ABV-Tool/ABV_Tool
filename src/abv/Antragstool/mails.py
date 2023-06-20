from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.template.loader import get_template
from django.db.models.signals import pre_save, post_save

from abv.settings import EMAIL_TOOL

from .models import Antrag, Referat, Sitzung


# TODO: Überlegungen zu weiteren E-Mails machen & StuRa fragen, ob die E-Mails so in Ordnung sind

#----------{ E-Mails an Antragssteller }----------#

# TODO: Binde Option ein, dass der Antragsteller seinen Antrag mit einem Token im Nachhinein bearbeiten kann
@receiver(post_save, sender=Antrag)
def mailAstellerEingangsbestaetigung(sender, instance: Antrag, **kwargs):
    """
    Sende dem Antragssteller eine Eingangsbestätigung für seinen Antrag
    """
    
    if instance.wurdeVertagt == False:
        print("Mail => Eingangsbestätigung an Antragsteller: ", instance.astellerID.astellerName)
        
        message = get_template("emails/asteller/eingangsbestaetigung_antrag.html").render({
            'antrag': instance
        })
        mail = EmailMessage(
            subject="Dein Antrag ist bei uns eingegangen!",
            body=message,
            from_email=EMAIL_TOOL,
            to=[instance.astellerID.astellerEmail], # type: ignore
            reply_to=[EMAIL_TOOL, instance.sitzID.refID.refEmail],
        )
        mail.content_subtype = "html"
        return mail.send()


@receiver(pre_save, sender=Antrag)
def mailAstellerVertagungAntrag(sender, instance: Antrag, **kwargs):
    """
    Sende dem Antragssteller eine Information über die Vertagung seines Antrags in eine andere Sitzung
    Signal wird ausgelöst, wenn der Antrag in eine andere Sitzung vertagt wird
    """
    
    # Prüfe, ob der Antrag bereits existiert (wenn nicht, dann ist es ein neuer Antrag)
    if Antrag.objects.filter(antragID=instance.antragID).exists():
        antrag_prev = Antrag.objects.get(antragID=instance.antragID)
    else:
        return
    
    # Prüfe, ob der Antrag in eine andere Sitzung vertagt wurde
    if instance.sitzID != antrag_prev.sitzID:
        print("Mail => Vertagung Antrag an Antragsteller: ", instance.astellerID.astellerName)
        
        # TODO: E-Mail Nachricht anpassen
        message = get_template("emails/asteller/vertagung_antrag.html").render({
            'antrag': instance
        })
        mail = EmailMessage(
            subject="Dein Antrag wurde in eine andere Sitzung vertagt!",
            body=message,
            from_email=EMAIL_TOOL,
            to=[instance.astellerID.astellerEmail], # type: ignore
            reply_to=[EMAIL_TOOL, instance.sitzID.refID.refEmail],
        )
        mail.content_subtype = "html"
        return mail.send()


@receiver(pre_save, sender=Sitzung)
def mailAstellerVertagungSitzung(sender, instance: Sitzung, **kwargs):
    """
    Sende dem Antragssteller eine Information über die Vertagung der Sitzung, in welcher sein Antrag ursprünglich behandelt werden sollte.
    """
    
    # Prüfe, ob die Sitzung bereits existiert (wenn nicht, dann ist es eine neue Sitzung)
    if Sitzung.objects.filter(sitzID=instance.sitzID).exists():
        vorherige_sitzung = Sitzung.objects.get(sitzID=instance.sitzID)
    else:
        return
    
    antraege_sitzung = Antrag.objects.filter(sitzID=instance.sitzID)
    
    # Prüfe, ob die Sitzung vertagt wurde
    if instance.sitzDate != vorherige_sitzung.sitzDate:
        
        print("Mail => Vertagung Sitzung an alle Antragsteller: ", [antrag.astellerID.astellerEmail for antrag in antraege_sitzung])
        
        # TODO: E-Mail Nachricht anpassen
        message = get_template("emails/asteller/vertagung_sitzung.html").render({
            'sitzung': instance,
            'antraege': antraege_sitzung
        })
        mail = EmailMessage(
            subject="Die Sitzung deines Antrages wurde vertagt!",
            body=message,
            from_email=EMAIL_TOOL,
            # Sende eine E-Mail an alle Antragssteller, deren Anträge in der vertagten Sitzung behandelt werden sollten
            to=[antrag.astellerID.astellerEmail for antrag in antraege_sitzung], # type: ignore
            reply_to=[EMAIL_TOOL, instance.refID.refEmail],
        )
        mail.content_subtype = "html"
        return mail.send()


@receiver(post_save, sender=Antrag)
def mailAstellerErgebnis(sender, instance: Antrag, **kwargs):
    """
    Sende dem Antragssteller eine Information über das Ergebnis seines Antrags
    Signal wird ausgelöst, wenn der Antrag eine BeschlussID zugewiesen bekommt
    """
    
    if instance.beschlussID and instance.beschlussID.beschlussErgebnis != 'Vertagt':
        print("Mail => Ergebnis Beschluss an Antragsteller: ", instance.astellerID.astellerName)
        
        # TODO: E-Mail Nachricht anpassen
        message = get_template("emails/asteller/ergebnis_antrag.html").render({
            'antrag': instance
        })
        mail = EmailMessage(
            subject="Dein Antrag wurde beschlossen!",
            body=message,
            from_email=EMAIL_TOOL,
            to=[instance.astellerID.astellerEmail], # type: ignore
            reply_to=[EMAIL_TOOL, instance.sitzID.refID.refEmail],
        )
        mail.content_subtype = "html"
        return mail.send()


#----------{ E-Mails an Referate }----------#

# TODO: Prüfe, ob der Antrag ein Eilantrag ist und verschicke eine andere E-Mail
@receiver(post_save, sender=Antrag)
def mailReferatAntragEingegangen(sender, instance: Antrag, created, **kwargs):
    """
    Sende dem Referat eine Information über den Eingang eines neuen Antrags
    """
    
    if instance.wurdeVertagt == False:
        print("Mail => Eingangsbestätigung an Referat: ", instance.sitzID.refID.refName)
        
        # TODO: E-Mail Nachricht anpassen
        message = get_template("emails/referat/antrag_eingegangen.html").render({
            'antrag': instance
        })
        mail = EmailMessage(
            subject="Ein neuer Antrag ist eingegangen!",
            body=message,
            from_email=EMAIL_TOOL,
            to=[instance.sitzID.refID.refEmail],
            reply_to=[]
        )
        mail.content_subtype = "html"
        return mail.send()
