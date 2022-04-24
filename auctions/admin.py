from django.contrib import admin
from .models import User, Watch_list, auction_listings,bid_record, comments
# Register your models here.
admin.site.register(User)
admin.site.register(Watch_list)
admin.site.register(auction_listings)
admin.site.register(bid_record)
admin.site.register(comments)
