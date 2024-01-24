# from allauth.account.adapter import DefaultAccountAdapter

# class CustomAdapter(DefaultAccountAdapter):
#     def save_user(self, request, user, form, commit=True):
#         user = super().save_user(request, user, form, commit=False)
#         user.username = user.email  # Set username to email
#         if commit:
#             user.save()
#         return user