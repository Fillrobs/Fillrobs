from django.conf.urls import url
from xui.aws_sg_edit import views

xui_urlpatterns = [
    url(
        r"^create_new_aws_sg/(?P<env_id>\d+)/$",
        views.create_new_aws_sg,
        name="create_new_aws_sg",
    ),
    url(
        r"^delete_aws_sg/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/$",
        views.delete_aws_sg,
        name="delete_aws_sg",
    ),
    url(
        r"^create_aws_sg_inbound/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/$",
        views.create_aws_sg_inbound,
        name="create_aws_sg_inbound",
    ),
    url(
        r"^delete_aws_sg_inbound/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/(?P<igresscnt>\d+)/(?P<ipProtocol>\d+)/(?P<fromPort>\d+)/(?P<toPort>\d+)/$",
        views.delete_aws_sg_inbound,
        name="delete_aws_sg_inbound",
    ),    
    url(
        r"^create_aws_sg_outbound/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/$",
        views.create_aws_sg_outbound,
        name="create_aws_sg_outbound",
    ),    
    url(
        r"^delete_aws_sg_outbound/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/(?P<egresscnt>\d+)/(?P<ipProtocol>\d+)/(?P<fromPort>\d+)/$",
        views.delete_aws_sg_outbound,
        name="delete_aws_sg_outbound",
    ),                                 
    url(
        r"^create_aws_sg_tag/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/$",
        views.create_aws_sg_tag,
        name="create_aws_sg_tag",
    ),
    url(
        r"^delete_aws_sg_tag/(?P<env_id>\d+)/(?P<aws_sg_id>\d+)/(?P<tag_key>\d+)/$",
        views.delete_aws_sg_tag,
        name="delete_aws_sg_tag",
    ),
]
