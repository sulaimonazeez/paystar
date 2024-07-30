from django.contrib import admin
from .models import Profile, Balance, VirtualAccounting,UserProfiles, Development, Download, GeneratePin, AccountUpgrade


#admin.site.register(Profile)
admin.site.register(Balance)
admin.site.register(VirtualAccounting)
admin.site.register(UserProfiles)
admin.site.register(Development)
admin.site.register(Download)
admin.site.register(GeneratePin)
admin.site.register(AccountUpgrade)