
import os
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(
     sender, instance, reset_password_token, *args, **kwargs):
    # send an e-mail to the user

    # build a base url
    url = f'{os.environ.get("FRONTEND_CONNECT")}/auth/reset-password'
    context = {
        'user': reset_password_token.user,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            url,
            reset_password_token.key)
    }
    # url goes to frontend reset component. token is the key

    # render email text
    email_html_message = render_to_string(
        'email/password_reset_email.html', context)
    email_plaintext_message = render_to_string(
        'email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Junk Free Recipes"),
        # message:
        email_plaintext_message,
        # from:
        "junkfreerecipes@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
